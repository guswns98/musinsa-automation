from pages.permission_page import PermissionPage
from pages.home_page import HomePage
from pages.login_page import LoginPage


def test_login_fail(driver):
    """잘못된 아이디/비밀번호 입력 시 로그인 실패 에러 팝업 노출 확인"""
    permission = PermissionPage(driver)
    home = HomePage(driver)
    login = LoginPage(driver)

    # 권한 처리 및 인트로 팝업 닫기
    if permission.is_permission_popup_visible(timeout=3):
        permission.handle_all_permissions()
    if home.is_intro_popup_visible(timeout=5):
        home.close_intro_popup()

    # 로그인 화면 진입
    login.navigate_to_login()

    # 잘못된 자격증명으로 로그인 시도
    login.login_with_credentials("test1234", "test125")

    # 에러 팝업 노출 확인
    assert login.is_login_error_visible(), "로그인 실패 에러 팝업이 표시되지 않습니다."
    login.dismiss_login_error()
