#!/usr/bin/env node
'use strict';

/**
 * Mentis-Paranoma-Audit-CN - 阶段JSON合并脚本 v2.2.0
 *
 * 用法: node merge-stages.js <output-dir> <brand> [product] [output-path]
 *   output-dir  — 各阶段JSON所在目录（必填）
 *   brand       — 品牌名称（必填）
 *   product     — 产品/品类（可选；缺省回退 ENTITY_MAP.entityType）
 *   output-path — 合并后JSON输出路径（可选，默认 <dir>/<brand>-diag-report.json）
 *
 * 本 skill 只有一种模式：完整全景审计（stage 0-4 全跑）。
 *
 * 阶段文件命名约定：
 *   stage0.json        — 阶段0 站外全景审计（ENTITY_MAP/PLATFORM_MATRIX/QUESTION_POOL/OPPORTUNITY_MAP）
 *   stage1.json        — 阶段1（USER_PROFILE + INFRA_EVAL + COMPETITOR）
 *   stage2.json        — 阶段2（AI_SEARCH + GEO_EFFECT + shouluResults）
 *   stage3.json        — 阶段3（SENTIMENT）
 *   stage4.json        — 阶段4（OVERVIEW + AIVO_SCORE + SUGGESTION）
 *   stage_product.json — 可选（Mentis 产品可见度真实数据，保留溯源不删）
 *   mentis-meta.json   — 可选（Mentis 元信息，保留溯源不删）
 *
 * 退出码:
 *   0 — 成功
 *   1 — 参数缺失/非法
 *   2 — 必需阶段文件缺失
 *   3 — JSON解析失败
 *   4 — 输出写入失败
 */

var fs = require('fs');
var path = require('path');

var positional = process.argv.slice(2).filter(function (a) {
  return a.indexOf('--') !== 0;
});

if (positional.length < 2) {
  console.error('用法: node merge-stages.js <output-dir> <brand> [product] [output-path]');
  process.exit(1);
}

var outputDir = path.resolve(positional[0]);
var brand = positional[1];
var product = positional[2] || '';
var outputPath = positional[3]
  ? path.resolve(positional[3])
  : path.join(outputDir, brand + '-diag-report.json');

// ── 读取阶段文件 ──
function readJson(fname, required) {
  var p = path.join(outputDir, fname);
  if (!fs.existsSync(p)) {
    if (required) {
      console.error('❌ 阶段文件缺失: ' + p);
      process.exit(2);
    }
    return null;
  }
  try {
    var data = JSON.parse(fs.readFileSync(p, 'utf8'));
    console.log('✅ 已读取: ' + fname + ' (' + Math.round(fs.statSync(p).size / 1024) + 'KB)');
    return data;
  } catch (e) {
    console.error('❌ JSON解析失败: ' + fname);
    console.error('   ' + e.message);
    process.exit(3);
  }
}

var s0 = readJson('stage0.json', true);
var s1 = readJson('stage1.json', true);
var s2 = readJson('stage2.json', true);
var s3 = readJson('stage3.json', true);
var s4 = readJson('stage4.json', true);

// ── 可选文件：产品可见度 + Mentis 元信息（缺失不阻断，保留溯源不删）──
var optionalFiles = { 'stage_product.json': 'productData', 'mentis-meta.json': 'metaData' };
var optionalData = {};
Object.keys(optionalFiles).forEach(function (fname) {
  var p = path.join(outputDir, fname);
  if (fs.existsSync(p)) {
    try {
      optionalData[optionalFiles[fname]] = JSON.parse(fs.readFileSync(p, 'utf8'));
      console.log('✅ 已读取(可选): ' + fname);
    } catch (e) {
      console.warn('⚠️ 可选文件解析失败，已跳过: ' + fname + ' (' + e.message + ')');
    }
  }
});

// ── 合并逻辑 ──
var entityType = (s0 && s0.entityMap && s0.entityMap.entityType) || '';
var category = product || entityType || '全景审计';

var merged = {
  version: '2.2',
  brand: brand,
  category: category,
  meta: (s4 && s4.meta) || (s3 && s3.meta) || (s2 && s2.meta) || (s1 && s1.meta) || (s0 && s0.meta) || {
    version: '2.2',
    brand: brand,
    product: product
  },
  stages: {}
};

// 阶段0 → ENTITY_MAP + PLATFORM_MATRIX + QUESTION_POOL + OPPORTUNITY_MAP
if (s0 && s0.entityMap) merged.stages.ENTITY_MAP = s0.entityMap;
if (s0 && s0.platformMatrix) merged.stages.PLATFORM_MATRIX = s0.platformMatrix;
if (s0 && s0.questionPool) merged.stages.QUESTION_POOL = s0.questionPool;
if (s0 && s0.opportunityMap) merged.stages.OPPORTUNITY_MAP = s0.opportunityMap;

// 阶段1 → USER_PROFILE + INFRA_EVAL + COMPETITOR
if (s1 && s1.userProfile) merged.stages.USER_PROFILE = s1.userProfile;
if (s1 && s1.infraEval) merged.stages.INFRA_EVAL = s1.infraEval;
if (s1 && s1.competitors) merged.stages.COMPETITOR = s1.competitors;

// 阶段2 → AI_SEARCH + GEO_EFFECT（shouluResults 嵌入 AI_SEARCH）
if (s2 && s2.aiSearch) {
  if (s2.shouluResults) {
    s2.aiSearch.shouluResults = s2.shouluResults;
  }
  merged.stages.AI_SEARCH = s2.aiSearch;
}
if (s2 && s2.geoEffect) merged.stages.GEO_EFFECT = s2.geoEffect;

// 阶段3 → SENTIMENT
if (s3 && s3.sentiment) merged.stages.SENTIMENT = s3.sentiment;

// 阶段4 → OVERVIEW + AIVO_SCORE + SUGGESTION
if (s4 && s4.overview) merged.stages.OVERVIEW = s4.overview;
if (s4 && s4.aivoScore) merged.stages.AIVO_SCORE = s4.aivoScore;
if (s4 && s4.suggestion) merged.stages.SUGGESTION = s4.suggestion;

// 可选 → PRODUCT_VISIBILITY + mentisMeta
if (optionalData.productData && optionalData.productData.productVisibility) {
  merged.stages.PRODUCT_VISIBILITY = optionalData.productData.productVisibility;
}
if (optionalData.metaData) {
  merged.mentisMeta = optionalData.metaData;
}

// ── stageCode 完整性验证 ──
var requiredStages = [
  'ENTITY_MAP', 'PLATFORM_MATRIX', 'QUESTION_POOL', 'OPPORTUNITY_MAP',
  'OVERVIEW', 'AIVO_SCORE', 'USER_PROFILE', 'AI_SEARCH', 'INFRA_EVAL',
  'COMPETITOR', 'GEO_EFFECT', 'SENTIMENT', 'SUGGESTION'
];

var missingStages = [];
for (var j = 0; j < requiredStages.length; j++) {
  if (!merged.stages[requiredStages[j]]) {
    missingStages.push(requiredStages[j]);
  }
}

if (missingStages.length > 0) {
  console.error('❌ 缺失必需stageCode(' + missingStages.length + '): ' + missingStages.join(', '));
  console.error('   全景审计要求 13 个 stageCode 齐全，禁止缺章交付。');
  process.exit(2);
}

// ── 写入合并JSON ──
try {
  var jsonStr = JSON.stringify(merged, null, 2);
  fs.writeFileSync(outputPath, jsonStr, 'utf8');
  var sizeKB = Math.round(Buffer.byteLength(jsonStr, 'utf8') / 1024);
  console.log('✅ 合并完成: ' + outputPath + ' (' + sizeKB + 'KB)');
  console.log('   品牌: ' + brand + ' | 品类: ' + category);
  console.log('   包含stageCode(' + Object.keys(merged.stages).length + '): ' + Object.keys(merged.stages).join(', '));
} catch (e) {
  console.error('❌ 写入失败: ' + e.message);
  process.exit(4);
}

// ── 清理阶段文件：仅删已读的 stage0-4.json；stage_product/mentis-meta 保留溯源 ──
['stage0.json', 'stage1.json', 'stage2.json', 'stage3.json', 'stage4.json'].forEach(function (f) {
  try {
    fs.unlinkSync(path.join(outputDir, f));
    console.log('🗑️ 已清理: ' + f);
  } catch (e) {
    // 忽略清理失败
  }
});

process.exit(0);
