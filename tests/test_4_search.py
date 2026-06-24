from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.product_page import ProductPage


def test_search_and_view_product(driver):
    """반팔 키워드 검색 후 스크롤하여 상품 상세 페이지 진입 확인"""
    home = HomePage(driver)
    search = SearchPage(driver)
    product = ProductPage(driver)

    # 홈에서 검색 진입
    home.go_to_home_tab()
    home.click_search()

    # 키워드 검색 및 상품 선택
    search.search_keyword("반팔")
    search.scroll_to_item("반팔")

    # 상품 상세 페이지 로드 확인
    assert product.is_product_detail_loaded(), "상품 상세 페이지가 로드되지 않았습니다."
