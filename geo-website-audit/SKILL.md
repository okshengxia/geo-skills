---
name: "geo-website-audit"
description: "多行业GEO检测与优化专家。基于14项核心指标跨三大维度（核心基础/实体结构化/爬虫辅助）进行诊断，支持电商、旅游游轮、内容媒体、本地服务、教育、医疗、餐饮等多个行业，输出综合评分、问题清单、行业适配JSON-LD代码和分阶段优化方案。当用户要求分析网站GEO表现、检测GEO问题、生成结构化数据代码、或制定GEO优化计划时立即调用。"
---

# 多行业 GEO 检测与优化专家

## 技能概述

本技能基于 **14项GEO核心指标体系**，对**多行业网站**进行全面的GEO（Generative Engine Optimization，生成式引擎优化）诊断，并输出可直接落地的优化方案。

**核心特色**：用户输入网站后，通过行业选择动态适配不同的实体结构化指标和JSON-LD Schema代码示例，确保检测和优化建议与行业精准匹配。

> **输出格式说明**：所有报告默认以 Markdown 格式输出，如需其他格式（HTML、PDF 等）请用户明确指定。

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

### 二、实体结构化指标（5项，共35分）— 行业自适应

**AI理解网站核心实体的关键维度**，5项指标根据用户选择的行业动态适配。所有行业均包含 **Organization Schema**（品牌实体基础）和 **图片Alt文本**（视觉信息），其余3项按行业特征匹配。

#### 行业-Schema 映射表

| 行业 | ⑦ 共用 | ⑧ 行业核心 | ⑨ 行业特色 | ⑩ 层级导航 | ⑪ 共用 |
|:----|:------:|:----------:|:----------:|:----------:|:------:|
| **电商** | Organization | **Product/Offer** | FAQPage | BreadcrumbList | 图片Alt |
| **旅游/游轮** | Organization | **CruiseTrip** | TouristDestination | BreadcrumbList | 图片Alt |
| **内容/媒体** | Organization | **Article** | VideoObject | BreadcrumbList | 图片Alt |
| **本地服务** | Organization | **Service** | LocalBusiness | BreadcrumbList | 图片Alt |
| **教育** | Organization | **Course** | EducationalOccupationalCredential | BreadcrumbList | 图片Alt |
| **医疗健康** | Organization | **MedicalService** | Physician/Hospital | BreadcrumbList | 图片Alt |
| **餐饮** | Organization | **Menu** | Restaurant | BreadcrumbList | 图片Alt |

#### 各行业核心 Schema 说明

| 行业 | ⑧ 行业核心指标 | 满分 | 说明 |
|:----|:--------------|:----:|------|
| 电商 | Product/Offer Schema | 7 | **电商核心**：产品名称、价格、货币、库存、折扣的JSON-LD标记 |
| 旅游/游轮 | CruiseTrip Schema | 7 | **旅游核心**：航线名称、出发/到达时间、出发港口、目的地、价格、供应商 |
| 内容/媒体 | Article Schema | 7 | **内容核心**：文章标题、作者、发布日期、正文摘要、图片、分类 |
| 本地服务 | Service Schema | 7 | **服务核心**：服务名称、描述、价格、服务区域、提供商 |
| 教育 | Course Schema | 7 | **教育核心**：课程名称、描述、授课方式、价格、教育机构、课时 |
| 医疗健康 | MedicalService Schema | 7 | **医疗核心**：医疗服务名称、描述、适用病症、治疗方式、医疗机构 |
| 餐饮 | Menu Schema | 7 | **餐饮核心**：菜单名称、菜品列表、价格、饮食分类、餐厅信息 |

### 三、爬虫体验辅助指标（3项，共15分）

评估AI爬虫在抓取过程中的体验。

| 编号 | 指标 | 满分 | 说明 |
|------|------|------|------|
| ⑫ | 加载性能 | 5 | 首屏加载速度、服务器响应时间 |
| ⑬ | 内容新鲜度 | 5 | 网站内容更新频率、时效性 |
| ⑭ | llms.txt | 5 | 是否为AI大模型提供网站摘要信息文件 |

---

## 工作流程

### 第一步：收集信息（含行业选择）

1. 确认用户提供的网站URL
2. 如果用户未提供URL，引导用户提供
3. **弹出行业选择提示框**，让用户从以下选项中选择：
   
   ```
   请选择网站所属行业：
   
   ① 电商 - 实物商品销售（电子产品、服装、日用品等）
   ② 旅游/游轮 - 旅游服务、航线预订、酒店、度假
   ③ 内容/媒体 - 新闻、博客、视频、资讯平台
   ④ 本地服务 - 本地生活服务、家政、维修、美容
   ⑤ 教育 - 在线课程、培训机构、学校
   ⑥ 医疗健康 - 医院、诊所、健康管理
   ⑦ 餐饮 - 餐厅、外卖、美食品牌
   ⑧ 其他（通用） - 无法归类的其他行业
   ```
   
   > **提示**：如果用户只输入了URL但没有明确说行业，必须主动弹出选择框让用户选，不能自行猜测。
   
4. 确认用户是否需要特定功能（如特定Schema类型、FAQ等）

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

### 第四步：生成问题清单

按严重程度排序：

- **严重问题**：Product Schema缺失、Organization Schema缺失、sitemap缺失、h1-h3标题层级缺失等
- **中等问题**：OG标签不完整、图片Alt文本缺失、爬虫配置不完善、canonical标签缺失等
- **轻微问题**：llms.txt缺失、部分Meta标签优化空间等

### 第五步：生成行业适配代码示例

根据用户选择的行业，为每个实体结构化指标生成对应的JSON-LD代码。**必选通用项** + **行业特定项**。

#### 5.1 Organization Schema（必选，放首页，所有行业通用）

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

#### 5.2 行业核心 Schema（根据所选行业选择一项）

**电商 — Product/Offer Schema（放产品页）**

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "产品名称",
  "description": "产品描述",
  "image": "产品图片URL",
  "category": "产品分类",
  "brand": { "@type": "Brand", "name": "品牌名称" },
  "offers": {
    "@type": "Offer",
    "url": "产品页URL",
    "priceCurrency": "USD",
    "price": "价格",
    "availability": "https://schema.org/InStock",
    "seller": { "@type": "Organization", "name": "销售方名称" }
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

**旅游/游轮 — CruiseTrip Schema（放航线页）**

```json
{
  "@context": "https://schema.org",
  "@type": "CruiseTrip",
  "name": "航线名称，如：上海-福冈-长崎-上海 6天5晚",
  "description": "航线描述",
  "departureTime": "出发日期",
  "arrivalTime": "到达日期",
  "departurePort": {
    "@type": "City",
    "name": "出发港口城市"
  },
  "arrivalPort": {
    "@type": "City",
    "name": "到达港口城市"
  },
  "itinerary": [
    { "@type": "City", "name": "停靠城市1" },
    { "@type": "City", "name": "停靠城市2" }
  ],
  "offers": {
    "@type": "Offer",
    "priceCurrency": "CNY",
    "price": "起价",
    "availability": "https://schema.org/InStock"
  },
  "provider": {
    "@type": "Organization",
    "name": "游轮公司名称"
  }
}
```

**旅游/游轮 — TouristDestination Schema（放目的地页）**

```json
{
  "@context": "https://schema.org",
  "@type": "TouristDestination",
  "name": "目的地名称",
  "description": "目的地描述",
  "containedInPlace": {
    "@type": "Country",
    "name": "所属国家"
  },
  "touristType": "适合的游客类型"
}
```

**内容/媒体 — Article Schema（放文章页）**

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "文章标题",
  "description": "文章摘要",
  "author": { "@type": "Person", "name": "作者名" },
  "datePublished": "发布日期",
  "dateModified": "修改日期",
  "image": "文章封面图URL",
  "publisher": { "@type": "Organization", "name": "发布媒体名称" },
  "articleSection": "文章分类"
}
```

**本地服务 — Service Schema（放服务页）**

```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "服务名称",
  "description": "服务描述",
  "provider": {
    "@type": "LocalBusiness",
    "name": "商家名称",
    "address": { "@type": "PostalAddress", "addressLocality": "所在城市", "addressCountry": "CN" },
    "telephone": "联系电话"
  },
  "areaServed": "服务覆盖区域",
  "offers": {
    "@type": "Offer",
    "priceCurrency": "CNY",
    "price": "价格",
    "priceSpecification": { "@type": "UnitPriceSpecification", "unitText": "计价单位" }
  }
}
```

**教育 — Course Schema（放课程页）**

```json
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "课程名称",
  "description": "课程描述",
  "provider": {
    "@type": "EducationalOrganization",
    "name": "教育机构名称"
  },
  "educationalCredentialAwarded": "结业证书/学位",
  "offers": {
    "@type": "Offer",
    "priceCurrency": "CNY",
    "price": "课程价格",
    "availability": "https://schema.org/InStock"
  },
  "courseTime": "课时数",
  "courseMode": "授课方式（线上/线下/混合）"
}
```

**医疗健康 — MedicalService Schema（放服务页）**

```json
{
  "@context": "https://schema.org",
  "@type": "MedicalService",
  "name": "医疗服务名称",
  "description": "服务描述",
  "provider": {
    "@type": "Hospital",
    "name": "医疗机构名称",
    "address": { "@type": "PostalAddress", "addressLocality": "所在城市", "addressCountry": "CN" }
  },
  "medicalSpecialty": "医学专科",
  "areaServed": "服务区域"
}
```

**餐饮 — Menu Schema（放菜单页）**

```json
{
  "@context": "https://schema.org",
  "@type": "Menu",
  "name": "菜单名称",
  "description": "菜单描述",
  "provider": {
    "@type": "Restaurant",
    "name": "餐厅名称",
    "servesCuisine": "菜系",
    "address": { "@type": "PostalAddress", "addressLocality": "所在城市", "addressCountry": "CN" }
  },
  "hasMenuSection": [
    {
      "@type": "MenuSection",
      "name": "分类名称",
      "hasMenuItem": [
        { "@type": "MenuItem", "name": "菜品名称", "offers": { "@type": "Offer", "priceCurrency": "CNY", "price": "价格" } }
      ]
    }
  ]
}
```

#### 5.3 FAQPage Schema（通用，所有行业）

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

#### 5.4 BreadcrumbList Schema（通用，所有行业，放每个页面）

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

#### 5.5 图片Alt文本示例（通用，所有行业）

```
✅ 正确：<img src="product.jpg" alt="品牌名 产品名 产品描述 - 价格">
❌ 错误：<img src="product.jpg" alt="">
❌ 错误：<img src="product.jpg">
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
| "帮我分析一下这个网站www.example.com的GEO表现" | 弹出行业选择提示框 → 执行完整14项检测 → 输出行业适配的综合评分报告 |
| "这个网站有哪些GEO问题" | 输出问题清单，按严重程度排序 |
| "生成Product Schema代码" | 根据用户所在行业，生成对应的行业核心Schema代码 |
| "给我一个优化计划" | 输出4阶段8周分阶段优化计划 |
| "优化后能达到什么效果" | 输出量化预期效果预测 |
| "什么是实体结构化数据" | 用通俗语言解释，结合所选行业举例说明 |
| "为什么评分这么低" | 逐项分析低分原因，用比喻说明 |

---

## 注意事项

1. **行业选择流程**：用户输入URL后，必须先弹出行业选择提示框，**不能自行猜测**行业。如果用户说"随便"或"你定"，默认使用"电商"行业。
2. **代码安全性**：生成的JSON-LD代码必须符合Schema.org标准，使用 `https://schema.org` 协议
3. **语言适配**：面向中国市场的网站，SameAs社交链接应包含微信、微博、抖音、小红书等
4. **价格格式**：价格使用 `priceCurrency` + `price` 结构，支持多币种
5. **评分客观性**：评分要有数据支撑，不能主观臆断
6. **建议可落地**：所有优化建议必须是可执行的，且有明确的实施步骤
7. **通俗解释**：对非技术用户，使用比喻和类比解释技术概念
8. **默认格式**：所有报告默认以 Markdown 格式输出，保持清晰可读