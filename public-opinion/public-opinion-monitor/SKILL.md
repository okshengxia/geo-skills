---
name: public-opinion-monitor
version: 2.1.0
display_name: 舆情监测助手
display_name_en: Public Opinion Monitor
description: "全网舆情监测助手。自动采集微博、抖音、小红书、B站、V2EX、知乎、主流新闻媒体、今日头条等平台的热榜、话题、评论、报道，输出舆情健康分、情感占比、分级负面预警、事件时间线、热度排行、竞品口碑对比、环比趋势与风险建议。用户问舆情监测/口碑/负面新闻/热搜讨论/品牌舆论/危机预警/竞品对比时调用。"
description_zh: "全网舆情监测助手。自动采集微博、抖音、小红书、B站、V2EX、知乎、主流新闻媒体等平台的热榜、话题、评论与报道，输出舆情健康分、情感占比、分级负面预警、事件时间线、热度排行、竞品口碑对比与环比趋势。触发词：舆情监测、口碑分析、负面新闻、热搜讨论、品牌舆论、危机预警、竞品对比、舆情简报、舆情周报。"
description_en: "All-platform public opinion monitoring assistant. Crawls Weibo, Douyin, Xiaohongshu, Bilibili, V2EX, Zhihu, news media and Toutiao, delivering a weighted opinion health score, sentiment ratios, graded negative alerts, event timelines, heat rankings, competitor comparison and trend deltas."
category: 信息资讯
author: 合作方名称
---

# 舆情监测助手（Public Opinion Monitor）v2.0

通过公开 API + 环境可用的抓取/搜索能力，从主流平台采集指定关键词或事件的舆论信息；去重、事件聚类、健康分、预警分级、环比等确定性计算全部交给 `scripts/analyze.py`，输出结构化舆情报告（Markdown 或单文件 HTML）。

## 跨平台兼容（重要）

本技能不写死任何宿主的工具名。采集时按**能力**映射到当前环境实际可用的工具：

| 所需能力 | TRAE/Solo 环境 | WorkBuddy 环境 | 纯 CLI 环境 |
|----------|----------------|----------------|-------------|
| 打开 URL / 取 JSON | browser_navigate | 浏览器操作 / WebFetch | curl / WebFetch |
| 页面元素解析 | browser_evaluate | 浏览器解析 / DOM 读取 | Jina Reader（r.jina.ai） |
| 关键词搜索 | WebSearch | 内置搜索 | Exa / WebSearch |
| 命令行工具 | RunCommand | Bash/终端 | 直接执行 |
| 登录态提示 | browser_wait_for_user | 对话内提示用户 | 手动配置 |

执行原则：环境里没有某工具时，用同类能力替代；都没有则走 @references/platform-channels.md 的降级链，并在报告开头注明"本次采集未覆盖的平台"。

## 触发条件

用户表达以下任一意图时使用本技能，不要自行发明搜索路径：

1. **舆情监测**：监测 XX 的舆情 / XX 口碑怎么样 / XX 最近有什么负面
2. **热点追踪**：XX 上热搜了吗 / 关于 XX 大家在讨论什么
3. **风险预警**：XX 有没有负面 / XX 的争议 / 危机公关
4. **竞品对比**：A 和 B 舆论对比 / 竞品口碑分析
5. **综合调研**：做一份 XX 舆情分析报告 / 全景舆论扫描 / 舆情周报

## 第 1 步：澄清监测参数（缺参数就问，默认值在括号里）

| 参数 | 含义 | 默认值 |
|------|------|--------|
| `keywords` | 关键词/品牌/人物/事件，多关键词逗号分隔 | 【必填，缺失必须问】 |
| `range` | 1h / 6h / 24h / 7d / 30d / 自定义 | `24h` |
| `platforms` | weibo,douyin,xiaohongshu,bilibili,v2ex,news,zhihu,twitter | 全平台 |
| `negative_alert` | 负面内容置顶预警 | `true` |
| `top_n` | 每平台 Top N | `10` |
| `report_format` | `summary` / `full` / `raw` / `compare`(竞品对比，需≥2组关键词) / `weekly`(周报) | `summary` |

## 第 2 步：渠道健康检查（建议先跑，多平台全采时必跑）

```
python3 scripts/check_channels.py
```

输出本次各平台无登录渠道的可用状态。❌ 的平台直接走降级链，不浪费采集等待时间。

## 第 3 步：多平台并行采集

各平台的 API 入口、页面解析字段与**失败降级链**全部见 @references/platform-channels.md，按其中的优先级顺序执行，失败自动降级。原则：

- 优先无登录 JSON API → 页面解析 → Exa/Jina 兜底
- 需登录态时一次性提示用户，不要每平台分别弹窗
- 每平台条数不超过 50，平台间间隔 ≥1.5s

## 第 4 步：统一数据结构

所有条目转成统一 JSON（`/tmp/pom-<keyword>-<timestamp>.json`），字段规范：

```json
{
  "meta": { "keywords": "...", "range": "24h", "platforms": ["weibo"], "collected_at": "ISO-8601" },
  "items": [
    {
      "platform": "weibo",
      "title_or_text": "正文或标题，限前 200 字",
      "url": "原文链接（去重与溯源依据，必填）",
      "author": "作者/账号名",
      "published_at": "ISO-8601 或相对时间",
      "metrics": { "views": 0, "likes": 0, "comments": 0, "reposts": 0, "engagement_total": 0, "rank": null },
      "sentiment": "positive | negative | neutral | controversial",
      "sentiment_reason": "一句话理由（50 字内）",
      "tags": ["负面预警","行业热点","KOL观点","官方通报","争议讨论","谣言风险","竞品相关"]
    }
  ]
}
```

## 第 5 步：情感判断

按 @references/sentiment-rules.md 的词典与规则打 `sentiment` 与 `sentiment_reason`。必须基于文本显式线索；不确定记 neutral 并标注"需人工复核"。

## 第 6 步：确定性分析（v2 核心，必须执行）

把第 4 步的 JSON 交给脚本处理，**不要用手算替代**：

```
python3 scripts/analyze.py /tmp/pom-<keyword>-<timestamp>.json --top-n <top_n>
```

脚本自动完成（AI 不得手算替代）：

- URL 精确去重 + 跨平台标题指纹合并（Jaccard ≥0.85）
- **舆情健康分**：互动量与 KOL/媒体加权的 0–100 情感分
- **事件聚类**：指纹阈值 0.6 聚成事件簇，输出传播阶段（苗头/活跃/发酵/回落/消退）
- **预警分级**：紧急 / 高 / 中 / 低（按热度、跨平台扩散、负面占比判定）
- **快照环比**：结果自动存入 `~/.public-opinion-monitor/snapshots/`，同关键词下次运行自动对比，新增负面标 "🆕 首次出现"，输出条目与负面占比变化
- 输出 analyzed.json / CSV（UTF-8 BOM）/ report-data.md 数据块

脚本结果与 AI 判断冲突时，以脚本统计为准并回查原始条目。

## 第 7 步：输出报告

- summary / weekly：按 @templates/report-summary.md
- full：按 @templates/report-full.md（追加平台子报告、话题聚类、KOL 清单、时间分布）
- compare：按 @templates/report-compare.md（A/B 口碑对比矩阵，对每组关键词各跑一次 analyze.py）
- 需要可分享版本时：`python3 scripts/report_html.py <analyzed.json> -o report.html`，生成无外部依赖的单文件 HTML（SVG 健康分弧形图、情感环图、热点榜、预警分级表、事件时间线），默认写到用户当前目录或用户指定位置（不要写 /tmp，除非用户只求临时）

## 红线（不得违反）

1. **绝不编造**：每条内容必须有 URL/来源，不存在则不写；标题正文必须是原文。
2. **绝不侵入**：禁止输账号密码、绕登录墙付费墙；遇登录墙提示用户或降级。
3. **绝不泄露**：监测关键词、结果、临时文件路径不写入可公开访问处。
4. **绝不制造恐慌**：负面必须附"情感理由 + 来源"；负面占比 < 5% 时明确写"舆情整体平稳"。
