from applitools.selenium import Eyes, Target
import os
from dotenv import load_dotenv

load_dotenv

# Eyes 객체는 외부에서도 쓸 수 있도록 전역 유지
eyes = Eyes()
eyes.api_key = os.getenv('API_KEY')

def eyes_open(driver, app_name="Musinsa App", test_name="Default Test"):
    eyes.open(driver, app_name, test_name)

def eyes_check(name, driver):
    eyes.check(name, Target.window())

def eyes_close():
    eyes.close()

def eyes_abort_if_not_closed():
    eyes.abort_if_not_closed()

def get_eyes():  # 필요하면 외부에서 eyes 객체 직접 접근
    return eyes