from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class LoginPage(BasePage):
    """무신사 로그인 페이지 객체"""

    # Locators
    MY_TAB = (By.ID, 'com.musinsa.store:id/item_my')
    LOGIN_BUTTON = (By.XPATH, '//android.widget.TextView[@text="로그인/회원가입하기"]')
    ID_INPUT = (By.XPATH, '//android.widget.EditText[@hint="아이디 입력"]')
    PASSWORD_INPUT = (By.XPATH, '//android.widget.EditText[@hint="비밀번호 입력"]')
    SUBMIT_LOGIN = (By.XPATH, '//android.widget.Button[@text="로그인"]')
    ERROR_CONFIRM = (By.ID, 'android:id/button1')
    KAKAO_LOGIN = (AppiumBy.ACCESSIBILITY_ID, 'kakao 로고 카카오 로그인')
    KAKAO_SHEET_CLOSE = (AppiumBy.ACCESSIBILITY_ID, '시트 닫기')
    SIGNUP_BUTTON = (AppiumBy.ACCESSIBILITY_ID, '회원가입')

    def navigate_to_login(self):
        """마이 탭을 통해 로그인 화면으로 이동합니다."""
        self._click(self.MY_TAB)
        self._click(self.LOGIN_BUTTON)

    def login_with_credentials(self, user_id: str, password: str):
        """아이디/비밀번호로 로그인을 시도합니다."""
        self._send_keys(self.ID_INPUT, user_id)
        self._send_keys(self.PASSWORD_INPUT, password)
        self._click(self.SUBMIT_LOGIN)
        self._wait(3)

    def is_login_error_visible(self, timeout=5) -> bool:
        """로그인 실패 에러 팝업이 표시되는지 확인합니다."""
        return self._is_element_present(self.ERROR_CONFIRM, timeout)

    def dismiss_login_error(self):
        """로그인 실패 에러 팝업을 닫습니다."""
        self._click(self.ERROR_CONFIRM)
        self._wait(2)

    def login_with_kakao(self):
        """카카오 계정으로 로그인합니다."""
        self._click(self.KAKAO_LOGIN)
        self._wait(5)
        self._click(self.KAKAO_SHEET_CLOSE)
        self._wait(5)

    def navigate_to_signup(self):
        """회원가입 화면으로 이동합니다."""
        self._click(self.SIGNUP_BUTTON)
        self._wait(7)
