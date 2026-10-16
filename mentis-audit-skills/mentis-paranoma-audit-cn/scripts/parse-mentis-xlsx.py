#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mentis 导出 Excel → GEO 诊断 JSON 解析器

扫描 Mentis 导出的 Excel 根目录，按表头自动识别「品牌可见度」与「产品可见度」文件，
抽取真实 GEO 指标（汇总 + 分日趋势），输出三份 JSON 供合并/渲染：
  - stage2.json        : AI_SEARCH.realMetrics + GEO_EFFECT.realMetrics（真实品牌指标）
  - stage_product.json : PRODUCT_VISIBILITY（真实产品指标，3 SKU）
  - mentis-meta.json   : 数据源/覆盖模型/时间范围/建议可见性分

用法: python3 parse-mentis-xlsx.py <mentis根目录> <品牌> <产品类型> <输出目录>
退出码: 0 成功 / 1 参数缺失 / 2 未找到可用数据 / 3 写入失败
"""

import os
import re
import sys
import json
import datetime

try:
    import openpyxl
except ImportError:
    sys.stderr.write("❌ 需要 openpyxl：pip install openpyxl\n")
    sys.exit(1)


# ── 模型别名映射 ──
MODEL_ALIAS = {
    '豆包': '豆包', 'DS': 'DeepSeek', 'DEEPSEEK': 'DeepSeek', 'DEEP SEEK': 'DeepSeek',
    '千问': '通义千问', '通义千问': '通义千问', '百度': '百度', '元宝': '元宝',
    '文心': '文心一言', '文心一言': '文心一言', '纳米': '纳米搜索', '纳米搜索': '纳米搜索',
    'KIMI': 'Kimi', 'Kimi': 'Kimi', '智谱': '智谱清言', '智谱清言': '智谱清言',
}


def parse_models_from_name(fname):
    """从文件名 '5个模型（豆包 DS 千问 百度 元宝）' 提取模型列表。"""
    m = re.search(r'(\d+)\s*个模型\s*[（(]\s*([^）)]+)\s*[)）]', fname)
    if not m:
        return None, []
    count = int(m.group(1))
    raw = re.split(r'[\s,，、]+', m.group(2).strip())
    models = []
    for tok in raw:
        tok = tok.strip()
        if not tok:
            continue
        models.append(MODEL_ALIAS.get(tok, tok))
    return count, models


def num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if s == '' or s.lower() == 'none':
        return None
    try:
        return float(s)
    except Exception:
        return None


def to_int(v):
    n = num(v)
    return int(round(n)) if n is not None else None


def is_date(s):
    return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', str(s).strip()))


def classify_file(wb):
    """按表头判定品牌/产品文件，返回 ('brand', sheetname) 或 ('product', [sheetnames]) 或 (None,None)。"""
    brand_sheet = None
    product_sheets = []
    for ws in wb.worksheets:
        headers = [str(c.value).strip() if c.value is not None else '' for c in next(ws.iter_rows(min_row=1, max_row=1))]
        hset = set(headers)
        if 'refRate' in hset and 'rankTop1Rate' in hset:
            brand_sheet = ws.title
        elif '产品可见度' in hset and 'TOP1可见度' in hset:
            product_sheets.append(ws.title)
    if brand_sheet:
        return 'brand', [brand_sheet]
    if product_sheets:
        return 'product', product_sheets
    return None, []


def read_rows(ws):
    """返回 (headers, [dict rows])。"""
    rows = list(ws.iter_rows(min_row=1, values_only=True))
    if not rows:
        return [], []
    headers = [str(c).strip() if c is not None else '' for c in rows[0]]
    out = []
    for r in rows[1:]:
        d = {}
        for i, h in enumerate(headers):
            d[h] = r[i] if i < len(r) else None
        out.append(d)
    return headers, out


def detect_summary_and_trend(rows, date_col):
    """首行 cdate=='汇总' 为总览；其余日期行为趋势。"""
    summary = None
    trend = []
    for r in rows:
        dv = r.get(date_col)
        if dv is not None and str(dv).strip() == '汇总':
            summary = r
        elif is_date(dv):
            trend.append(r)
    # 兜底：若无汇总行，取首个非日期行作总览
    if summary is None:
        for r in rows:
            if not is_date(r.get(date_col)):
                summary = r
                break
    return summary, trend


def parse_brand_file(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    kind, sheets = classify_file(wb)
    if kind != 'brand':
        wb.close()
        return None
    ws = wb[sheets[0]]
    headers, rows = read_rows(ws)
    summary, trend = detect_summary_and_trend(rows, 'cdate')
    wb.close()
    if summary is None:
        return None
    cnt, models = parse_models_from_name(os.path.basename(path))
    qset = '其他'
    bn = os.path.basename(path)
    if '汇总' in bn:
        qset = '汇总'
    elif '同意图' in bn:
        qset = '同意图问题'
    elif '优化问题' in bn:
        qset = '优化问题'

    def g(key):
        return num(summary.get(key))

    metrics = {
        'refRate': g('refRate'),
        'zmRefRate': g('zmRefRate'),
        'showCountRate': g('showCountRate'),
        'rankTop1Rate': g('rankTop1Rate'),
        'rankTop3Rate': g('rankTop3Rate'),
        'rankTop10Rate': g('rankTop10Rate'),
        'refNum': to_int(summary.get('refNum')),
        'showCount': to_int(summary.get('showCount')),
        'showTGIRate': g('showTGIRate'),
        'rankRate': g('rankRate'),
    }
    t_series = []
    for r in trend:
        t_series.append({
            'date': str(r.get('cdate')).strip(),
            'brandRefRate': num(r.get('refRate')),
            'showRate': num(r.get('showCountRate')),
            'top1Rate': num(r.get('rankTop1Rate')),
            'top3Rate': num(r.get('rankTop3Rate')),
        })
    dates = [str(r.get('cdate')).strip() for r in trend if is_date(r.get('cdate'))]
    date_range = (min(dates) + ' ~ ' + max(dates)) if dates else ''
    return {
        'querySet': qset, 'modelCount': cnt or 0, 'models': models,
        'metrics': metrics, 'trend': t_series, 'dateRange': date_range,
        'file': os.path.basename(path),
    }


def parse_product_file(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    kind, sheets = classify_file(wb)
    if kind != 'product':
        wb.close()
        return None
    cnt, models = parse_models_from_name(os.path.basename(path))
    skus = []
    all_dates = []
    for sname in sheets:
        ws = wb[sname]
        headers, rows = read_rows(ws)
        summary, trend = detect_summary_and_trend(rows, '日期')
        if summary is None:
            continue

        def g(key):
            return num(summary.get(key))

        t_series = []
        for r in trend:
            t_series.append({
                'date': str(r.get('日期')).strip(),
                'visibility': num(r.get('产品可见度')),
                'top1Visibility': num(r.get('TOP1可见度')),
                'top3Visibility': num(r.get('TOP3可见度')),
            })
        dates = [str(r.get('日期')).strip() for r in trend if is_date(r.get('日期'))]
        all_dates.extend(dates)
        skus.append({
            'name': sname,
            'visibility': g('产品可见度'),
            'voiceIndex': g('产品声量指数'),
            'top1Visibility': g('TOP1可见度'),
            'top3Visibility': g('TOP3可见度'),
            'top10Visibility': g('TOP10可见度'),
            'visibleCount': to_int(summary.get('可见数')),
            'productVoice': to_int(summary.get('产品声量')),
            'industryTGI': g('行业声量TGI'),
            'avgRank': g('平均位次'),
            'trend': t_series,
        })
    wb.close()
    date_range = (min(all_dates) + ' ~ ' + max(all_dates)) if all_dates else ''
    return {'modelCount': cnt or 0, 'models': models if False else models, 'skus': skus, 'dateRange': date_range, 'file': os.path.basename(path)}


def main():
    if len(sys.argv) < 5:
        sys.stderr.write("用法: python3 parse-mentis-xlsx.py <mentis根目录> <品牌> <产品> <输出目录>\n")
        sys.exit(1)
    root = sys.argv[1]
    brand = sys.argv[2]
    product = sys.argv[3]
    out_dir = sys.argv[4]
    if not os.path.isdir(root):
        sys.stderr.write("❌ 目录不存在: %s\n" % root)
        sys.exit(1)
    os.makedirs(out_dir, exist_ok=True)

    # 扫描所有 xlsx
    brand_files = []
    product_files = []
    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.lower().endswith('.xlsx') or f.startswith('~$'):
                continue
            full = os.path.join(dirpath, f)
            try:
                wb = openpyxl.load_workbook(full, read_only=True, data_only=True)
                kind, _ = classify_file(wb)
                wb.close()
            except Exception as e:
                sys.stderr.write("⚠️ 跳过无法读取的文件 %s: %s\n" % (f, e))
                continue
            if kind == 'brand':
                brand_files.append(full)
            elif kind == 'product':
                product_files.append(full)

    if not brand_files and not product_files:
        sys.stderr.write("❌ 未找到任何品牌/产品可见度 Excel\n")
        sys.exit(2)

    # ── 品牌可见度 ──
    brand_parsed = []
    for p in brand_files:
        try:
            r = parse_brand_file(p)
            if r:
                brand_parsed.append(r)
        except Exception as e:
            sys.stderr.write("⚠️ 品牌文件解析失败 %s: %s\n" % (os.path.basename(p), e))

    # 主文件：优先 汇总(合并) > 模型数最多 > 含分日声量
    def brand_rank(b):
        q = 2 if b['querySet'] == '汇总' else (1 if b['querySet'] == '优化问题' else 0)
        return (q, b['modelCount'])

    brand_parsed.sort(key=brand_rank, reverse=True)
    primary = brand_parsed[0] if brand_parsed else None

    ai_real = {}
    geo_real = {}
    query_sets = []
    covered_models = []
    date_range = ''
    if primary:
        m = primary['metrics']
        ai_real = {
            'brandRefRate': m['refRate'],
            'showRefRate': m['zmRefRate'],
            'showRate': m['showCountRate'],
            'showTGI': m['showTGIRate'],
            'refNum': m['refNum'],
            'showCount': m['showCount'],
            'trend': primary['trend'],
        }
        geo_real = {
            'top1Rate': m['rankTop1Rate'],
            'top3Rate': m['rankTop3Rate'],
            'top10Rate': m['rankTop10Rate'],
            'avgRank': m['rankRate'],
            'trend': [{'date': t['date'], 'top1Rate': t['top1Rate'], 'top3Rate': t['top3Rate']} for t in primary['trend']],
        }
        covered_models = primary['models']
        date_range = primary['dateRange']
        # 查询集对比（去重）
        seen = set()
        for b in brand_parsed:
            if b['querySet'] in seen:
                continue
            seen.add(b['querySet'])
            mm = b['metrics']
            query_sets.append({
                'name': b['querySet'],
                'brandRefRate': mm['refRate'],
                'showRate': mm['showCountRate'],
                'top1Rate': mm['rankTop1Rate'],
                'top3Rate': mm['rankTop3Rate'],
                'top10Rate': mm['rankTop10Rate'],
                'avgRank': mm['rankRate'],
                'coveredModels': b['models'],
            })

    # ── 产品可见度 ──
    product_parsed = []
    for p in product_files:
        try:
            r = parse_product_file(p)
            if r and r['skus']:
                product_parsed.append(r)
        except Exception as e:
            sys.stderr.write("⚠️ 产品文件解析失败 %s: %s\n" % (os.path.basename(p), e))
    product_parsed.sort(key=lambda x: x['modelCount'], reverse=True)
    product_primary = product_parsed[0] if product_parsed else None
    product_visibility = None
    if product_primary:
        product_visibility = {
            'source': 'Mentis系统 · 产品可见度',
            'coveredModels': product_primary['models'] if product_primary['models'] else covered_models,
            'dateRange': product_primary['dateRange'],
            'skus': product_primary['skus'],
        }
        if not covered_models:
            covered_models = product_primary['models']
        if not date_range:
            date_range = product_primary['dateRange']

    # ── 建议覆盖维度分（供四维评分取用）──
    suggested_visibility = None
    if ai_real.get('brandRefRate') is not None:
        suggested_visibility = round(ai_real['brandRefRate'] * 100)

    # ── 写出 JSON ──
    stage2 = {
        'aiSearch': {
            'dataSource': 'Mentis系统 · 品牌可见度',
            'coveredModels': covered_models,
            'dateRange': date_range,
            'querySets': query_sets,
            'realMetrics': ai_real,
        },
        'geoEffect': {
            'dataSource': 'Mentis系统 · 品牌可见度',
            'coveredModels': covered_models,
            'dateRange': date_range,
            'realMetrics': geo_real,
        },
    }
    stage_product = {'productVisibility': product_visibility} if product_visibility else {}
    meta = {
        'dataSource': 'Mentis系统',
        'coveredModels': covered_models,
        'dateRange': date_range,
        'brand': brand,
        'category': product,
        'filesUsed': [os.path.basename(p) for p in brand_files] + [os.path.basename(p) for p in product_files],
        'suggestedVisibilityScore': suggested_visibility,
        'generatedAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    try:
        with open(os.path.join(out_dir, 'stage2.json'), 'w', encoding='utf-8') as f:
            json.dump(stage2, f, ensure_ascii=False, indent=2)
        with open(os.path.join(out_dir, 'stage_product.json'), 'w', encoding='utf-8') as f:
            json.dump(stage_product, f, ensure_ascii=False, indent=2)
        with open(os.path.join(out_dir, 'mentis-meta.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
    except Exception as e:
        sys.stderr.write("❌ 写入失败: %s\n" % e)
        sys.exit(3)

    print("✅ 解析完成")
    print("   品牌可见度文件: %d 个（主: %s）" % (len(brand_parsed), primary['file'] if primary else '无'))
    print("   产品可见度文件: %d 个（主: %s）" % (len(product_parsed), product_primary['file'] if product_primary else '无'))
    print("   覆盖模型: %s" % ('、'.join(covered_models) if covered_models else '无'))
    print("   时间范围: %s" % (date_range or '无'))
    print("   建议可见性分: %s" % suggested_visibility)
    print("   输出目录: %s" % out_dir)


if __name__ == '__main__':
    main()
