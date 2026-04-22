# 기프트카드 관리 시스템

바코드 기반 기프트카드 충전·결제·조회 데스크탑 프로그램입니다.

## 시스템 요구사항

- Python 3.10 이상
- macOS / Windows / Linux (데스크탑 환경)

## 설치 방법

```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
python main.py
```

최초 실행 시 `giftcard.db`(SQLite)와 `giftcard.log`가 자동으로 생성됩니다.

## 사용 방법

### 카드 스캔
- 메인 화면 상단 입력창에 바코드를 스캔하거나 직접 입력 후 **Enter**를 누릅니다.
- 미등록 카드라면 **신규 등록 화면**이 자동으로 열립니다.

### 충전
- 카드 스캔 후 **[충전]** 버튼을 눌러 금액을 입력합니다.

### 결제
- 카드 스캔 후 **[결제]** 버튼을 눌러 금액을 입력합니다.
- 잔액 부족 시 오류 메시지가 표시되며 거래가 취소됩니다.

### 거래 내역 보기
- **[내역 보기]** 버튼으로 현재 카드의 거래 내역을 펼치거나 닫습니다.

### 관리자 화면
- **[관리자]** 버튼 → 기간 선택 후 **[조회]** 클릭.
- 총 충전 금액, 총 사용 금액, 전체 잔액 합계, 거래 리스트를 확인할 수 있습니다.

### 회원 조회
- **[회원 조회]** 버튼 → 전화번호 입력 후 **[조회]** 또는 **Enter**.
- 해당 회원의 카드 목록과 각 카드 거래 내역이 표시됩니다.

## 테스트 실행

```bash
pytest tests/ -v
```

## macOS 설치 파일(.app/.dmg) 만들기

PySide6 앱은 단일 바이너리보다 `.app` + `.dmg` 형태 배포가 안정적입니다.

1) 빌드 도구 설치

```bash
pip install pyinstaller
```

2) 설치 파일 생성

```bash
./scripts/build_macos.sh
```

3) 결과물
- 앱 번들: `dist/GiftCardSys.app`
- 설치 파일: `dist/GiftCardSys-installer.dmg`

`img/logo.png`가 있으면 자동으로 아이콘(`.icns`)을 생성해 앱 아이콘으로 사용합니다.

## Windows/macOS/Linux 배포 파일 만들기

하나의 실행파일로 모든 OS를 동시에 지원할 수는 없습니다. 대신 각 OS에서 해당 OS용 실행파일을 빌드해야 합니다.

### 로컬에서 현재 OS용 빌드

```bash
pip install -r requirements.txt pyinstaller
python scripts/build_release.py
```

- macOS: `dist/GiftCardSys.app` (+ 가능하면 `dist/GiftCardSys-installer.dmg`)
- Windows: `dist/release/GiftCardSys-windows.zip`
- Linux: `dist/release/GiftCardSys-linux.tar.gz`

### GitHub Actions로 3개 OS 동시 빌드

`.github/workflows/build-cross-platform.yml`가 추가되어 있으며, 실행 후 아티팩트로 OS별 배포 파일을 다운로드할 수 있습니다.

## 카카오 알림톡 설정 (선택)

카카오 비즈메시지 계정과 템플릿을 준비한 후, 환경 변수를 설정합니다.

```bash
export KAKAO_API_KEY="발급받은 API 키"
export KAKAO_SENDER_KEY="발신 채널 키"
export KAKAO_TEMPLATE_CODE_REGISTER="등록 템플릿 코드"
export KAKAO_TEMPLATE_CODE_CHARGE="충전 템플릿 코드"
export KAKAO_TEMPLATE_CODE_PAYMENT="결제 템플릿 코드"
```

키가 없으면 자동으로 UI 팝업 + 로그 알림만 동작합니다.

## 파일 구조

```
giftcardsys/
├── main.py            # 진입점
├── requirements.txt
├── giftcard.db        # 실행 후 자동 생성
├── giftcard.log       # 실행 후 자동 생성
├── config/            # 설정
├── src/
│   ├── db/            # DB 연결·스키마·쿼리
│   ├── service/       # 비즈니스 로직
│   ├── ui/            # PySide6 화면
│   └── notifications/ # 팝업·로그·카카오 알림
└── tests/             # pytest 단위 테스트
```
