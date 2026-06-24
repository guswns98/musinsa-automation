import os
import json
import subprocess
import urllib.request
from datetime import datetime

APP_PACKAGE = "com.musinsa.store"


def get_app_version(driver=None, package=APP_PACKAGE):
    """ADB를 통해 앱 버전 정보(versionName)를 가져옵니다."""
    try:
        result = subprocess.run(
            ['adb', 'shell', 'dumpsys', 'package', package],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.split('\n'):
            line = line.strip()
            if 'versionName=' in line:
                version = line.split('versionName=')[1].strip()
                if version:
                    return version
    except Exception as e:
        print(f"앱 버전 조회 실패 (adb subprocess): {e}")

    if driver:
        try:
            result = driver.execute_script('mobile: shell', {
                'command': 'dumpsys',
                'args': ['package', package]
            })
            for line in result.split('\n'):
                line = line.strip()
                if 'versionName=' in line:
                    version = line.split('versionName=')[1].strip()
                    if version:
                        return version
        except Exception as e:
            print(f"앱 버전 조회 실패 (mobile: shell): {e}")

    return "unknown"


def is_app_running(package=APP_PACKAGE):
    """ADB로 앱 프로세스가 살아있는지 확인. 죽었으면 False (OOM/크래시 가능성)"""
    try:
        result = subprocess.run(
            ['adb', 'shell', 'pidof', package],
            capture_output=True, text=True, timeout=5
        )
        return bool(result.stdout.strip())
    except Exception:
        return True


def take_screenshot(driver, test_name, report_dir=None):
    """스크린샷을 찍고 파일로 저장합니다."""
    save_dir = os.path.join(report_dir or "reports", "assets")
    os.makedirs(save_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(save_dir, f"{test_name}_{timestamp}.png")

    try:
        driver.save_screenshot(screenshot_path)
        print(f"스크린샷 저장: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"스크린샷 캡처 실패: {e}")
        return None


def send_slack_message(webhook_url, text, username="Musinsa-Bot", channel=None):
    """Slack으로 메시지를 발송합니다."""
    if not webhook_url:
        return
    payload = {"text": text, "username": username}
    if channel:
        payload["channel"] = channel
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            print(f"[Slack] 메시지 전송 완료: {response.getcode()}")
    except Exception as e:
        print(f"[Slack] 메시지 전송 실패: {e}")
