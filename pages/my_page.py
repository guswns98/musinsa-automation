from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class MyPage(BasePage):
    """무신사 마이페이지 객체"""

    # Locators
    MY_TAB = (By.ID, 'com.musinsa.store:id/item_my')
    LIKE_TAB = (By.ID, 'com.musinsa.store:id/item_like')
    LOGOUT_CONFIRM = (By.XPATH, '//android.view.ViewGroup/android.view.View/android.view.View/android.view.View/android.view.View[2]')

    def go_to_my_tab(self):
        """마이 탭으로 이동합니다."""
        self._click(self.MY_TAB)
        self._wait(3)

    def go_to_favorites(self):
        """즐겨찾기 탭으로 이동합니다."""
        self._click(self.LIKE_TAB)
        self._wait(3)

    def scroll_to_settings(self, scroll_count=3):
        """설정 영역까지 스크롤합니다."""
        for _ in range(scroll_count):
            self.swipe_up()
            self._wait(1)

    def click_logout(self, x=800, y=2560):
        """로그아웃 버튼을 탭합니다 (좌표 기반)."""
        self.tap_by_coordinates(x, y)

    def confirm_logout(self):
        """로그아웃 확인 팝업에서 확인을 누릅니다."""
        self._click(self.LOGOUT_CONFIRM)

    def is_favorites_loaded(self, timeout=10) -> bool:
        """즐겨찾기 화면이 로드되었는지 확인합니다."""
        return self._is_element_present(self.LIKE_TAB, timeout)
