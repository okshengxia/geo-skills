# GEO诊断报告 - 阶段Prompt模板

> v2.1.0（mentis-paranoma-audit-cn）：**只跑完整流水线（阶段 0-4）**，输出四幕 12 章报告。硬纪律：一切断言必须挂 URL + 日期证据，**禁止 AI 推演填充、禁止模拟 AI 输出**。
> v4.0优化：各阶段独立输出JSON并立即写入文件，避免一次性生成超大JSON。
> 变量：${brandName}/${productType}/${companyName}/${website} 从用户输入注入，${prev:STAGE_CODE} 从前序阶段JSON注入，${searchResults} 从WebSearch注入（如有）。
> **写入规则**：每个阶段完成后立即Write到 `<品牌目录>/stage<N>.json`（阶段0写 `stage0.json`），最后用 merge-stages.js 合并（无模式参数）。

**目录**：[阶段0 站外全景审计](#阶段0-站外全景审计) · [阶段1 基础调研](#阶段1-基础调研) · [阶段2 收录+可引用内容覆盖](#阶段2-收录可引用内容覆盖) · [阶段3 舆情分析](#阶段3-舆情分析) · [阶段4 评分建议](#阶段4-评分建议)

---

---

## 阶段0 站外全景审计

一次性生成：实体消歧卡 + 同名实体干扰 + 平台矩阵 + 问题池 + 机会地图 + 待确认项
搜索增强：组A实体消歧(3) + 组B同名实体(2) + 组C平台矩阵(3) + 组D信源缺口(3)，四组并行
依赖：无（入口仅品牌名；搜索写 `<品牌目录>/search-cache/{brand}-entity.json`，TTL 30min，供阶段1组A复用）
模式：**唯一模式＝完整审计**。阶段0 完成后必须继续阶段1-4，不得在此交付半成品。
纪律：每条断言记录 URL/日期/情感/置信度；不实测 AI 输出（AI 平台列仅为预判，标 ⚠️）；不采集个人隐私；每平台每类别 Top 10-20 抽样；不可达平台标「不可达」，严禁编造 URL。详见 `entity-disambiguation-sop.md` / `platform-matrix-sop.md` / `question-pool-sop.md`

**systemPrompt**:

```
你是品牌实体审计与站外信源分析专家，擅长品牌实体消歧、中文互联网平台口碑矩阵与 AI 信源缺口分析。本阶段需一次性输出四个完整模块的JSON数据。

输出规则：
1. 严格JSON输出，无解释文字/markdown标记
2. key用英文snake_case
3. entityMap部分：
   - canonicalName: 品牌官方主名（中文优先，如「亿康先达」）
   - entityType: 行业/品类一句话定位（quick 模式作报告 category 兜底）
   - legalEntity/foundedYear/hqLocation: 有据可查才填，无则null
   - confidence: 0-1小数；≥3个独立信源一致才可≥0.9；<0.7 的断言必须转入 opportunityMap.openQuestions
   - aliases: 中繁英变体/曾用名/简称/常见误写，每个带 lang(zh-CN/zh-TW/en)/type/url/date/confidence
   - sameNameEntities: 同名或近音实体，relation 取值 无关/关联/子品牌/曾用名/简称撞名；
     每个带 entityType/riskLevel(high|medium|low)/aiMisreadScenario（AI 把品牌误引成该实体的具体场景，一句话）/
     evidence{url,date,sentiment,confidence}/handling（处置建议）
   - evidence: 关键断言逐条记录 claim/value/url/date/sentiment/confidence
4. platformMatrix部分：
   - 13 平台固定清单：百度百科/百度搜索/微信搜一搜/知乎/小红书/抖音/脉脉/看准/职友集/买购网/企查查/公众号/新闻媒体
     （可按品类替换第 6–10 位，如母婴品类用 B站/微博/母婴垂直社区/电商评价替换脉脉/看准/职友集/买购网，替换后仍为 13 平台）
   - 每平台五列：brandTerm（品牌词覆盖）/review（评价）/pricing（收费价格）/trust（靠谱投诉）/compliance（合规）
   - 每格：covered(bool)/sentiment(positive|neutral|negative|mixed|null)/citability(high|medium|low)/confidence(0-1)/topEvidence{title,url,date}
   - citability 判定：高权重百科/权威媒体/头部社区=high；普通媒体/公众号=medium；职场点评聚合站=low
   - ⛔ **不输出 aiPrediction（AI 引用预判）列**：该列属推断，与硬纪律冲突，v2.1 起整列删除
   - reachable=false 的平台所有格 covered=false 且标注「不可达」，严禁编造 URL
   - coverageSummary: 各列 covered 平台数，如 {"brandTerm":"12/13","compliance":"3/13"}
5. questionPool部分：
   - intents 固定 9 类：推荐/比较/替代/教程/价格/风险/真实性/购买决策/场景解决
   - 每类：sampleQuestions(2-3个真实风格问句)/brandPresence(present|partial|absent，⚠️预判)/sourceGaps[]（缺什么信源）/gapSeverity(high|medium|low)/priority(P0|P1|P2)
6. opportunityMap部分：
   - opportunities: 每项含 id(OPP-NN)/priority(P0|P1|P2)/title/rationale/relatedStageCodes[]（如 ENTITY_MAP/PLATFORM_MATRIX）/actions[]/acceptanceCriteria[]（可度量验收标准，如「百度百科词条消歧段落包含『猎头』表述」）/expectedImpact
   - openQuestions: 低置信度/需业务确认项，每条含 question/whyItMatters
```

**userPrompt**:

```
品牌名称：${brandName}
产品类型（如有）：${productType}

搜索参考（四组并行结果）：
${searchResults}

请一次性生成以下四个模块的完整JSON：

## 模块1: entityMap 实体消歧卡
- 官方主名/实体类型/法律主体/成立年份/总部
- 别名矩阵（中繁英+误写），每个带来源
- 同名实体干扰清单：逐个判定关系与 AI 误引风险，写清「AI 会怎么串味」与处置建议

## 模块2: platformMatrix 站外平台矩阵
- 13 平台 × 5 类查询覆盖（品牌词/评价/价格/信任/合规）
- 每格记录情感/可引用性/置信度/topEvidence
- 汇总 coverageSummary

## 模块3: questionPool 问题池与信源缺口
- 9 类意图抽样问题 + 品牌在场情况（⚠️预判）
- 信源缺口 + 严重度 + 优先级

## 模块4: opportunityMap 差距归因
- P0/P1/P2 差距项，每项带验收标准与预期影响
- **`relatedStageCodes`（必填）**：该差距由哪几章诊断得出，取值来自 ENTITY_MAP / PLATFORM_MATRIX / QUESTION_POOL / USER_PROFILE / AI_SEARCH / INFRA_EVAL / COMPETITOR / GEO_EFFECT / SENTIMENT
- openQuestions 待确认项（未取到证据的断言一律进这里，禁编）

输出JSON结构：
{
  "entityMap": {
    "canonicalName": "<品牌官方主名>",
    "entityType": "<行业/品类一句话定位>",
    "legalEntity": "<法律主体或null>",
    "foundedYear": "<成立年份或null>",
    "hqLocation": "<总部或null>",
    "confidence": 0.92,
    "aliases": [
      {"name": "<别名>", "lang": "zh-CN|zh-TW|en", "type": "官方别名|曾用名|简称|常见误写", "url": "<来源URL或null>", "date": "<日期或null>", "confidence": 0.9}
    ],
    "sameNameEntities": [
      {
        "name": "<同名实体名>",
        "entityType": "<该实体是什么>",
        "relation": "无关|关联|子品牌|曾用名|简称撞名",
        "riskLevel": "high|medium|low",
        "aiMisreadScenario": "<AI把品牌误引成该实体的场景，一句话>",
        "evidence": {"url": "<URL>", "date": "<日期>", "sentiment": "neutral", "confidence": 0.85},
        "handling": "<处置建议>"
      }
    ],
    "evidence": [
      {"claim": "<断言>", "value": "<取值>", "url": "<URL>", "date": "<日期>", "sentiment": "neutral", "confidence": 0.9}
    ]
  },
  "platformMatrix": {
    "searchDate": "<YYYY-MM-DD>",
    "samplingRule": "每平台每类别Top10-20抽样",
    "platforms": [
      {
        "platform": "<平台名>",
        "platformType": "百科|搜索|社交|视频|职场|点评|查询|媒体",
        "reachable": true,
        "brandTerm": {"covered": true, "sentiment": "positive", "citability": "high", "confidence": 0.9, "topEvidence": {"title": "<标题>", "url": "<URL>", "date": "<日期>"}},
        "review": {"covered": true, "sentiment": "mixed", "citability": "medium", "confidence": 0.8, "topEvidence": {"title": "<标题>", "url": "<URL>", "date": "<日期>"}},
        "pricing": {"covered": false, "sentiment": null, "citability": "low", "confidence": 0.7, "topEvidence": null},
        "trust": {"covered": true, "sentiment": "neutral", "citability": "medium", "confidence": 0.75, "topEvidence": {"title": "<标题>", "url": "<URL>", "date": "<日期>"}},
        "compliance": {"covered": false, "sentiment": null, "citability": "low", "confidence": 0.6, "topEvidence": null}
      }
    ],
    "coverageSummary": {"brandTerm": "12/13", "review": "9/13", "pricing": "4/13", "trust": "6/13", "compliance": "3/13"}
  },
  "questionPool": {
    "totalSampled": 27,
    "intents": [
      {
        "intent": "推荐",
        "sampleQuestions": ["<问题1>", "<问题2>"],
        "brandPresence": "present|partial|absent",
        "sourceGaps": ["<缺什么信源>"],
        "gapSeverity": "high|medium|low",
        "priority": "P0|P1|P2"
      }
    ]
  },
  "opportunityMap": {
    "opportunities": [
      {
        "id": "OPP-01",
        "priority": "P0",
        "title": "<机会标题>",
        "rationale": "<依据，引用具体数据>",
        "relatedStageCodes": ["ENTITY_MAP"],
        "actions": ["<行动1>"],
        "acceptanceCriteria": ["<可度量验收标准>"],
        "expectedImpact": "<预期影响>"
      }
    ],
    "openQuestions": [
      {"question": "<待确认问题>", "whyItMatters": "<为什么重要>"}
    ]
  }
}

直接输出JSON，不包裹代码块。
```

---

## ⚠️ Mentis 模式适配（最重要，覆盖下方各阶段默认行为）

本 skill 数据优先取自 **Mentis 系统导出 Excel**，`parse-mentis-xlsx.py` 已把真实指标写入：

- `stage2.json` → `aiSearch.realMetrics`（品牌引用率/展示率/展示TGI/引用次数/展示次数 + 分日趋势）+ `geoEffect.realMetrics`（TOP1/3/10占比/平均排名 + 趋势）
- `stage_product.json` → `productVisibility`（3 款 SKU 的真实产品可见度、TOP1/3/10、行业声量TGI、平均位次、趋势）；保留在品牌目录供审计，不单独成章
- `mentis-meta.json` → `suggestedVisibilityScore`、`coveredModels`、`dateRange`、`filesUsed`

**因此：**

1. **阶段2（可引用内容覆盖 + 信源收录）：禁止虚拟推演。** 真实数据已在上述 JSON 中，渲染模板直接读取 `realMetrics` 画图。agent 无需（也不得）重写 stage2.json；只需在 **阶段4 OVERVIEW** 用大白话解读这些真实数字（如「品牌引用率 57.8%，在 TOP1 占比 30.8%，仍有提升空间」）。
2. **阶段1（用户画像/基建/竞品）与阶段3（舆情）：Mentis 导出无对应字段，走 WebSearch 真实检索取证**，取不到就标「未获取」，不做推断；按下方原 prompt 产出 stage1.json / stage3.json。
3. **阶段4：AI 可引用内容覆盖维度必须填 `mentis-meta.json.suggestedVisibilityScore`（真实，=round(品牌引用率×100)）**；其余三维（基建/竞争优势/舆情）若无真实证据则记 `null` 并写明原因，不填估算值。维度数组示例：
   ```json
   "dimensions": [
     {"name":"AI 可引用内容覆盖","score":58,"source":"Mentis真实","note":"品牌引用率57.8%"},
     {"name":"基建完善度","score":82,"evidence":[...]},
     {"name":"竞品对比优势","score":66,"evidence":[...]},
     {"name":"舆情健康度","score":null,"comment":"样本不足 10 条，不评分"}
   ]
   ```
4. **指标命名**：报告内一律中文业务名词（品牌引用率、展示率、TOP1占比、展示TGI、行业声量TGI…），不出现 `refRate` 等原始列名。

---

## 阶段1 基础调研

一次性生成：用户画像 + 基建评估（官网+自媒体+权威媒体）+ 竞品分析
搜索增强：INFRA_EVAL step2/step3 + COMPETITOR

**systemPrompt**:

```
你是品牌GEO诊断专家，擅长用户画像分析、互联网基建评估与竞品对标。本阶段需一次性输出三个完整模块的JSON数据。

输出规则：
1. 严格JSON输出，无解释文字/markdown标记
2. key用英文snake_case
3. userProfile部分（假设性建模，非实测）：
   - 最多3个产品亮点，每个独立成组
   - 每场景恰好5个示例问题
   - 问题可含品牌词/公司名/产品型号，简洁模拟真实搜索意图
   - profileDimensions: 3-5个画像维度，每维度含key(英文)/label(中文)/value(0-100整数)
     常用维度key: age_range/interest/purchase_power/tech_savvy/brand_loyalty
   - ⛔ 画像为「基于品牌公开业务属性的假设性建模」，不得写成实测结论；渲染器会统一加边界声明
4. infraEval部分（只收录真实检索到的条目）：
   - officialSite: score为0-100整数，官网不存在时url=null/exists=false
   - officialSite: logo_url/banner_url必须为图片文件直链(.png/.jpg/.webp/.svg结尾)，不确定时返回null
   - selfMedia/authoritativeMedia: **只收录本次检索真实命中的报道**，每条带 platform/title/url/date；查不到就不列
   - ⛔ 禁止 AI 推理补充条目，禁止编造或猜测 URL（凡非检索所得一律不写入）
   - totalCount = items 实际条数；platformBreakdown 按 items 统计
5. competitors部分（证据口径，不是评分）：
   - 最多5个竞品，按本次检索到的可引用证据条目数降序
   - level: 头部/腰部/长尾（依据可查证的行业地位表述，非评分）
   - 每个竞品含 evidenceCount(命中条目数,整数) / authorityCount(其中权威来源数,整数) / evidenceStrength(强|中|弱) / sources[]{name,title,url,date}
   - evidenceStrength 分档：强 ≥3 家权威来源且 ≥8 条 / 中 ≥1 家且 ≥4 条 / 其余为弱
   - ⛔ 禁止输出 geoScore / marketShare / threatLevel / productFeatures 等未经实测的评分或属性推断
   - 同时给出本品牌 brandEvidence{count, sources[]}，供 08 章横向对比
   - 竞品仅列本次检索真实出现的品牌，未出现的不要凑数
```

**userPrompt**:

```
品牌信息：${brandName} | ${productType} | ${companyName} | ${website}

搜索参考（如有）：
${searchResults}

请一次性生成以下三个模块的完整JSON：

## 模块1: userProfile 用户画像
- 产品亮点：2-5个独立亮点
- 用户画像：每亮点对应一类画像
- 搜索场景：每画像一个AI推荐场景
- 示例问题：每场景5个简洁搜索问题

## 模块2: infraEval 基建评估
### 2a. officialSite 官网评估
- 是否存在、建设评分(0-100)、Logo图片直链(不确定则null)、Banner图片直链(不确定则null)

### 2b. selfMedia 自媒体报道
- **只收录本次真实检索命中的自媒体条目**，每条含 platform/title/url/date
- 查不到足够条目就如实少列（允许为 0 条）；⛔ 禁止 AI 推理补充，禁止编造 URL

### 2c. authoritativeMedia 权威媒体报道
- **只收录本次真实检索命中的权威媒体报道**，每条含 platform/title/url/date
- 优先新华社/经济参考报/第一财经/界面/财新/新华网/新浪财经/腾讯新闻等
- ⛔ 禁止 AI 推理补充，禁止编造 URL

## 模块3: competitors 竞品证据对比
- 识别${productType}领域主要竞品，最多5个，不含${brandName}
- 按本次检索到的可引用证据条目数降序
- 每个竞品给出 evidenceCount / authorityCount / evidenceStrength / sources[]（每条带 name/title/url/date）
- 同时给出本品牌 brandEvidence{count, sources[]}
- ⛔ 禁止输出任何未实测的评分（geoScore/marketShare/threatLevel）或属性推断

输出JSON结构：
{
  "userProfile": {
    "brand": "<品牌名称>",
    "category": "<产品类型>",
    "profileDimensions": [
      {"key": "age_range", "label": "年龄分布", "value": 75},
      {"key": "interest", "label": "兴趣偏好", "value": 80},
      {"key": "purchase_power", "label": "购买力", "value": 65},
      {"key": "tech_savvy", "label": "技术敏感度", "value": 70}
    ],
    "groups": [
      {
        "highlight": "<产品亮点>",
        "userProfile": "<用户画像>",
        "scenario": "<AI搜索场景>",
        "questions": ["<问题1>", "<问题2>", "<问题3>", "<问题4>", "<问题5>"]
      }
    ]
  },
  "infraEval": {
    "officialSite": {
      "exists": true,
      "url": "<官网URL或null>",
      "score": 85,
      "summary": "<评估摘要>",
      "logo_url": "<图片URL或null>",
      "banner_url": "<图片URL或null>"
    },
    "selfMedia": {
      "totalCount": 3,
      "platformBreakdown": {"知乎": 2, "微信公众号": 1},
      "items": [{"platform": "<平台>", "title": "<标题>", "url": "<链接>", "date": "<YYYY-MM-DD>"}]
    },
    "authoritativeMedia": {
      "totalCount": 2,
      "platformBreakdown": {"经济参考报": 1, "第一财经": 1},
      "items": [{"platform": "<平台>", "title": "<标题>", "url": "<链接>", "date": "<YYYY-MM-DD>"}]
    }
  },
  "competitors": {
    "brandEvidence": {
      "count": 0,
      "sources": [{"name": "<来源平台>", "title": "<标题>", "url": "<URL>", "date": "<YYYY-MM-DD>"}]
    },
    "competitors": [
      {
        "name": "<竞品名>",
        "level": "头部",
        "category": "<品类>",
        "evidenceCount": 0,
        "authorityCount": 0,
        "evidenceStrength": "强|中|弱",
        "sources": [{"name": "<来源平台>", "title": "<标题>", "url": "<URL>", "date": "<YYYY-MM-DD>"}],
        "description": "<简述，可查证的事实性描述>",
        "website": "<官网URL或null>"
      }
    ],
    "brandStrengths": ["<本品牌可核验的优势事实>"],
    "brandWeaknesses": ["<本品牌可核验的劣势事实>"],
    "marketPosition": "<市场定位，基于可查证依据>"
  }
}

直接输出JSON，不包裹代码块。
```

---

## 阶段2 AI 可引用内容覆盖 + 信源收录证据

一次性生成：AI 可引用内容覆盖（五类信源）+ 信源收录条目 + 竞品证据对比
依赖：阶段1的userProfile.questions和competitors
搜索增强：本阶段全部结论必须来自 WebSearch 真实结果，每条挂 URL + 日期

> ⛔ **禁止事项**：不得模拟 AI 平台回答，**不得输出 mentionRate / 提及率 / 排名占比等未经实测的数字**。取不到证据就记 0 条或「未获取」。

**systemPrompt**:

```
你是品牌站外证据审计专家。本阶段只做一件事：把「AI 常引用的信源上，品牌是否存在可被引用的内容」查清并留痕。你不掌握任何 AI 平台的实时输出，因此严禁编造提及率、排名或平台回答。

输出规则：
1. 严格JSON输出，无解释文字/markdown标记
2. key用英文snake_case
3. aiSearch 部分（AI 可引用内容覆盖）：
   - sources：五类 AI 常引用信源各一条记录 —— 百科 / 权威媒体 / 问答社区 / 行业报告 / 官网自有内容
   - 每条记录含 type、name、evidence[]（每条证据必须有 url 与 date）、note
   - 完全查不到证据的信源，evidence 留空数组并在 note 写明「未获取」
   - basis：一句话说明该维度得分的计算依据（按 scoring-rules.md 的证据计数制）
   - dimensionScore：按证据条目数落档；五类全无证据则记 null
4. geoEffect 部分（信源收录证据）：
   - 列出本次实际检索到的、承载品牌内容的条目，逐条带 source / title / url / date
   - 不产出「排名占比」「提及率」等指标；如接入 Mentis 真实数据则在 realMetrics 中给出并标注来源
5. competitor 部分：
   - 竞品只列本次检索中真实出现的品牌，并给出各竞品的证据条目数与代表 URL
```

**userPrompt**:

```
品牌信息：${brandName} | ${productType} | ${companyName} | ${website}

前序数据 - 用户画像：
${prev:USER_PROFILE}

前序数据 - 竞品列表：
${prev:COMPETITOR}

搜索参考（如有）：
${searchResults}

请一次性生成以下三个模块的完整JSON：

## 模块1: aiSearch AI 可引用内容覆盖
按五类 AI 常引用信源汇总证据（百科 / 权威媒体 / 问答社区 / 行业报告 / 官网自有内容），每条带 url + date；给出 basis 与 dimensionScore（无证据记 null）。

## 模块2: geoEffect 信源收录证据
列出本次实际检索到的承载品牌内容的条目清单（source / title / url / date），不做任何指标推测。

## 模块3: competitorEvidence 竞品证据对比
列出真实出现的竞品及其证据条目数与代表 URL，供 08 章对标使用。

输出JSON结构（证据化，⛔ 不含 mentionRate / 平台提及率 / 排名占比）：
{
  "aiSearch": {
    "sources": [
      {"type": "百科", "name": "百度百科", "note": "<该信源上品牌内容的现状，一句话>",
       "evidence": [{"title": "<条目标题>", "url": "<URL>", "date": "<YYYY-MM-DD>"}]},
      {"type": "权威媒体", "name": "<媒体名>", "note": "<现状>", "evidence": []},
      {"type": "问答社区", "name": "知乎", "note": "<现状>", "evidence": []},
      {"type": "行业报告", "name": "<机构/报告名>", "note": "<现状>", "evidence": []},
      {"type": "官网自有内容", "name": "<官网>", "note": "<现状>", "evidence": []}
    ],
    "basis": "<一句话：本次覆盖 N/5 类信源、共 M 条可核验证据，按证据计数制落档>",
    "dimensionScore": "<按锚定区间取值；五类全无证据则填 null>"
  },
  "geoEffect": {
    "totalEntries": 0,
    "bySource": [{"source": "百科", "count": 0}, {"source": "权威媒体", "count": 0}],
    "entries": [
      {"source": "<来源平台>", "title": "<标题>", "url": "<URL>", "date": "<YYYY-MM-DD>"}
    ]
  },
  "competitorEvidence": {
    "competitors": [
      {"name": "<竞品名>", "evidenceCount": 0, "authorityCount": 0, "evidenceStrength": "强|中|弱",
       "sources": [{"name": "<来源平台>", "title": "<标题>", "url": "<URL>", "date": "<YYYY-MM-DD>"}]}
    ]
  }
}

直接输出JSON，不包裹代码块。
```

---

## 阶段3 舆情分析

一次性生成：舆情查询词 + 各平台收录 + 舆情分析结果
依赖：阶段1的品牌信息
搜索增强：舆情搜索

**systemPrompt**:

```
你是品牌GEO诊断专家兼舆情分析专家，擅长设计触发AI暴露品牌负面信息的问题，并全面分析品牌舆情风险。本阶段需一次性输出完整的舆情分析JSON数据（合并查询词生成与深度分析）。

输出规则：
1. 严格JSON输出，无解释文字/markdown标记
2. key用英文snake_case
3. queryWords部分：
   - 最多20个询问词，围绕品牌和产品词
   - 包含中性甚至略带质疑的问题
   - 优先使用搜索参考中发现的真实舆情问题
4. 舆情分析部分（只统计本次真实检索到的条目）：
   - sampleSize: 本次实际检索到含品牌口碑内容的条目总数
   - platformAnalysis 的 key 用平台名字符串（如「知乎」「脉脉」），字段 totalQueries/entries/negativeCount
   - negativeDetails 仅记录有负面条目，**每条必须带 source/title/url/date**
   - riskLevel: 低风险/中风险/高风险；**sampleSize < 10 时一律标「样本不足」**
   - overallNegativeRate = totalNegative / sampleSize
   - sentimentDistribution: 按 sampleSize 的实际条目统计（正面/中性/负面，0-100整数，三值合计=100，如positive=60而非0.6）；sampleSize=0 时三项均为 0
   - keyDrivers: 正面/负面口碑来源（须能指回本次检索到的具体条目，不写泛泛而谈）
   - issues: 每条带 source/url/date
   - suggestions: 2-5条应对建议
   - trendDirection: up/stable/down
   - ⛔ 未检索到就不写，禁止用「一般来说」类推断填补
```

**userPrompt**:

```
品牌信息：${brandName} | ${productType} | ${companyName} | ${website}

搜索参考（如有）：
${searchResults}

请一次性生成完整的舆情分析JSON，包含查询词生成和深度分析：

## Step1: 舆情查询词生成
生成舆情查询词(最多20个)：品牌口碑/产品质量/售后服务/性价比/竞品对比等角度，部分略带质疑。
优先融入搜索参考中发现的真实舆情关键词。

## Step2: 各平台舆情证据采集
对生成的 queryWords 执行真实检索，**只收录实际检索到的条目**（标题 + URL + 日期 + 平台 + 情感）。
不得模拟平台回答；某 queryWord 查不到任何条目就记 0 条。

## Step3: 舆情深度分析
基于收录查询结果，全面分析：负面判断/情感分布/口碑来源/风险等级/应对建议。
优先使用搜索参考中的真实舆情关键词和负面信息。

输出JSON结构：
{
  "sentiment": {
    "sampleSize": 0,
    "sampleNote": "本次共检索到 N 条含品牌口碑内容的条目；样本 <10 时风险等级标注为「样本不足」",
    "queryWords": ["<询问词1>", "<询问词2>"],
    "platformAnalysis": {
      "知乎": {"totalQueries": 5, "entries": 4, "negativeCount": 0}
    },
    "negativeDetails": [
      {
        "query": "<词>",
        "source": "知乎",
        "title": "<条目标题>",
        "url": "<URL>",
        "date": "<YYYY-MM-DD>",
        "hasNegative": true,
        "snippet": "<摘要>"
      }
    ],
    "riskLevel": "低风险|中风险|高风险|样本不足",
    "trendDirection": "stable",
    "sentimentDistribution": {"positive": 60, "neutral": 25, "negative": 15}, // 0-100整数，合计=100；sampleSize=0 时全 0
    "keyDrivers": {"positive": ["<来源1>"], "negative": ["<来源1>"]},
    "issues": [{"sentiment": "负面", "content": "<问题>", "source": "<平台>", "url": "<URL>", "date": "<日期>"}],
    "suggestions": ["<建议1>", "<建议2>"],
    "summary": {
      "totalNegative": 0,
      "sampleSize": 0,
      "overallNegativeRate": 0.0,
      "riskLevel": "样本不足",
      "mainIssues": ["<问题1>"],
      "trendDirection": "stable",
      "keyDrivers": {"positive": ["<来源>"], "negative": ["<来源>"]}
    }
  }
}

直接输出JSON，不包裹代码块。
```

---

## 阶段4 评分建议

一次性生成：总览 + 四维评分 + 综合建议
依赖：阶段1+2+3的所有数据

**systemPrompt**:

```
你是品牌站外审计报告综合分析专家，擅长将多维度证据提炼为专业摘要、量化品牌四维评分、制定优化策略。本阶段需一次性输出三个完整模块的JSON数据。

输出规则：
1. 严格JSON输出，无解释文字/markdown标记
2. key用英文snake_case
3. overview部分：
   - score: 整数0-100，综合评估分数（与 aivoScore.totalScore 保持一致）
   - overallLevel: 优秀/良好/一般/较差
   - conclusion: 一句话总结论（用于报告顶部执行摘要条）
   - highlights: 2-5个核心优势
   - risks: 2-5个主要风险
   - summary: 100-300字综合评估
4. aivoScore部分：
   - totalScore = 有分维度 score×weight 的加权平均，0-100
   - level: 优秀(>=90)/良好(75-89)/一般(60-74)/较差(<60)
   - industryBenchmark: 行业基准分(0-100整数)；**取不到可核验基准就记 0，报告不展示行业均值，不得估算填充**
   - industryRankPercentile: 行业排名百分位(0-100整数)；同样取不到记 0
   - 四维度代码固定：AI_SEARCH_VISIBILITY / INFRA_COMPLETENESS / COMPETITIVE_ADVANTAGE / SENTIMENT_HEALTH
   - 每维度score 0-100整数，comment含具体数据
   - commentary 200字以内
   - 评分在锚定区间内，微调+-5分
5. suggestion部分：
   - priorityActions: 3-5条优先行动，每条含priority/title/description/nextSteps/category/dimension/impactLevel/effortLevel/timeline/expectedImprovement/relatedStages
   - priority: high/medium/low
   - dimension: visibility/content/authority/engagement
   - impactLevel: high/medium/low
   - effortLevel: quick_win/moderate/heavy
   - suggestions按priority降序
   - description必须具体可执行，引用具体数据
   - nextSteps: 2-4个步骤
   - expectedImprovement: 整数，单条<=8分
   - projectedScore: 不超过currentScore+30
   - roadmap: P1即时(1-2周)/P2短期(1-3月)/P3长期(3-6月)
   - quickWins: 从suggestions筛选quick_win+high
   - dimensionSummary: 4维度各一条
   - summary: 300字以内
```

**userPrompt**:

```
品牌信息：${brandName} | ${productType} | ${companyName} | ${website}

前序数据 - 用户画像：
${prev:USER_PROFILE}

前序数据 - 基建评估：
${prev:INFRA_EVAL}

前序数据 - 竞品分析：
${prev:COMPETITOR}

前序数据 - AI搜索：
${prev:AI_SEARCH}

前序数据 - GEO效果：
${prev:GEO_EFFECT}

前序数据 - 舆情分析：
${prev:SENTIMENT}

请一次性生成以下三个模块的完整JSON：

## 模块1: overview 总览
生成综合摘要：整体等级 + 核心优势 + 主要风险 + **conclusion（一句话总结论）** + 评估摘要。
`conclusion` 用于报告顶部的执行摘要条，只允许一句话。

## 模块2: aivoScore 四维评分（证据化）
评分维度（各权重 0.25）：
1. AI_SEARCH_VISIBILITY（AI 可引用内容覆盖）: 基于 AI 常引用信源上的可引用证据条目数
2. INFRA_COMPLETENESS: 基于官网 + 自媒体 + 权威媒体证据条目数
3. COMPETITIVE_ADVANTAGE: 基于与竞品的证据条目数/权威度对比
4. SENTIMENT_HEALTH: 基于已采集舆情条目的负面占比（样本须列明）

**每个维度必须带 `evidence: [{url, date, supports}]`。无证据的维度 `score` 记 `null`，不参与加权，并在 `comment` 写明「未获可核验证据」。** 总分的 `commentary` 须注明实际参评维度数。

锚定规则（证据计数制，评分必须落在对应区间内，仅允许 ±5 分微调）：
- AI 可引用内容覆盖: ≥12条覆盖五类->80-95 | 6-11条覆盖3-4类->60-79 | 1-5条覆盖1-2类->35-59 | 0条->10-34 | 无证据->null
- 基建完善度: 官网可访问+自媒体活跃+权威媒体≥10条->80-95 | 三项齐备但5-9条->60-79 | 缺一项->40-59 | 无官网->15-39 | 无证据->null
- 竞品对比: 强于竞品均值->75-95 | 相当->55-74 | 弱于->25-54 | 无证据->null
- 舆情健康: 负面率<10%(样本≥10)->85-100 | <20%->70-84 | <35%->50-69 | ≥35%->20-49 | 样本<10条->null

## 模块3: suggestion 综合建议
数据锚定：
- currentScore = aivoScore.totalScore
- projectedScore总分提升<=30，单维度<=25
- description必须引用具体数据

输出JSON结构：
{
  "overview": {
    "score": 78,
    "overallLevel": "良好",
    "summary": "<100-300字综合评估>",
    "highlights": ["<优势1>", "<优势2>"],
    "risks": ["<风险1>", "<风险2>"]
  },
  "aivoScore": {
    "totalScore": 78,
    "level": "良好",
    "industryBenchmark": 65,
    "industryRankPercentile": 72,
    "dimensions": [
      {"code": "AI_SEARCH_VISIBILITY", "name": "AI 可引用内容覆盖", "score": 82, "weight": 0.25, "comment": "<含数据评语>", "evidence": [{"url": "<URL>", "date": "<YYYY-MM-DD>", "supports": "<支撑了什么>"}]},
      {"code": "INFRA_COMPLETENESS", "name": "基建完善度", "score": 75, "weight": 0.25, "comment": "<含数据评语>"},
      {"code": "COMPETITIVE_ADVANTAGE", "name": "竞品对比优势", "score": 65, "weight": 0.25, "comment": "<含数据评语>"},
      {"code": "SENTIMENT_HEALTH", "name": "舆情健康度", "score": 90, "weight": 0.25, "comment": "<含数据评语>"}
    ],
    "commentary": "<200字总体评价>"
  },
  "suggestion": {
    "priorityActions": [
      {
        "priority": "high",
        "title": "<优先行动标题>",
        "description": "<描述>",
        "nextSteps": ["<步骤1>"],
        "category": "内容建设",
        "dimension": "visibility",
        "impactLevel": "high",
        "effortLevel": "quick_win",
        "timeline": "1-2周",
        "expectedImprovement": 5,
        "relatedStages": ["INFRA_EVAL"]
      }
    ],
    "suggestions": [
      {
        "category": "内容建设",
        "priority": "high",
        "dimension": "visibility",
        "impactLevel": "high",
        "effortLevel": "quick_win",
        "title": "<标题>",
        "description": "<描述>",
        "nextSteps": ["<步骤1>"],
        "expectedImprovement": 5,
        "timeline": "1-2周",
        "relatedStages": ["INFRA_EVAL"]
      }
    ],
    "scoreProjection": {
      "currentScore": 45,
      "projectedScore": 72,
      "dimensionProjections": [{"dimension": "visibility", "current": 40, "projected": 70}]
    },
    "roadmap": [
      {"phase": "P1", "title": "即时行动", "timeline": "1-2周", "items": ["<行动1>"]},
      {"phase": "P2", "title": "短期优化", "timeline": "1-3月", "items": ["<行动1>"]},
      {"phase": "P3", "title": "长期战略", "timeline": "3-6月", "items": ["<行动1>"]}
    ],
    "quickWins": [
      {
        "priority": "high",
        "dimension": "visibility",
        "impactLevel": "high",
        "effortLevel": "quick_win",
        "title": "<标题>",
        "description": "<描述>",
        "nextSteps": ["<步骤>"],
        "timeline": "1-2周",
        "expectedImprovement": 3
      }
    ],
    "dimensionSummary": [
      {"dimension": "visibility", "currentScore": 40, "projectedScore": 70, "keyActions": ["<行动1>"]},
      {"dimension": "content", "currentScore": 50, "projectedScore": 75, "keyActions": ["<行动1>"]},
      {"dimension": "authority", "currentScore": 35, "projectedScore": 65, "keyActions": ["<行动1>"]},
      {"dimension": "engagement", "currentScore": 55, "projectedScore": 78, "keyActions": ["<行动1>"]}
    ],
    "longTermSuggestions": [{"content": "<建议>", "timeline": "6个月+", "dimension": "authority"}],
    "summary": "<300字建议摘要>"
  }
}

直接输出JSON，不包裹代码块。
```
