---
name: "mentis-website-audit"
description: "多行业网站GEO（生成式引擎优化）检测与优化专家。基于14项核心指标跨三大维度（核心基础/实体结构化/爬虫辅助）进行诊断，支持电商、旅游游轮、内容媒体、专业服务、教育、医疗、餐饮等多个行业，输出综合评分、问题清单、行业适配JSON-LD代码和分阶段优化方案。当用户要求分析网站GEO表现、检测GEO问题、生成结构化数据代码、或制定GEO优化计划时立即调用。"
---

# Mentis Website Audit

## 技能概述

本技能基于 **14项GEO核心指标体系**，对多行业网站进行全面的GEO（Generative Engine Optimization，生成式引擎优化）诊断，并输出可直接落地的优化方案。

> **输出格式说明**：所有报告默认以 Markdown 格式输出，如需其他格式（HTML、PDF 等）请用户明确指定。
>
> **输出文件规范**：报告文件命名格式为 `「品牌名」网站 GEO 检测报告.md`，并保存在当前工作目录下与品牌同名的文件夹中。例如：检测「皇家加勒比」官网时，报告路径为 `皇家加勒比/皇家加勒比网站 GEO 检测报告.md`。

### 评分体系

| 维度 | 权重 | 满分 |
|------|------|------|
| 核心基础指标 | 50% | 50 |
| 实体结构化指标 | 35% | 35 |
| 爬虫体验辅助指标 | 15% | 15 |
| **综合** | **100%** | **100** |

### 等级判定

| 综合评分 | 等级 | 说明 |
|---------|------|------|
| ≥ 90 | 优秀 | AI搜索表现优异，仅需持续监控 |
| 70 - 89 | 良好 | 基础良好，存在少量优化空间 |
| 50 - 69 | 中等 | 存在明显缺陷，需系统化优化 |
| < 50 | 重大缺陷 | 核心要素严重缺失，亟需全面整改 |

---

## 14项指标详解

### 一、核心基础指标（6项，共50分）

评估AI爬虫能否顺利发现并读取网站内容。

| 编号 | 指标 | 满分 | 说明 |
|------|------|------|------|
| ① | robots.txt 配置规范 | 8.33 | 配置是否完整，是否为AI爬虫（Bytespider、GPTBot等）设置访问规则 |
| ② | sitemap.xml 完整度 | 8.33 | 站点地图是否存在、是否覆盖所有产品页面、是否更新及时 |
| ③ | Meta 元数据 | 8.33 | Title/Description/OG标签/Twitter Card/Canonical标签是否完整 |
| ④ | HTML 可读文本 | 8.33 | 是否为SSR服务端渲染，核心内容是否直接在HTML源码中可读 |
| ⑤ | HTML 语义化 | 8.33 | h1-h6标题层级、nav/main/article等语义化标签是否完整 |
| ⑥ | 静态内链 | 8.33 | 页面间链接体系是否完整，是否有死链或假链接（javascript:void(0)） |

### 二、实体结构化指标（5项，共35分）

**GEO 最核心的维度**，评估AI能否以结构化方式理解品牌/产品/服务信息。

| 编号 | 指标 | 满分 | 说明 |
|------|------|------|------|
| ⑦ | Organization Schema | 7 | 品牌实体信息（名称、Logo、联系方式、社交媒体）的JSON-LD标记 |
| ⑧ | 行业核心 Schema | 7 | **核心指标**：根据行业选择对应 Schema（电商=Product/Offer、旅游游轮=CruiseTrip、专业服务=ProfessionalService/Service 等） |
| ⑨ | FAQPage Schema | 7 | 常见问题页面的JSON-LD标记，让AI直接引用官网权威回答 |
| ⑩ | BreadcrumbList Schema | 7 | 页面层级路径的JSON-LD标记 |
| ⑪ | 图片Alt文本 | 7 | 图片Alt描述，让AI"看懂"图片内容 |

### 三、爬虫体验辅助指标（3项，共15分）

评估AI爬虫在抓取过程中的体验。

| 编号 | 指标 | 满分 | 说明 |
|------|------|------|------|
| ⑫ | 加载性能 | 5 | 首屏加载速度、服务器响应时间 |
| ⑬ | 内容新鲜度 | 5 | 网站内容更新频率、时效性 |
| ⑭ | llms.txt | 5 | 是否为AI大模型提供网站摘要信息文件 |

---

## 工作流程

### 第一步：收集信息

1. 确认用户提供的网站URL
2. 如果用户未提供URL，引导用户提供
3. **向用户确认网站所属行业**（必须询问，不能自行猜测），可选行业：
   - 电商零售
   - 旅游/游轮
   - 内容媒体
   - 专业服务/本地服务
   - 教育培训
   - 医疗健康
   - 餐饮
   - 其他（需用户描述）
4. 确认用户是否需要特定功能（如价格Schema、FAQ等）
5. 确认品牌名称（用于报告文件命名）

### 第二步：检测14项指标

对每项指标进行检测，记录得分和问题描述。

**检测要点：**

- **robots.txt**：检查 `{domain}/robots.txt` 是否返回200，内容是否包含User-agent规则和Sitemap引用
- **sitemap.xml**：检查 `{domain}/sitemap.xml` 是否存在，是否包含产品页面URL
- **Meta元数据**：检查页面Title、Description、OG:title、OG:description、OG:image、Twitter Card
- **HTML语义化**：检查h1-h6标签层级是否完整，是否存在nav/main/article/section等语义化标签
- **JSON-LD结构化数据**：检查页面是否包含 `<script type="application/ld+json">` 及内容类型
- **图片Alt**：检查所有 `<img>` 标签的alt属性填充率
- **llms.txt**：检查 `{domain}/llms.txt` 是否存在

### 第三步：生成综合评分报告（Markdown格式）

输出包含以下内容的报告：

1. **综合评分**：总分 + 等级判定
2. **三大维度分值表**：各维度得分及占比
3. **可视化描述**：文本版雷达图或表格对比
4. **输出文件**：将报告保存为 `「品牌名」网站 GEO 检测报告.md`，存放于当前工作目录下与品牌同名的文件夹中（如文件夹不存在则创建）

### 第四步：生成问题清单

按严重程度排序：

- **严重问题**：Product Schema缺失、Organization Schema缺失、sitemap缺失、h1-h3标题层级缺失等
- **中等问题**：OG标签不完整、图片Alt文本缺失、爬虫配置不完善、canonical标签缺失等
- **轻微问题**：llms.txt缺失、部分Meta标签优化空间等

### 第五步：生成代码示例

为每个实体结构化指标生成可直接部署的JSON-LD代码：

#### 5.1 Organization Schema（放首页）

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "品牌名称",
  "alternateName": "品牌英文/别名",
  "url": "https://www.example.com",
  "logo": "https://www.example.com/logo.png",
  "description": "品牌描述",
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "客服电话",
    "contactType": "customer service",
    "areaServed": "CN",
    "availableLanguage": ["Chinese", "English"]
  },
  "sameAs": ["社交媒体链接"]
}
```

#### 5.2 Product/Offer Schema（放产品页）

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "产品名称",
  "description": "产品描述",
  "image": "产品图片URL",
  "category": "产品分类",
  "brand": {
    "@type": "Brand",
    "name": "品牌名称"
  },
  "offers": {
    "@type": "Offer",
    "url": "产品页URL",
    "priceCurrency": "USD",
    "price": "价格",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "销售方名称"
    }
  }
}
```

**多规格产品使用 AggregateOffer：**

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "产品系列名称",
  "offers": {
    "@type": "AggregateOffer",
    "priceCurrency": "USD",
    "lowPrice": "最低价",
    "highPrice": "最高价",
    "offerCount": "规格数量",
    "offers": [
      {"@type": "Offer", "name": "规格1", "price": "价格1", "priceCurrency": "USD"},
      {"@type": "Offer", "name": "规格2", "price": "价格2", "priceCurrency": "USD"}
    ]
  }
}
```

#### 5.3 FAQPage Schema（放FAQ页）

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "问题标题",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "答案内容"
      }
    }
  ]
}
```

#### 5.4 BreadcrumbList Schema（放每个页面）

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "首页", "item": "首页URL"},
    {"@type": "ListItem", "position": 2, "name": "分类名", "item": "分类URL"},
    {"@type": "ListItem", "position": 3, "name": "产品名", "item": "产品URL"}
  ]
}
```

#### 5.5 图片Alt文本示例

```
✅ 正确：<img src="wifi-unlimited.jpg" alt="品牌名 产品名 产品描述 - 价格">
❌ 错误：<img src="wifi-unlimited.jpg" alt="">
❌ 错误：<img src="wifi-unlimited.jpg">
```

### 第六步：制定分阶段优化计划

按4阶段8周规划：

| 阶段 | 时间 | 内容 | 优先级 |
|------|------|------|--------|
| Phase 1 紧急修复 | 第1周 | Product Schema + sitemap修复 | P0 |
| Phase 2 核心建设 | 第2-3周 | Organization Schema + BreadcrumbList + 标题层级 | P1 |
| Phase 3 扩展完善 | 第4-6周 | FAQPage Schema + 图片Alt文本 + OG标签 | P2 |
| Phase 4 持续优化 | 第7-8周 | llms.txt + robots.txt优化 + 持续监控 | P3 |

### 第七步：量化预期效果

根据行业经验，优化后可预期的效果：

- **AI引用率提升**：50-80%（AI搜索中引用官网信息的频率）
- **索引率提升**：40-60%（搜索引擎收录的页面比例）
- **结构化数据展示**：从0到100%的页面获得富媒体展示
- **品牌权威性**：显著提升，AI能准确识别品牌实体
- **用户信任度**：AI引用官网信息，用户获取信息更准确

---

## 用户提问示例

| 用户问题 | 技能响应 |
|---------|---------|
| "帮我分析一下这个网站的GEO表现" | 执行完整14项检测，输出综合评分报告（Markdown） |
| "这个网站有哪些GEO问题" | 输出问题清单，按严重程度排序 |
| "生成Product Schema代码" | 根据产品信息生成JSON-LD代码 |
| "给我一个优化计划" | 输出4阶段8周分阶段优化计划 |
| "优化后能达到什么效果" | 输出量化预期效果预测 |
| "什么是实体结构化数据" | 用通俗语言解释，上代码示例 |
| "为什么评分这么低" | 逐项分析低分原因，用比喻说明 |

---

## 注意事项

1. **代码安全性**：生成的JSON-LD代码必须符合Schema.org标准，使用 `https://schema.org` 协议
2. **语言适配**：面向中国市场的网站，SameAs社交链接应包含微信、微博、抖音、小红书等
3. **价格格式**：价格使用 `priceCurrency` + `price` 结构，支持多币种
4. **评分客观性**：评分要有数据支撑，不能主观臆断
5. **建议可落地**：所有优化建议必须是可执行的，且有明确的实施步骤
6. **通俗解释**：对非技术用户，使用比喻和类比解释技术概念
7. **默认格式**：所有报告默认以 Markdown 格式输出，保持清晰可读
8. **文件命名规范**：报告文件名固定为 `「品牌名」网站 GEO 检测报告.md`，存放于与品牌同名的目录下
9. **行业确认**：检测前必须向用户确认行业类型，不同行业使用不同的核心 Schema 体系