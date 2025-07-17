from appium import webdriver
from appium.options.android import UiAutomator2Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from datetime import datetime
import os

desired_caps = {
    "platformName": "Android",
    "appium:deviceName": "R5CT22SD0GJ",
    "appium:appPackage": "com.musinsa.store",
    "appium:appActivity": "com.musinsa.store.scenes.deeplink.DeepLinkActivity",
    "appium:automationName": "UiAutomator2"
}


options = UiAutomator2Options().load_capabilities(desired_caps)


# 스크린샷 저장
def save_screenshot(driver, name="screenshot", folder="screenshots"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder, f"{name}_{timestamp}.png")

    driver.save_screenshot(filename)

# 리포트 생성
def generate_html_report(image_folder="screenshots", output_file="report.html"):
    from datetime import datetime
    result_map = {
        "launch_and_close_intro": ("앱 실행 및 인트로 광고 닫기", "success"),
        "login_fail": ("로그인 실패", "fail"),
        "signup_phone_verification": ("회원가입 - 문자 인증", "success"),
        "kakao_login_complete": ("카카오 로그인 완료", "success"),
        "search_item_detail": ("상품 상세보기", "success"),
        "favorites_view": ("즐겨찾기 화면", "success"),
        "settings_before_logout": ("로그아웃 이전 화면", "success"),
        "logout_complete": ("로그아웃 완료", "success")
    }

    screenshots = sorted([f for f in os.listdir(image_folder) if f.endswith(".png")])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("""
        <html><head>
        <meta charset='utf-8'>
        <title>테스트 리포트</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .success { color: green; }
            .fail { color: red; }
            .img-wrapper { text-align: center; margin-top: 10px; }
            img { max-width: 600px; border: 1px solid #ccc; }
            .timestamp { font-size: 0.9em; color: #555; }
        </style>
        </head><body>
        <h1>자동화 테스트 리포트</h1><hr>
        """)

        for img in screenshots:
            key = img.replace(".png", "")
            matched_key = next((k for k in result_map if key.startswith(k)), None)
            description, status = result_map.get(matched_key, ("알 수 없는 항목", "unknown"))
            status_class = "success" if status == "success" else "fail" if status == "fail" else ""
            status_icon = "✅" if status == "success" else "❌" if status == "fail" else "❔"

            img_path = os.path.join(image_folder, img)
            timestamp = datetime.fromtimestamp(os.path.getmtime(img_path)).strftime("%Y-%m-%d %H:%M:%S")

            f.write(f"<h3 class='{status_class}'>{status_icon} {description}</h3>")
            f.write(f"<p class='timestamp'>🕒 실행 시간: {timestamp}</p>")
            f.write(f"<div class='img-wrapper'><img src='{image_folder}/{img}' alt='{description}'></div><br><br>")

        f.write("</body></html>")


# driver 실행
driver = webdriver.Remote("http://localhost:4723", options=options)
time.sleep(5)

# 실행 권한
driver.find_element("xpath", '//android.view.ViewGroup/android.view.View/android.view.View/android.view.View/android.view.View[2]').click()
time.sleep(3)
driver.find_element("id", 'com.android.permissioncontroller:id/permission_allow_button').click()
time.sleep(5)

intro_popup = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//android.widget.TextView[@text="닫기"]'))
)

intro_popup.click()
save_screenshot(driver, "launch_and_close_intro")


# 로그인 실패
my = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'com.musinsa.store:id/item_my'))
)
my.click()

login = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//android.widget.TextView[@text="로그인/회원가입하기"]'))
)
login.click()

id_input = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//android.widget.EditText[@hint="아이디 입력"]'))
)
id_input.click()
id_input.send_keys("test1234")


password_input = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//android.widget.EditText[@hint="비밀번호 입력"]'))
)
password_input.click()
password_input.send_keys("test125") 

driver.find_element("xpath", '//android.widget.Button[@text="로그인"]').click()
time.sleep(3)
save_screenshot(driver, "login_fail")
driver.find_element("id", 'android:id/button1').click()
time.sleep(3)



# 회원 가입
signup_button = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "회원가입")
signup_button.click()
time.sleep(7)

check = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//android.widget.CheckBox[@resource-id="loginJoinMembershipAllCheckbox"]'))
)
check.click()

agree = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//android.widget.Button[@resource-id="openSelfCertifyPopup"]'))
)
agree.click()
time.sleep(5)

message = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "문자로 본인 인증"))
)
message.click()
time.sleep(5)
save_screenshot(driver, "signup_phone_verification")


driver.back()
time.sleep(5)
driver.back()
time.sleep(5)


# 카카오 로그인 성공
kakao = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "kakao 로고 카카오 로그인"))
)
kakao.click()
time.sleep(5)

close = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "시트 닫기"))
)
close.click()
time.sleep(5)
save_screenshot(driver, "kakao_login_complete")



# 검색/리스트 스크롤
main_home = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "com.musinsa.store:id/item_home"))
)
main_home.click()

time.sleep(5)

search = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[3]"))
)
search.click()

time.sleep(1) # 키보드 열리고 대기 

search_input = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((AppiumBy.CLASS_NAME, "android.widget.EditText"))  
) # 키보드가 열린 UI에서 다시 요소를 찾음(UI 갱신시간 고려 필요)
search_input.click()
search_input.send_keys("반팔")
driver.press_keycode(66)
time.sleep(5)

item = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().descriptionContains("반팔"))'
    ))
)
time.sleep(5)
item.click()
save_screenshot(driver, "search_item_detail")

like_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//android.widget.Button[@text="좋아요 버튼"]'))
)
like_button.click()

back_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, '이전 페이지로 이동'))
)
back_button.click()


# 즐겨찾기 
like = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'com.musinsa.store:id/item_like'))
)
like.click()
time.sleep(3)
save_screenshot(driver, "favorites_view")


# 로그아웃
my = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'com.musinsa.store:id/item_my'))
)
my.click()

def swipe_up(driver, duration=0.2):
    size = driver.get_window_size()
    start_x = size["width"] // 2
    start_y = int(size["height"] * 0.8)
    end_y = int(size["height"] * 0.3)

    finger = PointerInput("touch", "finger")
    actions = ActionBuilder(driver, mouse=finger)

    actions.pointer_action.move_to_location(start_x, start_y)
    actions.pointer_action.pointer_down()
    actions.pointer_action.pause(duration)
    actions.pointer_action.move_to_location(start_x, end_y)
    actions.pointer_action.pointer_up()

    actions.perform()

for _ in range(3):
    swipe_up(driver)
    time.sleep(1)

save_screenshot(driver, "settings_before_logout")

def tap_by_coordinates(driver, x, y):
    finger = PointerInput("touch", "finger")
    actions = ActionBuilder(driver, mouse=finger)

    actions.pointer_action.move_to_location(x, y)
    actions.pointer_action.pointer_down()
    actions.pointer_action.pause(0.1)
    actions.pointer_action.pointer_up()

    actions.perform()

tap_by_coordinates(driver, 800, 2560)

okay_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//android.view.ViewGroup/android.view.View/android.view.View/android.view.View/android.view.View[2]'))
)
okay_button.click()
save_screenshot(driver, "logout_complete")

generate_html_report()

