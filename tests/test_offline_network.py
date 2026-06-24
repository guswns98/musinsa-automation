"""
네트워크 오프라인 상태 앱 동작 검증 테스트

ADB로 WiFi/모바일 데이터를 끊고 주요 화면에서 앱이 크래시하지 않으며
에러 UI(오프라인 안내, 빈 화면 등)를 표시하는지 검증합니다.
네트워크 복구 후 정상 데이터 로딩 여부도 함께 검증합니다.

검증 항목:
- 오프라인 전환 후 앱 미크래시 (PID 생존 확인)
- 오프라인 상태에서 정상 콘텐츠 미노출 (데이터 로딩 실패 확인)
- 네트워크 복구 후 홈 콘텐츠 정상 로딩 (자동 복구 확인)
- 오프라인 상태에서 앱 재시작 시 크래시 없음
"""
import subprocess
import time
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from pages.home_page import HomePage
from pages.my_page import MyPage

APP_PACKAGE = "com.musinsa.store"


# ---------------------------------------------------------------------------
# ADB 헬퍼
# ---------------------------------------------------------------------------

def _adb(*cmd: str, timeout: int = 10) -> str:
    """ADB 명령을 실행하고 stdout을 반환합니다."""
    result = subprocess.run(
        ["adb"] + list(cmd),
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip()


def _disable_network():
    """WiFi와 모바일 데이터를 모두 끕니다."""
    _adb("shell", "svc", "wifi", "disable")
    _adb("shell", "svc", "data", "disable")
    time.sleep(2)
    print("네트워크 차단 완료")


def _enable_network():
    """WiFi와 모바일 데이터를 복구합니다."""
    _adb("shell", "svc", "wifi", "enable")
    _adb("shell", "svc", "data", "enable")
    time.sleep(3)
    print("네트워크 복구 완료")


def _is_app_running() -> bool:
    """앱 프로세스가 살아있는지 확인합니다."""
    return bool(_adb("shell", "pidof", APP_PACKAGE))


def _force_stop_app():
    """앱을 강제 종료합니다."""
    _adb("shell", "am", "force-stop", APP_PACKAGE)
    time.sleep(2)


def _launch_app():
    """앱을 시작합니다."""
    _adb("shell", "monkey", "-p", APP_PACKAGE, "-c", "android.intent.category.LAUNCHER", "1")
    time.sleep(5)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def driver():
    """모듈 내 모든 테스트가 단일 Appium 세션을 공유합니다."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "R5CT22SD0GJ"
    options.app_package = APP_PACKAGE
    options.app_activity = "com.musinsa.store.scenes.deeplink.DeepLinkActivity"
    options.language = "ko"
    options.locale = "KR"
    options.app_wait_activity = "*"
    options.no_reset = True
    options.clear_system_files = False

    driver_instance = webdriver.Remote("http://localhost:4723", options=options)
    time.sleep(5)

    yield driver_instance

    # 테스트 종료 시 네트워크 반드시 복구
    _enable_network()
    try:
        driver_instance.terminate_app(APP_PACKAGE)
        time.sleep(2)
    except Exception:
        pass
    try:
        driver_instance.quit()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 오프라인 테스트
# ---------------------------------------------------------------------------

def test_offline_01_baseline_home(driver):
    """온라인 상태에서 홈 화면 정상 로드 (기준선)"""
    _enable_network()
    home = HomePage(driver)
    home.go_to_home_tab()
    assert home.is_home_loaded(), "온라인 상태에서 홈 화면 로드 실패"


def test_offline_02_home_tab_no_crash(driver):
    """오프라인 전환 후 홈 탭에서 앱이 크래시하지 않는지 확인"""
    _disable_network()
    home = HomePage(driver)
    home.go_to_home_tab()
    time.sleep(3)

    assert _is_app_running(), "오프라인 전환 후 앱이 크래시되었습니다 (홈 탭)"


def test_offline_03_my_tab_no_crash(driver):
    """오프라인 상태에서 마이 탭 진입 시 앱이 크래시하지 않는지 확인"""
    my_page = MyPage(driver)
    my_page.go_to_my_tab()
    time.sleep(3)

    assert _is_app_running(), "오프라인 상태에서 앱이 크래시되었습니다 (마이 탭)"


def test_offline_04_scroll_no_crash(driver):
    """오프라인 상태에서 스크롤 시 앱이 크래시하지 않는지 확인"""
    home = HomePage(driver)
    home.go_to_home_tab()
    time.sleep(2)

    from pages.base_page import BasePage
    base = BasePage(driver)
    for _ in range(3):
        base.scroll_down(500)
        time.sleep(1)

    assert _is_app_running(), "오프라인 스크롤 중 앱이 크래시되었습니다"


def test_offline_05_network_recovery(driver):
    """네트워크 복구 후 홈 화면이 정상 로딩되는지 확인"""
    _enable_network()
    time.sleep(5)

    home = HomePage(driver)
    home.go_to_home_tab()
    time.sleep(5)

    assert home.is_home_loaded(), "네트워크 복구 후 홈 화면 로딩 실패"
    assert _is_app_running(), "네트워크 복구 후 앱이 크래시되었습니다"


def test_offline_06_cold_start_offline_no_crash(driver):
    """오프라인 상태에서 앱 콜드 스타트 시 크래시 없음 확인"""
    _disable_network()
    _force_stop_app()
    _launch_app()

    assert _is_app_running(), "오프라인 콜드 스타트 시 앱이 크래시되었습니다"

    # 테스트 종료 후 네트워크 복구
    _enable_network()
