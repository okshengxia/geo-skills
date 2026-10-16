#!/usr/bin/env bash
# Mentis-Paranoma-Audit-CN 一键编排（完整全景审计，无 quick 模式）
#
# 用法: bash orchestrate.sh <品牌目录> <品牌> [产品类型] [Mentis导出根目录]
#   <品牌目录>   — 品牌专属输出目录（需已含 agent 产出的 stage0-4.json）
#   <Mentis导出> — 可选；提供时先解析 Mentis Excel 得到真实品牌指标（产品级数据仅留档，不成章）
#
# 产物: <品牌目录>/<品牌>全景审计报告.html ＋ <品牌目录>/<品牌>全景审计报告.md
# 运行时可经环境变量覆盖: MENTIS_PY / MENTIS_NODE
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "用法: bash orchestrate.sh <品牌目录> <品牌> [产品类型] [Mentis导出根目录]" >&2
  exit 1
fi

BRAND_DIR="$1"; BRAND="$2"; PROD="${3:-}"; MENTIS_ROOT="${4:-}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PY="${MENTIS_PY:-python3}"
NODE="${MENTIS_NODE:-node}"

mkdir -p "$BRAND_DIR"

if [ -n "$MENTIS_ROOT" ]; then
  echo "==> [1/4] 解析 Mentis Excel（真实数据）"
  "$PY" "$SKILL_DIR/parse-mentis-xlsx.py" "$MENTIS_ROOT" "$BRAND" "$PROD" "$BRAND_DIR"
else
  echo "==> [1/4] 跳过 Mentis Excel（未提供导出目录）"
fi

echo "==> [2/4] 合并阶段 JSON"
"$NODE" "$SKILL_DIR/merge-stages.js" "$BRAND_DIR" "$BRAND" "$PROD"

echo "==> [3/4] 渲染 HTML 报告"
"$NODE" "$SKILL_DIR/build-report.js" "$BRAND_DIR/$BRAND-diag-report.json"

echo "==> [4/4] 渲染 Markdown 报告"
"$NODE" "$SKILL_DIR/build-report-md.js" "$BRAND_DIR/$BRAND-diag-report.json"

echo "✅ 完成: $BRAND_DIR/$BRAND全景审计报告.html ＋ $BRAND_DIR/$BRAND全景审计报告.md"
