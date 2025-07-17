# Appium 기반 Android 앱 자동화

Python과 Appium을 사용하여 musinsa APP 주요 기능들을 자동화한 QA 테스트 스크립트입니다. 테스트 실행 중 각 단계를 스크린샷으로 저장하고, 실행 후 결과를 HTML 리포트로 제공합니다.


## 사용 기술
- Python 3.13
- Appium 2.x
- Appium Inspector
- Android Studio (sdk)
- Real Device (USB 디버깅)

## 프로젝트 구조
- project/
- ├── screenshots/ # 자동화 저장 스크린샷
- ├── musinsa.py # 테스트 스크립트
- ├── report.html # HTML 테스트 결과 리포트
- └── README.md # 설명 파일