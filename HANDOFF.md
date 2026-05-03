# HANDOFF.md

이 파일은 작업 완료 후 누적 기록되는 인수인계 문서입니다.

---

## [2026-04-21] UI 전면 재작성 (img 와이어프레임 기반)

### 작업 내용
`img/` 폴더의 7개 화면 와이어프레임을 분석하고 전체 UI를 재설계했다.

**확정된 화면 흐름:**
- 메인 → 바코드 스캔 → (등록됨) 이미 등록된 회원 화면 / (미등록) 신규등록 화면
- 메인 → [등록버튼] → 신규등록 화면
- 메인 → [회원버튼] → 회원 정보 화면(리스트)
- 이미 등록된 회원 → [충전/결제] → 충전/결제 화면 (다이얼 패드)
- 이미 등록된 회원 → [회원정보버튼] → 회원 정보 화면(리스트)
- 회원 정보 화면 → 항목 더블클릭 → 회원정보 수정 화면

**변경 내용:**
- 메인 페이지: 기간별/회원코드별/전화번호별 필터 + 사용내역 리스트 + 하단 [회원버튼] [등록버튼]
- 충전/결제 화면: QSpinBox → QLineEdit + 숫자 다이얼(0~9, 00, C) + 키보드 동시 지원
- 신규등록 화면: 바코드 필드 추가, 메인 [등록버튼]으로도 직접 열 수 있게 수정

### 변경된 파일
- `src/ui/main_window.py` — 전면 재작성 (거래내역 리스트 + 필터 + 바코드입력 + 하단버튼)
- `src/ui/card_info_window.py` — 신규 생성 (이미 등록된 회원 화면)
- `src/ui/card_register_dialog.py` — 바코드 필드 추가, 단독 열기 지원
- `src/ui/transaction_dialog.py` — QSpinBox 제거, 다이얼 패드 추가
- `src/ui/member_search.py` — QTreeWidget → QTableWidget, 더블클릭 수정 화면 연결
- `src/ui/member_edit_dialog.py` — 신규 생성 (회원정보 수정 화면)
- `src/ui/messages.py` — 새 화면 문자열 추가
- `src/db/queries.py` — `fetch_transactions_filtered`, `update_user_phone`, `search_users` 추가
- `src/service/card_service.py` — `update_user_phone`, `search_users`, `get_transactions_filtered` 추가

### 다음 작업 시 참고사항
- `admin_panel.py`는 현재 메인 페이지에 흡수됐으나 파일은 잔존. 필요 없으면 삭제 가능
- 신규등록 화면에서 [등록버튼]으로 열 때는 바코드를 직접 입력해야 함 (바코드 스캔으로 열 때는 자동 입력됨)
- 다이얼 패드 C 버튼 = 전체 지우기 (백스페이스 기능은 없음). 필요시 추가 가능

---

## [2026-04-21] 기프트카드 관리 시스템 전체 구현

### 작업 내용
- `prompt1.md` 스펙 기반으로 PySide6 데스크탑 기프트카드 관리 시스템 전체 구현
- DB 계층, 서비스 계층, UI 계층, 알림 계층 모두 신규 작성
- 단위 테스트 19개 (전부 통과)
- 서비스 계층 핵심 불변식 확인: `cards.balance == transactions.balance_after` (원자적 트랜잭션 보장)

### 변경된 파일 (모두 신규 생성)
- `main.py` — 진입점, DB 초기화, 알림 객체 구성
- `requirements.txt`
- `README.md` — 한국어 실행 가이드
- `config/settings.py` — DB 경로, 로그 경로, 카카오 API 환경 변수
- `src/exceptions.py` — 6가지 커스텀 예외 클래스
- `src/db/connection.py` — SQLite 컨텍스트 매니저 (foreign_keys ON, row_factory)
- `src/db/schema.py` — CREATE TABLE + 인덱스 + `init_db()`
- `src/db/queries.py` — 전체 SQL 집중 관리 (정렬: `created_at DESC, id DESC`)
- `src/service/card_service.py` — 바코드 조회, 신규 등록, 전화번호 기반 조회
- `src/service/transaction_service.py` — 충전/결제 (원자적 트랜잭션)
- `src/service/admin_service.py` — 기간별 통계
- `src/ui/messages.py` — 한국어 문자열 상수 모음
- `src/ui/main_window.py` — POS 메인 화면 (바코드 → Enter 자동 제출)
- `src/ui/card_register_dialog.py` — 신규 카드 등록 다이얼로그
- `src/ui/transaction_dialog.py` — 충전/결제 공용 다이얼로그
- `src/ui/admin_panel.py` — 관리자 통계 + 거래 리스트
- `src/ui/member_search.py` — 전화번호 기반 회원 조회
- `src/notifications/base.py` — Notifier ABC
- `src/notifications/popup.py` — QMessageBox 팝업 알림
- `src/notifications/logger.py` — 파일 로그 알림
- `src/notifications/kakao.py` — 카카오 알림톡 API (키 없으면 no-op)
- `tests/conftest.py`, `tests/test_card_service.py`, `tests/test_transaction_service.py`, `tests/test_admin_service.py`

### 다음 작업 시 참고사항
- **카카오 알림톡 활성화**: 카카오 비즈메시지 가입 후 환경 변수 4개 설정 (`KAKAO_API_KEY`, `KAKAO_SENDER_KEY`, `KAKAO_TEMPLATE_CODE_*`)
- **알림 팝업 동작**: 충전/결제 완료 후 `PopupNotifier`가 QMessageBox로 결과를 띄움. 매 거래마다 팝업이 불편하면 `main.py`에서 `PopupNotifier` 제거하고 로그만 유지 가능
- **바코드 형식**: 현재 숫자 전용으로 검증 (`isdigit()`). 영문 포함 바코드가 필요하면 `card_service._validate_barcode()` 수정 필요
- **잔액 단위**: 정수 원화(KRW). 소수점 지원 필요 시 `INTEGER` → `REAL`로 스키마 변경 필요 (마이그레이션 고려)
- **앱 패키징**: 배포용 실행 파일이 필요하면 `PyInstaller` 또는 `briefcase` 사용 권장

---

## [2026-04-21] CLAUDE.md 초기 작성 및 협업 규칙 수립

### 작업 내용
- `prompt1.md` 요구사항 분석 후 `CLAUDE.md` 초안 작성
- 프로젝트 아키텍처, DB 스키마, 핵심 비즈니스 로직, 예외 처리 요구사항 문서화
- 협업 규칙 3가지 추가 및 사용자 인터뷰를 통해 세부 내용 확정:
  - 모든 응답/출력 한국어, 코드 주석은 영어 유지
  - HANDOFF.md 누적 추가 방식 채택
  - 인터뷰는 모호하거나 사용자 결정이 필요한 경우에만 진행

### 변경된 파일
- `CLAUDE.md` — 신규 생성
- `HANDOFF.md` — 신규 생성 (이 파일)

### 다음 작업 시 참고사항
- 프로젝트 코드가 아직 없음. `prompt1.md` 스펙 기준으로 개발 시작 필요
- 첫 작업은 프로젝트 폴더 구조 생성 + `requirements.txt` + DB 초기화 코드(`src/db/schema.py`) 순서 권장

## [2026-04-21] Supanova Design Skill 기반 UI/UX 전면 개선

### 작업 내용
GitHub의 `uxjoseph/supanova-design-skill`에서 설계 원칙을 추출하여 PySide6 데스크톱 앱에 적용했다.
해당 스킬은 원래 HTML 랜딩페이지용이나, 핵심 디자인 철학(다크 퍼스트, 단일 액센트, 깊이감 있는 카드, 명확한 버튼 계층)을 Qt 스타일시트로 변환했다.

**적용된 디자인 원칙:**
- **다크 모드**: zinc-950(`#09090b`) 기반, 모든 배경에 일관 적용
- **단일 액센트**: 에메랄드(`#10b981`) — Primary/충전완료 등
- **버튼 역할 계층**: `role=primary`(에메랄드), `role=charge`(앰버), `role=pay`(에메랄드 아웃라인), `role=danger`(레드 아웃라인), `role=numpad`
- **카드 깊이감**: GroupBox/Frame에 zinc-900 배경 + zinc-800 테두리 + 10px border-radius
- **잔액 카드**: 에메랄드 액센트 보더로 시각적 강조
- **통계 카드**: 충전(앰버)/결제(에메랄드)/잔액(스카이) 각각 색상 구분
- **테이블**: showGrid=False, 수직헤더 숨김, 선택 시 emerald-dim 배경
- **메인 헤더바**: 앱 이름 + 날짜 표시 상단 고정 bar
- **거래 유형 색상**: 충전=초록, 결제=노랑으로 한눈에 구분

### 변경된 파일
- `src/ui/theme.py` — **신규 생성** — 전체 Qt 스타일시트 + 컬러 팔레트 상수
- `main.py` — `apply_theme(app)` 호출 추가
- `src/ui/main_window.py` — 헤더 바, 그룹박스 구조, 버튼 role 적용
- `src/ui/transaction_dialog.py` — 배지, 잔액 카드, numpad role, 컬러 구분
- `src/ui/card_info_window.py` — 정보 카드 3개, 잔액 accent 카드, 버튼 role
- `src/ui/card_register_dialog.py` — 서브타이틀, 버튼 role
- `src/ui/admin_panel.py` — 3개 통계 카드 (충전/결제/잔액 색상 구분)
- `src/ui/member_search.py` — 타이틀, 버튼 role, hint 색상
- `src/ui/member_edit_dialog.py` — 타이틀, 버튼 role

### 다음 작업 시 참고사항
- `theme.py`의 색상 상수(ACCENT, WARNING, DANGER 등)를 수정하면 전체 앱 색상이 일괄 변경된다.
- `QPushButton`에 `setProperty("role", "primary")` 등으로 역할 지정 → 스타일시트 자동 적용.
- 한국어 폰트는 macOS에서 "Apple SD Gothic Neo", Windows에서 "Malgun Gothic" 폴백.
- Supanova 스킬 원본은 HTML/Tailwind CDN 기반이므로, Qt에 직접 적용 불가한 요소(Pretendard CDN, 애니메이션 등)는 생략했다.

## [2026-04-21] UI 색상 라이트 모드로 전환 + 직관성 개선

### 작업 내용
다크 모드(zinc-950 기반) → 라이트 모드(slate-50/white 기반)로 전면 전환.
색상 역할을 더 직관적으로 재정의했다.

**색상 역할 정리:**
| 역할 | 색상 | 사용처 |
|------|------|--------|
| Primary (파랑 `#2563eb`) | 조회, 확인, 스캔 버튼 |
| Charge (앰버 `#f59e0b`) | 충전 버튼, 충전 통계 카드 |
| Pay (에메랄드 `#10b981`) | 결제 버튼, 잔액 카드, 결제 통계 |
| Danger (빨강 `#ef4444`) | 취소, 삭제 버튼 |
| Info (스카이 `#0ea5e9`) | 현재 잔액 표시, 통계 |
| 배경 | slate-50(`#f1f5f9`) + 흰 카드(`#ffffff`) |

**주요 변경:**
- 헤더바 색상: Primary 파랑 배경, 흰 텍스트
- 잔액 카드: sky-50 배경 + sky 테두리
- 통계 카드: 각 역할별 light 배경 (amber-50 / emerald-50 / sky-50)
- 테이블 선택: Primary light blue
- 수자패드: 호버 시 blue-light, Clear 버튼은 red-light
- 테이블 거래유형 색상: 충전=amber-dark, 결제=emerald-dark (라이트에서 잘 보이도록)

### 변경된 파일
- `src/ui/theme.py` — 팔레트 전면 교체 (라이트 모드)
- `src/ui/main_window.py` — 헤더 색상, 테이블 거래유형 색상
- `src/ui/transaction_dialog.py` — 잔액 카드 sky 계열
- `src/ui/card_info_window.py` — 잔액 카드 emerald 계열, 거래유형 색상
- `src/ui/admin_panel.py` — 통계 카드 각 역할별 light 배경, 거래유형 색상

### 다음 작업 시 참고사항
- 라이트 모드에서 테이블 텍스트는 `QColor(theme.WARNING_DARK)` / `QColor(theme.ACCENT_DARK)` 사용 (밝은 배경에서 가시성).
- `_make_stat_card()`에 `light_map` / `border_map` 딕셔너리로 accent → light bg 자동 매핑.

## [2026-04-21] 전체 UI/UX 리디자인 (Flux Dashboard 스타일)

### 작업 내용
사용자가 제공한 Flux 트레이딩 대시보드 이미지를 참고하여 전체 UI/UX를 현대적인 대시보드 스타일로 전면 리디자인.

**주요 변경 사항:**
- **다크 네이비 헤더바** (`#0f172a`) — 모든 화면에 일관 적용
- **카드 레이아웃** — QGroupBox → QFrame + 드롭 섀도우(`QGraphicsDropShadowEffect`)로 교체
- **인디고 기본 색상** (`#4f46e5`) — 기존 블루에서 변경
- **뱃지 pill 스타일** — 거래 내역 "구분" 컬럼을 `setCellWidget` 기반 초록/빨강 뱃지로 렌더링
- **잔액 히어로 카드** — `card_info_window`에 인디고-퍼플 그라디언트 대형 잔액 표시 카드 추가
- **통계 카드** — `admin_panel` 통계 카드 아이콘/색상 리뉴얼
- **거래 건수 뱃지** — 메인 화면 테이블 헤더에 "N건" 뱃지 추가
- **관리자 버튼** — 메인 화면 헤더 우측에 관리자 버튼 통합

### 변경된 파일
- `src/ui/theme.py` — 디자인 토큰 전면 개편, `card_shadow()` · `make_badge()` 헬퍼 추가
- `src/ui/main_window.py` — 레이아웃 재구성, 관리자 버튼 헤더 통합, 뱃지 셀
- `src/ui/card_info_window.py` — 히어로 잔액 카드, 그라디언트 액션 버튼
- `src/ui/transaction_dialog.py` — 다크 헤더, 인디고 잔액 카드, 패드 반경 개선
- `src/ui/card_register_dialog.py` — 다크 헤더, 카드형 폼
- `src/ui/member_search.py` — 다크 헤더, 카드형 테이블
- `src/ui/admin_panel.py` — 다크 헤더, 통계 카드 리뉴얼, 뱃지 셀
- `src/ui/member_edit_dialog.py` — 다크 헤더, 카드형 폼

### 다음 작업 시 참고사항
- `QGraphicsDropShadowEffect`는 위젯당 하나만 설정 가능 (두 번 호출 시 이전 것이 대체됨)
- 뱃지 셀(`setCellWidget`)이 있는 열은 `QTableWidgetItem.setForeground` 대신 QLabel 스타일로 색상 제어
- 기존 `BTN_HISTORY`, `BTN_ADMIN` 상수는 messages.py에 이미 있으므로 유지

## [2026-04-21] 전체 UI 리디자인 — Craftwork 스타일

### 작업 내용
사용자가 제공한 Craftwork 디자인 마켓플레이스 스크린샷을 참고하여 전체 UI를 재설계함.

**주요 변경사항:**
- **배경색**: 다크 네이비 헤더 제거 → 밝은 회색(`#ebebeb`) 단일 배경
- **포인트 컬러**: 인디고/블루 그라디언트 → **라임 옐로우-그린(`#c5e12b`)** 단색 플랫 버튼
- **버튼 스타일**: 모든 그라디언트 제거 → 플랫 솔리드 컬러, 테두리형 기본 버튼
- **카드 스타일**: 흰색 카드 + 얇은 테두리(`border: 1.5px solid`) + 미묘한 그림자
- **타이포그래피**: 헤딩 `font-weight: 800` 강화, 섹션 레이블 letter-spacing 추가
- **메인 윈도우**: 다크 헤더바 → 라이트 헤더 카드로 교체, 스캔/필터 영역 분리
- **카드 정보 창**: 잔액 카드 배경을 다크(`#0a0a0a`)로 변경하고 라임 장식 추가
- **숫자패드**: 직사각형 라운드(`border-radius: 14px`)로 변경
- **취소 버튼**: danger role 제거 → 기본 테두리 스타일로 변경

### 변경된 파일
- `src/ui/theme.py` — 전면 재설계
- `src/ui/main_window.py` — 헤더 통합, 스캔/필터 분리
- `src/ui/card_info_window.py` — 다크 잔액 카드, 라이트 헤더
- `src/ui/admin_panel.py` — 라이트 헤더, 통계 카드 스타일
- `src/ui/transaction_dialog.py` — 다크 잔액 카드, 플랫 버튼
- `src/ui/card_register_dialog.py` — 다크 헤더 카드(다양성)
- `src/ui/member_search.py` — 라이트 헤더 카드

### 다음 작업 시 참고사항
- `PRIMARY_BTN = "#c5e12b"` 이 라임 포인트 컬러. 조정이 필요하면 theme.py 한 곳만 수정
- 다크 잔액 카드(`BRIGHT = "#0a0a0a"`)는 card_info_window와 transaction_dialog에 사용
- 취소 버튼에서 `role="danger"` 제거 — 기본 테두리 스타일 사용

## [2026-04-21] macOS 배포용 설치 파일 빌드 세팅

### 작업 내용
- `PyInstaller` 기반으로 macOS 배포 파이프라인을 추가해 `.app` 및 `.dmg` 생성 흐름을 자동화했다.
- 빌드 스크립트에서 아이콘(`img/logo.png`)이 작거나 변환 실패 시 기본 아이콘으로 자동 폴백하도록 처리했다.
- 샌드박스/권한 이슈를 피하기 위해 `PYINSTALLER_CONFIG_DIR`를 프로젝트 내부 경로로 고정했다.
- 스크립트 실행 검증 결과 `dist/GiftCardSys.app`는 정상 생성되었고, 현재 실행 환경에서는 `hdiutil` 제한으로 `.dmg` 생성은 실패할 수 있도록 안전 처리했다.

### 변경된 파일
- `giftcardsys.spec` — 앱 번들 빌드 설정 추가 (`main.py` 엔트리, `img` 데이터 포함)
- `scripts/build_macos.sh` — macOS 빌드 자동화 스크립트 신규 추가 (`.app`/`.dmg`)
- `README.md` — macOS 설치 파일 생성 가이드 추가

### 다음 작업 시 참고사항
- 로컬 터미널에서 `PATH="$PWD/.venv/bin:$PATH" ./scripts/build_macos.sh` 실행 시 `.app` 생성 가능
- `.dmg`는 환경에 따라 `hdiutil` 제한이 있을 수 있으며, 일반 로컬 macOS 터미널에서는 정상 생성 가능
- `img/logo.png` 해상도가 낮으면 `.icns` 변환이 실패할 수 있음 (1024x1024 정사각 PNG 권장)

## [2026-04-21] 크로스 플랫폼(OS별) 배포 자동화 추가

### 작업 내용
- 단일 실행파일로 모든 OS를 공통 지원하는 방식은 불가능하므로, OS별 네이티브 빌드 파이프라인을 추가했다.
- `scripts/build_release.py`를 새로 만들어 현재 OS 기준으로 PyInstaller 빌드 후 배포 패키징까지 자동 수행하게 구성했다.
  - macOS: `.app` + 가능 시 `.dmg`
  - Windows: 실행 폴더를 `.zip`으로 패키징
  - Linux: 실행 폴더를 `.tar.gz`로 패키징
- GitHub Actions 워크플로를 추가해 Ubuntu/macOS/Windows에서 동시 빌드 후 아티팩트 업로드가 가능하도록 설정했다.
- README에 크로스 플랫폼 빌드 사용법과 제약사항(단일 파일 전 OS 공통 불가)을 명시했다.

### 변경된 파일
- `scripts/build_release.py` — 신규 생성 (OS별 공통 빌드/패키징 스크립트)
- `.github/workflows/build-cross-platform.yml` — 신규 생성 (3개 OS CI 빌드)
- `README.md` — 크로스 플랫폼 배포 가이드 추가

### 다음 작업 시 참고사항
- Windows용 `.exe`는 Windows 환경에서 빌드해야 하고, Linux용 ELF는 Linux 환경에서 빌드해야 한다.
- macOS에서 `hdiutil`이 제한되는 환경에서는 `.dmg` 없이 `.app`만 생성될 수 있다.
- 배포 파일 명칭은 `GiftCardSys-*` 규칙으로 통일되어 아티팩트 식별이 쉽다.

## [2026-04-21] GitHub 업로드 준비 및 저장소 초기화

### 작업 내용
- 로컬 프로젝트를 Git 저장소로 초기화하고 기본 브랜치를 `main`으로 설정했다.
- 배포/로컬 실행 산출물이 커밋되지 않도록 `.gitignore`를 추가했다.
- 제외 대상에는 가상환경, 빌드 산출물, PyInstaller 캐시, 로컬 SQLite DB/로그를 포함했다.

### 변경된 파일
- `.gitignore` — 신규 생성

### 다음 작업 시 참고사항
- 원격 저장소 푸시는 사용자 GitHub 인증 상태(SSH 키 또는 토큰)에 따라 성공/실패가 갈릴 수 있다.
- 현재 설정으로 소스 코드 중심 커밋이 가능하며 로컬 환경 파일은 자동 제외된다.

## [2026-04-21] 회원정보 화면 충전/결제 버튼 잘림 수정

### 작업 내용
- 회원 검색(회원정보) 테이블의 액션 컬럼 폭이 좁아 충전/결제 버튼이 일부 환경에서 잘리는 문제를 수정했다.
- 액션 컬럼 고정 너비를 `110`에서 `132`로 확대했다.
- 셀 위젯 좌우 여백을 축소하고 버튼 폭을 소폭 확장해 아이콘/버튼 표시 안정성을 높였다.

### 변경된 파일
- `src/ui/member_search.py` — 액션 컬럼 폭 및 버튼 셀 레이아웃 조정

### 다음 작업 시 참고사항
- 고해상도/배율 환경에서도 액션 컬럼은 130px 이상 유지하는 것을 권장한다.

---

## [2026-04-22] Windows EXE 빌드 설정 (PyInstaller + 아이콘)

### 작업 내용
- `img/logo1.png`를 아이콘으로 사용하는 Windows EXE 빌드 파이프라인을 정비했다.
- PyInstaller는 Windows 아이콘으로 `.ico` 형식이 필요하므로 빌드 시 Pillow로 자동 변환한다.
- `build_release.py`가 플랫폼 감지 후 PNG → ICO/PNG 변환 및 `--icon` 옵션을 자동 처리한다.

### 변경된 파일
- `requirements.txt` — Pillow>=10.0.0 추가 (PNG→ICO 변환)
- `scripts/build_release.py` — 아이콘 변환 로직, `--icon` 옵션, `config` 디렉토리 번들, PySide6 hidden imports 추가
- `giftcardsys.spec` — Windows 기준으로 재작성 (아이콘, hidden imports, config 포함)
- `.github/workflows/build-cross-platform.yml` — Pillow 설치 추가
- `build_windows.bat` — Windows 사용자용 원클릭 빌드 스크립트 신규 생성

### 다음 작업 시 참고사항
- PyInstaller는 크로스 컴파일 불가 — `.exe`는 반드시 Windows 환경에서 빌드해야 한다.
- GitHub Actions 워크플로(`build-cross-platform.yml`)를 트리거하면 자동으로 Windows EXE ZIP이 아티팩트로 생성된다.
- Windows에서 직접 빌드하려면 `build_windows.bat`을 더블클릭하면 된다.
- `img/logo1.ico`는 빌드 시 자동 생성되므로 직접 만들 필요 없다.
- `.spec` 파일을 직접 사용할 경우 먼저 `python scripts/build_release.py`로 `logo1.ico`를 생성해야 한다.

---

## [2026-04-22] DB 백업 기능 추가

### 작업 내용
- 관리자 화면 헤더에 "DB 백업" 버튼 추가.
- 버튼 클릭 시 `giftcard.db`를 `backups/giftcard_YYYYMMDD_HHMMSS.db` 형태로 복사.
- 성공/실패 여부를 팝업 다이얼로그로 표시.

### 변경된 파일
- `config/settings.py` — `BACKUP_DIR` 설정 추가 (기본값: `backups/`)
- `src/service/backup_service.py` — 신규 생성 (`create_backup`, `list_backups`)
- `src/ui/messages.py` — 백업 관련 문자열 상수 추가
- `src/ui/admin_panel.py` — "DB 백업" 버튼 및 `_on_backup` 핸들러 추가

### 다음 작업 시 참고사항
- 백업 파일은 EXE 실행 위치 기준 `backups/` 폴더에 생성된다.
- `GIFTCARD_BACKUP_DIR` 환경변수로 경로 변경 가능.
- 백업 후 `build_windows.bat` 재실행하면 새 EXE에 기능이 포함된다.

---

## [2026-04-22] Windows 빌드 스크립트 인코딩 오류 및 pyinstaller PATH 문제 수정

### 작업 내용
- `build_windows.bat` 실행 시 한국어 UTF-8 문자가 CMD에서 잘못 파싱되어 `pip install`이 `l` + `stall` 등으로 쪼개지는 문제 수정.
- `scripts/build_release.py`에서 `subprocess.run(["pyinstaller", ...])` 호출이 `[WinError 2]`로 실패하는 문제 수정.

### 변경된 파일
- `build_windows.bat` — echo 메시지의 한국어 제거, ASCII 텍스트로 대체
- `scripts/build_release.py` — `"pyinstaller"` → `sys.executable, "-m", "PyInstaller"` 로 교체

### 다음 작업 시 참고사항
- Windows 배치 파일에 한국어(EUC-KR/UTF-8 혼용)를 echo로 출력하면 CMD 파서가 오작동할 수 있으므로 ASCII 텍스트 유지를 권장한다.
- `sys.executable -m PyInstaller` 방식은 가상환경 활성화 여부와 무관하게 동작한다.

---

## [2026-04-22] 최소화 숨기기 + 복귀 버튼 기능 구현 (prompt2.md)

### 작업 내용
- POS 환경에서 메인 윈도우를 최소화하면 완전히 숨기고(작업표시줄에서도 제거),
  화면 우측 하단에 항상 위에 떠 있는 "복귀" 버튼을 표시하는 기능을 구현했다.
- Ctrl+Alt+A 전역 단축키로 어떤 프로그램 사용 중에도 메인 창으로 즉시 복귀 가능.

**동작 흐름:**
1. 최소화 버튼 클릭 → `changeEvent`에서 감지 → `hide()` + `FloatingReturnButton.show()`
2. 복귀 버튼 클릭 또는 Ctrl+Alt+A → `restore_window()` → 버튼 숨김 + 메인 창 복원
3. X 버튼(종료) → `closeEvent` → 복귀 버튼도 함께 닫힘

**Tkinter 요구 → PySide6 구현 대응:**
| Tkinter | PySide6 |
|---------|---------|
| `withdraw()` | `hide()` |
| `deiconify()` | `show()` + `activateWindow()` |
| `topmost=True` | `WindowStaysOnTopHint \| Tool` |

### 변경된 파일
- `src/ui/return_button.py` — **신규 생성** (`FloatingReturnButton`: 항상 위 복귀 버튼 창)
- `src/ui/main_window.py` — `changeEvent`, `restore_window`(`@Slot`), `closeEvent` 추가
- `main.py` — `_setup_global_hotkey()` 추가 (`keyboard` 라이브러리 사용)
- `requirements.txt` — `keyboard>=0.13.5` 추가

### 다음 작업 시 참고사항
- `keyboard` 라이브러리는 Windows에서 **관리자 권한** 없이도 동작하나, 일부 보안 환경에서는 권한이 필요할 수 있다. 실패 시 예외를 무시하므로 앱 실행에는 영향 없음.
- `FloatingReturnButton`은 인스턴스를 재사용(`hide`/`show`)하며 최소화할 때마다 새로 생성하지 않아 중복 방지가 보장된다.
- 복귀 버튼의 위치 또는 크기 변경은 `src/ui/return_button.py`의 `setFixedSize`와 `_reposition()` 메서드만 수정하면 된다.

---

## [2026-04-22] 32비트 호환을 위한 Qt 프레임워크 전환 (PySide6 -> PyQt5)
### 작업 내용
- Windows에서 발생한 `shiboken6` DLL 로드 오류(`올바른 Win32 응용 프로그램이 아닙니다`)를 해소하기 위해 Qt 바인딩을 `PySide6`에서 `PyQt5`로 전환했다.
- 전체 UI 코드의 import를 `PyQt5`로 교체하고, Qt6 전용 enum/메서드 문법을 PyQt5 호환 문법으로 수정했다.
- 주요 호환 수정: `exec()` -> `exec_()`, `Qt.AlignmentFlag.*` -> `Qt.Align*`, `Qt.WindowType.*` -> `Qt.*`, `QDialogButtonBox.StandardButton.*` -> `QDialogButtonBox.*`.
- 패키징 설정도 함께 갱신해 빌드 시 hidden import가 `PyQt5.*`를 참조하도록 변경했다.
- 로컬 환경에서 `PySide6/shiboken6` 계열 패키지 제거 후 `PyQt5` 설치까지 완료했다.

### 변경된 파일
- `requirements.txt` — `PySide6` 제거, `PyQt5` 추가
- `main.py` — `PyQt5` import 전환, 이벤트 루프/핫키 invoke 방식 호환 수정
- `src/ui/theme.py` — `PyQt5` import 및 헤더 설명 갱신
- `src/ui/transaction_dialog.py` — `PyQt5` import 및 정렬 enum 호환
- `src/ui/return_button.py` — `pyqtSignal` 적용, 윈도우/커서 enum 호환
- `src/ui/member_search.py` — `PyQt5` 전환, 테이블 enum/다이얼로그 `exec_` 호환
- `src/ui/member_edit_dialog.py` — `PyQt5` 전환, 버튼 enum 호환
- `src/ui/main_window.py` — `PyQt5` 전환, 슬롯/윈도우 상태/스크롤/정렬 enum 호환
- `src/ui/card_register_dialog.py` — `PyQt5` 전환, 폼/버튼 enum 호환
- `src/ui/card_info_window.py` — `pyqtSignal` 적용, 테이블/정렬/다이얼로그 enum 호환
- `src/ui/admin_panel.py` — `PyQt5` 전환, 테이블 enum 호환
- `src/notifications/popup.py` — `PyQt5` import 전환
- `scripts/build_release.py` — hidden imports를 `PyQt5` 기준으로 변경
- `giftcardsys.spec` — hiddenimports를 `PyQt5` 기준으로 변경

### 다음 작업 시 참고사항
- 현재 설치 로그를 보면 `PyQt5` 휠이 `win_amd64`로 설치되므로, 진짜 32비트 Python을 사용하려면 반드시 32비트 인터프리터/가상환경에서 다시 설치해야 한다.
- `python main.py` 실행 검증 시 즉시 에러 없이 GUI 이벤트 루프가 정상 진입했다.

---

## [2026-04-23] EXE 관리자 페이지 열면 꺼지는 버그 수정

### 작업 내용
Python 3.8 32-bit EXE에서 관리자 버튼 클릭 시 프로그램이 조용히 종료되는 문제를 분석하고 수정했다.

**원인:**
- `backup_service.py:23`의 `def list_backups() -> list[Path]:` 반환 타입 어노테이션이 Python 3.9+ 전용 문법(PEP 585)이었음.
- Python 3.8에서 이 모듈이 로딩될 때 `TypeError: 'type' object is not subscriptable` 발생.
- 관리자 패널은 lazy import 방식이라 버튼을 처음 클릭하는 순간 `backup_service`가 임포트되며 즉시 크래시.
- EXE 빌드 설정 `console=False`로 인해 에러 메시지 없이 프로그램이 종료됨.
- `scripts/build_release.py`도 동일 문제: `list[str]`(3.9+), `Path | None`(3.10+) 문법 포함.

**수정 내용:**
- `list[Path]` → `List[Path]` (`from typing import List` 추가)
- `list[str]` → `List[str]`, `Path | None` → `Optional[Path]` (`from typing import List, Optional` 추가)
- `_on_open_admin()`에 try/except 추가 — 이후 어떤 예외든 에러 팝업으로 표시됨

### 변경된 파일
- `src/service/backup_service.py` — `list[Path]` → `List[Path]`, `from typing import List` 추가
- `scripts/build_release.py` — `list[str]` → `List[str]`, `Path | None` → `Optional[Path]`, typing import 추가
- `src/ui/main_window.py` — `_on_open_admin()`에 try/except 추가

### 다음 작업 시 참고사항
- Python 3.8 호환을 위해 타입 힌트는 반드시 `typing` 모듈 사용: `List`, `Dict`, `Optional`, `Tuple` 등.
- `X | Y` union 문법은 Python 3.10+. 3.8에서는 `Optional[X]` 또는 `Union[X, Y]` 사용.
- `dict[str, int]`, `list[str]` 등 내장 타입 직접 구독은 Python 3.9+. 3.8에서는 `Dict[str, int]`, `List[str]` 사용.
- 빌드 후 EXE를 `console=True`로 임시 전환하면 에러 메시지를 터미널에서 확인할 수 있어 디버깅에 유용하다.

---

## [2026-04-23] 회원 삭제 기능 추가

### 작업 내용
회원정보 수정 화면(더블클릭 → MemberEditDialog)에 "회원 삭제" 버튼을 추가하고 삭제 기능을 구현했다.

**삭제 흐름:**
1. [회원 삭제] 버튼 클릭 → 비밀번호 입력 다이얼로그 (QInputDialog, 비밀번호 마스킹)
2. 비밀번호 "0000" 일치 확인 → 최종 확인 팝업(QMessageBox.question)
3. 확인 시 DB 처리:
   - `cards.balance = 0, user_id = NULL` (잔액 초기화 + 회원 연결 끊기)
   - `users` 레코드 삭제
   - `transactions` 레코드 보존 (card_id 참조 유지)
4. 삭제 완료 팝업 → 다이얼로그 닫힘 → 회원 목록 자동 갱신

**삭제 후 데이터 상태:**
- 회원(users) 레코드: 삭제
- 카드(cards) 레코드: 유지 (user_id=NULL, balance=0)
- 거래내역(transactions): 전부 보존 (카드 ID로 여전히 조회 가능)
- 삭제된 회원의 카드는 회원 목록에서 보이지 않음 (고아 카드)

**Python 3.8 호환 처리:**
- 타입 힌트에 `typing` 모듈 사용 (member_edit_dialog.py 인라인 주석 방식 적용)

### 변경된 파일
- `src/ui/messages.py` — 삭제 관련 문자열 상수 7개 추가
- `src/db/queries.py` — `delete_member(conn, user_id)` 추가
- `src/service/card_service.py` — `delete_member(user_id)` 추가
- `src/ui/member_edit_dialog.py` — 버튼 행 재구성, 삭제 버튼 + `_on_delete()` 구현

### 다음 작업 시 참고사항
- 삭제 비밀번호는 `member_edit_dialog.py`의 `_DELETE_PASSWORD = "0000"` 상수로 관리.
- 비밀번호 변경이 필요하면 이 상수 값만 수정하면 된다.
- 고아 카드(user_id=NULL)는 바코드 스캔 시 `card_service.lookup()`에서 users 조회 시 `None`이 반환될 수 있으므로 추후 이 경로에 대한 방어 처리가 필요할 수 있다.

---

## [2026-04-23] 신규 회원 등록 화면 전화번호 기본값 체크박스 추가

### 작업 내용
`CardRegisterDialog`의 전화번호 입력 필드에 "기본값 입력" 체크박스를 추가했다.

**동작:**
- 기본 상태: 체크박스 ON → 전화번호 필드 비활성화, 값 = "01000000000"
- 체크 해제 시: 전화번호 필드 활성화 + 내용 초기화, 포커스 자동 이동
- 다시 체크 시: "01000000000"으로 복원, 필드 비활성화

**추가 수정:**
- `result_data: dict | None = None` (Python 3.10+ 문법) → `result_data = None`으로 교체
- f-string 스타일 일부를 `.format()` 방식으로 교체 (일관성)

### 변경된 파일
- `src/ui/card_register_dialog.py` — 체크박스 추가, Python 3.10+ 문법 수정

### 다음 작업 시 참고사항
- 기본 전화번호는 `_DEFAULT_PHONE = "01000000000"` 상수로 관리.
- 체크박스 상태 변경은 `stateChanged` 시그널 → `_on_phone_default_changed(state)` 슬롯에서 처리.
- `Qt.Checked`는 PyQt5 호환 상수 (PyQt6에서는 `Qt.CheckState.Checked`).

---

## [2026-04-23] 신규 등록 화면 — 초기 충전 금액 숫자패드 추가

### 작업 내용
초기 충전 금액 입력 필드 우측 끝에 ⌨ 키보드 아이콘 버튼을 추가하고,
클릭 시 다이얼로그 우측에 숫자패드 패널이 열리도록 구현했다.

**레이아웃 구조 변경:**
- 기존: `QVBoxLayout` 단일 폼
- 변경: `QHBoxLayout` (외부) → 왼쪽 폼 패널(440px 고정) + 오른쪽 숫자패드 패널(222px, 토글)
- 숫자패드 표시 시 `adjustSize()`로 다이얼로그 폭 자동 확장(440→662px), 숨김 시 자동 축소

**키보드 버튼 동작:**
- `setCheckable(True)` → 토글 버튼으로 동작
- 체크됨(라임색): 숫자패드 표시 / 해제(회색): 숫자패드 숨김

**숫자패드 입력 로직:**
- 0~9, 00: 현재 값에 자릿수 추가 (`_format_amount`가 자동으로 쉼표 포맷)
- C: 전체 지우기
- 키보드 직접 입력과 동시 사용 가능 (같은 `_amount` 필드 공유)

### 변경된 파일
- `src/ui/card_register_dialog.py` — 전체 레이아웃 재구성, 숫자패드 패널 추가

### 다음 작업 시 참고사항
- 숫자패드 버튼 크기: `_NP_BTN_W = 62`, `_NP_BTN_H = 56` 상수로 조정 가능.
- 패널 너비: `_NP_W = _NP_BTN_W * 3 + _NP_GAP * 2 + _NP_PAD * 2 = 222px`.
- `adjustSize()`는 각 패널에 `setFixedWidth()`가 적용되어 있으므로 정확히 동작함.

---

## [2026-04-23] 체크박스 스타일 개선 + 복귀 버튼 드래그 후 클릭 불가 버그 수정

### 작업 내용

**체크박스 스타일 (card_register_dialog.py)**
- "기본값 입력" 체크박스에 초록색 스타일 적용 (`border: #22c55e`, checked 배경: `#22c55e`)
- 전화번호 필드에 `:disabled` 스타일 추가 → 비활성 시 배경 `#d1d5db`, 텍스트 `#6b7280`으로 시각적 구분

**복귀 버튼 드래그 버그 수정 (return_button.py)**
- 원인: `eventFilter`에서 `MouseButtonPress`에 `return True`로 이벤트 소비 → 버튼이 마우스 캡처를 못함 → 창 이동 후 `MouseButtonRelease`가 버튼에 전달 안 됨 → `_is_dragging` 리셋 안 됨 → 다음 클릭도 드래그로 판단
- 해결: `btn.setAttribute(Qt.WA_TransparentForMouseEvents)` 적용 → 마우스 이벤트를 부모 QWidget에서 직접 처리
- `eventFilter` 제거, `mousePressEvent` / `mouseMoveEvent` / `mouseReleaseEvent` / `enterEvent` / `leaveEvent` 오버라이드로 교체
- hover/pressed 시각 피드백은 `enterEvent`·`leaveEvent`·`mousePress/Release`에서 버튼 스타일 직접 전환

### 변경된 파일
- `src/ui/card_register_dialog.py` — 체크박스 초록 스타일, 전화번호 필드 `:disabled` 스타일
- `src/ui/return_button.py` — `WA_TransparentForMouseEvents` 방식으로 전면 재작성

### 다음 작업 시 참고사항
- `WA_TransparentForMouseEvents` 방식은 버튼의 CSS `:hover`/`:pressed` 의사 클래스가 동작하지 않음. 대신 `enterEvent`/`leaveEvent`에서 스타일 문자열을 직접 교체하는 방식으로 처리.
- 체크박스 체크마크 이미지(`image: url(...)`)를 따로 지정하지 않았으므로 플랫폼 기본 체크마크가 사용됨. 원하는 이미지 아이콘이 있으면 `image: url(path)` 추가 가능.

---

## [2026-04-23] 복귀 버튼 위치 변경 + 드래그 이동 기능 추가

### 작업 내용
- 복귀 버튼 초기 위치를 오른쪽 아래 → **왼쪽 아래**로 변경.
- 마우스 드래그로 버튼 위치를 자유롭게 이동할 수 있도록 구현.

**드래그 구현 방식:**
- `QPushButton.clicked` 시그널 대신 `eventFilter`로 마우스 이벤트를 직접 제어.
- `MouseButtonPress`: 시작 좌표(`_drag_start`)와 위젯 위치(`_drag_origin`) 기록, 커서 → `SizeAllCursor`.
- `MouseMove`: 이동량이 `_DRAG_THRESHOLD(5px)` 초과 시 드래그 모드로 전환, `widget.move()` 호출.
- `MouseButtonRelease`: 드래그가 없었으면 클릭으로 판단 → `restore_requested` emit. 커서 → `PointingHandCursor` 복원.

**클릭 vs 드래그 구분:**
- 마우스를 5px 이상 움직이면 드래그 처리 (복귀 시그널 발생 안 함).
- 5px 미만 이동 후 떼면 클릭으로 처리 (창 복귀 동작).

### 변경된 파일
- `src/ui/return_button.py` — 위치 변경, eventFilter 기반 드래그 구현, `btn.clicked` 제거

### 다음 작업 시 참고사항
- 드래그 임계값은 `_DRAG_THRESHOLD = 5` 상수로 조정 가능.
- 초기 위치 변경은 `_reposition()` 메서드의 `screen.left() + margin` 부분 수정.
- 드래그 후 위치는 저장되지 않음 — 프로그램 재시작 시 항상 왼쪽 아래로 초기화.

---

## [2026-04-23] 회원 삭제 NOT NULL 오류 수정 (더미 유저 방식)

### 작업 내용
`cards.user_id NOT NULL` 제약 때문에 `user_id = NULL` 방식으로 카드를 분리할 수 없었던 문제를 수정.
탈퇴 회원 전용 더미 유저(`phone_number = "__deleted__"`)를 사용하는 방식으로 변경했다.

**삭제 처리 흐름:**
1. `__deleted__` 전화번호를 가진 더미 유저 조회 (없으면 자동 생성)
2. 삭제 대상 회원의 카드를 더미 유저로 재배정 + 잔액 0 초기화
3. 원래 회원 레코드 삭제

**추가 수정:**
- `search_users` 쿼리에 `AND u.phone_number != '__deleted__'` 조건 추가
  → 더미 유저가 회원 목록에 노출되지 않음

### 변경된 파일
- `src/db/queries.py` — `get_or_create_deleted_placeholder()` 추가, `delete_member()` 시그니처 변경, `search_users()` 더미 유저 제외 조건 추가
- `src/service/card_service.py` — `delete_member()` 에서 placeholder 생성 후 쿼리 호출

### 다음 작업 시 참고사항
- 더미 유저 식별자는 `queries._DELETED_PLACEHOLDER_PHONE = "__deleted__"` 상수로 관리.
- 더미 유저는 첫 삭제 시 자동 생성되며 이후 재사용된다.
- 더미 유저의 카드(탈퇴 회원 카드)는 바코드 스캔 시 `card_service.lookup()`에서 user가 더미 유저로 반환된다. 필요 시 UI에서 `phone_number == "__deleted__"` 체크로 별도 처리 가능.

---

## [2026-04-23] 최소화 버튼 다중 클릭 문제 수정 + 회원 목록 충전/결제 동작 수정

### 작업 내용

**1. 최소화 버튼 다중 클릭 문제 수정**
`_on_minimize()`에서 `setWindowState(Qt.WindowNoState)`를 먼저 호출하면 OS 윈도우 매니저가 최소화를 되돌리려 하여 충돌 발생 → 버튼을 3회 눌러야 최소화되는 증상.
- `_on_minimize()`: `setWindowState(Qt.WindowNoState)` 제거, `hide()` 만 호출
- `restore_window()`: `show()` 전에 `setWindowState(Qt.WindowNoState)` 추가

**2. 회원 목록 충전/결제 수정**
- 문제 1: 충전/결제 완료 후 성공 팝업 없음 → `QMessageBox.information`으로 완료 메세지 추가
- 문제 2: 메인 화면 거래내역이 갱신되지 않음 → `MemberSearchPanel`에 `transaction_done` 시그널 추가, `MainWindow._on_open_member_search()`에서 시그널 연결
- 문제 3: 카드 정보 창에서 회원 검색 후 거래해도 카드 정보가 갱신되지 않음 → `CardInfoWindow._on_open_member_search()`에서 `panel.transaction_done.connect(self._refresh)` 연결
- 추가: `TransactionDialog`의 `dict | None` Python 3.10+ 문법 → `None` 으로 수정 (Python 3.8 호환)

### 변경된 파일
- `src/ui/main_window.py`: `_on_minimize`, `restore_window`, `_on_open_member_search` 수정
- `src/ui/member_search.py`: `transaction_done` 시그널 추가, `_open_transaction` 완료 팝업 + emit 추가
- `src/ui/card_info_window.py`: `_on_open_member_search`에서 `transaction_done` 연결
- `src/ui/transaction_dialog.py`: `result_data: dict | None = None` → Python 3.8 호환으로 수정

### 다음 작업 시 참고사항
- `MemberSearchPanel.transaction_done` 시그널: 충전/결제 완료 시 emit → 연결된 창(`MainWindow`, `CardInfoWindow`)이 자동 새로고침
- 메인 창에서 회원 검색 창 열 때 반드시 `panel.transaction_done.connect(self._refresh_list)` 연결 필요

---

## [2026-04-23] 복귀 버튼 — 서브 창 열린 상태에서 작동 안 하는 버그 수정

### 작업 내용
서브 창(카드 정보, 회원 검색, 관리자 등)이 열린 채로 다른 프로그램에 가려지거나 최소화됐을 때 복귀 버튼이 동작하지 않는 버그를 수정했다.

**원인:**
- `restore_window()`에 "자식 창이 하나라도 열려 있으면 early return" 가드가 있었음.
- Qt의 `isVisible()`은 "명시적으로 `hide()` 된 적 없으면 True"를 반환 → 다른 프로그램에 가려진 서브 창도 `isVisible() == True`.
- 결과: 서브 창이 열린 순간부터 복귀 버튼이 완전히 무력화됨.

**수정 내용 (A 방법 — 앱 전체를 포그라운드로):**
- early return 가드 제거.
- 메인 창이 숨겨져 있거나 최소화된 경우 복구 후 앞으로 가져오기.
- 열려 있는 자식 창 전부도 최소화 복구 + `raise_()` + `activateWindow()` 처리.

### 변경된 파일
- `src/ui/main_window.py` — `restore_window()` 로직 전면 교체

### 다음 작업 시 참고사항
- `findChildren(QWidget)`은 재귀적으로 모든 자식을 반환하지만, `child.isWindow()`가 True인 것만 실제 독립 창 (CardInfoWindow, MemberSearchPanel, AdminPanel 등).
- `isHidden()`이 False여도 최소화 상태(`windowState() & Qt.WindowMinimized`)일 수 있으므로 두 조건을 모두 체크.
- 자식 창을 마지막에 올리므로 (메인 창 먼저 raise → 자식 창 나중에 raise) 자식 창이 최종 포커스를 가짐.

---

## [2026-04-24] Python 3.8 32비트 환경 호환성 수정

### 작업 내용
전체 파일을 탐색하여 Python 3.8 32비트 환경에서 발생할 수 있는 호환성 문제를 찾아 수정했다.

**발견 및 수정 사항:**
- `QFrame.Shape.VLine` / `QFrame.Shape.HLine` → `QFrame.VLine` / `QFrame.HLine` 으로 변경 (4개 파일)
  - 원인: PySide6에서 PyQt5로 마이그레이션 시 남겨진 PySide6 스타일 enum 접근법
  - PyQt5에서는 `QFrame.VLine` / `QFrame.HLine` 이 올바른 방식

**문제 없음으로 확인된 사항:**
- `requirements.txt`: `PyQt5>=5.15.11` → PyPI에서 `PyQt5-5.15.11-cp38-abi3-win32.whl` 확인 (32비트 Python 3.8 지원)
- 5.15.8~5.15.10은 32비트 wheel 없음, 5.15.11이 32비트 지원 재개한 첫 버전
- `Pillow>=10.0.0` → pip가 자동으로 Python 3.8 호환 버전(10.4.0) 설치
- 타입 힌트: 모두 Python 3.8 호환 (`typing.Optional`, `typing.List` 사용)
- `match` 문, `list[...]` 소문자 제네릭 등 Python 3.9+ 문법 없음
- `keyboard` 라이브러리: main.py에서 try/except로 감싸져 있어 안전

### 변경된 파일
- `src/ui/main_window.py` (line 189): `QFrame.Shape.VLine` → `QFrame.VLine`
- `src/ui/card_info_window.py` (line 166): `QFrame.Shape.HLine` → `QFrame.HLine`
- `src/ui/member_search.py` (line 157): `QFrame.Shape.HLine` → `QFrame.HLine`
- `src/ui/admin_panel.py` (line 193): `QFrame.Shape.HLine` → `QFrame.HLine`

### 다음 작업 시 참고사항
- PyQt5 32비트 Python 3.8 지원 버전: 5.15.11 (cp38-abi3-win32.whl). 5.15.8~5.15.10은 32비트 wheel 없음.
- 빌드 시 PyInstaller가 필요하지만 requirements.txt에는 없음 — 별도 설치 필요: `pip install pyinstaller`
- 32비트 빌드는 반드시 python38-32 인터프리터로 `python scripts/build_release.py` 실행해야 함

## [2026-05-01] 회원 이름 필드 추가

### 작업 내용
1. **회원 이름 필드 추가** — users 테이블에 `name TEXT NOT NULL DEFAULT '홍길동'` 컬럼 추가.
2. **자동 마이그레이션** — 기존 `giftcard.db`에 `ALTER TABLE users ADD COLUMN name TEXT NOT NULL DEFAULT '홍길동'`으로 자동 적용. 기존 회원도 '홍길동'으로 채워짐.
3. **신규 등록 다이얼로그** — 이름 입력행 추가. 전화번호와 동일한 "기본값 입력" 체크박스 패턴 (기본값 "홍길동"). 바코드 아래, 전화번호 위에 위치.
4. **이름으로 검색** — 회원 검색창에서 전화번호/바코드에 이름(LIKE) 조건 추가.
5. **회원 식별 정책 변경** — 기존 '같은 전화번호는 같은 user' 정책 폐기. 이제 바코드만 유일. 신규 등록 시 항상 새 user 생성.
6. **모든 리스트에 이름 표시**:
   - 회원 검색 테이블: 이름 컬럼 첫 번째에 추가 (6컬럼)
   - 메인 거래내역: 이름 컬럼 추가 (9컬럼)
   - 카드 정보 창: 이름 info 카드 추가 (3개로)
   - 관리자 화면: 전화번호+이름 컬럼 추가 (8컬럼, ADMIN_TX_HEADERS)
7. **회원 수정 다이얼로그** — 이름 입력 필드 추가, 이름도 수정 가능.

### 변경된 파일
- `src/db/schema.py` — users DDL에 name 컬럼 추가, init_db에 PRAGMA 마이그레이션 추가
- `src/db/queries.py` — insert_user/update_user 시그니처 변경, search_users에 이름 LIKE, fetch_transactions_by_period JOIN users 추가, fetch_transactions_filtered에 name 추가
- `src/service/card_service.py` — register에 name 파라미터 추가, 항상 신규 user 생성, update_user_phone→update_user, find_cards_by_phone JOIN 방식으로 변경
- `src/ui/messages.py` — MAIN_LIST_HEADERS/MEMBER_LIST_HEADERS/ADMIN_TX_HEADERS/REGISTER_NAME_LABEL/MEMBER_EDIT_NAME 추가
- `src/ui/card_register_dialog.py` — 이름 입력행(체크박스 패턴) 추가, _on_accept name 처리
- `src/ui/member_search.py` — 6컬럼으로 확장, 이름 표시, MemberEditDialog 호출 시 name 전달
- `src/ui/card_info_window.py` — 이름 info 카드 추가
- `src/ui/admin_panel.py` — ADMIN_TX_HEADERS 사용, 행 데이터에 phone_number/name 추가
- `src/ui/member_edit_dialog.py` — current_name 파라미터 추가, 이름 필드, update_user 호출
- `src/ui/main_window.py` — ResizeToContents 인덱스 수정(6→7), values에 name 추가
- `tests/test_card_service.py` — register 시그니처 반영, test_same_phone_reuses_user → test_each_registration_creates_new_user로 변경
- `tests/test_transaction_service.py` — _register 헬퍼 시그니처 반영
- `tests/test_admin_service.py` — register 시그니처 반영

### 다음 작업 시 참고사항
- `update_user_phone` 함수는 제거됨. 호출처는 모두 `update_user(user_id, phone, name)`으로 변경됨.
- 회원 식별: 바코드만 유일. 같은 전화번호라도 다른 카드 등록이면 다른 user row 생성됨.
- 관리자 화면 거래목록은 `ADMIN_TX_HEADERS` (8컬럼), 카드 정보 창 거래내역은 `TX_TABLE_HEADERS` (6컬럼) 각각 다른 헤더 사용.
- Python 3.8 32비트 호환 유지: typing.Optional, f-string 허용, match/case 및 list[X] 제네릭 형식 사용 금지.

---

## [2026-05-03] 1366x768 POS 환경 자동 진단 + 잘림/스크롤 수정

### 작업 내용
1366x768 소형 POS 환경에서 모든 화면이 잘리거나 겹치지 않는지 자동 검증하는 진단 하네스를 추가하고, 발견된 두 가지 잘림 문제를 수정했다.

**자동 진단 하네스 (`scripts/diagnose_ui.py`)**
- 임시 SQLite DB에 더미 데이터(회원 30명, 카드 30장, 거래 200건)를 자동 생성.
- 모든 주요 화면(메인/등록/충전/결제/회원검색/회원수정/관리자/카드정보)을 차례로 띄워 PNG 스크린샷 + 위젯 크기/텍스트 잘림 검사 → `tests/diagnostics/{report.json, screenshots/*.png}`.
- 큰 모니터에서도 작은 화면 동작을 검증하기 위해 `GIFTCARD_FAKE_SCREEN_H` 환경변수로 가상 화면 높이 시뮬레이션.

**발견된 실제 문제 2건 → 수정**
1. **메인 윈도우 minimumSize 720px** → 1366×768에서 작업표시줄+타이틀바 빼면 빠듯하여 `1060×720` → `1060×640`으로 낮춤. 거래내역 테이블은 본래 자체 스크롤이라 화면이 작아져도 OK.
2. **결제 다이얼로그 720px 고정** → 1366×768에서 잘림 위험. `setFixedSize(_W, content_h)` → 화면 높이에 따라 자동 축소(`min(content_h, screen_h - 80)`)하고, 컨텐츠를 `QScrollArea`로 감쌌다. 작은 화면(예: 600px)에서 ScrollArea가 정상 작동(스크롤 200px)함을 확인.
3. **카드 등록 다이얼로그**: 같은 패턴으로 `setMaximumHeight(screen_h - 80)` 적용 + 왼쪽 폼/오른쪽 숫자패드 둘 다 `QScrollArea`로 감싸 작은 화면 대응.

**검증 결과**
- 1366×768 시뮬레이션 (`GIFTCARD_FAKE_SCREEN_H=768`) → 11개 화면 모두 가로/세로 fits, 텍스트 잘림 0건.
- pytest 19개 단위 테스트 회귀 없음.

### 변경된 파일
- `src/ui/main_window.py` — minimumSize 720→640
- `src/ui/transaction_dialog.py` — `_available_screen_height()` 헬퍼 + ScrollArea 적용 + 화면 높이 자동 축소
- `src/ui/card_register_dialog.py` — `setMaximumHeight` + ScrollArea 적용 (왼쪽 폼/오른쪽 숫자패드 모두)
- `scripts/diagnose_ui.py` — 신규 생성 (자동 진단 하네스)
- `tests/diagnostics/{report.json, screenshots/}` — 진단 산출물

### 다음 작업 시 참고사항
- `GIFTCARD_FAKE_SCREEN_H` 환경변수가 0이거나 미설정이면 실제 `QApplication.primaryScreen().availableGeometry().height()` 사용. 테스트 외에는 일반적으로 설정 불필요.
- 진단 하네스 실행: `set QT_QPA_PLATFORM_PLUGIN_PATH=...\PyQt5\Qt5\plugins\platforms` 후 `venv32\Scripts\python.exe scripts\diagnose_ui.py`.
- ScrollArea가 활성화되는 임계 높이는 결제 다이얼로그 720, 등록 다이얼로그 589(닫힘)/필요 시 패드 312. 화면 높이가 그보다 작아져도 자동 축소되어 모든 컨텐츠 접근 가능.
- Python 3.8 32비트 호환 유지: 새 코드는 `os.environ.get(...) or "0"` 패턴, `int(...)`, 타이핑 어노테이션 미사용 또는 `typing.*` 사용.

---

## [2026-05-03] 신규 등록 다이얼로그 비율 축소 — 첫 화면에서 스크롤 없이 전체 표시

### 작업 내용
신규 회원 등록 다이얼로그가 처음 열렸을 때 확인/취소 버튼이 잘려 스크롤로만 보이는 문제를 발견하고 수정했다. 컨텐츠 sizeHint=491px이지만 다이얼로그가 408px로만 열려 83px이 초기 상태로 잘려있었음.

**수정: 비율 축소 + minimum height 보정**

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| 폼 너비 (`_FORM_W`) | 440 | 400 |
| 숫자패드 버튼 | 62×56 | 54×46 |
| 숫자패드 패널 너비 (`_NP_W`) | 222 | 192 |
| 숫자패드 패널 상하 여백 | 24 | 16 |
| 헤더 높이 / 폰트 | 56 / 13pt | 46 / 12pt |
| 폼 카드 마진 | 20,18,20,18 | 16,14,16,14 |
| 폼 vertical/horizontal spacing | 12 / 12 | 8 / 10 |
| 입력 필드 height | 40 | 34 |
| 키보드 토글 버튼 | 40×40 | 34×34 |
| root 마진 / spacing | 24 / 14 | 18,16,18,16 / 10 |
| 다이얼로그 minimumHeight | 400 (낮음) | `min(500, max_h)` |

**핵심 포인트**
- `setMinimumHeight(min(500, max_h))` — 1366×768 환경(max_h=688)에서는 500으로 열려 컨텐츠 491px이 다 보이고, 더 작은 화면에서는 `max_h`가 minimum을 잘라 자동 축소되며 ScrollArea가 활성화됨.
- 420px 매우 작은 화면 시뮬레이션 결과: 다이얼로그=340, 폼 content=491, 스크롤 max=151. 즉 작은 화면에서는 정상적으로 스크롤로 접근 가능.

### 변경된 파일
- `src/ui/card_register_dialog.py` — 위 표의 모든 치수 일괄 축소, minimum height 로직 변경

### 다음 작업 시 참고사항
- 컨텐츠가 다시 늘어나서 잘리는 일이 생기면 `_build_ui` 내 `setMinimumHeight(min(500, max_h))` 의 500 값을 새 컨텐츠 sizeHint에 맞춰 키울 것.
- 폼 row를 추가/제거하면 컨텐츠 높이도 변하므로 진단 하네스(`scripts/diagnose_ui.py`)로 재검증 권장.
- 비율 축소 후에도 텍스트 잘림 0건, pytest 19개 모두 PASS 유지.

---

## [2026-05-03] EXE 빌드 시 이미지 누락 문제 수정 (sys._MEIPASS 대응)

### 작업 내용
PyInstaller로 빌드한 EXE에서 회원/신규/관리자 버튼 아이콘, 체크박스 체크마크, 복귀 버튼 로고 등 대부분의 이미지가 표시되지 않는 문제를 수정했다.

**근본 원인**
- PyInstaller 6.x onedir 모드는 `--add-data img;img`로 지정해도 데이터 파일을 `dist/<APP>/_internal/img/`에 배치한다.
- 하지만 코드는 다음 두 가지 잘못된 경로 패턴을 사용 중이었다:
  1. `main_window.py` — `"img/회원.png"` 같은 cwd 상대경로. EXE 실행 시 cwd는 `dist/<APP>/`이므로 `_internal/`을 거치지 못함.
  2. `card_register_dialog.py` / `return_button.py` — `os.path.join(__file__, "..", "..", "img", ...)`. EXE에선 `__file__`이 PyInstaller 가상 경로를 가리켜 실제 데이터 위치와 다름.
- 결과: EXE에선 모든 이미지 호출이 `QPixmap.isNull() == True`로 떨어지고 텍스트만 표시됨.

**수정 — `src/paths.py` 신규 추가**
- `resource_path(rel)` 헬퍼 함수: `sys._MEIPASS` → 프로젝트 루트 → exe 폴더 → `exe/_internal` → cwd 순으로 후보 경로를 검사하고 존재하는 첫 경로를 반환.
- onefile / onedir / 일반 Python 실행 모두 동일 코드로 동작.

**호출처 일괄 변경**
- `src/ui/main_window.py` — 3개 nav 버튼 아이콘 (`회원/신규/관리자`)
- `src/ui/card_register_dialog.py` — `_CHECKMARK_IMG`(체크박스 체크마크 이미지)
- `src/ui/return_button.py` — `_LOGO_PATH` (복귀 버튼 로고)

### 변경된 파일
- `src/paths.py` — 신규 생성 (`resource_path()` 헬퍼)
- `src/ui/main_window.py` — `from src.paths import resource_path` + 3개 이미지 경로 적용
- `src/ui/card_register_dialog.py` — `_CHECKMARK_IMG = resource_path("img/checkmark_white.png")`
- `src/ui/return_button.py` — `_LOGO_PATH = resource_path("img/logo.png")`

### 검증
- 일반 실행: 5개 이미지 모두 발견 (`OK -> .../img/...png`)
- PyInstaller 시뮬레이션 (`sys._MEIPASS = .../dist/GiftCardSys/_internal`): 5개 이미지 모두 `_internal/img/...png`에서 발견
- 진단 하네스 — 회귀 0건, 텍스트 잘림 0건
- pytest — 19개 모두 PASS
- 메인 화면 스크린샷 — 회원/신규/관리자 버튼에 아이콘 정상 표시 확인

### 다음 작업 시 참고사항
- 새 이미지를 코드에서 참조할 때는 반드시 `from src.paths import resource_path` + `resource_path("img/...")` 패턴 사용. 절대로 `__file__` 기반 상대경로나 `"img/..."` 직접 사용 금지.
- 새 리소스 폴더(예: `assets/`)를 추가하면 `giftcardsys.spec`의 `datas`와 `scripts/build_release.py`의 `--add-data` 양쪽 모두에 추가해야 함.
- PyInstaller 6.x onedir → `_internal/`, 5.x onedir → 루트, onefile → `sys._MEIPASS` 임시폴더. 헬퍼는 모든 케이스를 자동 처리함.
- 빌드 후 검증: `dist/GiftCardSys/GiftCardSys.exe`를 실행했을 때 메인 화면 회원/신규/관리자 버튼에 아이콘이 보이는지 / 신규 등록 다이얼로그의 체크박스에 체크마크가 보이는지 / 복귀 버튼이 로고로 표시되는지 육안 확인.

---

## [2026-05-03] 격리된 32-bit venv 새로 만들고 EXE 빌드 — 두 가지 환경 이슈 발견 & 우회

### 작업 내용
완전 격리된 새 가상환경(`venv_clean`)에서 `GiftCardSys.exe` 32-bit 빌드를 성공시켰다. 진행 중 두 가지 환경 이슈를 발견했고 모두 우회/해결했다.

**이슈 ① 시스템 환경변수 `PYTHONPATH`가 venv 격리를 깨고 있었음**
- `PYTHONPATH=c:\users\aha94\appdata\local\programs\python\python38\lib\site-packages` (64-bit Python 3.8)가 사용자 환경에 설정되어 있었음.
- 이 때문에 32-bit venv 내부 Python 실행 시 `sys.path`에 64-bit site-packages가 강제 주입됨.
- 32-bit Python이 64-bit 휠을 import하려 시도 → 호환성 충돌 가능, venv가 격리되지 않은 상태.
- **우회**: 빌드 세션 동안 `$env:PYTHONPATH=""`로 비워서 진행. 시스템 설정은 건드리지 않음.

**이슈 ② 한글 + 공백 경로에서 PyInstaller 6.20의 PyQt5 hook이 콘솔 인코딩 깨짐으로 빌드 실패**
- 프로젝트 경로 `C:\Users\aha94\OneDrive\바탕 화면\새 폴더 (2)\giftcardsys_32BIT`.
- `hook-PyQt5.py:18` → `qt/__init__.py:257`의 `pathlib.Path(self.location['PrefixPath']).resolve()`에서 한글 경로가 `?? ??\? ?? (2)`로 깨진 채 전달 → `OSError [WinError 123]`.
- `PYTHONUTF8=1` + `chcp 65001`로도 해결 안 됨 (Qt5 내부 PrefixPath 조회 자체가 깨짐).
- **우회**: NTFS junction `C:\gcsys` → 원래 폴더로 만들고, 그 ASCII 경로에서 새 venv 생성 + 빌드. dist 결과는 양쪽 경로에서 모두 접근 가능.

**최종 빌드 환경 (venv_clean)**
- Python: 3.8.7 32-bit (`MSC v.1928 32 bit (Intel)`)
- 격리: `sys.prefix=C:\gcsys\venv_clean` ≠ `base_prefix`
- include-system-site-packages: false
- 모든 패키지 cp38-win32 native wheel:
  - PyQt5-5.15.11 (cp38-abi3-win32) / PyQt5-Qt5-5.15.2 (win32) / PyQt5-sip-12.15.0 (cp38-win32)
  - Pillow-10.4.0 (cp38-win32)
  - keyboard-0.13.5
  - pyinstaller-6.20.0

**빌드 결과**
- `dist/GiftCardSys/GiftCardSys.exe` — 2,022,817 bytes, **32-bit (i386)** machine type 검증
- `dist/GiftCardSys/_internal/img/` — 8개 이미지 모두 번들 (회원/신규/관리자/충전/결제/checkmark_white/logo/logo1)
- `dist/release/GiftCardSys-windows.zip` — 배포 zip
- 부트로더: `Windows-32bit-intel\runw.exe` (PyInstaller가 자동으로 32-bit native 사용)
- EXE 실행 검증: 메인 창 정상 표시, exit code 0

### 변경된 파일
- (소스 코드 변경 없음 — 환경 구성만)
- 새 위치: `C:\gcsys\venv_clean\` (junction 통해 프로젝트 루트에서도 접근 가능)
- `dist/GiftCardSys.spec` — PyInstaller가 자동 생성

### 다음 작업 시 참고사항

**다시 빌드하려면 다음 순서 준수**
```powershell
# 1. junction (이미 있으면 건너뛰기)
cmd /c 'mklink /J C:\gcsys "C:\Users\aha94\OneDrive\바탕 화면\새 폴더 (2)\giftcardsys_32BIT"'

# 2. PYTHONPATH 비우기
$env:PYTHONPATH=""; $env:PYTHONHOME=""

# 3. ASCII 경로에서 빌드
Set-Location C:\gcsys
& "C:\gcsys\venv_clean\Scripts\python.exe" "scripts\build_release.py"
```

- **시스템 PYTHONPATH 영구 제거 권장**: 제어판 → 시스템 → 환경변수에서 `PYTHONPATH` 항목을 삭제하면 추후 빌드/테스트 시 매번 `$env:PYTHONPATH=""` 호출 안 해도 됨. (단 다른 프로젝트가 이 변수에 의존할 수 있으니 사용자가 판단 필요)
- 한글 경로에서 직접 빌드는 PyInstaller 6.x + PyQt5 조합에서 막힘. `C:\gcsys` junction 필수.
- `venv_clean`을 다시 만들 때는 `C:\gcsys\venv_clean` 경로(ASCII)에서 만들어야 venv 내부 경로가 깨지지 않음.
- 기존 `venv32`는 그대로 보존 (개발/테스트용으로 계속 사용 가능). `venv_clean`은 빌드 전용.
- `build_windows.bat`이 있다면 PYTHONPATH 비우기 + ASCII junction 사용으로 업데이트 필요할 수 있음.

---

## [2026-05-03] 백업 복원 시 "공유 user" 카드 자동 분리 마이그레이션

### 작업 내용
정책 변경 [2026-05-01] 이전 데이터(또는 그 시점 백업의 복원본)에서 한 user_id에 카드 N장(N>1)이 매달려 있을 경우, 한 카드의 회원 정보를 수정하면 같은 user에 매달린 다른 카드까지 함께 변경되는 문제를 자동 마이그레이션으로 해결했다.

**문제 재현 결과**
- 시뮬레이션: user_id=1 회원에 카드 두 장(11111, 22222)이 매달린 상태에서 한 카드의 이름을 "이몽룡"으로 변경 → 두 카드 모두 "이몽룡"으로 함께 변경됨.
- 원인: `member_search.py`의 `users LEFT JOIN cards`가 같은 `u.id`를 가진 row를 N개 반환 → 더블클릭 → `update_user(user_id, ...)`로 user 한 명을 update → 그 user에 연결된 모든 카드가 함께 영향받음.
- 신규 등록 정책(`card_service.register()`)은 매번 무조건 새 user 생성하므로 신규 등록 케이스에는 발생 안 함. 백업 복원/raw SQL 주입 케이스에서만 발생.

**해결: `init_db()` 마이그레이션에 자동 분리 로직 추가**
- `src/db/schema.py:_split_shared_users(conn)` 신규 함수.
- 한 user_id에 카드 N장이 매달리면 첫 번째 카드는 기존 user에 두고, 2~N번째 카드는 새 user row(phone/name/created_at 그대로 복사)로 옮긴다.
- 거래내역(transactions)은 `card_id`만 가지고 있으므로 영향 없음 — 그대로 유지됨.
- 탈퇴 회원용 placeholder(`__deleted__`)는 의도된 공유라 분리 대상에서 제외.
- 멱등(idempotent) — 두 번째 호출에서는 분리할 게 없어서 아무 일도 일어나지 않음.

**검증**
- 시뮬레이션: user_id 공유 카드 5장 + 단독 카드 1장 → 마이그레이션 후 6 users / 6 cards (모든 user_id unique)
- 분리된 카드 22222의 회원 이름을 "이몽룡"으로 변경 → 11111/33333은 "홍길동" 그대로, 44444/55555는 "김철수" 그대로 ✓
- 거래내역 2건 보존
- pytest: 기존 19개 + 신규 분리 마이그레이션 5개 = **24개 모두 PASS**
- 진단 하네스: UI 회귀 0건

### 변경된 파일
- `src/db/schema.py` — `_split_shared_users()` 함수 추가, `init_db()` 끝에서 호출
- `tests/test_split_shared_users.py` — 신규 생성 (5개 테스트: 분리 동작 / 거래내역 보존 / 분리 후 독립 수정 / 멱등성 / placeholder 제외)

### 다음 작업 시 참고사항
- **현재 정책 정리**:
  - 같은 카드 = 같은 바코드. 그 외에는 모두 분리.
  - 신규 등록(`register()`): 항상 새 user_id 생성. 같은 phone+name+balance라도 별개 user.
  - 회원 검색의 `LEFT JOIN cards` 자체는 그대로 유지 (한 user에 여러 카드가 있을 가능성을 막는 건 마이그레이션이 담당).
- **마이그레이션 트리거 시점**: `init_db()` 호출 시(앱 시작) 또는 백업 복원 직후 EXE를 실행하면 자동 적용됨. 사용자 액션 불필요.
- **사이드 이펙트**: 분리된 user들은 phone/name이 동일하므로 회원 검색 결과에 외관상 같은 row로 보임. 그러나 내부적으로는 각 카드가 독립된 user에 매달려 있어 한 카드의 정보 수정이 다른 카드에 영향을 주지 않음.
- **삭제 placeholder(`__deleted__`)는 분리 안 함** — `queries._DELETED_PLACEHOLDER_PHONE`을 직접 참조하지 않고 `schema.py`에 같은 상수를 별도로 두었음. 두 상수 값이 어긋나지 않도록 주의(둘 다 `"__deleted__"`).
- **마이그레이션 비활성화하려면**: `init_db()` 끝부분의 `_split_shared_users(conn)` 호출 한 줄을 주석 처리.
