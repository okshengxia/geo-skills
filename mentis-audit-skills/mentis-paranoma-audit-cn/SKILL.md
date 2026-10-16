---
name: mentis-paranoma-audit-cn
description: "Mentis 品牌全景审计（中国平台包）：输入品牌名，输出「四幕 12 章」可交付报告（HTML + Markdown 双格式）——结论（诊断总览+四维评分）→ 身份（实体身份诊断/同名实体消歧）→ 资产（站外资产矩阵+问题池与信源缺口）→ 表现（用户画像/AI 可引用内容覆盖/基建评估/竞品对标/舆情分析/信源收录证据）→ 行动（差距归因+行动路线图）。硬纪律：所有结论必须挂 URL+日期证据，不推断、不模拟 AI 输出。触发词：品牌审计、全景审计、品牌诊断、GEO诊断、GEO报告、AI搜索排名、品牌曝光、品牌提及率、实体消歧、品牌名混淆、同名实体、Mentis诊断、审计报告。"
description_zh: "Mentis 品牌全景审计：品牌名入口，四幕 12 章报告（HTML + Markdown），全部结论附可核验的 URL+日期证据，不做 AI 推演"
description_en: "Mentis brand panorama audit: brand-name entry, four-act 12-chapter report (HTML + Markdown), every finding backed by a verifiable URL and date"
version: 2.2.0
display_name: "Mentis品牌全景审计"
display_name_en: "mentis-paranoma-audit"
visibility: "public"
agent_created: true
allowed-tools: Read, Write, Bash, Glob, WebSearch, WebFetch, AskUserQuestion, Agent
metadata:
  clawdbot:
    emoji: "🛡️"
---

# Mentis-Paranoma-Audit-CN 品牌全景审计

品牌 AI 可见性的**全链路站外审计**专家。以品牌名为入口（不依赖官网），采集可核验的公开证据，产出一份「四幕 12 章」的可交付 HTML 报告。

**只有一种模式：完整全景审计（阶段 0–4 全跑）。**

## 两条不可妥协的硬纪律

1. **一切结论必须有证据。** 报告中每一条断言都必须能点回原始页面（URL + 日期）。**不推断、不补全、不模拟。** 拿不到证据的条目要么写进「待确认项」，要么明确标注「未获取」——**绝不为了报告好看而编数**。
2. **不实测 AI 输出，也不假装实测。** 本 skill 没有调用任何 AI 平台的能力，因此**禁止出现"AI 提及率 XX%"这类数字**。「AI 可引用内容覆盖」以站外信源上**是否存在可被 AI 引用的品牌内容**计量，并在报告页脚与相关章节显式声明这一边界。

## 术语纪律

对外文案不使用 `AIVO`，也不使用「AI 可见性 / AI 搜索可见度」这类在别家系统里含义不同的词。统一用：

| 场景 | 用词 |
| --- | --- |
| 第 06 章标题、四维之一 | **AI 可引用内容覆盖** |
| 全报告唯一评分 | **综合评分 / 四维评估** |
| 优化建议章的分数预测 | **优化后预期评分** |

## 核心概念

- **实体消歧（本章为全库独家能力）** — 同名/近音实体污染是 GEO 头号隐形税：AI 回答「某品牌是什么」时串味到无关实体（实证：亿康先达 vs 早孕试纸/生物科技）。消歧不做，后面所有可见性工作都是给别人的品牌做嫁衣。
- **四维评分（证据化）** — AI 可引用内容覆盖(25%) × 基建完善度(25%) × 竞品对比优势(25%) × 舆情健康度(25%)。**每一维必须挂证据链；某维无证据可依时记 `null` 并写明原因，不参与加权**。≥90 优秀 / ≥75 良好 / ≥60 一般 / <60 较差。
- **四幕叙事** — 结论 → 身份 → 资产 → 表现 → 行动。一条线读完，不再"结论→细节→又跳回结论"。
- **差距归因 vs 行动路线图** — 第 11 章回答「**差在哪**」（每条差距溯源到 02–10 的诊断章节），第 12 章回答「**怎么干**」（分数预测 + roadmap + quick wins）。两章相邻，不重叠。

## 四幕 12 章（报告结构）

| 幕 | 章 | 章节名 | stageCode | 回答的问题 |
| --- | --- | --- | --- | --- |
| 结论 | 01 | 诊断总览 | OVERVIEW + AIVO_SCORE **合并** | 多少分、什么级、发现什么、风险在哪（**全报告唯一评分**，hero 环同源） |
| 身份 | 02 | 实体身份诊断 | ENTITY_MAP | 这个牌子在 AI 眼里到底是谁 |
| 资产 | 03 | 站外资产矩阵 | PLATFORM_MATRIX | 13 个平台上有没有货 |
| 资产 | 04 | 问题池与信源缺口 | QUESTION_POOL | 用户会问的 9 类意图，答不答得上 |
| 表现 | 05 | 用户画像 | USER_PROFILE | 谁在问、怎么问 |
| 表现 | 06 | AI 可引用内容覆盖 | AI_SEARCH | AI 常引用的信源上，有没有可被引用的内容 |
| 表现 | 07 | 基建评估 | INFRA_EVAL | 官网/自媒体/权威媒体家底 |
| 表现 | 08 | 竞品对标 | COMPETITOR | 对手在站外长什么样 |
| 表现 | 09 | 舆情分析 | SENTIMENT | 口碑健康度与风险 |
| 表现 | 10 | 信源收录证据 | GEO_EFFECT | 各信源的收录条目清单（口径 = 第 06 章五类信源证据 + 其他信源条目） |
| 行动 | 11 | 差距归因 | OPPORTUNITY_MAP | **差在哪** + 每条溯源到来源章节 |
| 行动 | 12 | 行动路线图 | SUGGESTION | **怎么干**：分数预测 + roadmap + quick wins |

`PRODUCT_VISIBILITY`（Mentis 单品级数据）不在本结构内；有 Mentis 导出时保留在品牌目录供审计，不单独成章。

## 工作流程

```
用户: "审计一下亿康先达"
  │
  ├─ 📥 Step 1: 收集输入
  │   brandName(必填) + productType(可选，缺省由 ENTITY_MAP.entityType 兜底)
  │   website(可选) + mentisFolder(可选，有 Mentis 导出时)
  │
  ├─ 📁 Step 2: 建品牌目录 <workDir>/<品牌>/
  │
  ├─ ⚙️ Step 3: 阶段 0-4 流水线（见下）
  │   每阶段完成 → Write <品牌目录>/stageN.json
  │
  ├─ 🧾 Step 4: merge-stages.js → <品牌>-diag-report.json
  │
  ├─ 📤 Step 5: build-report.js → <品牌>全景审计报告.html
  │
  └─ 📝 Step 6: build-report-md.js → <品牌>全景审计报告.md
```

## 输入参数

| 参数 | 必填 | 说明 | 示例 |
| --- | --- | --- | --- |
| brandName | ✅ | 品牌名称 | "亿康先达" |
| productType | ❌ | 产品/品类；缺省回退 ENTITY_MAP.entityType | "高管寻访" |
| website | ❌ | 官网地址 | "https://www.egonzehnder.com" |
| mentisFolder | ❌ | Mentis 导出 Excel 根目录（提供则第 06/10 章用真实数据） | "/path/to/A2报告" |
| workDir | ❌ | 输出根目录，默认当前工作目录 | "./audit" |

### 交互快捷规则

| 场景 | 规则 |
| --- | --- |
| ✅ 消息已含品牌名 | 直接提取，仅补产品类型等缺失项 |
| ✅ 品牌名 + 品类都给全 | 不再反问，直接开跑 |
| ⚠️ 品牌名有歧义（重名） | 先 AskUserQuestion 确认是哪一个实体，再开跑 |

---

## 阶段 0：站外全景审计（十一组搜索并行）

```
0a 实体身份卡      组A（3次并行）: "{brand}" 百科/工商主体/成立年份/英文别称
0b 同名实体干扰清单 组B（2次并行）: "{brand}" 是什么 / "{brand}" 招聘 新闻 用途
0c 站外资产矩阵     组C（3次并行）: site:zhihu / site:xiaohongshu、"{brand}" 收费 价格、"{brand}" 靠谱 投诉 合规
0d 问题池 九类意图   组D（2次并行）: "{品类}" 推荐 排行、"{brand}" 对比 哪个好
0e 差距归因 P0/P1/P2 + 验收标准（每条带 relatedStageCodes 溯源）
0f 待确认项（未取到证据的断言，禁编）
  ↓ Write <品牌目录>/stage0.json
```

**阶段 0 硬规则**：每条断言记录 `url` + `date` + `confidence`；平台不可达就标「未获取」，**严禁编造 URL**；不采集个人隐私（职场平台只取公司维度）；每平台每类别 Top 10–20 抽样；情感证据不足一律 `neutral`。

SOP 详见 `references/entity-disambiguation-sop.md` / `platform-matrix-sop.md` / `question-pool-sop.md`。

---

## 阶段 1–4

```
阶段0（前置，搜索写 <品牌目录>/search-cache/{brand}-entity.json，TTL 30min）
   ↓
阶段1 画像 + 基建 + 竞品
   ↓
┌──────────────────────────────────────────────┐
│ 阶段2 可引用内容覆盖 + 收录证据 ←并行→ 阶段3 舆情分析 │
└──────────────────────────────────────────────┘
   ↓                          ↓
阶段4 总览 + 四维评分（证据化） + 行动路线图
```

| 阶段 | 内容 | 依赖 | 搜索 | 预估耗时 |
| --- | --- | --- | --- | --- |
| 阶段0 | 实体身份 + 平台矩阵 + 问题池 + 差距归因 | 无 | 组A–D 并行（约 11 次） | 3-4min |
| 阶段1 | 画像 + 基建(3子步) + 竞品 | 阶段0 | 组A(3)+组B(2) 并行 | 3-4min |
| 阶段2 | 可引用内容覆盖 + 信源收录证据 | 阶段1 | 组A(2) 并行 | 2-3min |
| 阶段3 | 舆情词 → 收录 → 分析 | 阶段1 | 组A(3) 并行 | 2-3min |
| 阶段4 | 总览 + 四维评分 + 行动路线图 | 阶段1+2+3 | 无 | 2-3min |

### Mentis Excel 注入（可选，真数据优先）

有 Mentis 导出时：`python3 scripts/parse-mentis-xlsx.py <mentisFolder> <brand> <product> <品牌目录>` → 预写 `stage2.json`（真实品牌指标）/ `stage_product.json` / `mentis-meta.json`。**阶段 2 禁止虚拟推演，agent 不得重写 stage2.json**；阶段 4 的「AI 可引用内容覆盖」维度必须取 `mentis-meta.json.suggestedVisibilityScore` 并附数据来源说明。`stage_product.json` 保留在品牌目录供审计，不单独成章。

### 四维评分证据化规则（阶段 4）

- 每个维度对象必须含 `evidence: [{url, date, supports}]`，`supports` 说明该证据支撑了什么判断。
- `score` 为空/无证据时写 `null`，并在 `comment` 写明「未获可核验证据」。**总分为有分维度的加权平均**，同时在 `commentary` 注明实际参评维度数。
- 禁止为了凑分而构造证据。

---

## 输出规则

```
1. 建目录: <workDir>/<品牌>/                   例: 亿康先达/
2. 阶段0-4 各 Write <品牌目录>/stage<N>.json
3. Bash: node "mentis-paranoma-audit-cn/scripts/merge-stages.js" <品牌目录> <品牌> [产品]
4. Bash: node "mentis-paranoma-audit-cn/scripts/build-report.js" "<品牌目录>/<品牌>-diag-report.json"
5. Bash: node "mentis-paranoma-audit-cn/scripts/build-report-md.js" "<品牌目录>/<品牌>-diag-report.json"
6. ✅ 产物: <品牌目录>/<品牌>全景审计报告.html ＋ <品牌>全景审计报告.md
```

- **双格式报告（同一 JSON 两个出口）**：`build-report.js` 产 HTML（可视化主交付）、`build-report-md.js` 产 Markdown（文本化报告），**两份同时产出**；章节结构、四维评分、证据 URL/日期与边界声明完全同口径，Markdown 版不另做推断、不新增数字。
- **输出目录名 = 品牌名**，报告文件名 = `<品牌>全景审计报告.html` / `<品牌>全景审计报告.md`。例：`亿康先达/亿康先达全景审计报告.html`、`亿康先达/亿康先达全景审计报告.md`。
- 中间产物 `<品牌>-diag-report.json` 与 merge 后保留的 `stage_product.json` / `mentis-meta.json` 留在同目录，供复跑与审计。
- 便捷编排（有 Mentis Excel 时）：`bash scripts/orchestrate.sh <品牌目录> <品牌> [产品] [mentisFolder]`（HTML 与 Markdown 一并产出）
- 版本四处一致：SKILL.md `2.2.0` / merge-stages.js `'2.2'` / renderer 页脚 `v2.2` / Markdown 页脚 `v2.2`。

---

## 错误恢复

| 错误 | 操作 |
| --- | --- |
| ⚠️ JSON 解析失败 | 重试 1 次 → 仍失败则中止并报告（缺章禁止交付） |
| 🔍 WebSearch 不可用 | 中止并告知用户：本 skill 的硬纪律要求真实证据，无搜索能力时不得输出推断内容 |
| 🌐 build-report.js / build-report-md.js 失败 | 检查 JSON 契约 → 修复后重跑；**不得**降级为手写 HTML / Markdown |
| 📊 某维无证据 | 记 `null` + 写明原因，**不得**填推断分 |
| 🚫 平台不可达 | 标「未获取」，`covered=false`，**严禁编造 URL** |
| 📦 openpyxl 缺失 | `pip install openpyxl` → 失败则按无 Excel 路径继续 |

---

## 引用文件

### references/

| 引用文件 | 内容 | 加载时机 |
| --- | --- | --- |
| `references/entity-disambiguation-sop.md` | 实体身份 SOP（数据源/名称矩阵/置信度分档/同名实体判定树/行业包/隐私纪律） | 阶段0 前 Read |
| `references/platform-matrix-sop.md` | 13 平台矩阵 SOP（检索入口/五类句式/可引用性/证据纪律） | 阶段0 前 Read |
| `references/question-pool-sop.md` | 问题池与差距归因 SOP（九类意图/缺口写法/验收标准句式/relatedStageCodes） | 阶段0 前 Read |
| `references/prompts.md` | 阶段0-4 Prompt 模板与 JSON 契约 | 各阶段执行时 Read 对应 section |
| `references/search-strategy.md` | 搜索策略+执行规范+阶段0 搜索组 | 搜索阶段前 Read |
| `references/search-templates.md` | 各阶段搜索查询模板 | 搜索阶段前 Read |
| `references/scoring-rules.md` | 四维评分（**含证据化规则**）+ 配色规范 + 裁剪 + 质量检查 + 反模式 | 评分时 Read |
| `references/platform-data.md` | 平台编码+偏好参数 | 阶段2 Read |
| `references/mentis-data-schema.md` | Mentis Excel 目录约定+列→指标映射 | 解析 Excel 前 Read |
| `references/skill-relations.md` | 编排模式 + 旧 skill 指向 | 编排诊断前 Read |
| `references/changelog.md` | 版本更新日志 | 需要时 Read |
| `references/evals/evals.json` | Skill 评测用例 | 评测时 Read |

### scripts/

| 文件 | 内容 | 调用方式 |
| --- | --- | --- |
| `scripts/parse-mentis-xlsx.py` | Mentis Excel → 真实品牌/产品 GEO JSON | 有 Mentis 导出时 Bash |
| `scripts/merge-stages.js` | 阶段 JSON 合并（要求 13 个 stageCode 齐全） | 各阶段完成后 Bash |
| `scripts/build-report.js` | HTML 报告构建（默认输出 `<品牌>全景审计报告.html`） | 输出时 Bash |
| `scripts/build-report-md.js` | Markdown 报告构建（默认输出 `<品牌>全景审计报告.md`，与 HTML 消费同一 JSON） | 输出时 Bash |
| `scripts/orchestrate.sh` | 一键编排（解析+合并+渲染 HTML 与 Markdown） | 可选 |
| `scripts/assets/audit-renderer.html` | HTML 渲染模板（VI + 四幕 12 章 + 证据块） | build-report.js 自动读取 |

**执行顺序**（Bash 路径相对 workbuddy-skills 根目录，Read 相对 skill 根目录）：

1. 编排前：Read `references/skill-relations.md`
2. 阶段0 前：Read `prompts.md` 阶段0 + 三份阶段0 SOP + `search-strategy.md` + `search-templates.md`（一次性加载，后续复用）
3. 阶段2+3 前：Read `prompts.md` 阶段2+3 + `platform-data.md`（两阶段并行）
4. 阶段4 前：Read `prompts.md` 阶段4 + `scoring-rules.md`
5. 旧 skill 已废弃（2026-10-16）：`geo-diag-report` / `mentis-diag-report` 能力已并入本 skill，勿再引用旧路径
