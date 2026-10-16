#!/usr/bin/env node
'use strict';

/**
 * Mentis-Paranoma-Audit-CN Markdown 报告构建脚本 v2.2.0
 *
 * 用法: node build-report-md.js <json-path> [output-path]
 *   json-path   — DiagReport JSON 文件路径（必填，merge-stages.js 产物）
 *   output-path — 输出 Markdown 路径（可选，默认与 JSON 同目录，文件名 = <品牌>全景审计报告.md）
 *
 * 与 build-report.js 消费同一份合并 JSON，产出与 HTML 报告同口径、同章节的 Markdown 版：
 * 四幕 12 章 + 页脚边界声明；每条断言附 URL 与日期。
 *
 * 退出码:
 *   0 — 成功
 *   1 — 参数缺失 / JSON 不可读
 *   2 — JSON 解析失败
 *   4 — 输出写入失败
 */

var fs = require('fs');
var path = require('path');

var args = process.argv.slice(2);
if (args.length < 1) {
  console.error('用法: node build-report-md.js <json-path> [output-path]');
  process.exit(1);
}

var jsonPath = path.resolve(args[0]);
var outputPathArg = args[1] ? path.resolve(args[1]) : null;

var jsonRaw;
try {
  jsonRaw = fs.readFileSync(jsonPath, 'utf8');
} catch (e) {
  console.error('❌ JSON 文件不存在或不可读: ' + jsonPath);
  console.error('   ' + e.message);
  process.exit(1);
}

var reportData;
try {
  reportData = JSON.parse(jsonRaw);
} catch (e) {
  console.error('❌ JSON 解析失败: ' + jsonPath);
  console.error('   ' + e.message);
  process.exit(2);
}

var S = reportData.stages || {};
var brand = reportData.brand || path.basename(jsonPath, '.json').replace(/-diag-report$/, '');
var category = reportData.category || '全景审计';
var today = new Date().toISOString().slice(0, 10);

var outputPath = outputPathArg || path.join(path.dirname(jsonPath), brand + '全景审计报告.md');

// ─────────────────────────── helpers ───────────────────────────
function txt(v) { return v === null || v === undefined ? '' : String(v); }
function esc(v) { return txt(v).replace(/\|/g, '\\|').replace(/\r?\n+/g, ' ').trim(); }
function arr(a) { return Object.prototype.toString.call(a) === '[object Array]' ? a : []; }
function host(u) { return txt(u).replace(/^https?:\/\//i, '').split('/')[0].replace(/^www\./i, ''); }
function link(url, label) { return url ? '[' + esc(label || host(url)) + '](' + url + ')' : esc(label || ''); }
function ev(url, date, label) {
  var s = url ? link(url, label) : esc(label || '');
  if (date) s += ' `' + esc(date) + '`';
  return s;
}
function anyVal(v) {
  if (v === null || v === undefined) return '';
  if (typeof v === 'string') return v;
  if (typeof v === 'number' || typeof v === 'boolean') return String(v);
  return JSON.stringify(v);
}

var L = [];
function out(s) { L.push(s === undefined || s === null ? '' : String(s)); }
function blank() { L.push(''); }
function table(headers, rows) {
  out('| ' + headers.map(esc).join(' | ') + ' |');
  out('| ' + headers.map(function () { return '---'; }).join(' | ') + ' |');
  rows.forEach(function (r) { out('| ' + r.map(function (c) { return txt(c); }).join(' | ') + ' |'); });
  blank();
}

// ─────────────────────────── 头部 ───────────────────────────
var aivo = S.AIVO_SCORE || {};
var ov = S.OVERVIEW || {};
var score = (aivo.totalScore !== null && aivo.totalScore !== undefined) ? aivo.totalScore : (ov.score !== null && ov.score !== undefined ? ov.score : null);
var level = aivo.level || ov.overallLevel || '';
var dims = arr(aivo.dimensions);

out('# ' + brand + '全景审计报告');
blank();
out('**品类**：' + esc(category) + '　|　**综合评分**：' + (score === null ? '—' : score) + '/100' + (level ? '（' + esc(level) + '）' : '') + '　|　**生成时间**：' + today);
blank();
out('> 本报告为「四幕 12 章」全景审计：结论（01）→ 身份（02）→ 资产（03–04）→ 表现（05–10）→ 行动（11–12）。所有结论均标注可核验的证据来源（URL + 日期）；未取得证据的条目不做推断、不计分。「AI 可引用内容覆盖」以站外信源上是否存在可被 AI 引用的品牌内容计量，本报告未实测各 AI 平台的实时输出。');
blank();

var CHAPTERS = [
  '01 诊断总览', '02 实体身份诊断', '03 站外资产矩阵', '04 问题池与信源缺口', '05 用户画像', '06 AI 可引用内容覆盖',
  '07 基建评估', '08 竞品对标', '09 舆情分析', '10 信源收录证据', '11 差距归因', '12 行动路线图'
];
out('## 目录');
blank();
CHAPTERS.forEach(function (c) { out('- [' + c + '](#' + c.toLowerCase().replace(/\s+/g, '-') + ')'); });
blank();
out('---');
blank();

// ─────────────────────────── 01 诊断总览 ───────────────────────────
out('## 01 诊断总览');
blank();
out('**综合评分 ' + (score === null ? '—' : score) + '/100（' + esc(level || '—') + '）**');
blank();
if (ov.conclusion) { out('**结论**：' + esc(ov.conclusion)); blank(); }

if (dims.length) {
  out('### 四维评估');
  blank();
  table(['维度', '得分', '权重', '评语'], dims.map(function (d) {
    return [esc(d.name), (d.score === null || d.score === undefined ? 'null' : d.score),
      (d.weight !== null && d.weight !== undefined ? Math.round(d.weight * 100) + '%' : '—'), esc(d.comment)];
  }));
  dims.forEach(function (d) {
    var e = arr(d.evidence);
    if (!e.length) return;
    out('**' + esc(d.name) + ' · 证据链**');
    blank();
    e.forEach(function (x) { out('- ' + ev(x.url, x.date) + ' — ' + esc(x.supports)); });
    blank();
  });
}

if (aivo.commentary) { out('> **评分口径**：' + esc(aivo.commentary)); blank(); }

var aivoEv = arr(aivo.evidence);
if (aivoEv.length) {
  out('### 评分依据');
  blank();
  aivoEv.forEach(function (x) { out('- ' + ev(x.url, x.date) + ' — ' + esc(x.supports)); });
  blank();
}

if (arr(ov.highlights).length) {
  out('### 关键发现');
  blank();
  arr(ov.highlights).forEach(function (x, i) { out((i + 1) + '. ' + esc(x)); });
  blank();
}
if (arr(ov.risks).length) {
  out('### 主要风险');
  blank();
  arr(ov.risks).forEach(function (x, i) { out((i + 1) + '. ' + esc(x)); });
  blank();
}
if (ov.summary) { out('### 报告摘要'); blank(); out(esc(ov.summary)); blank(); }
out('---');
blank();

// ─────────────────────────── 02 实体身份诊断 ───────────────────────────
var em = S.ENTITY_MAP || {};
out('## 02 实体身份诊断');
blank();
out('### 身份卡');
blank();
var idRows = [
  ['标准名称', esc(em.canonicalName)], ['实体类型', esc(em.entityType)], ['法律主体', esc(em.legalEntity)],
  ['成立年份', esc(em.foundedYear)], ['总部', esc(em.hqLocation)],
  ['识别置信度', (em.confidence === null || em.confidence === undefined ? '' : em.confidence)]
].filter(function (r) { return r[1] !== ''; });
if (idRows.length) table(['字段', '内容'], idRows);

if (arr(em.aliases).length) {
  out('### 名称与别名');
  blank();
  table(['名称', '语言', '类型', '证据'], arr(em.aliases).map(function (a) {
    return [esc(a.name), esc(a.lang), esc(a.type), ev(a.url, a.date)];
  }));
}

if (arr(em.sameNameEntities).length) {
  out('### 同名 / 近音实体干扰（实体消歧）');
  blank();
  arr(em.sameNameEntities).forEach(function (x, i) {
    out('#### ' + (i + 1) + '. ' + esc(x.name));
    blank();
    out('- **实体类型**：' + esc(x.entityType));
    out('- **与本品牌关系**：' + esc(x.relation));
    out('- **风险等级**：' + esc(x.riskLevel));
    if (x.evidence && (x.evidence.url || x.evidence.date)) out('- **证据**：' + ev(x.evidence.url, x.evidence.date));
    blank();
    if (x.aiMisreadScenario) { out('**AI 误读场景**：' + esc(x.aiMisreadScenario)); blank(); }
    if (x.handling) { out('**处置建议**：' + esc(x.handling)); blank(); }
  });
}

if (arr(em.evidence).length) {
  out('### 证据清单');
  blank();
  table(['断言', '内容', '来源', '日期'], arr(em.evidence).map(function (e) {
    return [esc(e.claim), esc(e.value), (e.url ? link(e.url) : ''), esc(e.date)];
  }));
}
out('---');
blank();

// ─────────────────────────── 03 站外资产矩阵 ───────────────────────────
var pm = S.PLATFORM_MATRIX || {};
var COLS = [['brandTerm', '品牌词'], ['review', '评价'], ['pricing', '价格'], ['trust', '信任'], ['compliance', '合规']];
var platforms = arr(pm.platforms);
out('## 03 站外资产矩阵');
blank();
out('- **检索日期**：' + esc(pm.searchDate || '—'));
if (pm.samplingRule) out('- **抽样规则**：' + esc(pm.samplingRule));
blank();

out('### 平台覆盖矩阵（' + platforms.length + ' 平台 × 5 类查询）');
blank();
out('| 平台 | 类型 | ' + COLS.map(function (c) { return c[1]; }).join(' | ') + ' |');
out('| --- | --- | ' + COLS.map(function () { return '---'; }).join(' | ') + ' |');
platforms.forEach(function (p) {
  var cells = COLS.map(function (c) {
    var v = p[c[0]];
    return (v && v.covered) ? '✅' : '—';
  });
  out('| ' + esc(p.platform) + ' | ' + esc(p.platformType) + ' | ' + cells.join(' | ') + ' |');
});
blank();

if (pm.coverageSummary) {
  out('**覆盖汇总**：' + COLS.map(function (c) {
    return c[1] + ' ' + esc(pm.coverageSummary[c[0]] || '—');
  }).join('　|　'));
  blank();
}

var pmEv = [];
platforms.forEach(function (p) {
  COLS.forEach(function (c) {
    var v = p[c[0]];
    if (v && v.covered && v.topEvidence && v.topEvidence.url) {
      pmEv.push('- **' + esc(p.platform) + ' · ' + c[1] + '**：' + ev(v.topEvidence.url, v.topEvidence.date, v.topEvidence.title) + (v.citability ? '（可引用性：' + esc(v.citability) + '）' : ''));
    }
  });
});
if (pmEv.length) {
  out('### 各格证据');
  blank();
  pmEv.forEach(function (l) { out(l); });
  blank();
}
out('> ⚠️ 本表仅记录本次检索可核验到的覆盖情况，未实测 AI 输出。');
blank();
out('---');
blank();

// ─────────────────────────── 04 问题池与信源缺口 ───────────────────────────
var qp = S.QUESTION_POOL || {};
out('## 04 问题池与信源缺口');
blank();
out('- **抽样问题总数**：' + esc(qp.totalSampled === null || qp.totalSampled === undefined ? '—' : qp.totalSampled));
blank();
arr(qp.intents).forEach(function (it, i) {
  out('### ' + (i + 1) + '. ' + esc(it.intent));
  blank();
  out('- **优先级**：' + esc(it.priority) + '　**缺口严重度**：' + esc(it.gapSeverity) + '　**品牌在场**：' + esc(it.brandPresence));
  blank();
  if (arr(it.sampleQuestions).length) {
    out('**示例问题**');
    blank();
    arr(it.sampleQuestions).forEach(function (q) { out('- ' + esc(q)); });
    blank();
  }
  if (arr(it.sourceGaps).length) {
    out('**信源缺口**');
    blank();
    arr(it.sourceGaps).forEach(function (g) { out('- ' + esc(g)); });
    blank();
  }
});
out('> ⚠️ 「品牌在场」是基于 03 站外资产矩阵的覆盖情况所做的推断，非实测 AI 输出；「信源缺口」指该类意图下缺少哪一类可被 AI 引用的信源，是可核验的结论。');
blank();
out('---');
blank();

// ─────────────────────────── 05 用户画像 ───────────────────────────
var up = S.USER_PROFILE || {};
out('## 05 用户画像');
blank();
out('> ⚠️ 本章的用户画像、搜索场景与示例问题为「基于品牌公开业务属性的假设性建模」，用于指导内容规划，不是实测数据；维度分值为建模权重，不代表任何实测指标。');
blank();
if (arr(up.profileDimensions).length) {
  out('### 画像维度');
  blank();
  table(['维度', '取值'], arr(up.profileDimensions).map(function (d) { return [esc(d.label), esc(d.value)]; }));
}
arr(up.groups).forEach(function (g, i) {
  out('### ' + (i + 1) + '. ' + esc(g.highlight));
  blank();
  if (g.userProfile) { out('**用户画像**：' + esc(g.userProfile)); blank(); }
  if (g.scenario) { out('**搜索场景**：' + esc(g.scenario)); blank(); }
  if (arr(g.questions).length) {
    out('**典型问题**');
    blank();
    arr(g.questions).forEach(function (q) { out('- ' + esc(q)); });
    blank();
  }
});
out('---');
blank();

// ─────────────────────────── 06 AI 可引用内容覆盖 ───────────────────────────
var ais = S.AI_SEARCH || {};
var aisSources = arr(ais.sources);
out('## 06 AI 可引用内容覆盖');
blank();
out('> ⚠️ 本章不含对 AI 平台输出的实测。下列条目是「某信源上是否存在可被 AI 引用的品牌内容」的可核验记录，每条附 URL 与日期。');
blank();
var aisCount = 0;
aisSources.forEach(function (s) { aisCount += arr(s.evidence).length; });

if (!aisCount) {
  out('> ⚠️ 本次检索未采集到可核验的信源证据条目，本维度不计分。本报告不对 AI 平台的输出做任何推算或模拟——若某条结论没有可点开的原始页面，它就不会出现在本报告里。建议优先补齐百科词条、权威媒体报道与行业报告等信源内容，使品牌在 AI 检索中具备可被引用的素材。');
  blank();
} else {
  out('- **覆盖维度得分**：' + esc(ais.dimensionScore === null || ais.dimensionScore === undefined ? '—' : ais.dimensionScore));
  out('- **可核验信源证据合计**：' + aisCount + ' 条');
  blank();
  table(['类型', '信源', '说明', '证据条数'], aisSources.map(function (s) {
    return [esc(s.type), esc(s.name), esc(s.note), arr(s.evidence).length];
  }));
  if (ais.basis) { out('**计分依据**：' + esc(ais.basis)); blank(); }
  aisSources.forEach(function (s) {
    var e = arr(s.evidence);
    if (!e.length) return;
    out('**' + esc(s.name) + '（' + esc(s.type) + '）证据**');
    blank();
    e.forEach(function (x) { out('- ' + ev(x.url, x.date, x.title)); });
    blank();
  });
}
out('---');
blank();

// ─────────────────────────── 07 基建评估 ───────────────────────────
var ie = S.INFRA_EVAL || {};
var os = ie.officialSite || {};
var sm = ie.selfMedia || {};
var am = ie.authoritativeMedia || {};
out('## 07 基建评估');
blank();
out('### 官网');
blank();
out('- **是否存在**：' + (os.exists ? '是' : '否'));
if (os.url) out('- **地址**：' + link(os.url));
if (os.score !== null && os.score !== undefined) out('- **官网评分**：' + os.score);
if (os.summary) { blank(); out(esc(os.summary)); }
blank();
function mediaBlock(title, m) {
  out('### ' + title);
  blank();
  out('- **条目总数**：' + esc(m.totalCount === null || m.totalCount === undefined ? '—' : m.totalCount));
  blank();
  var pb = m.platformBreakdown || {};
  var pbKeys = Object.keys(pb);
  if (pbKeys.length) {
    table(['平台', '条数'], pbKeys.map(function (k) { return [esc(k), esc(pb[k])]; }));
  }
  var items = arr(m.items);
  if (items.length) {
    table(['平台', '内容', '来源', '日期'], items.map(function (it) {
      return [esc(it.platform), esc(it.title), (it.url ? link(it.url) : ''), esc(it.date)];
    }));
  }
}
mediaBlock('自媒体', sm);
mediaBlock('权威媒体', am);
out('---');
blank();

// ─────────────────────────── 08 竞品对标 ───────────────────────────
var cp = S.COMPETITOR || {};
var be = cp.brandEvidence || {};
var comps = arr(cp.competitors);
out('## 08 竞品对标');
blank();
out('> ⚠️ 本章对比的是「各品牌在公开信源上可被 AI 引用的内容条目数」，不是 AI 提及率。证据强度按权威来源条数与总条目数分档：强 ≥3 家权威来源且 ≥8 条 / 中 ≥1 家且 ≥4 条 / 其余为弱。每条证据均可点回原始页面。');
blank();
out('### 本品牌可引用证据');
blank();
out('- **证据条目数**：' + esc(be.count === null || be.count === undefined ? '—' : be.count));
blank();
if (arr(be.sources).length) {
  table(['来源', '标题', '链接', '日期'], arr(be.sources).map(function (s) {
    return [esc(s.name), esc(s.title), (s.url ? link(s.url) : ''), esc(s.date)];
  }));
}
if (comps.length) {
  out('### 竞品对比');
  blank();
  table(['竞品', '层级', '品类', '证据条数', '权威条数', '证据强度'], comps.map(function (c) {
    return [esc(c.name), esc(c.level), esc(c.category), esc(c.evidenceCount), esc(c.authorityCount), esc(c.evidenceStrength)];
  }));
  comps.forEach(function (c) {
    var srcs = arr(c.sources);
    if (!srcs.length) return;
    out('**' + esc(c.name) + ' · 证据**');
    blank();
    srcs.forEach(function (s) { out('- ' + ev(s.url, s.date, s.name + '｜' + (s.title || ''))); });
    blank();
    if (c.description) { out('　说明：' + esc(c.description)); blank(); }
  });
}
if (arr(cp.brandStrengths).length) {
  out('### 本品牌优势');
  blank();
  arr(cp.brandStrengths).forEach(function (x, i) { out((i + 1) + '. ' + esc(x)); });
  blank();
}
if (arr(cp.brandWeaknesses).length) {
  out('### 本品牌短板');
  blank();
  arr(cp.brandWeaknesses).forEach(function (x, i) { out((i + 1) + '. ' + esc(x)); });
  blank();
}
if (cp.marketPosition) { out('**市场位置**：' + esc(cp.marketPosition)); blank(); }
out('---');
blank();

// ─────────────────────────── 09 舆情分析 ───────────────────────────
var st = S.SENTIMENT || {};
var sampleSize = (st.sampleSize === null || st.sampleSize === undefined) ? 0 : st.sampleSize;
out('## 09 舆情分析');
blank();
out('> ⚠️ 本章基于本次检索到的 ' + sampleSize + ' 条含品牌口碑内容的公开条目统计' + (sampleSize < 10 ? '，样本不足 10 条，风险等级仅供参考' : '') + '。本报告不实测 AI 平台输出的负面内容；未检索到的舆情不作推断。');
blank();
out('- **样本量**：' + sampleSize + (st.sampleNote ? '（' + esc(st.sampleNote) + '）' : ''));
out('- **风险等级**：' + esc(st.riskLevel));
out('- **趋势**：' + esc(st.trendDirection));
var dist = st.sentimentDistribution || {};
if (Object.keys(dist).length) {
  out('- **情感分布**：正面 ' + esc(dist.positive) + ' ｜ 中性 ' + esc(dist.neutral) + ' ｜ 负面 ' + esc(dist.negative));
}
blank();
if (arr(st.queryWords).length) {
  out('**检索词**：' + arr(st.queryWords).map(esc).join('、'));
  blank();
}
var nd = arr(st.negativeDetails);
if (nd.length) {
  out('### 负面条目明细');
  blank();
  table(['检索词', '来源', '标题', '链接', '日期'], nd.map(function (x) {
    return [esc(x.query), esc(x.source), esc(x.title), (x.url ? link(x.url) : ''), esc(x.date)];
  }));
  nd.forEach(function (x) {
    if (x.snippet) { out('> **' + esc(x.source) + '**：' + esc(x.snippet)); blank(); }
  });
}
var issues = arr(st.issues);
if (issues.length) {
  out('### 关键问题');
  blank();
  table(['情感', '内容', '来源', '链接', '日期'], issues.map(function (x) {
    return [esc(x.sentiment), esc(x.content), esc(x.source), (x.url ? link(x.url) : ''), esc(x.date)];
  }));
}
var kd = st.keyDrivers || {};
if (arr(kd.positive).length) { out('### 正面驱动因素'); blank(); arr(kd.positive).forEach(function (x) { out('- ' + esc(x)); }); blank(); }
if (arr(kd.negative).length) { out('### 负面驱动因素'); blank(); arr(kd.negative).forEach(function (x) { out('- ' + esc(x)); }); blank(); }
if (arr(st.suggestions).length) { out('### 舆情应对建议'); blank(); arr(st.suggestions).forEach(function (x, i) { out((i + 1) + '. ' + esc(x)); }); blank(); }
var pa = st.platformAnalysis || {};
var paKeys = Object.keys(pa);
if (paKeys.length) {
  out('### 分平台分析');
  blank();
  table(['平台', '分析'], paKeys.map(function (k) { return [esc(k), esc(anyVal(pa[k]))]; }));
}
out('---');
blank();

// ─────────────────────────── 10 信源收录证据 ───────────────────────────
var ge = S.GEO_EFFECT || {};
var entries = arr(ge.entries);
var total = (ge.totalEntries === null || ge.totalEntries === undefined) ? entries.length : ge.totalEntries;
var bySource = arr(ge.bySource);
out('## 10 信源收录证据');
blank();
var FIVE = ['百科', '权威媒体', '问答社区', '行业报告', '官网自有内容'];
var extraNames = bySource.filter(function (b) { return FIVE.indexOf(b.source) < 0; }).map(function (b) { return b.source; });
var extraLabel = extraNames.length ? extraNames.join('、') : '其他信源条目';
var aisExtra = total - aisCount;
out('> ⚠️ 本章是「信源收录清单」：把本次实际检索到的、承载品牌内容的页面逐条列出。不含任何提及率、排名占比等未经实测的指标。某类信源查不到条目即为 0 条，不做估计。' +
  (aisExtra > 0 ? '与第 06 章的口径关系：本章 ' + total + ' 条 = 第 06 章五类信源证据 ' + aisCount + ' 条，另加' + extraLabel + ' ' + aisExtra + ' 条。' : ''));
blank();
out('- **收录条目总数**：' + total);
blank();
if (bySource.length) {
  out('### 按信源分布');
  blank();
  table(['信源', '条数'], bySource.map(function (b) { return [esc(b.source), esc(b.count)]; }));
}
if (entries.length) {
  out('### 收录条目清单');
  blank();
  table(['信源', '标题', '链接', '日期'], entries.map(function (e) {
    return [esc(e.source), esc(e.title), (e.url ? link(e.url) : ''), esc(e.date)];
  }));
}
out('---');
blank();

// ─────────────────────────── 11 差距归因 ───────────────────────────
var om = S.OPPORTUNITY_MAP || {};
var opps = arr(om.opportunities);
out('## 11 差距归因');
blank();
opps.forEach(function (o, i) {
  out('### ' + (i + 1) + '. ' + esc(o.title) + '（' + esc(o.priority) + '）');
  blank();
  if (o.id) out('- **编号**：' + esc(o.id));
  if (o.rationale) out('- **归因**：' + esc(o.rationale));
  if (arr(o.relatedStageCodes).length) out('- **溯源章节**：' + arr(o.relatedStageCodes).map(esc).join('、'));
  if (o.expectedImpact) out('- **预期影响**：' + esc(o.expectedImpact));
  blank();
  if (arr(o.actions).length) {
    out('**行动项**');
    blank();
    arr(o.actions).forEach(function (a) { out('- ' + esc(a)); });
    blank();
  }
  if (arr(o.acceptanceCriteria).length) {
    out('**验收标准**');
    blank();
    arr(o.acceptanceCriteria).forEach(function (a) { out('- ' + esc(a)); });
    blank();
  }
});
if (arr(om.openQuestions).length) {
  out('### 待确认项（低置信度，需业务侧确认）');
  blank();
  table(['待确认问题', '为何重要'], arr(om.openQuestions).map(function (q) { return [esc(q.question), esc(q.whyItMatters)]; }));
}
out('---');
blank();

// ─────────────────────────── 12 行动路线图 ───────────────────────────
var sg = S.SUGGESTION || {};
var sp = sg.scoreProjection || {};
// 维度短码 → 中文名（与 HTML 渲染器的 dimLabelMap 保持一致）
var DIM_LABEL = { 'visibility': '可引用内容覆盖', 'content': '内容适配度', 'authority': '权威性', 'engagement': '用户参与度' };
function dimName(code) { return DIM_LABEL[code] || code; }
out('## 12 行动路线图');
blank();
if (sp.currentScore !== null && sp.currentScore !== undefined) {
  out('- **当前评分**：' + esc(sp.currentScore) + ' → **优化后预期评分**：' + esc(sp.projectedScore === null || sp.projectedScore === undefined ? '—' : sp.projectedScore));
  blank();
  if (arr(sp.dimensionProjections).length) {
    table(['维度', '当前 → 预期'], arr(sp.dimensionProjections).map(function (d) {
      return [esc(dimName(d.dimension || d.name)), esc((d.currentScore !== undefined ? d.currentScore : d.current) ) + ' → ' + esc((d.projectedScore !== undefined ? d.projectedScore : d.projected))];
    }));
  }
}
if (arr(sg.priorityActions).length) {
  out('### 优先行动');
  blank();
  arr(sg.priorityActions).forEach(function (a, i) {
    out('#### ' + (i + 1) + '. ' + esc(a.title) + '（' + esc(a.priority) + '）');
    blank();
    if (a.description) out('- **说明**：' + esc(a.description));
    if (a.dimension) out('- **对应维度**：' + esc(dimName(a.dimension)));
    if (a.impactLevel) out('- **影响 / 投入 / 周期**：' + esc(a.impactLevel) + ' / ' + esc(a.effortLevel) + ' / ' + esc(a.timeline));
    if (a.expectedImprovement) out('- **预期提升**：' + esc(a.expectedImprovement));
    if (arr(a.relatedStages).length) out('- **关联章节**：' + arr(a.relatedStages).map(esc).join('、'));
    blank();
    if (arr(a.nextSteps).length) {
      out('**下一步**');
      blank();
      arr(a.nextSteps).forEach(function (s) { out('- ' + esc(s)); });
      blank();
    }
  });
}
var roadmap = arr(sg.roadmap);
if (roadmap.length) {
  out('### 路线图');
  blank();
  roadmap.forEach(function (ph) {
    out('#### ' + esc(ph.phase) + '：' + esc(ph.title) + '（' + esc(ph.timeline) + '）');
    blank();
    arr(ph.items).forEach(function (it) { out('- ' + esc(it)); });
    blank();
  });
}
if (arr(sg.quickWins).length) {
  out('### 快速见效项');
  blank();
  table(['优先级', '维度', '事项', '影响 / 投入', '周期'], arr(sg.quickWins).map(function (q) {
    return [esc(q.priority), esc(q.dimension), esc(q.title), esc(q.impactLevel) + ' / ' + esc(q.effortLevel), esc(q.timeline)];
  }));
}
if (arr(sg.dimensionSummary).length) {
  out('### 分维度提升一览');
  blank();
  table(['维度', '当前 → 预期', '关键动作'], arr(sg.dimensionSummary).map(function (d) {
    return [esc(dimName(d.dimension)), esc(d.currentScore) + ' → ' + esc(d.projectedScore), esc(d.keyActions)];
  }));
}
if (arr(sg.longTermSuggestions).length) {
  out('### 长期建议');
  blank();
  arr(sg.longTermSuggestions).forEach(function (x) {
    out('- ' + esc(x.content) + '（' + esc(x.timeline) + '）');
  });
  blank();
}
if (sg.summary) { out('**小结**：' + esc(sg.summary)); blank(); }
out('---');
blank();

// ─────────────────────────── 页脚 ───────────────────────────
out('## 评估方法与边界');
blank();
out('本报告为「四幕 12 章」全景审计：结论（01）→ 身份（02）→ 资产（03–04）→ 表现（05–10）→ 行动（11–12）。所有结论均标注可核验的证据来源（URL + 日期）；未取得证据的条目不做推断、不计分。「AI 可引用内容覆盖」以站外信源上是否存在可被 AI 引用的品牌内容计量，本报告未实测各 AI 平台的实时输出。');
blank();
out('> 生成时间：' + today + '　|　评估引擎：Mentis-Paranoma-Audit-CN v2.2　|　Mentis · 可信 GEO');
blank();

// ─────────────────────────── 写入 ───────────────────────────
var md = L.join('\n').replace(/\n{3,}/g, '\n\n').replace(/\s+$/, '') + '\n';
try {
  fs.writeFileSync(outputPath, md, 'utf8');
} catch (e) {
  console.error('❌ 输出文件写入失败: ' + outputPath);
  console.error('   ' + e.message);
  process.exit(4);
}

console.log('✅ Markdown 报告生成成功');
console.log('   品牌: ' + brand + ' | 类型: ' + category);
console.log('   输出: ' + outputPath);
console.log('   大小: ' + (Buffer.byteLength(md, 'utf8') / 1024).toFixed(1) + ' KB (' + md.split('\n').length + ' 行)');
