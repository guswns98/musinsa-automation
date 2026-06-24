import sys
import os
import json
import urllib.request
import urllib.parse
import zipfile
import io
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
elif hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import inspect
import time as _time
import time

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from dotenv import load_dotenv
from utils.common_utils import get_app_version, is_app_running
from utils.performance_utils import get_performance_snapshot, save_performance_log

load_dotenv()

_session_start_time = None
_app_version_sent = False

APP_PACKAGE = 'com.musinsa.store'


# ---------------------------------------------------------------------------
# Session hooks
# ---------------------------------------------------------------------------

def pytest_sessionstart(session):
    global _session_start_time
    _session_start_time = _time.time()
    _cleanup_old_reports(hours=6)


def _cleanup_old_reports(hours=6):
    """reports/ 디렉터리에서 N시간 이상 된 리포트 폴더 삭제"""
    import shutil
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    if not os.path.isdir(reports_dir):
        return
    cutoff = _time.time() - hours * 3600
    for entry in os.listdir(reports_dir):
        entry_path = os.path.join(reports_dir, entry)
        if os.path.isdir(entry_path) and entry not in ('assets',):
            if os.path.getmtime(entry_path) < cutoff:
                shutil.rmtree(entry_path, ignore_errors=True)
                print(f"[cleanup] 폴더 삭제: {entry}")


def pytest_configure(config):
    """HTML 리포트 경로로부터 세션 리포트 디렉터리를 결정"""
    from datetime import datetime as _dt
    html_path = getattr(config.option, "htmlpath", None)
    if html_path:
        abs_html = os.path.abspath(html_path)
        parent = os.path.dirname(abs_html)
        parent_name = os.path.basename(parent)
        if parent_name != "reports":
            config._report_dir = parent
        else:
            ts = _dt.now().strftime("%Y%m%d_%H%M%S")
            config._report_dir = os.path.join(parent, ts)
            new_html = os.path.join(config._report_dir, os.path.basename(abs_html))
            config.option.htmlpath = new_html
    else:
        ts = _dt.now().strftime("%Y%m%d_%H%M%S")
        config._report_dir = os.path.abspath(os.path.join("reports", ts))
    os.makedirs(config._report_dir, exist_ok=True)


def pytest_addoption(parser):
    """커맨드 라인 옵션 추가"""
    group = parser.getgroup("slack")

    def add_option_safe(name, **kwargs):
        try:
            group.addoption(name, **kwargs)
        except ValueError:
            pass

    add_option_safe("--slack_webhook", action="store", dest="slack_webhook", default=None, help="Slack Webhook URL")
    add_option_safe("--slack_channel", action="store", dest="slack_channel", default=None, help="Slack Channel")
    add_option_safe("--slack_username", action="store", dest="slack_username", default="Musinsa-Bot", help="Slack Username")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def driver():
    """각 테스트마다 새로운 Appium 세션을 생성합니다."""
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.automation_name = 'UiAutomator2'
    options.device_name = 'R5CT22SD0GJ'
    options.app_package = APP_PACKAGE
    options.app_activity = 'com.musinsa.store.scenes.deeplink.DeepLinkActivity'
    options.language = 'ko'
    options.locale = 'KR'
    options.app_wait_activity = '*'

    options.no_reset = True
    options.clear_system_files = False

    driver_instance = webdriver.Remote('http://localhost:4723', options=options)
    print("--- Appium 드라이버 세션 시작 ---")

    time.sleep(5)

    if not hasattr(pytest, '_version_collected'):
        version = get_app_version(driver_instance)
        pytest.app_version = version
        pytest._version_collected = True
        print(f"앱 버전: {version}")

    yield driver_instance

    print("--- Appium 드라이버 세션 종료 ---")
    try:
        driver_instance.terminate_app(APP_PACKAGE)
        time.sleep(3)
    except Exception:
        pass
    try:
        driver_instance.quit()
    except Exception:
        pass


@pytest.fixture(scope="function", autouse=True)
def performance_monitoring(driver, request):
    """각 테스트 시작/종료 시 앱 성능 스냅샷 수집"""
    before = get_performance_snapshot(driver)
    yield
    try:
        after = get_performance_snapshot(driver)
        report_dir = getattr(request.config, '_report_dir', None)
        result = save_performance_log(request.node.name, before, after, report_dir=report_dir)
        if not hasattr(request.config, '_perf_results'):
            request.config._perf_results = []
        request.config._perf_results.append(result)
    except Exception as e:
        print(f"성능 로그 저장 실패: {e}")


# ---------------------------------------------------------------------------
# Report hooks
# ---------------------------------------------------------------------------

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """테스트 실패 시 스크린샷을 캡처하여 pytest-html 리포트에 추가합니다."""
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])

    if report.when == "call":
        time.sleep(3)

        if "driver" in item.fixturenames:
            driver = item.funcargs["driver"]
            try:
                screenshot_base64 = driver.get_screenshot_as_base64()
                html = (
                    '<div>'
                    '<p>최종 화면 스크린샷:</p>'
                    f'<img src="data:image/png;base64,{screenshot_base64}" alt="screenshot" '
                    'style="width:300px; height:auto; border:1px solid #ccc;" '
                    'onclick="window.open(this.src)" />'
                    '</div>'
                )
                extra.append(pytest_html.extras.html(html))
            except Exception as e:
                print(f"스크린샷 캡처 실패: {e}")

        # Slack 알림 전송 (개별 테스트 결과)
        webhook_url = item.config.getoption("slack_webhook")
        if webhook_url:
            global _app_version_sent
            if not _app_version_sent:
                _app_version_sent = True
                app_ver = getattr(pytest, 'app_version', 'unknown')
                ver_payload = {
                    "text": f"*테스트 시작* | 앱 버전: {app_ver}",
                    "username": item.config.getoption("slack_username"),
                    "channel": item.config.getoption("slack_channel")
                }
                try:
                    ver_req = urllib.request.Request(webhook_url, data=json.dumps(ver_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(ver_req) as ver_resp:
                        print(f"[Slack] 앱 버전 알림 전송: {ver_resp.getcode()}")
                except Exception as e:
                    print(f"[Slack] 앱 버전 알림 전송 실패: {e}")

            status_emoji = "Pass" if report.passed else "Fail"
            status_text = "성공" if report.passed else "실패"
            scenario_name = inspect.getdoc(item.obj) or f"Test: {item.name}"
            message = f"{status_emoji} [{status_text}] {scenario_name}"

            if report.failed and call.excinfo:
                error_msg = str(call.excinfo.value)
                if "; For documentation on this error" in error_msg:
                    error_msg = error_msg.split("; For documentation on this error")[0]
                if not is_app_running():
                    message += f"\n앱 크래시 감지 (프로세스 종료됨)"
                    if not hasattr(item.config, '_crash_detected'):
                        item.config._crash_detected = []
                    item.config._crash_detected.append(item.name)
                message += f"\n실패 원인: {error_msg}"

            payload = {
                "text": message,
                "username": item.config.getoption("slack_username"),
                "channel": item.config.getoption("slack_channel")
            }
            try:
                req = urllib.request.Request(webhook_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req) as response:
                    print(f"[Slack] 개별 알림 전송: {response.getcode()}")
            except Exception as e:
                print(f"[Slack] 알림 전송 실패: {e}")

    report.extras = extra


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """pytest-html이 리포트 쓰기를 완전히 마친 후 Slack으로 결과 전송"""
    global _session_start_time

    try:
        webhook_url = config.getoption("slack_webhook", default=None)
        if not webhook_url:
            return

        elapsed = _time.time() - (_session_start_time or _time.time())
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        passed = len(terminalreporter.stats.get("passed", []))
        failed = len(terminalreporter.stats.get("failed", []))
        total = passed + failed

        channel = config.getoption("slack_channel", default=None)
        if channel and channel.startswith('#'):
            channel = channel[1:]
        username = config.getoption("slack_username", default="Musinsa-Bot")
        bot_token = os.getenv("SLACK_BOT_TOKEN")
        html_path = getattr(config.option, "htmlpath", None)

        # 성능 모니터링 결과 집계
        perf_results = getattr(config, '_perf_results', [])
        perf_summary = ""
        if perf_results:
            mem_values = [r["after"].get("memory_mb") for r in perf_results if r.get("after", {}).get("memory_mb") is not None]
            diffs = [r["diff_memory_mb"] for r in perf_results if r.get("diff_memory_mb") is not None]
            if mem_values:
                max_mem = max(mem_values)
                avg_mem = round(sum(mem_values) / len(mem_values), 1)
                max_diff = max(diffs) if diffs else 0
                max_diff_test = next((r["test"] for r in perf_results if r.get("diff_memory_mb") == max_diff), "")
                diff_str = f"+{max_diff}" if max_diff > 0 else str(max_diff)
                perf_summary = (
                    f"\n*성능 모니터링*\n"
                    f"최대 메모리: {max_mem}MB | 평균: {avg_mem}MB\n"
                    f"메모리 최대 증가: {diff_str}MB ({max_diff_test})"
                )

        # 앱 크래시 감지 결과 집계
        crash_detected = getattr(config, '_crash_detected', [])
        crash_summary = ""
        if crash_detected:
            first_crash = crash_detected[0]
            crash_summary = (
                f"\n*앱 크래시 감지*\n"
                f"최초 발생: {first_crash} (이후 {len(crash_detected)}건 연쇄 실패 포함)"
            )

        app_version = getattr(pytest, 'app_version', 'unknown')
        status_emoji = "Pass" if failed == 0 else "Fail"
        summary = (
            f"{status_emoji} *테스트 전체 완료*\n"
            f"앱 버전: {app_version}\n"
            f"총 {total}개 | Pass {passed} 통과 | Fail {failed} 실패\n"
            f"소요 시간: {minutes}분 {seconds}초"
            f"{crash_summary}"
            f"{perf_summary}"
        )

        if bot_token and html_path and os.path.exists(html_path):
            html_filename = os.path.basename(html_path)
            zip_filename = html_filename.replace('.html', '.zip')
            headers_auth = {'Authorization': f'Bearer {bot_token}'}

            report_dir = getattr(config, '_report_dir', os.path.dirname(os.path.abspath(html_path)))
            assets_dir = os.path.join(report_dir, 'assets')
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(html_path, html_filename)
                if os.path.isdir(assets_dir):
                    for asset_file in os.listdir(assets_dir):
                        asset_path = os.path.join(assets_dir, asset_file)
                        zf.write(asset_path, os.path.join('assets', asset_file))
                for json_file in os.listdir(report_dir):
                    if json_file.startswith('perf_log_') and json_file.endswith('.json'):
                        json_path = os.path.join(report_dir, json_file)
                        zf.write(json_path, os.path.join('perf_logs', json_file))
            file_content = zip_buffer.getvalue()

            try:
                msg_body = json.dumps({'channel': channel, 'text': summary}).encode('utf-8')
                req0 = urllib.request.Request(
                    'https://slack.com/api/chat.postMessage',
                    data=msg_body,
                    headers={**headers_auth, 'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req0) as r0:
                    res0 = json.loads(r0.read().decode('utf-8'))
                if not res0.get('ok'):
                    raise Exception(f"chat.postMessage 실패: {res0.get('error')}")

                params = urllib.parse.urlencode({'filename': zip_filename, 'length': len(file_content)}).encode('utf-8')
                req1 = urllib.request.Request(
                    'https://slack.com/api/files.getUploadURLExternal',
                    data=params,
                    headers={**headers_auth, 'Content-Type': 'application/x-www-form-urlencoded'}
                )
                with urllib.request.urlopen(req1) as r1:
                    res1 = json.loads(r1.read().decode('utf-8'))
                if not res1.get('ok'):
                    raise Exception(res1.get('error'))

                upload_url = res1['upload_url']
                file_id = res1['file_id']

                req2 = urllib.request.Request(upload_url, data=file_content, headers={'Content-Type': 'application/zip'})
                req2.method = 'POST'
                with urllib.request.urlopen(req2):
                    pass

                body3 = json.dumps({
                    'files': [{'id': file_id}],
                    'channel_id': channel,
                    'initial_comment': f'{zip_filename} (압축 해제 후 브라우저로 열어주세요)'
                }).encode('utf-8')
                req3 = urllib.request.Request(
                    'https://slack.com/api/files.completeUploadExternal',
                    data=body3,
                    headers={**headers_auth, 'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req3):
                    pass
            except Exception as e:
                print(f"[Slack] 오류: {e}")
        else:
            payload = {"text": summary, "username": username, "channel": channel}
            try:
                req = urllib.request.Request(
                    webhook_url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req):
                    pass
            except Exception as e:
                print(f"[Slack] 최종 요약 전송 실패: {e}")

    except Exception as e:
        print(f"[Slack] pytest_terminal_summary 오류: {e}")
