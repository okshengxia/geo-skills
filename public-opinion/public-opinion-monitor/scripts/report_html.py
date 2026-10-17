#!/usr/bin/env python3
"""生成单文件 HTML 舆情报告（无外部依赖，SVG 图表内联，可直接分享）。

用法:
  python3 report_html.py <pom-analyzed-*.json> [-o report.html]

输入为 analyze.py 产出的 analyzed.json（含 health_score 与 items）。
"""
import argparse
import html
import json
import math
from collections import Counter
from datetime import datetime

RED, ORANGE, YELLOW, GREEN, GRAY = "#e74c3c", "#f39c12", "#f1c40f", "#2ecc71", "#95a5a6"
SENTI_COLOR = {"positive": GREEN, "negative": RED, "controversial": ORANGE, "neutral": GRAY}


def esc(s):
    return html.escape(str(s or ""))


def score_arc(score):
    angle = math.pi * (1 - score / 100)
    x, y = 100 + 80 * math.cos(angle), 100 - 80 * math.sin(angle)
    large = 1 if score > 50 else 0
    color = GREEN if score >= 80 else ORANGE if score >= 60 else RED
    return f'''<svg width="200" height="120" viewBox="0 0 200 120">
<path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#eee" stroke-width="16" stroke-linecap="round"/>
<path d="M 20 100 A 80 80 0 {large} 1 {x:.1f} {y:.1f}" fill="none" stroke="{color}" stroke-width="16" stroke-linecap="round"/>
<text x="100" y="88" text-anchor="middle" font-size="40" font-weight="bold" fill="{color}">{score}</text>
<text x="100" y="112" text-anchor="middle" font-size="12" fill="#888">舆情健康分 / 100</text></svg>'''


def donut(counter, total):
    r, cx, cy, acc = 70, 100, 100, -90
    paths = []
    for senti, n in counter.most_common():
        frac = n / total if total else 0
        if frac <= 0:
            continue
        a2 = acc + frac * 360
        large = 1 if frac > 0.5 else 0
        x1, y1 = cx + r * math.cos(math.radians(acc)), cy + r * math.sin(math.radians(acc))
        x2, y2 = cx + r * math.cos(math.radians(a2 - 0.6)), cy + r * math.sin(math.radians(a2 - 0.6))
        paths.append(f'<path d="M {cx} {cy} L {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 1 {x2:.1f} {y2:.1f} Z" '
                     f'fill="{SENTI_COLOR[senti]}" opacity="0.85"/>')
        acc = a2
    legend = " ".join(f'<span style="margin:0 8px"><i style="display:inline-block;width:10px;height:10px;'
                      f'background:{SENTI_COLOR[s]};border-radius:2px"></i> {s} {n}</span>'
                      for s, n in counter.most_common())
    return f'<svg width="200" height="200" viewBox="0 0 200 200">{"".join(paths)}</svg><p>{legend}</p>'


def bars(counter, color=GRAY):
    mx = max(counter.values()) if counter else 1
    rows = "".join(f'<div class="bar-row"><span class="bar-label">{esc(k)}</span>'
                   f'<div class="bar" style="width:{v / mx * 70}%;background:{color}"></div>'
                   f'<span class="bar-num">{v}</span></div>' for k, v in counter.most_common())
    return f'<div>{rows}</div>'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default="opinion-report.html")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)
    items, meta = data["items"], data.get("meta", {})
    score = data.get("health_score", 100)
    events = data.get("events", [])
    total = len(items)
    senti = Counter(it.get("sentiment", "neutral") for it in items)
    heat = Counter(it.get("hot_level", "weak") for it in items)
    plats = Counter(it["platform"] for it in items)
    negs = [it for it in items if it.get("sentiment") in ("negative", "controversial")]
    top = items[:10]

    def rows(lst):
        return "".join(
            f'<tr><td>{esc(it["platform"])}{" 🆕" if it.get("is_new") else ""}</td>'
            f'<td><a href="{esc(it.get("url"))}" target="_blank">{esc((it.get("title_or_text") or "")[:60])}</a></td>'
            f'<td>{it["metrics"]["engagement_total"]:,}</td>'
            f'<td><span class="tag" style="background:{SENTI_COLOR[it.get("sentiment", "neutral")]}">{esc(it.get("sentiment"))}</span></td>'
            f'<td>{esc(it.get("hot_level"))}</td><td>{esc(it.get("alert_level", ""))}</td></tr>'
            for it in lst)

    neg_rows = "".join(
        f'<tr class="neg"><td><b>[{esc(it.get("alert_level", "中"))}]</b> {esc(it["platform"])}</td>'
        f'<td><a href="{esc(it.get("url"))}" target="_blank">{esc((it.get("title_or_text") or "")[:60])}</a></td>'
        f'<td>{esc(it.get("sentiment_reason"))}</td></tr>'
        for it in sorted(negs, key=lambda x: {"紧急": 0, "高": 1, "中": 2, "低": 3}.get(x.get("alert_level"), 3)))

    ev_html = "".join(
        f'<div class="event"><b>{esc(e["id"])}</b> {esc((e.get("title") or "")[:50])} '
        f'<span class="muted">（{e["count"]} 条｜{"、".join(e.get("platforms", []))}｜{esc(e.get("phase"))}）</span></div>'
        for e in events)

    doc = f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<title>舆情报告：{esc(meta.get('keywords', ''))}</title>
<style>
body{{font-family:-apple-system,'PingFang SC',sans-serif;max-width:960px;margin:24px auto;padding:0 16px;color:#333}}
h1{{font-size:22px}} h2{{font-size:16px;border-left:4px solid #4a90d9;padding-left:8px;margin-top:32px}}
table{{width:100%;border-collapse:collapse;font-size:13px}} td,th{{border-bottom:1px solid #eee;padding:7px 6px;text-align:left}}
tr.neg td{{background:#fdf0ef}} .tag{{color:#fff;border-radius:3px;padding:1px 6px;font-size:11px}}
.cards{{display:flex;gap:24px;flex-wrap:wrap}} .muted{{color:#999;font-size:12px}}
.bar-row{{display:flex;align-items:center;margin:4px 0}} .bar{{height:14px;border-radius:3px}}
.bar-label{{width:110px;font-size:12px;color:#666}} .bar-num{{margin-left:8px;font-size:12px;color:#666}}
.event{{padding:6px 0;border-bottom:1px dashed #eee;font-size:13px}}
a{{color:#4a90d9;text-decoration:none}} .meta{{color:#888;font-size:13px}}
</style></head><body>
<h1>舆情监测报告：{esc(meta.get('keywords', ''))}</h1>
<p class="meta">范围 {esc(meta.get('range', '24h'))}｜平台 {esc(','.join(meta.get('platforms', [])))}｜生成 {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
<div class="cards">
<div>{score_arc(score)}</div>
<div>{donut(senti, total)}</div>
<div><h3 style="margin:4px 0">条目规模</h3><p style="font-size:28px;margin:4px">{total}</p>
<p class="muted">去重后条目（原始 {esc(meta.get('raw_count', total))}）</p>
<h3 style="margin:12px 0 4px">平台分布</h3>{bars(plats)}</div>
</div>
<h2>热点榜 Top {len(top)}</h2>
<table><tr><th>平台</th><th>标题（点击看原文）</th><th>互动</th><th>情感</th><th>热度</th><th>预警</th></tr>{rows(top)}</table>
<h2>负面预警（{len(negs)} 条）</h2>
{'<table><tr><th>级别/平台</th><th>标题</th><th>理由</th></tr>' + neg_rows + '</table>' if neg_rows else '<p class="muted">无负面内容，舆情整体平稳。</p>'}
<h2>事件时间线</h2>
{ev_html if ev_html else '<p class="muted">本次未识别出多来源事件簇。</p>'}
<h2>热度分布</h2>{bars(heat, '#4a90d9')}
<p class="meta">数据来源：各平台公开接口与页面采集，详见 analyzed.csv｜生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</body></html>"""
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"HTML 报告已生成: {args.output}")


if __name__ == "__main__":
    main()
