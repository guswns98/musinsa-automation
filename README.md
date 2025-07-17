# Appium 기반 Android APP 자동화

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

## TEST 시나리오
    - 실행 권한
        - 권한 허용 후 Main Activity 진입 확인 > 인트로 광고 팝업 닫기
    - 로그인 실패
        - 잘못된 아이디 비밀번호 입력 > 로그인 실패 팝업 확인
    - 회원 가입
        - 회원 가입 선택 후 > 이메일 비밀번호 입력  > 약관 동의 체크  > 본인인증 화면
    - 로그인 성공
        - KAKAO 로그인(사전 조건: KAKAO와 계정 연동) > 마이정보 아이디 노출 > 로그인 성공 시트 닫기
    - 검색 / 리스트 스크롤
        - 검색 선택 > “특정 단어” 검색어 입력 > “특정 단어” 포함된 아이템 나올 때 까지 스크롤 후 선택
    - 즐겨찾기
        - 아이템 선택 후 즐겨찾기 > 즐겨찾기 항목 확인
    - 로그아웃
        - 화면 하단 스크롤 > 로그아웃 후 회원 정보 확인


[데모 영상 보기](https://www.youtube.com/shorts/B9G32050-IM)