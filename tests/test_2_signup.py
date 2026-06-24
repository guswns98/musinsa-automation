from pages.permission_page import PermissionPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.signup_page import SignupPage


def test_signup_flow(driver):
    """회원가입 화면에서 전체 동의 후 문자 본인 인증 화면까지 진입 확인"""
    permission = PermissionPage(driver)
    home = HomePage(driver)
    login = LoginPage(driver)
    signup = SignupPage(driver)

    # 권한 처리 및 인트로 팝업
    if permission.is_permission_popup_visible(timeout=3):
        permission.handle_all_permissions()
    if home.is_intro_popup_visible(timeout=5):
        home.close_intro_popup()

    # 로그인 화면 -> 회원가입
    login.navigate_to_login()
    login.navigate_to_signup()

    # 전체 동의 및 본인 인증
    signup.agree_all_terms()
    signup.click_verify_button()
    signup.select_sms_verification()

    # 뒤로가기로 로그인 화면 복귀
    signup.go_back_to_login()
