from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class PermissionPage(BasePage):
    """앱 실행 시 권한 허용 및 초기 화면 처리 페이지 객체"""

    # Locators
    INITIAL_CONFIRM = (By.XPATH, '//android.view.ViewGroup/android.view.View/android.view.View/android.view.View/android.view.View[2]')
    PERMISSION_ALLOW = (By.ID, 'com.android.permissioncontroller:id/permission_allow_button')

    def handle_initial_popup(self):
        """앱 최초 실행 시 팝업을 처리합니다."""
        self._click(self.INITIAL_CONFIRM)
        self._wait(3)

    def allow_permission(self):
        """시스템 권한 팝업에서 허용을 누릅니다."""
        self._click(self.PERMISSION_ALLOW)
        self._wait(5)

    def handle_all_permissions(self):
        """초기 팝업 + 권한 허용을 순서대로 처리합니다."""
        self.handle_initial_popup()
        self.allow_permission()

    def is_permission_popup_visible(self, timeout=5) -> bool:
        """권한 팝업이 표시되는지 확인합니다."""
        return self._is_element_present(self.PERMISSION_ALLOW, timeout)
