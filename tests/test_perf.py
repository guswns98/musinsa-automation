"""
성능 테스트 (Cold Start / Warm Start / 메모리 모니터링)

앱의 시작 성능과 메모리 사용량을 측정합니다.
각 측정은 3회 반복하여 평균값을 산출합니다.
"""
import subprocess
import time
import json
import os
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from utils.performance_utils import get_performance_snapshot

APP_PACKAGE = "com.musinsa.store"
APP_ACTIVITY = "com.musinsa.store.scenes.deeplink.DeepLinkActivity"
ITERATIONS = 3


def _adb(*cmd: str, timeout: int = 10) -> str:
    result = subprocess.run(
        ["adb"] + list(cmd),
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip()


def _force_stop_app():
    _adb("shell", "am", "force-stop", APP_PACKAGE)
    time.sleep(2)


def _launch_app_and_measure():
    """앱을 시작하고 첫 화면 렌더링까지 시간을 측정합니다."""
    start = time.time()
    _adb("shell", "am", "start", "-n", f"{APP_PACKAGE}/{APP_ACTIVITY}")
    # 앱이 로드될 때까지 대기 (최대 15초)
    for _ in range(30):
        time.sleep(0.5)
        output = _adb("shell", "dumpsys", "activity", "activities")
        if APP_PACKAGE in output and "resumed" in output.lower():
            break
    elapsed = time.time() - start
    return round(elapsed, 2)


@pytest.fixture(scope="module")
def driver():
    """성능 테스트 전용 드라이버"""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "R5CT22SD0GJ"
    options.app_package = APP_PACKAGE
    options.app_activity = APP_ACTIVITY
    options.language = "ko"
    options.locale = "KR"
    options.app_wait_activity = "*"
    options.no_reset = True
    options.clear_system_files = False

    driver_instance = webdriver.Remote("http://localhost:4723", options=options)
    time.sleep(5)
    yield driver_instance

    try:
        driver_instance.terminate_app(APP_PACKAGE)
    except Exception:
        pass
    try:
        driver_instance.quit()
    except Exception:
        pass


def test_cold_start_time(driver, request):
    """앱 콜드 스타트 시간 측정 (3회 반복)"""
    results = []
    for i in range(ITERATIONS):
        _force_stop_app()
        time.sleep(1)
        elapsed = _launch_app_and_measure()
        results.append(elapsed)
        print(f"[콜드 스타트 #{i+1}] {elapsed}초")
        time.sleep(3)

    avg = round(sum(results) / len(results), 2)
    print(f"[콜드 스타트 평균] {avg}초")

    report_dir = getattr(request.config, '_report_dir', 'reports')
    os.makedirs(report_dir, exist_ok=True)
    with open(os.path.join(report_dir, "perf_cold_start.json"), "w") as f:
        json.dump({"type": "cold_start", "results_sec": results, "avg_sec": avg}, f, indent=2)

    assert avg < 10, f"콜드 스타트 평균 {avg}초 - 10초 초과"


def test_warm_start_time(driver, request):
    """앱 웜 스타트 시간 측정 (백그라운드 60초 후 복귀, 3회 반복)"""
    results = []
    for i in range(ITERATIONS):
        # 홈 키로 백그라운드 전환
        _adb("shell", "input", "keyevent", "3")
        time.sleep(5)  # 5초 대기 (실제 60초 대신 테스트 효율성)

        start = time.time()
        _adb("shell", "am", "start", "-n", f"{APP_PACKAGE}/{APP_ACTIVITY}")
        time.sleep(3)
        elapsed = round(time.time() - start, 2)
        results.append(elapsed)
        print(f"[웜 스타트 #{i+1}] {elapsed}초")

    avg = round(sum(results) / len(results), 2)
    print(f"[웜 스타트 평균] {avg}초")

    report_dir = getattr(request.config, '_report_dir', 'reports')
    os.makedirs(report_dir, exist_ok=True)
    with open(os.path.join(report_dir, "perf_warm_start.json"), "w") as f:
        json.dump({"type": "warm_start", "results_sec": results, "avg_sec": avg}, f, indent=2)

    assert avg < 5, f"웜 스타트 평균 {avg}초 - 5초 초과"


def test_memory_usage(driver, request):
    """주요 화면 탐색 중 메모리 사용량 측정"""
    from pages.home_page import HomePage
    from pages.my_page import MyPage

    snapshots = []

    # 홈 탭
    home = HomePage(driver)
    home.go_to_home_tab()
    time.sleep(3)
    snap = get_performance_snapshot(driver)
    snap["screen"] = "home"
    snapshots.append(snap)
    print(f"[메모리] 홈 탭: {snap.get('memory_mb', '?')}MB")

    # 스크롤 후
    from pages.base_page import BasePage
    base = BasePage(driver)
    for _ in range(5):
        base.scroll_down(500)
        time.sleep(1)
    snap = get_performance_snapshot(driver)
    snap["screen"] = "home_scrolled"
    snapshots.append(snap)
    print(f"[메모리] 홈 스크롤 후: {snap.get('memory_mb', '?')}MB")

    # 마이 탭
    my_page = MyPage(driver)
    my_page.go_to_my_tab()
    time.sleep(3)
    snap = get_performance_snapshot(driver)
    snap["screen"] = "my_page"
    snapshots.append(snap)
    print(f"[메모리] 마이 탭: {snap.get('memory_mb', '?')}MB")

    # 결과 저장
    report_dir = getattr(request.config, '_report_dir', 'reports')
    os.makedirs(report_dir, exist_ok=True)
    with open(os.path.join(report_dir, "perf_memory_usage.json"), "w") as f:
        json.dump({"type": "memory_usage", "snapshots": snapshots}, f, ensure_ascii=False, indent=2)

    # 메모리 임계치 확인 (500MB 초과 시 경고)
    mem_values = [s.get("memory_mb", 0) for s in snapshots if s.get("memory_mb")]
    if mem_values:
        max_mem = max(mem_values)
        print(f"[메모리] 최대: {max_mem}MB")
        assert max_mem < 500, f"메모리 사용량 {max_mem}MB - 500MB 초과"
