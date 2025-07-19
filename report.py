import os

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

