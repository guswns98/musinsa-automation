from datetime import datetime
import os

# 스크린샷 저장
def save_screenshot(driver, name="screenshot", folder="screenshots"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder, f"{name}_{timestamp}.png")

    driver.save_screenshot(filename)