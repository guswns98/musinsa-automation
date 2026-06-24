import pytest
from pages.my_page import MyPage


def test_my_page_and_logout(driver):
    """마이페이지에서 설정까지 스크롤 후 로그아웃 성공 확인"""
    my_page = MyPage(driver)

    # 마이 탭 이동
    my_page.go_to_my_tab()

    # 설정 영역까지 스크롤
    my_page.scroll_to_settings(scroll_count=3)

    # 로그아웃
    my_page.click_logout()
    my_page.confirm_logout()
