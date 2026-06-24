from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.product_page import ProductPage
from pages.my_page import MyPage


def test_add_to_favorites(driver):
    """상품 좋아요 후 즐겨찾기 탭에서 상품 노출 확인"""
    home = HomePage(driver)
    search = SearchPage(driver)
    product = ProductPage(driver)
    my_page = MyPage(driver)

    # 검색 -> 상품 상세 -> 좋아요
    home.go_to_home_tab()
    home.click_search()
    search.search_keyword("반팔")
    search.scroll_to_item("반팔")
    product.click_like()
    product.go_back()

    # 즐겨찾기 탭 이동 및 확인
    my_page.go_to_favorites()
    assert my_page.is_favorites_loaded(), "즐겨찾기 화면이 로드되지 않았습니다."
