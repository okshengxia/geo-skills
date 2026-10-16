# Mentis 导出数据 → 报告字段映射（mentis-geo-report）

> 本 skill 的数据优先取自 **Mentis 系统导出 Excel**。本文档固化目录约定、列→指标映射与解析规则，供 `scripts/parse-mentis-xlsx.py` 与渲染模板共用。

## 一、目录与文件约定

运行时用户传入一个**文件夹**（Mentis 导出根目录），脚本自动扫描两个子目录：

```
<mentis导出根目录>/
├── 品牌可见度/        ← 品牌级 GEO 指标（sheet 名固定为 a2）
│   ├── 【优化问题】分日声量 4.24 - 7.19 - 4个模型（豆包 DS 千问 百度）.xlsx
│   ├── 【同意图问题】分日声量 6.22 - 7.19 - 5个模型（豆包 DS 千问 百度 元宝）.xlsx
│   ├── 【汇总】优化问题+同意图 - 4.24 - 7.19 - 5个模型（豆包 DS 千问 百度 元宝）.xlsx
│   └── ...（可能含 TOP1/TOP3 分日声量、外溢对比等变体）
└── 产品可见度/        ← 单品级 GEO 指标（sheet 名 = 具体 SKU）
    ├── [3款产品] 4.24 -7 19 【优化问题】4大模型.xlsx
    └── [3款产品] 4.24 -7 19 【优化问题】5大模型.xlsx
```

- **模型集识别**：从文件名 `(\d+)个模型（…）` 提取，如 `5个模型（豆包 DS 千问 百度 元宝）` → `[豆包, DeepSeek, 通义千问, 百度, 元宝]`。
- **时间范围**：取所有分日行的 `cdate`/`日期` 最小~最大值。
- **主文件选择**：品牌可见度优先选文件名含「汇总」且模型数最多者作头条；其余按查询集（优化问题 / 同意图问题）归并作对比。产品可见度优先选模型数最多者。

## 二、品牌可见度（→ 报告 AI_SEARCH + GEO_EFFECT 两章）

Sheet `a2`，列：`cdate, brand, refRate, zmRefRate, showCountRate, rankTop1Rate, rankTop3Rate, rankTop10Rate, refNum, showCount, showTGIRate, rankRate, model`

首行 `cdate='汇总'` 为总览值，其余 `cdate` 形如 `2026-07-19` 为分日趋势。

| 列名 | 报告中文名 | 落入 stage | 说明 |
|------|-----------|-----------|------|
| `refRate` | 品牌引用率 | AI_SEARCH.realMetrics.brandRefRate | 核心 GEO 指标，AI 回答中提及品牌的比例 |
| `zmRefRate` | 展示引用率 | AI_SEARCH.realMetrics.showRefRate | ⚠️ 口径待与主子最终确认（疑似加权/展示位引用率） |
| `showCountRate` | 展示率/曝光率 | AI_SEARCH.realMetrics.showRate | 品牌被展示的比例 |
| `showTGIRate` | 展示 TGI（相对行业） | AI_SEARCH.realMetrics.showTGI | 相对行业均值的展示强度 |
| `refNum` | 引用次数 | AI_SEARCH.realMetrics.refNum | 累计引用计数 |
| `showCount` | 展示次数 | AI_SEARCH.realMetrics.showCount | 累计展示计数 |
| `rankTop1Rate` | TOP1 占比 | GEO_EFFECT.realMetrics.top1Rate | 排第 1 名的比例 |
| `rankTop3Rate` | TOP3 占比 | GEO_EFFECT.realMetrics.top3Rate | 进前 3 的比例 |
| `rankTop10Rate` | TOP10 占比 | GEO_EFFECT.realMetrics.top10Rate | 进前 10 的比例 |
| `rankRate` | 平均排名 | GEO_EFFECT.realMetrics.avgRank | 数值越低越好 |
| `cdate` | 日期 | *.realMetrics.trend[].date | 趋势横轴 |

> 建议派生：AI 可引用内容覆盖维度分 `suggestedVisibilityScore = round(brandRefRate × 100)`，供四维评分取用。

## 三、产品可见度（→ PRODUCT_VISIBILITY，保留在品牌目录供审计，不单独成章）

Sheet = 具体 SKU（如 `鱼油乳铁蛋白中老年奶粉`）。列：`日期, 产品可见度, 产品声量指数, TOP1可见度, TOP3可见度, TOP10可见度, 可见数, 产品声量, 行业声量TGI, 平均位次, AI模型`

| 列名 | 报告中文名 | 落入字段 | 说明 |
|------|-----------|---------|------|
| `产品可见度` | 产品可见度 | sku.visibility | 该 SKU 被 AI 提及/展示的比例 |
| `产品声量指数` | 产品声量指数 | sku.voiceIndex | 声量强度指数 |
| `TOP1可见度` | TOP1 可见度 | sku.top1Visibility | 该 SKU 排第 1 的比例 |
| `TOP3可见度` | TOP3 可见度 | sku.top3Visibility | 进前 3 的比例 |
| `TOP10可见度` | TOP10 可见度 | sku.top10Visibility | 进前 10 的比例 |
| `可见数` | 可见数 | sku.visibleCount | 累计可见计数 |
| `产品声量` | 产品声量 | sku.productVoice | 累计声量计数 |
| `行业声量TGI` | 行业声量 TGI | sku.industryTGI | 相对行业均值的声量强度 |
| `平均位次` | 平均位次 | sku.avgRank | 数值越低越好 |
| `日期` | 日期 | sku.trend[].date | 趋势横轴 |

## 四、缺覆盖维度的处理

`USER_PROFILE / INFRA_EVAL / COMPETITOR / SENTIMENT` 四类在 Mentis 导出中无对应字段，按主子决策**保持原技能逻辑**（WebSearch + 虚拟推演）兜底，由 agent 产出 `stage1.json` / `stage3.json`，渲染沿用原模板函数，不作改造。

## 五、解析输出契约（JSON）

`parse-mentis-xlsx.py` 写三份文件到输出目录：

- `stage2.json`：`{ aiSearch:{ realMetrics, dataSource, coveredModels, dateRange, querySets, trend }, geoEffect:{ realMetrics, ... } }`
- `stage_product.json`：`{ productVisibility:{ source, coveredModels, dateRange, skus:[...] } }`
- `mentis-meta.json`：`{ dataSource, coveredModels, dateRange, filesUsed, suggestedVisibilityScore, generatedAt }`

`merge-stages.js` 扩展后将上述并入最终 `stages.PRODUCT_VISIBILITY` 与 `mentisMeta`；渲染模板读取 `realMetrics` 与 `productVisibility` 渲染真实数据看板。
