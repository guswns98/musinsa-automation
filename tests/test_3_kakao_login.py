from pages.permission_page import PermissionPage
from pages.home_page import HomePage
from pages.login_page import LoginPage


def test_kakao_login(driver):
    """카카오 계정으로 로그인하여 홈 화면 정상 진입 확인"""
    permission = PermissionPage(driver)
    home = HomePage(driver)
    login = LoginPage(driver)

    # 권한 처리 및 인트로 팝업
    if permission.is_permission_popup_visible(timeout=3):
        permission.handle_all_permissions()
    if home.is_intro_popup_visible(timeout=5):
        home.close_intro_popup()

    # 로그인 화면 진입 후 카카오 로그인
    login.navigate_to_login()
    login.login_with_kakao()

    # 홈 화면 로드 확인
    assert home.is_home_loaded(), "카카오 로그인 후 홈 화면에 진입하지 못했습니다."
