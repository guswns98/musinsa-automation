from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
import time


class BasePage:
    """모든 페이지 객체의 부모가 되는 기본 페이지 클래스입니다."""

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def _find_element(self, locator: tuple, timeout: int = 10):
        """지정된 시간(timeout) 동안 요소를 기다려 찾습니다."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            raise NoSuchElementException(f"요소를 찾을 수 없습니다: {locator} (시간 초과: {timeout}초)")

    def _find_elements(self, locator: tuple, timeout: int = 10):
        """지정된 시간 동안 여러 요소를 찾습니다."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
            return self.driver.find_elements(*locator)
        except TimeoutException:
            return []

    def _click(self, locator: tuple, timeout: int = 10):
        """요소를 찾아 클릭합니다. 클릭 가능할 때까지 기다립니다."""
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            raise NoSuchElementException(f"요소를 찾거나 클릭할 수 없습니다: {locator} (시간 초과: {timeout}초)")
        try:
            element.click()
        except StaleElementReferenceException:
            time.sleep(1.5)
            try:
                element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(locator))
                element.click()
            except TimeoutException:
                raise NoSuchElementException(f"재시도 중 요소를 찾을 수 없습니다: {locator}")

    def _send_keys(self, locator: tuple, text: str, timeout: int = 10):
        """요소를 찾아 텍스트를 입력합니다."""
        element = self._find_element(locator, timeout)
        element.click()
        element.send_keys(text)

    def _get_text(self, locator: tuple, timeout: int = 10) -> str:
        """요소의 텍스트를 반환합니다."""
        return self._find_element(locator, timeout).text

    def _is_element_present(self, locator: tuple, timeout: int = 5) -> bool:
        """요소가 존재하는지 확인합니다."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def _wait(self, seconds: float):
        """지정된 시간(초)만큼 명시적으로 대기합니다."""
        time.sleep(seconds)

    def scroll_down(self, distance=500):
        """화면을 아래로 스크롤합니다."""
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = int(size['height'] * 0.8)
        end_y = start_y - distance

        self.driver.swipe(start_x, start_y, start_x, end_y, 500)

    def scroll_up(self, distance=500):
        """화면을 위로 스크롤합니다."""
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = int(size['height'] * 0.2)
        end_y = start_y + distance

        self.driver.swipe(start_x, start_y, start_x, end_y, 500)

    def swipe_up(self, duration=0.2):
        """화면을 빠르게 위로 스와이프합니다."""
        size = self.driver.get_window_size()
        start_x = size["width"] // 2
        start_y = int(size["height"] * 0.8)
        end_y = int(size["height"] * 0.3)

        finger = PointerInput("touch", "finger")
        actions = ActionBuilder(self.driver, mouse=finger)
        actions.pointer_action.move_to_location(start_x, start_y)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(duration)
        actions.pointer_action.move_to_location(start_x, end_y)
        actions.pointer_action.pointer_up()
        actions.perform()

    def tap_by_coordinates(self, x: int, y: int):
        """좌표를 직접 탭합니다."""
        finger = PointerInput("touch", "finger")
        actions = ActionBuilder(self.driver, mouse=finger)
        actions.pointer_action.move_to_location(x, y)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(0.1)
        actions.pointer_action.pointer_up()
        actions.perform()

    def press_back(self):
        """안드로이드 물리 뒤로가기 버튼을 누릅니다."""
        self.driver.press_keycode(4)

    def press_enter(self):
        """엔터 키를 누릅니다."""
        self.driver.press_keycode(66)
