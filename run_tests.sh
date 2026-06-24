#!/bin/bash
# 무신사 앱 자동화 테스트 실행 스크립트

# Appium 서버 종료 후 재시작
pkill -f "appium" 2>/dev/null
sleep 2
appium &
sleep 10

# 타임스탬프 폴더 생성
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_DIR="reports/${TIMESTAMP}"
mkdir -p "${REPORT_DIR}"

# 기능 테스트 실행
pytest tests/ \
    --html="${REPORT_DIR}/report.html" \
    --self-contained-html \
    --json-report --json-report-file="${REPORT_DIR}/result.json" \
    -v \
    --ignore=tests/test_offline_network.py \
    --ignore=tests/test_perf.py \
    --ignore=tests/test_e2e_scenario.py \
    "$@"

echo "리포트 생성 완료: ${REPORT_DIR}/report.html"

# Appium 서버 종료
pkill -f "appium" 2>/dev/null
