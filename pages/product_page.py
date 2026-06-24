from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class ProductPage(BasePage):
    """무신사 상품 상세 페이지 객체"""

    # Locators
    LIKE_BUTTON = (By.XPATH, '//android.widget.Button[@text="좋아요 버튼"]')
    BACK_BUTTON = (AppiumBy.ACCESSIBILITY_ID, '이전 페이지로 이동')

    def click_like(self):
        """좋아요 버튼을 클릭합니다."""
        self._click(self.LIKE_BUTTON)

    def go_back(self):
        """이전 페이지로 돌아갑니다."""
        self._click(self.BACK_BUTTON)

    def is_product_detail_loaded(self, timeout=10) -> bool:
        """상품 상세 페이지가 로드되었는지 확인합니다."""
        return self._is_element_present(self.LIKE_BUTTON, timeout)
