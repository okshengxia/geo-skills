#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mentis2-intentmap-seed-questions 生成脚本（参数化版本）

基于小红书/巨量引擎两大平台的「以词推词」原始表格 + Brandinfo品牌卖点，
生成符合GEO搜索优化的品牌种子问题池。

用法:
  python generate_seed_questions.py \
    --input /path/to/以词推词结果.xlsx \
    --brandinfo "海天薄盐醇香生抽：原粒黄豆一级酿造..." \
    --output-dir /path/to/output/ \
    --expected 1000 \
    --brand-name 海天薄盐生抽

或从文件读取 brandinfo:
  python generate_seed_questions.py \
    --input /path/to/以词推词结果.xlsx \
    --brandinfo-file /path/to/brandinfo.txt \
    --output-dir /path/to/output/ \
    --expected 1000 \
    --brand-name 海天薄盐生抽
"""

import argparse
import os
import re
import sys
from datetime import datetime

import pandas as pd


# ========== 搜索意图信号（定义1）==========
INTENT_PATTERNS = [
    r'怎么', r'如何', r'哪种', r'什么', r'推荐', r'价格', r'多少钱',
    r'区别', r'对比', r'vs', r'品牌', r'排名', r'排行榜', r'送礼',
    r'选购', r'哪个好', r'测评', r'评测', r'做法', r'配方', r'好用',
    r'值得', r'适合', r'需要', r'可以', r'有吗', r'是吗', r'好吗',
    r'怎么样', r'好不好', r'买', r'选', r'用', r'吃', r'做',
    r'.*的.*推荐', r'.*推荐.*', r'.*哪个.*', r'.*怎么.*', r'.*如何.*',
    r'.*什么.*', r'.*好吗.*', r'.*怎么样.*', r'.*值得.*', r'.*适合.*'
]

# 意图动作词（用户明确在"求"某物，而非品类名词本身）
INTENT_ACTION_WORDS = [
    '推荐', '做法', '配方', '吃法', '搭配',
    '区别', '对比', '功效', '作用',
    '选购', '测评', '评测', '排行',
    '必备', '大全',
]

# 疑问尾缀
QUESTION_SUFFIX = ['吗', '呢', '？', '?', '好不好', '怎么样']


def has_intent_signal(text):
    """
    检查是否包含搜索意图信号（严格按定义1）
    意图信号 = 疑问词/需求词/场景词/对比词/选购词/品类+动词组合
    纯品类名词（如"调料""炒菜""酱料"）不算意图信号，必须剔除
    """
    if pd.isna(text):
        return False
    text = str(text).strip()
    if not text:
        return False

    # 1) 正则意图信号
    for pattern in INTENT_PATTERNS:
        if re.search(pattern, text):
            return True

    # 2) 显式意图动作词
    for word in INTENT_ACTION_WORDS:
        if word in text:
            return True

    # 3) 疑问尾缀
    for suf in QUESTION_SUFFIX:
        if suf in text:
            return True

    # 4) 纯品类名词、纯场景词、纯菜名 → 不通过
    return False


def get_intent_gap_reason(text):
    """分析文本缺少哪些意图信号，返回可读的原因描述"""
    if pd.isna(text):
        return '文本为空'
    text = str(text).strip()
    if not text:
        return '文本为空'

    gaps = []
    if not any(re.search(p, text) for p in INTENT_PATTERNS):
        gaps.append('不含疑问词/需求词/对比词等意图模式(怎么/如何/什么/推荐/价格等)')
    if not any(w in text for w in INTENT_ACTION_WORDS):
        gaps.append('不含动作词(推荐/攻略/评测/对比等)')
    if not any(s in text for s in QUESTION_SUFFIX):
        gaps.append('不含疑问尾缀(吗/呢/？等)')

    return '；'.join(gaps) if gaps else '未知原因'


def load_excel_data(input_path):
    """读取 Excel 文件，返回两个平台的 DataFrame"""
    xl = pd.ExcelFile(input_path)
    sheet_names = xl.sheet_names

    # 自动识别 sheet
    xhs_name = next((s for s in sheet_names if '小红书' in s), None)
    jl_name = next((s for s in sheet_names if '巨量' in s), None)

    if not all([xhs_name, jl_name]):
        raise ValueError(f"无法识别平台sheet，请检查Excel。现有sheets: {sheet_names}")

    xiaohongshu = pd.read_excel(input_path, sheet_name=xhs_name)
    juliang = pd.read_excel(input_path, sheet_name=jl_name)

    for df in [xiaohongshu, juliang]:
        unnamed_cols = [c for c in df.columns if str(c).startswith('Unnamed')]
        if unnamed_cols:
            df.drop(columns=unnamed_cols, inplace=True)

    xiaohongshu['平台'] = '小红书'
    juliang['平台'] = '巨量引擎'
    return xiaohongshu, juliang


def step1_clean(xiaohongshu, juliang, temp_dir):
    """Step 1: 基础数据清洗 - 剔除相关性=不相关"""
    print("=" * 60)
    print("Step 1: 基础数据清洗")
    print("=" * 60)

    total_orig = len(xiaohongshu) + len(juliang)
    print(f"原始数据量：小红书 {len(xiaohongshu)}, 巨量引擎 {len(juliang)}, 总计 {total_orig}")

    # 筛出不相关数据
    xhs_removed = xiaohongshu[xiaohongshu['相关性'] == '不相关'].copy()
    jl_removed = juliang[juliang['相关性'] == '不相关'].copy()

    xhs_removed['删除原因'] = '平台标注为「不相关」，与目标品牌/产品无关联'
    jl_removed['删除原因'] = '平台标注为「不相关」，与目标品牌/产品无关联'

    removed_data = pd.concat([xhs_removed, jl_removed], ignore_index=True)
    if len(removed_data) > 0:
        removed_data.to_csv(os.path.join(temp_dir, '_step1_removed.csv'),
                            index=False, encoding='utf-8-sig')

    xhs_clean = xiaohongshu[xiaohongshu['相关性'] != '不相关'].copy()
    jl_clean = juliang[juliang['相关性'] != '不相关'].copy()

    total_clean = len(xhs_clean) + len(jl_clean)
    print(f"剔除'不相关'后：小红书 {len(xhs_clean)}, 巨量引擎 {len(jl_clean)}, 总计 {total_clean}")
    print(f"淘汰数据: {len(removed_data)} 条 (已保存到 temp/_step1_removed.csv)")

    all_data = pd.concat([xhs_clean, jl_clean], ignore_index=True)
    print(f"\nStep 1 输出: 清洗后剩余 {len(all_data)} 行")
    return all_data


def step2_filter_valid(all_data, temp_dir):
    """Step 2: 筛选有效种子问题"""
    print("\n" + "=" * 60)
    print("Step 2: 筛选有效种子问题")
    print("=" * 60)

    all_data['有意图信号'] = all_data['推荐词'].apply(has_intent_signal)
    valid_data = all_data[all_data['有意图信号'] == True].copy()
    removed_data = all_data[all_data['有意图信号'] == False].copy()

    # 生成针对性的删除原因
    def build_step2_reason(row):
        word = str(row['推荐词'])
        relevance = str(row.get('相关性', ''))
        gap = get_intent_gap_reason(word)

        type_label = {
            '品类词': '纯品类名词',
            '场景词': '纯场景词',
            '品牌词': '品牌名词',
            '需求词': '平台标注需求词但',
        }.get(relevance, '未知类型')

        return f'{type_label}「{word}」，{gap}'

    if len(removed_data) > 0:
        removed_data['删除原因'] = removed_data.apply(build_step2_reason, axis=1)
        removed_data.to_csv(os.path.join(temp_dir, '_step2_removed.csv'),
                            index=False, encoding='utf-8-sig')

    print(f"有效种子问题: {len(valid_data)}")
    print(f"淘汰数据: {len(removed_data)} 条 (已保存到 temp/_step2_removed.csv)")
    print(f"\nStep 2 输出: 筛选后剩余 {len(valid_data)} 行")
    return valid_data


def step3_deduplicate(valid_data, temp_dir):
    """Step 3: 去重合并"""
    print("\n" + "=" * 60)
    print("Step 3: 去重合并")
    print("=" * 60)

    before_count = len(valid_data)

    # 找出重复的推荐词（同一词在多个平台或同平台出现多次）
    dup_counts = valid_data['推荐词'].value_counts()
    dup_words = dup_counts[dup_counts > 1].index.tolist()

    # 记录被合并的重复项
    removed_records = []
    for word in dup_words:
        word_rows = valid_data[valid_data['推荐词'] == word].sort_values(
            '搜索热度', ascending=False)
        platforms = word_rows['平台'].tolist()
        heats = word_rows['搜索热度'].tolist()
        relevances = word_rows['相关性'].tolist()
        removed_records.append({
            '推荐词': word,
            '相关性': relevances[0],
            '重复次数': len(word_rows),
            '涉及平台': '、'.join(platforms),
            '各平台热度': '、'.join(str(h) for h in heats),
            '删除原因': f'跨平台/同平台重复({len(word_rows)}条)，已合并为一行，热度取各平台最大值',
        })

    if removed_records:
        removed_df = pd.DataFrame(removed_records)
        removed_df.to_csv(os.path.join(temp_dir, '_step3_removed.csv'),
                          index=False, encoding='utf-8-sig')

    pivot_data = valid_data.pivot_table(
        index='推荐词', columns='平台', values='搜索热度', aggfunc='max'
    ).reset_index()
    pivot_data.columns.name = None

    column_map = {'小红书': '小红书热度', '巨量引擎': '巨量引擎热度'}
    for old, new in column_map.items():
        if old in pivot_data.columns:
            pivot_data = pivot_data.rename(columns={old: new})
        if new not in pivot_data.columns:
            pivot_data[new] = 0

    for col in ['小红书热度', '巨量引擎热度']:
        pivot_data[col] = pivot_data[col].fillna(0)

    merged_count = before_count - len(pivot_data)
    print(f"去重前: {before_count} 行")
    print(f"重复词: {len(dup_words)} 个，合并 {merged_count} 条")
    print(f"去重后: {len(pivot_data)} 行")
    if removed_records:
        print(f"淘汰数据: {len(removed_records)} 条 (已保存到 temp/_step3_removed.csv)")
    print(f"\nStep 3 输出: 去重后剩余 {len(pivot_data)} 行")
    return pivot_data


def step4_heat_calc(pivot_data):
    """Step 4: 热度计算 & 排序"""
    print("\n" + "=" * 60)
    print("Step 4: 热度计算 & 排序")
    print("=" * 60)

    # 综合热度 = 小红书热度 + 巨量引擎热度
    pivot_data['综合热度'] = (
        pivot_data['小红书热度'] + pivot_data['巨量引擎热度']
    )

    def get_hottest_platform(row):
        xhs = row['小红书热度']
        jl = row['巨量引擎热度']
        if xhs >= jl and xhs > 0:
            return '小红书'
        elif jl > 0:
            return '巨量引擎'
        return '小红书'

    pivot_data['最热平台'] = pivot_data.apply(get_hottest_platform, axis=1)
    pivot_data = pivot_data.sort_values('综合热度', ascending=False).reset_index(drop=True)

    print(f"热度计算完成，最高热度: {pivot_data['综合热度'].max():.0f}")
    print(f"本步不删除数据，仅计算综合热度并排序")
    print(f"\nStep 4 输出: 排序后总数据 {len(pivot_data)} 行")
    return pivot_data


def extract_brand_keywords(brandinfo):
    """从 brandinfo 中提取品牌关键词"""
    brand_keywords_5 = []
    brand_name_short = None

    # 提取冒号前的品牌产品名
    lines = brandinfo.strip().split('\n')
    for line in lines:
        if '：' in line or ':' in line:
            sep = '：' if '：' in line else ':'
            name_part = line.split(sep)[0].strip()
            if len(name_part) >= 2:
                brand_keywords_5.append(name_part)
                if len(name_part) >= 2:
                    brand_name_short = name_part[:2]

    if brand_name_short:
        brand_keywords_5.append(brand_name_short)

    # 核心卖点词
    advantage_signals = [
        '减盐', '0添加', '零添加', '有机', '低盐', '轻盐',
        '无防腐剂', '无蔗糖', '无碘', '配料表', '酿造', '特级', '头道',
        '原粒黄豆', '黄豆酿造', '防腐剂', '蔗糖', '碘', '三高',
        '健康调味', '健康饮食', '健康调料',
        '生抽 推荐', '酱油 推荐', '生抽 哪个', '酱油 哪个',
        '生抽 品牌', '酱油 品牌', '生抽 排行', '酱油 排行',
        '生抽 测评', '酱油 测评', '生抽 对比', '酱油 对比',
        '生抽 价格', '酱油 价格', '生抽 怎么', '酱油 怎么',
        '生抽 做法', '酱油 做法', '生抽 选购', '酱油 选购',
        '特级酱油', '特级生抽', '头道酱油', '头道生抽',
        '酿造酱油', '酿造生抽', '有机酱油', '有机生抽',
        '0添加酱油', '0添加生抽', '零添加酱油', '零添加生抽',
        '减盐酱油', '减盐生抽', '薄盐酱油', '薄盐生抽',
        '轻盐酱油', '轻盐生抽', '健康酱油', '健康生抽',
        '无碘酱油', '无碘生抽', '无蔗糖酱油', '无蔗糖生抽',
        '配料表干净', '配料表简单',
    ]

    advantage_keywords_4 = []
    for signal in advantage_signals:
        if signal.replace(' ', '') in brandinfo:
            advantage_keywords_4.append(signal)

    # 品类词（3分）
    category_keywords_3 = [
        '酱油', '生抽', '调味品', '调料', '调味', '厨房调味',
        '炒菜', '凉拌', '烹饪', '厨房', '家庭', '美味', '鲜味', '提鲜',
        '家常菜', '美食', '料理', '下厨', '佐料', '调味料',
        '蚝油', '老抽', '料酒', '醋', '酱料', '酱汁',
    ]

    # 通用知识词（2分）
    general_keywords_2 = [
        '食谱', '做法', '教程', '自制', '怎么做好吃', '技巧',
        '窍门', '秘诀', '攻略', '菜单', '菜谱'
    ]

    return brand_keywords_5, advantage_keywords_4, category_keywords_3, general_keywords_2


def step5_brand_scoring(pivot_data, brandinfo, temp_dir):
    """Step 5: 品牌露出评分"""
    print("\n" + "=" * 60)
    print("Step 5: 品牌露出评分")
    print("=" * 60)

    brand_kws_5, adv_kws_4, cat_kws_3, gen_kws_2 = extract_brand_keywords(brandinfo)

    print(f"品牌关键词(5分): {brand_kws_5[:5]}...")
    print(f"优势关键词(4分): {len(adv_kws_4)} 个")
    print(f"品类关键词(3分): {len(cat_kws_3)} 个")

    def score_brand_exposure(text):
        if pd.isna(text):
            return 1, 'high', '无法自然植入品牌'

        text = str(text).strip()
        text_lower = text.lower()

        # 5分: 意图直接指向品牌
        for bk in brand_kws_5:
            if bk and bk in text:
                if any(k in text for k in ['薄盐', '生抽', '酱油', '0添加', '零添加', '有机', '减盐']):
                    return 5, 'high', '直接推荐品牌薄盐生抽系列产品'
                elif '蚝油' in text:
                    return 5, 'high', '以品牌蚝油为引展开薄盐生抽品牌线'
                else:
                    return 5, 'high', '顺势展开品牌薄盐生抽品牌线'

        # 4分: 意图指向品牌核心优势
        for kw in adv_kws_4:
            if kw.lower() in text_lower or kw in text:
                if '减盐' in text or '低盐' in text or '轻盐' in text:
                    return 4, 'high', '以减盐技术为卖点推荐薄盐生抽'
                elif '0添加' in text or '零添加' in text or '配料表' in text:
                    return 4, 'high', '以0添加纯净配方切入推荐'
                elif '有机' in text:
                    return 4, 'high', '推荐有机酱油系列彰显品质'
                elif '特级' in text or '头道' in text:
                    return 4, 'high', '以特级头道酿造工艺为卖点'
                elif '酿造' in text:
                    return 4, 'high', '强调原粒黄豆酿造工艺优势'
                elif '推荐' in text or '哪个' in text or '品牌' in text:
                    return 4, 'high', '在选购推荐中突出海天品牌'
                elif '价格' in text or '多少钱' in text:
                    return 4, 'high', '对比价位时推荐品牌性价比'
                elif '测评' in text or '评测' in text:
                    return 4, 'high', '测评场景中展示薄盐生抽优势'
                elif '做法' in text or '配方' in text:
                    return 4, 'high', '食谱中自然融入薄盐生抽用法'
                else:
                    return 4, 'medium', '结合酿造工艺优势自然露出品牌'

        # 3分: 意图指向品类
        for kw in cat_kws_3:
            if kw.lower() in text_lower or kw in text:
                if '凉拌' in text:
                    return 3, 'high', '凉拌场景中推荐薄盐生抽提鲜'
                elif '炒菜' in text:
                    return 3, 'high', '炒菜场景中自然带出品牌'
                elif '火锅' in text or '蘸料' in text or '蘸水' in text:
                    return 3, 'high', '火锅蘸料场景中推荐品牌调味'
                elif '家常' in text:
                    return 3, 'high', '家常菜场景推荐健康调味'
                elif '厨房' in text:
                    return 3, 'high', '厨房必备调料清单中出场'
                elif '美食' in text:
                    return 3, 'high', '美食分享中融入品牌推荐'
                elif '蚝油' in text:
                    return 3, 'high', '蚝油话题中延伸至薄盐生抽'
                elif '酱油' in text or '生抽' in text:
                    return 3, 'high', '作为健康酱油代表推荐出场'
                else:
                    return 3, 'high', '品牌作为健康酱油代表在推荐列表出场'

        # 2分: 意图偏向通用知识
        for kw in gen_kws_2:
            if kw in text:
                return 2, 'medium', '烹饪演示中不经意使用品牌调味'

        # 食品/餐饮相关词
        food_related = ['菜', '肉', '鱼', '鸡', '蛋', '汤', '面', '饭', '餐', '食材', '料理']
        if any(fw in text for fw in food_related):
            return 2, 'low', '美食场景中顺带提及品牌'

        return 1, 'high', '无法自然植入品牌'

    scores = pivot_data['推荐词'].apply(score_brand_exposure)
    pivot_data['品牌露出机会'] = [s[0] for s in scores]
    pivot_data['置信度'] = [s[1] for s in scores]
    pivot_data['品牌如何露出'] = [s[2] for s in scores]

    print("\n品牌露出评分分布:")
    print(pivot_data['品牌露出机会'].value_counts().sort_index())

    review_data = pivot_data[pivot_data['置信度'].isin(['medium', 'low'])].copy()
    review_data.to_csv(os.path.join(temp_dir, '_brand_exposure_review.csv'),
                       index=False, encoding='utf-8-sig')
    print(f"\nMedium/Low 置信度条目: {len(review_data)} (已保存到 temp/_brand_exposure_review.csv)")

    print(f"本步不删除数据，仅打分。1分条目将在 Step 6 被剔除。")
    print(f"\nStep 5 输出: 评分完成，总计 {len(pivot_data)} 行")
    return pivot_data


def step6_filter_output(pivot_data, expected_count, temp_dir):
    """Step 6: 筛选输出 & 回捞"""
    print("\n" + "=" * 60)
    print("Step 6: 筛选输出 & 回捞")
    print("=" * 60)

    # 第一轮: 只保留5或4分
    round1 = pivot_data[pivot_data['品牌露出机会'].isin([5, 4])].copy()
    print(f"第一轮 (5/4分): {len(round1)} 条")

    final_data = round1.copy()
    selected_indices = set(round1.index.tolist())

    # 第二轮: 回捞3分
    round2_taken = pd.DataFrame()
    if len(final_data) < expected_count:
        needed = expected_count - len(final_data)
        round2_candidates = pivot_data[pivot_data['品牌露出机会'] == 3].copy()
        round2_taken = round2_candidates.head(needed)
        final_data = pd.concat([final_data, round2_taken], ignore_index=True)
        selected_indices.update(round2_taken.index.tolist())
        print(f"回捞3分: 补入 {len(round2_taken)} 条")

    # 第三轮: 回捞2分
    round3_taken = pd.DataFrame()
    if len(final_data) < expected_count:
        needed = expected_count - len(final_data)
        round3_candidates = pivot_data[pivot_data['品牌露出机会'] == 2].copy()
        round3_taken = round3_candidates.head(needed)
        final_data = pd.concat([final_data, round3_taken], ignore_index=True)
        selected_indices.update(round3_taken.index.tolist())
        print(f"回捞2分: 补入 {len(round3_taken)} 条")

    # 记录未被选入的条目
    removed_mask = ~pivot_data.index.isin(selected_indices)
    removed_data = pivot_data[removed_mask].copy()

    # 生成删除原因
    def build_step6_reason(row):
        score = row['品牌露出机会']
        word = str(row['推荐词'])
        heat = row['综合热度']
        if score == 1:
            return f'品牌露出=1分，意图与品牌基本无关，无法自然植入「{word}」'
        elif score == 3:
            return f'品牌露出=3分(指向品类)，综合热度{heat:.0f}不足以进入回捞范围'
        elif score == 2:
            return f'品牌露出=2分(偏向通用知识)，综合热度{heat:.0f}不足以进入回捞范围'
        else:
            return f'品牌露出={score}分，未被选入'

    if len(removed_data) > 0:
        removed_data['删除原因'] = removed_data.apply(build_step6_reason, axis=1)
        removed_data.to_csv(os.path.join(temp_dir, '_step6_removed.csv'),
                            index=False, encoding='utf-8-sig')

    final_data = final_data.sort_values('综合热度', ascending=False).reset_index(drop=True)

    print(f"\n最终输出: {len(final_data)} 条")
    print(f"淘汰数据: {len(removed_data)} 条 (已保存到 temp/_step6_removed.csv)")
    print(f"评分分布:")
    print(final_data['品牌露出机会'].value_counts().sort_index())

    return final_data


def format_output(final_data):
    """格式化输出"""
    score_labels = {
        5: "5.意图直指品牌",
        4: "4.指向品牌核心优势",
        3: "3.指向品类",
        2: "2.偏向通用知识"
    }

    final_data['品牌露出机会_格式化'] = final_data['品牌露出机会'].map(score_labels)

    output_df = final_data[['推荐词', '综合热度', '最热平台', '品牌露出机会_格式化', '品牌如何露出']].copy()
    output_df.columns = ['种子问题', '综合热度', '最热平台', '品牌露出机会', '品牌如何露出']

    # 品牌如何露出不超过25字
    output_df['品牌如何露出'] = output_df['品牌如何露出'].apply(
        lambda x: x[:25] if len(str(x)) > 25 else x
    )

    return output_df


def main():
    parser = argparse.ArgumentParser(
        description='生成GEO搜索优化的品牌种子问题池',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --input data.xlsx --brandinfo "海天薄盐生抽：..." --brand-name 海天薄盐生抽
  %(prog)s --input data.xlsx --brandinfo-file brandinfo.txt --output-dir ./out --expected 1000
        """
    )
    parser.add_argument('--input', required=True, help='Excel文件路径（以词推词结果）')
    parser.add_argument('--brandinfo', help='品牌卖点文本（直接传入）')
    parser.add_argument('--brandinfo-file', help='品牌卖点文本文件路径')
    parser.add_argument('--output-dir', default='.', help='输出目录（默认当前目录）')
    parser.add_argument('--expected', type=int, default=1000, help='期望输出条数（默认1000）')
    parser.add_argument('--brand-name', default='品牌', help='品牌名（用于文件命名，默认"品牌"）')

    args = parser.parse_args()

    # 获取 brandinfo
    brandinfo = ''
    if args.brandinfo:
        brandinfo = args.brandinfo
    elif args.brandinfo_file:
        with open(args.brandinfo_file, 'r', encoding='utf-8') as f:
            brandinfo = f.read().strip()
    else:
        print("警告: 未提供 brandinfo，将降级为默认关键词评分", file=sys.stderr)

    # 创建输出目录和temp目录
    temp_dir = os.path.join(args.output_dir, 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    # 读取数据
    print(f"输入文件: {args.input}")
    print(f"输出目录: {args.output_dir}")
    print(f"期望条数: {args.expected}")
    print(f"品牌名: {args.brand_name}")
    print()

    xiaohongshu, juliang = load_excel_data(args.input)

    # 六步流程
    all_data = step1_clean(xiaohongshu, juliang, temp_dir)
    valid_data = step2_filter_valid(all_data, temp_dir)
    pivot_data = step3_deduplicate(valid_data, temp_dir)
    pivot_data = step4_heat_calc(pivot_data)
    pivot_data = step5_brand_scoring(pivot_data, brandinfo, temp_dir)
    final_data = step6_filter_output(pivot_data, args.expected, temp_dir)

    # 格式化输出
    output_df = format_output(final_data)

    print("\n" + "=" * 60)
    print("最终数据预览")
    print("=" * 60)
    print(output_df.head(20).to_string())

    # 保存文件
    month_day = datetime.now().strftime("%m%d")
    output_file = os.path.join(args.output_dir, f'{args.brand_name}_种子问题池_{month_day}.csv')
    output_df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"\n文件已保存: {output_file}")

    # 全流程校验数据
    print("\n" + "=" * 60)
    print("全流程校验数据")
    print("=" * 60)
    print(f"Step 1 清洗后: {len(all_data)} 行 (淘汰 → temp/_step1_removed.csv)")
    print(f"Step 2 筛选后: {len(valid_data)} 行 (淘汰 → temp/_step2_removed.csv)")
    print(f"Step 3 去重后: {len(pivot_data)} 行 (合并 → temp/_step3_removed.csv)")
    print(f"Step 4 排序后: {len(pivot_data)} 行 (不删除数据)")
    score_counts = pivot_data['品牌露出机会'].value_counts().sort_index()
    print(f"Step 5 评分后: {len(pivot_data)} 行 (5分:{score_counts.get(5,0)}, 4分:{score_counts.get(4,0)}, 3分:{score_counts.get(3,0)}, 2分:{score_counts.get(2,0)}, 1分:{score_counts.get(1,0)})")
    print(f"Step 6 最终输出: {len(final_data)} 行 (淘汰 → temp/_step6_removed.csv)")
    print(f"\n最终文件: {output_file}")
    print(f"中间文件:")
    print(f"  temp/_step1_removed.csv      (Step 1 淘汰: 不相关数据)")
    print(f"  temp/_step2_removed.csv      (Step 2 淘汰: 无意图信号数据)")
    print(f"  temp/_step3_removed.csv      (Step 3 合并: 重复词条)")
    print(f"  temp/_brand_exposure_review.csv (Step 5 待复核: medium/low置信度)")
    print(f"  temp/_step6_removed.csv      (Step 6 淘汰: 未被选入最终输出)")


if __name__ == '__main__':
    main()
