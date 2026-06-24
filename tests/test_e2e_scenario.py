"""
E2E 통합 시나리오 테스트

앱 실행부터 로그아웃까지 전체 사용자 여정을 단일 세션에서 검증합니다.
메모리 누적 추이를 관찰하기 위해 module 스코프 드라이버를 사용합니다.
"""
import time
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from utils.common_utils import get_app_version
from utils.performance_utils import get_performance_snapshot, save_performance_log
from pages.permission_page import PermissionPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from pages.search_page import SearchPage
from pages.product_page import ProductPage
from pages.my_page import MyPage

APP_PACKAGE = 'com.musinsa.store'


@pytest.fixture(scope="module")
def driver():
    """E2E 전용: 모듈 내 모든 테스트가 하나의 세션을 공유합니다."""
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.automation_name = 'UiAutomator2'
    options.device_name = 'R5CT22SD0GJ'
    options.app_package = APP_PACKAGE
    options.app_activity = 'com.musinsa.store.scenes.deeplink.DeepLinkActivity'
    options.language = 'ko'
    options.locale = 'KR'
    options.app_wait_activity = '*'
    options.no_reset = True
    options.clear_system_files = False

    driver_instance = webdriver.Remote('http://localhost:4723', options=options)
    time.sleep(5)

    version = get_app_version(driver_instance)
    pytest.app_version = version
    print(f"[E2E] 앱 버전: {version}")

    yield driver_instance

    try:
        driver_instance.terminate_app(APP_PACKAGE)
        time.sleep(3)
    except Exception:
        pass
    try:
        driver_instance.quit()
    except Exception:
        pass


@pytest.fixture(scope="function", autouse=True)
def performance_monitoring(driver, request):
    """각 E2E 스텝 시작/종료 시 성능 스냅샷 수집 (단일 세션 누적)"""
    before = get_performance_snapshot(driver)
    yield
    try:
        after = get_performance_snapshot(driver)
        report_dir = getattr(request.config, '_report_dir', None)
        result = save_performance_log(request.node.name, before, after, report_dir=report_dir)
        if not hasattr(request.config, '_perf_results'):
            request.config._perf_results = []
        request.config._perf_results.append(result)
    except Exception as e:
        print(f"성능 로그 저장 실패: {e}")


# ---------------------------------------------------------------------------
# E2E 시나리오 테스트
# ---------------------------------------------------------------------------

def test_e2e_01_launch_and_permission(driver):
    """E2E: 앱 실행 및 권한 처리"""
    permission = PermissionPage(driver)
    home = HomePage(driver)

    if permission.is_permission_popup_visible(timeout=3):
        permission.handle_all_permissions()
    if home.is_intro_popup_visible(timeout=5):
        home.close_intro_popup()

    assert home.is_home_loaded(), "홈 화면 로드 실패"


def test_e2e_02_login_fail(driver):
    """E2E: 로그인 실패 시나리오"""
    login = LoginPage(driver)

    login.navigate_to_login()
    login.login_with_credentials("test1234", "test125")
    assert login.is_login_error_visible(), "로그인 실패 에러 팝업 미노출"
    login.dismiss_login_error()


def test_e2e_03_signup_flow(driver):
    """E2E: 회원가입 플로우"""
    login = LoginPage(driver)
    signup = SignupPage(driver)

    login.navigate_to_signup()
    signup.agree_all_terms()
    signup.click_verify_button()
    signup.select_sms_verification()
    signup.go_back_to_login()


def test_e2e_04_kakao_login(driver):
    """E2E: 카카오 로그인 성공"""
    login = LoginPage(driver)
    home = HomePage(driver)

    login.login_with_kakao()
    assert home.is_home_loaded(), "카카오 로그인 후 홈 진입 실패"


def test_e2e_05_search_product(driver):
    """E2E: 상품 검색 및 상세 페이지 진입"""
    home = HomePage(driver)
    search = SearchPage(driver)
    product = ProductPage(driver)

    home.go_to_home_tab()
    home.click_search()
    search.search_keyword("반팔")
    search.scroll_to_item("반팔")

    assert product.is_product_detail_loaded(), "상품 상세 페이지 로드 실패"


def test_e2e_06_add_favorite(driver):
    """E2E: 상품 좋아요 추가"""
    product = ProductPage(driver)
    my_page = MyPage(driver)

    product.click_like()
    product.go_back()

    my_page.go_to_favorites()
    assert my_page.is_favorites_loaded(), "즐겨찾기 화면 로드 실패"


def test_e2e_07_my_page_scroll(driver):
    """E2E: 마이페이지 스크롤"""
    my_page = MyPage(driver)

    my_page.go_to_my_tab()
    my_page.scroll_to_settings(scroll_count=3)


def test_e2e_08_logout(driver):
    """E2E: 로그아웃"""
    my_page = MyPage(driver)

    my_page.click_logout()
    my_page.confirm_logout()
