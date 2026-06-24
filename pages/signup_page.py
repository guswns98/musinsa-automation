from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class SignupPage(BasePage):
    """무신사 회원가입 페이지 객체"""

    # Locators
    ALL_AGREE_CHECKBOX = (By.XPATH, '//android.widget.CheckBox[@resource-id="loginJoinMembershipAllCheckbox"]')
    VERIFY_BUTTON = (By.XPATH, '//android.widget.Button[@resource-id="openSelfCertifyPopup"]')
    SMS_VERIFY = (AppiumBy.ACCESSIBILITY_ID, '문자로 본인 인증')

    def agree_all_terms(self):
        """전체 동의 체크박스를 클릭합니다."""
        self._click(self.ALL_AGREE_CHECKBOX)

    def click_verify_button(self):
        """본인 인증 버튼을 클릭합니다."""
        self._click(self.VERIFY_BUTTON)
        self._wait(5)

    def select_sms_verification(self):
        """문자 본인 인증을 선택합니다."""
        self._click(self.SMS_VERIFY)
        self._wait(5)

    def go_back_to_login(self):
        """로그인 화면으로 돌아갑니다."""
        self.press_back()
        self._wait(5)
        self.press_back()
        self._wait(5)
