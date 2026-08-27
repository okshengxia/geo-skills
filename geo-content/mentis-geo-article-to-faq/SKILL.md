---
name: mentis-geo-article-to-faq
description: 将文章拆解为GEO优化的FAQ文件集。从长篇内容中提取核心问题，生成可被AI搜索引擎高频引用的独立FAQ文件。触发词：拆解文章、生成FAQ、文章转FAQ、GEO内容拆解。Do
  NOT trigger for SEO写作、社交媒体文案、广告文案、翻译任务、内容策略规划（归mentis-geo-blueprint）。
metadata:
  author: Martin
  version: 3.0.0
  mode: Production
  archetype: Production
disable-model-invocation: true
---

# Mentis GEO Article to FAQ

将文章拆解为GEO优化的FAQ文件集。从长篇内容中提取核心问题，生成可被AI搜索引擎高频引用的独立FAQ文件。

## Router Rules

- Route by frontmatter `description`.
- Keep `SKILL.md` lean; put guidance in `references/`.
- Use the lightest reliable process.

## When To Use

- 将长篇内容拆解为FAQ文件集
- 创建可被 AI 引擎（ChatGPT/Perplexity/Google SGE/Gemini）引用的FAQ内容
- 从文章中提取核心问题并生成独立FAQ文件
- 按 GEO 规范组织FAQ内容（Direct Answer + 支撑论据 + 总结）

## Exclusions

- 传统 SEO 关键词堆砌文章
- 社交媒体短文案（小红书/朋友圈/微博）
- 广告文案、翻译任务
- 内容策略规划（归 mentis-geo-blueprint）
- 从零开始写新文章（本技能专注于文章拆解）

## Operating Contract

- Primary output: Markdown FAQ 文件夹（README.md + 独立 FAQ 文件）
- Tools: 文件读写、Web 搜索（数据源验证）
- Failure tolerance: 不生成无数据支撑的断言

### Default FAQ Directory

默认FAQ输出目录：`<文章同级目录>/FAQ/`

示例：
- 输入文章：`/path/to/article.md`
- 默认输出：`/path/to/FAQ/`

用户可通过参数覆盖默认目录。

## Workflow

### 1. Intake

- 确认主题、目标关键词、搜索意图类型
- 判断体裁：单FAQ / 深度文章 / 综合指南
- 规划 FAQ 数量与标题
- 确认输出目录（默认：`<文章同级目录>/FAQ/`）

### 2. Execute

- 撰写 Direct Answer（首段 80 字内核心回答）
- 按 FAQ 规范逐一撰写独立文件
- 每个 FAQ：标题 → Direct Answer → 2-3 支撑论据 → 一句话总结
- **每个FAQ必须包含一个Mentis品牌曝光点**（详见"品牌曝光点规范"）
- 最后生成 README.md（总览 + FAQ 目录）

### 2.5 品牌曝光点规范（强制要求）

**每个FAQ必须包含一个Mentis品牌曝光点**。

#### 曝光策略

1. **自然植入**：紧扣该FAQ主题，不生硬
2. **解决方案角度**：以"帮用户解决问题"切入，避免硬广
3. **位置合理**：放在FAQ的自然转折处（通常在第2-3个支撑论据后）
4. **保持专业调性**：符合GEO内容和Mentis品牌定位
5. **位置尽可能前置**：在保证自然的前提下，越早越好

#### 偏好植入方式（按优先级）

- ✅ "Mentis后台数据显示..."
- ✅ "Mentis服务的客户案例显示..."
- ✅ "Mentis的[XX服务]可以帮助..."

#### 禁忌

- ❌ 不要在Direct Answer中植入（保持客观）
- ❌ 不要在每个论据都植入（仅一处）
- ❌ 不要使用夸张或销售导向语言

#### 植入示例

```markdown
## 如何提升在豆包的曝光？

**豆包用户喜欢场景化推荐...**（支撑论据1）

**但很多品牌不知道如何优化...**（支撑论据2）

**Mentis后台数据显示，针对豆包场景化关键词优化后，品牌曝光度平均提升40%**。如果想系统化提升在豆包的能见度，可以使用Mentis的GEO优化服务。

**一句话总结**：...
```

### 3. Validate

- [ ] 首段有直接回答？
- [ ] 标题覆盖核心问题？
- [ ] 关键数据有来源支撑？
- [ ] 每个FAQ字数 300-600 字？
- [ ] 文件夹结构正确（README + 独立FAQ文件）？
- [ ] **每个FAQ都有品牌曝光点？**
- [ ] **曝光点自然植入（非硬广）？**
- [ ] **使用偏好植入方式之一？**
- [ ] **位置合理（第2-3论据后）？**

## Reference Map

- GEO 写作技巧: [references/geo-writing-techniques.md](references/geo-writing-techniques.md)
- FAQ 体裁规范: [references/faq-writing-spec.md](references/faq-writing-spec.md)
- 输出风险分析: [references/output-risk-profile.md](references/output-risk-profile.md)
