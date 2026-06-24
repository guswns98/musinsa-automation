#!/bin/bash
# 비기능 테스트 (오프라인 네트워크, 성능) 실행 스크립트

pkill -f "appium" 2>/dev/null
sleep 2
appium &
sleep 10

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_DIR="reports/${TIMESTAMP}_nonfunctional"
mkdir -p "${REPORT_DIR}"

# 비기능 테스트 실행
pytest tests/test_offline_network.py tests/test_perf.py \
    --html="${REPORT_DIR}/report.html" \
    --self-contained-html \
    -v \
    "$@"

echo "비기능 테스트 리포트: ${REPORT_DIR}/report.html"

pkill -f "appium" 2>/dev/null
