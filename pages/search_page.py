from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class SearchPage(BasePage):
    """무신사 검색 결과 페이지 객체"""

    # Locators
    SEARCH_INPUT = (AppiumBy.CLASS_NAME, 'android.widget.EditText')

    def search_keyword(self, keyword: str):
        """키워드를 입력하고 검색합니다."""
        self._send_keys(self.SEARCH_INPUT, keyword)
        self.press_enter()
        self._wait(5)

    def scroll_to_item(self, keyword: str):
        """스크롤하여 특정 키워드가 포함된 상품을 찾아 클릭합니다."""
        locator = (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiScrollable(new UiSelector().scrollable(true))'
            f'.scrollIntoView(new UiSelector().descriptionContains("{keyword}"))'
        )
        element = self._find_element(locator)
        self._wait(5)
        element.click()
        self._wait(2)

    def is_search_results_loaded(self, timeout=10) -> bool:
        """검색 결과가 로드되었는지 확인합니다."""
        return self._is_element_present(self.SEARCH_INPUT, timeout)
