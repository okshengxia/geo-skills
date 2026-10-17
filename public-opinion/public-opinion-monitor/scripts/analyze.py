#!/usr/bin/env python3
"""舆情条目确定性分析 v2：去重、事件聚类、健康分、预警分级、快照环比。

用法:
  python3 analyze.py <pom-*.json> [--top-n 10] [--outdir /tmp] [--store DIR]

输入 JSON: SKILL.md 第 3 步的统一数据结构 {meta, items}
输出（--outdir，文件名带时间戳）:
  - analyzed.json        去重排序后完整数据（含 is_new / alert_level / event_id）
  - analyzed.csv         原始数据表（UTF-8 BOM）
  - report-data.md       报告数据块：健康分/总览/环比/热点榜/预警分级/事件时间线
  - （快照自动存入 --store，默认 ~/.public-opinion-monitor/snapshots/，
     下次同关键词运行自动作为 baseline 计算环比与"首次出现"标记）
"""
import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_STORE = Path.home() / ".public-opinion-monitor" / "snapshots"


def norm_text(s):
    return re.sub(r"[\s\W_]+", "", (s or "").lower())


def bigrams(s):
    s = norm_text(s)
    return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) > 1 else {s}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def engagement(item):
    m = item.get("metrics") or {}
    return int(m.get("engagement_total") or
               (m.get("likes") or 0) + (m.get("comments") or 0) + (m.get("reposts") or 0) or 0)


def reclassify_heat(item):
    m = item.get("metrics") or {}
    rank = m.get("rank")
    eng = engagement(item)
    platform = item.get("platform", "")
    if platform.startswith("weibo") and isinstance(rank, int) and rank <= 20:
        return "hotspot"
    if platform.startswith("douyin") and isinstance(rank, int) and rank <= 10:
        return "hotspot"
    if eng >= 10000:
        return "hotspot"
    if eng >= 100:
        return "normal"
    return "weak"


def dedup(items):
    """URL 精确去重 + 跨平台标题指纹合并（Jaccard≥0.85）。"""
    seen_urls, merged, fingerprints, dropped = set(), [], [], 0
    for it in items:
        url = (it.get("url") or "").split("?")[0]
        if url and url in seen_urls:
            dropped += 1
            continue
        fp = bigrams(it.get("title_or_text", ""))
        dup = next((i for i, (_, f) in enumerate(fingerprints) if fp and jaccard(fp, f) >= 0.85), None)
        if dup is not None:
            dropped += 1
            tgt = merged[dup]
            tgt.setdefault("metrics", {})["engagement_total"] = max(engagement(tgt), engagement(it))
            tgt.setdefault("synced_from", []).append(it.get("platform", ""))
            continue
        if url:
            seen_urls.add(url)
        merged.append(it)
        if fp:
            fingerprints.append((id(it), fp))
    return merged, dropped


def parse_time(item):
    t = item.get("published_at") or ""
    try:
        return datetime.fromisoformat(t.replace("Z", "+00:00"))
    except ValueError:
        return None


def cluster_events(items, keywords="", containment=0.55):
    """把条目聚成事件簇：标题包含度 ≥0.55，或共享 ≥8 个二元组且同含监测关键词。
    （新闻标题常在原报道基础上扩写，字符 Jaccard 会偏低，故用 min 包含度为主。）"""
    kw = norm_text(keywords)[:6]
    clusters = []  # [(centroid_fp, [items])]
    for it in sorted(items, key=lambda x: x.get("published_at") or ""):
        fp = bigrams(it.get("title_or_text", ""))
        placed = False
        for c in clusters:
            inter = len(fp & c[0])
            contain = inter / min(len(fp), len(c[0])) if fp and c[0] else 0
            same_kw = bool(kw) and kw in norm_text(it.get("title_or_text", "")) and kw in norm_text(c[1][0].get("title_or_text", ""))
            if contain >= containment or (same_kw and inter >= 8):
                c[1].append(it)
                placed = True
                break
        if not placed:
            clusters.append((fp, [it]))
    out = []
    for i, (_, group) in enumerate(sorted(clusters, key=lambda c: -len(c[1])), 1):
        if len(group) >= 2:
            for it in group:
                it["event_id"] = f"E{i:02d}"
            out.append((f"E{i:02d}", group))
    return out


def event_phase(group):
    times = sorted(t for t in (parse_time(it) for it in group) if t)
    if not times:
        return "未知"
    now = datetime.now(timezone.utc) if times[-1].tzinfo else datetime.now()
    since_last = now - times[-1]
    span = times[-1] - times[0]
    if span.total_seconds() < 6 * 3600:
        return "苗头期"
    if since_last.total_seconds() > 48 * 3600:
        return "消退期"
    if since_last.total_seconds() > 24 * 3600:
        return "回落期"
    return "发酵期" if len(group) >= 3 else "活跃期"


def event_line(eid, group):
    times = sorted(t for t in (parse_time(it) for it in group) if t)
    span = f"{(times[-1] - times[0]).total_seconds() / 3600:.0f}h" if len(times) >= 2 else "<1h"
    plats = ",".join(dict.fromkeys(it["platform"] for it in group))
    senti = Counter(it.get("sentiment", "neutral") for it in group)
    top = max(group, key=engagement)
    return (f"- **{eid}**「{(top.get('title_or_text') or '')[:30]}…」 "
            f"{len(group)}条/{plats}/{span}｜阶段：{event_phase(group)}｜"
            f"情感：负{senti['negative']} 正{senti['positive']} 中{senti['neutral']} 争{senti['controversial']}｜"
            f"峰值互动 {engagement(top):,}")


def health_score(items):
    """互动量加权情感分：100=全好评。争议按 0.5 权重计负。"""
    if not items:
        return 100
    w_pos = w_neg = w_all = 0.0
    for it in items:
        w = 1 + (engagement(it) ** 0.5) / 100  # 平滑权重：互动越大声音越大
        if it["platform"] in ("news",) or "KOL观点" in it.get("tags", []):
            w *= 1.5  # 媒体/KOL 声量放大
        s = it.get("sentiment", "neutral")
        w_all += w
        if s == "negative":
            w_neg += w
        elif s == "controversial":
            w_neg += w * 0.5
        elif s == "positive":
            w_pos += w
    if w_all == 0:
        return 100
    score = 100 - (w_neg / w_all) * 100
    return max(0, min(100, round(score)))


def alert_levels(negatives, all_items, heat_of):
    neg_share = len(negatives) / len(all_items) if all_items else 0
    for it in negatives:
        h = it.get("hot_level")
        cross_platform = bool(it.get("synced_from")) or h == "hotspot"
        if h == "hotspot" and (neg_share > 0.3 or "官方通报" in it.get("tags", [])):
            it["alert_level"] = "紧急"
        elif cross_platform and it.get("sentiment") == "negative":
            it["alert_level"] = "高"
        elif h == "normal":
            it["alert_level"] = "中"
        else:
            it["alert_level"] = "低"
    return negatives


def load_baseline(meta, store):
    """找同关键词最近一次快照（加载发生在本次保存之前，天然不含当次）。"""
    key = hashlib.md5(str(sorted(str(k) for k in re.split(r"[,,，]", meta.get("keywords", "")))).encode()).hexdigest()[:10]
    candidates = sorted(store.glob(f"snap-{key}-*.json"))
    if not candidates:
        return None, key
    with open(candidates[-1], encoding="utf-8") as f:
        return json.load(f), key


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--top-n", type=int, default=10)
    ap.add_argument("--outdir", default="/tmp")
    ap.add_argument("--store", default=str(DEFAULT_STORE))
    ap.add_argument("--no-store", action="store_true", help="不读写快照库（不产生环比）")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)
    items, meta = data.get("items", []), data.get("meta", {})
    if not items:
        print("输入 JSON 无 items")
        sys.exit(1)

    merged, dropped = dedup(items)
    for it in merged:
        it.setdefault("platform", "unknown")
        it["hot_level"] = reclassify_heat(it)
        it.setdefault("metrics", {})["engagement_total"] = engagement(it)

    # baseline 环比
    base, key = (None, "") if args.no_store else load_baseline(meta, Path(args.store))
    if base:
        prev_fps = [bigrams(it.get("title_or_text", "")) for it in base["items"]]
        prev_urls = {(it.get("url") or "").split("?")[0] for it in base["items"]}
        for it in merged:
            u = (it.get("url") or "").split("?")[0]
            fp = bigrams(it.get("title_or_text", ""))
            it["is_new"] = not (u in prev_urls or any(fp and jaccard(fp, f) >= 0.85 for f in prev_fps))

    events = cluster_events(merged, meta.get("keywords", ""))
    negatives = [it for it in merged if it.get("sentiment") in ("negative", "controversial")]
    alert_levels(negatives, merged, None)
    score = health_score(merged)

    sent_rank = {"negative": 0, "controversial": 1, "neutral": 2, "positive": 3}
    heat_rank = {"hotspot": 0, "normal": 1, "weak": 2}
    merged.sort(key=lambda it: (sent_rank.get(it.get("sentiment"), 2),
                                heat_rank.get(it.get("hot_level"), 2), -it["metrics"]["engagement_total"]))
    total, top = len(merged), merged[: args.top_n]

    senti = Counter(it.get("sentiment", "neutral") for it in merged)
    pct = lambda n: f"{n / total * 100:.0f}%" if total else "0%"
    heat = Counter(it["hot_level"] for it in merged)
    new_neg = [it for it in negatives if it.get("is_new")]
    stamps = [t for t in (parse_time(it) for it in merged) if t]
    range_note = (f"{(max(stamps) - min(stamps)).total_seconds() / 3600:.0f} 小时跨度" if len(stamps) >= 2 else "")

    now_iso = datetime.now(timezone.utc).isoformat()
    if not args.no_store:
        store = Path(args.store)
        store.mkdir(parents=True, exist_ok=True)
        with open(store / f"snap-{key}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json", "w", encoding="utf-8") as f:
            json.dump({"saved_at": now_iso, "meta": meta, "items": merged}, f, ensure_ascii=False)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base_p = f"{args.outdir}/pom-analyzed-{stamp}"
    meta_out = dict(meta)
    meta_out["raw_count"] = len(items)
    with open(base_p + ".json", "w", encoding="utf-8") as f:
        json.dump({"meta": meta_out, "health_score": score, "items": merged,
                   "events": [{"id": eid, "phase": event_phase(group), "count": len(group),
                               "title": max(group, key=engagement).get("title_or_text", ""),
                               "platforms": list(dict.fromkeys(it["platform"] for it in group)),
                               "sentiment": dict(Counter(it.get("sentiment", "neutral") for it in group))}
                              for eid, group in events]}, f, ensure_ascii=False, indent=1)

    fields = ["platform", "title_or_text", "url", "author", "published_at",
              "engagement_total", "sentiment", "sentiment_reason", "hot_level", "alert_level", "is_new", "tags"]
    with open(base_p + ".csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for it in merged:
            w.writerow([it.get("platform"), it.get("title_or_text"), it.get("url"), it.get("author"),
                        it.get("published_at"), it["metrics"]["engagement_total"], it.get("sentiment"),
                        it.get("sentiment_reason"), it.get("hot_level"), it.get("alert_level", ""),
                        it.get("is_new", ""), ",".join(it.get("tags", []))])

    L = [
        f"## 舆情健康分：{score} / 100（{('🟢 良好' if score >= 80 else '🟡 一般' if score >= 60 else '🔴 风险')}，"
        f"互动量与 KOL 加权计算）", "",
        f"- 采集条目：原始 {len(items)} 条 → 去重后 {total} 条（合并/剔除 {dropped} 条）{('，' + range_note) if range_note else ''}",
        f"- 情感占比：正面 {pct(senti['positive'])}｜负面 {pct(senti['negative'])}｜中性 {pct(senti['neutral'])}｜争议 {pct(senti['controversial'])}",
        f"- 热度分布：hotspot {heat['hotspot']}｜normal {heat['normal']}｜weak {heat['weak']}",
        f"- 负面预警：{len(negatives)} 条" + (f"（🆕 首次出现 {len(new_neg)} 条）" if base else ""),
    ]
    if base:
        prev_total = len(base["items"])
        prev_senti = Counter(it.get("sentiment", "neutral") for it in base["items"])
        prev_neg_share = prev_senti["negative"] / prev_total * 100 if prev_total else 0
        delta = senti["negative"] / total * 100 - prev_neg_share
        L.append(f"- 环比上次（{base['saved_at'][:10]}）：条目 {prev_total}→{total}，负面占比 {prev_neg_share:.0f}%→{senti['negative'] / total * 100:.0f}%（{'↑' if delta >= 0 else '↓'}{abs(delta):.0f}pct）")
    if senti["negative"] / total < 0.05:
        L.append("- ⚠️ 负面占比 <5%，舆情整体平稳")

    L += ["", f"## 热点榜 Top {len(top)}",
          "| # | 平台 | 标题/摘要 | 发布时间 | 互动量 | 情感 | 热度 | 预警 |",
          "|---|------|-----------|----------|--------|------|------|------|"]
    for i, it in enumerate(top, 1):
        flag = ("🆕" if it.get("is_new") else "") + it.get("alert_level", "")
        L.append(f"| {i} | {it.get('platform')} | {(it.get('title_or_text') or '')[:40]} | "
                 f"{it.get('published_at', '')} | {it['metrics']['engagement_total']:,} | "
                 f"{it.get('sentiment')} | {it.get('hot_level')} | {flag} |")

    if negatives:
        order = {"紧急": 0, "高": 1, "中": 2, "低": 3}
        L += ["", "## 负面预警（按级别排序）", ""]
        for lv in ("紧急", "高", "中", "低"):
            group = [it for it in negatives if it.get("alert_level") == lv]
            for it in group:
                newmark = " 🆕首次出现" if it.get("is_new") else ""
                L.append(f"- **[{lv}]** [{it['platform']}] {(it.get('title_or_text') or '')[:50]} — "
                         f"{it.get('url', '')}（理由：{it.get('sentiment_reason', '')}）{newmark}")
    if events:
        L += ["", "## 事件时间线", ""]
        for eid, group in events:
            L.append(event_line(eid, group))

    report = "\n".join(L)
    with open(base_p + "-report-data.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(f"分析完成: {len(items)} → {total} 条（去重 {dropped}），健康分 {score}/100，事件簇 {len(events)}")
    print(f"  输出: {base_p}.json / .csv / -report-data.md")
    print("\n" + report)


if __name__ == "__main__":
    main()
