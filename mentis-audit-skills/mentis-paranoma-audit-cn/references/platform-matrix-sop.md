# 站外平台矩阵 SOP（阶段0 模块2：PLATFORM_MATRIX）

> 适用：mentis-paranoma-audit-cn 阶段0。字段契约见 `prompts.md` 阶段0 模块2。

## 一、13 平台固定清单与检索入口

| # | 平台 | 类型 | 检索入口 | 可引用性基线 |
|---|------|------|----------|--------------|
| 1 | 百度百科 | 百科 | WebSearch「{brand} 百科」或直接抓取 | high |
| 2 | 百度搜索 | 搜索 | WebSearch 主结果（含快照/百家号） | high |
| 3 | 微信搜一搜 | 社交 | WebSearch + 公众号检索 | medium |
| 4 | 知乎 | 社交 | WebSearch `site:zhihu.com` | high（问答被 AI 高频引用） |
| 5 | 小红书 | 社交 | WebSearch `site:xiaohongshu.com` | high（笔记/合集） |
| 6 | 抖音 | 视频 | WebSearch「{brand} 视频」 | medium |
| 7 | 脉脉 | 职场 | WebSearch「{brand} 脉脉」 | low（公司维度聚合） |
| 8 | 看准 | 职场 | WebSearch「{brand} 看准/面试」 | low |
| 9 | 职友集 | 职场 | WebSearch「{brand} 职友集」 | low |
| 10 | 买购网 | 点评 | WebSearch「{brand} 买购/十大品牌」 | medium（榜单被引用） |
| 11 | 企查查 | 查询 | WebSearch「{brand} 企查查」 | medium |
| 12 | 公众号 | 社交 | WebSearch「{brand} 公众号」 | medium |
| 13 | 新闻媒体 | 媒体 | WebSearch「{brand} 新闻」（36氪/虎嗅/界面等） | high |

> 行业适配：第 6/7/8/9/10 位可按品类替换（如母婴品类可将脉脉/看准/职友集/买购网替换为 B 站/微博/母婴垂直社区/电商评价），**替换后仍为 13 平台，不得增列推断型平台**。

> 猎头业实证提示：B 端服务品牌在消费型平台（小红书/抖音）天然稀薄，矩阵要解释「覆盖为零是品类特性还是运营缺位」——买购 8.9/10（283 人评分）与看准仅 1 条面试评价并存时，样本量必须写明。

## 二、五类查询句式（每平台执行）

| 类别 | 查询句式 | 回答什么问题 |
|------|----------|--------------|
| brandTerm 品牌词 | 「"{brand}"」 | 官方口径在不在场 |
| review 评价 | 「"{brand}" 怎么样/评价/体验」 | 口碑结构与情感 |
| pricing 价格 | 「"{brand}" 收费/价格/多少钱」 | 定价叙事谁在说（服务品牌必查） |
| trust 信任 | 「"{brand}" 靠谱/投诉/骗」 | 信任资产与负面 |
| compliance 合规 | 「"{brand}" 合规/PIPL/监管/资质」 | 高风险问题的品牌层面应答 |

## 三、抽样与记录规范

- 每平台每类别 **Top 10-20 抽样**；结果不足记录实际数量，不凑数。
- 每格五字段：`covered / sentiment / citability / confidence / topEvidence{title,url,date}`。
- **URL 必须来自当次搜索结果**；抓不到就 `covered=false` 并标「不可达」，**严禁编造 URL**。
- 情感保守判定：无明确倾向 → neutral；正负混杂 → mixed；无法判断 → null。
- citability 判定：高权重百科/权威媒体/头部社区 = high；普通媒体/公众号/垂直站 = medium；职场点评聚合站/论坛散帖 = low。

## 四、交付话术纪律（v2.1 移除 AI 预判列）

- **不再输出「AI 预判」列。** v2.0 曾以信源结构推理「AI 引用概率」，属推断，与「一切基于事实」硬纪律冲突，v2.1 起整列删除，矩阵只保留本次检索可核验的 5 类覆盖。
- 交付话术纪律：本报告只回答「AI 引用你们的条件齐不齐」，**不得对客户说「AI 现在这么说你们」**——那句需要真去问 AI，属另一次实测，本报告明确声明未做。
- 缺口排序改用可核验口径：某列 covered 平台数为 0 或极少 → 该列为高优先级机会（P0 通常落在 compliance 与 pricing——品牌层面零说明的高风险区）。

## 五、coverageSummary 与机会排序

- 按列统计 covered 平台数（如 `brandTerm "12/13"`、`compliance "3/13"`）。
- 覆盖缺口最大的列 = 最高优先级机会（P0 通常落在 compliance 与 pricing——品牌层面零说明的高风险区）。

## 六、输出

→ `stage0.json` 的 `platformMatrix` 模块；不可达平台如实标注，缺口列直接喂给 `opportunityMap`。
