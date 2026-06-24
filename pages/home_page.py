from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class HomePage(BasePage):
    """무신사 홈 화면 페이지 객체"""

    # Locators
    HOME_TAB = (By.ID, 'com.musinsa.store:id/item_home')
    SEARCH_ICON = (By.XPATH, '//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[3]')
    INTRO_POPUP_CLOSE = (By.XPATH, '//android.widget.TextView[@text="닫기"]')

    def go_to_home_tab(self):
        """홈 탭으로 이동합니다."""
        self._click(self.HOME_TAB)
        self._wait(3)

    def close_intro_popup(self):
        """인트로 팝업을 닫습니다."""
        self._click(self.INTRO_POPUP_CLOSE)
        self._wait(2)

    def is_intro_popup_visible(self, timeout=5) -> bool:
        """인트로 팝업이 표시되는지 확인합니다."""
        return self._is_element_present(self.INTRO_POPUP_CLOSE, timeout)

    def click_search(self):
        """검색 아이콘을 클릭합니다."""
        self._click(self.SEARCH_ICON)
        self._wait(1)

    def is_home_loaded(self, timeout=10) -> bool:
        """홈 화면이 로드되었는지 확인합니다."""
        return self._is_element_present(self.HOME_TAB, timeout)
