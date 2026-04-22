# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 협업 규칙 (Collaboration Rules)

1. **모든 응답과 출력은 한국어로 작성한다.** UI 텍스트, 에러 메시지, Claude의 대화 응답 모두 한국어를 사용한다. 코드 변수명/함수명/주석은 영어로 유지한다.

2. **작업 시작 전 인터뷰를 진행한다.** 요청이 모호하거나, 작업 중 사용자가 결정해야 할 사항이 생기면 바로 구현하지 말고 먼저 질문한다. 질문은 한 번에 몰아서 한다 (여러 번 나눠 묻지 않는다). 명확한 작업(버그 수정 등)은 질문 없이 진행한다.

3. **작업 완료 후 HANDOFF.md에 누적 추가한다.** 매 작업이 끝나면 `HANDOFF.md` 하단에 내용을 추가한다 (덮어쓰지 않는다). 형식은 아래를 따른다:
   ```
   ## [날짜] 작업 제목
   ### 작업 내용
   ### 변경된 파일
   ### 다음 작업 시 참고사항
   ```

## Project Overview

A PySide6 desktop gift card management system (기프트카드 관리 시스템) for retail use — handles card registration, payment, recharge, and admin reporting via barcode scanner. Offline-first with SQLite. Priority order: **data accuracy > exception handling > stability > speed > UI**.

The full requirements spec is in `prompt1.md`.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Run tests
pytest tests/ -v

# Run a single test file
pytest tests/test_card_service.py -v

# Lint
flake8 src/ --max-line-length=100

# Type check
mypy src/
```

## Architecture

```
[Barcode Scanner] → [PySide6 GUI] → [Service Layer] → [SQLite DB]
                                          ↓
                                  [Notification Module]
```

On startup: connect to SQLite → auto-create DB/tables if missing → launch main window.

### Module Structure

```
main.py              # Entry point — DB init + launch QApplication
src/
  db/
    schema.py        # CREATE TABLE statements, runs on startup
    queries.py       # All raw SQL operations
  service/
    card_service.py        # Card scan, registration, lookup
    transaction_service.py # Payment and recharge logic
    admin_service.py       # Period-based statistics queries
  ui/
    main_window.py         # POS main screen with barcode input
    card_register.py       # New card registration dialog
    transaction.py         # Payment / recharge dialog
    admin_panel.py         # Admin statistics screen
    member_search.py       # Member lookup by phone number
  notifications/
    ui_popup.py            # Phase 1: popup alerts
    sms.py                 # Phase 2: SMS API
    kakao_talk.py          # Phase 2: Kakao Talk 알림톡
  exceptions.py      # Custom exception classes
tests/
config/
  settings.py        # App configuration
```

## Database Schema

```sql
-- users: one row per member
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- cards: barcode → balance (denormalized for O(1) lookup)
CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    balance INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- transactions: immutable audit log — never UPDATE or DELETE rows here
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER REFERENCES cards(id),
    type TEXT NOT NULL CHECK(type IN ('충전', '사용')),
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key invariant:** `cards.balance` must always equal the `balance_after` of that card's latest transaction. Update both atomically in a single SQLite transaction.

## Core Business Logic

**Card scan flow:** barcode input → DB lookup → if found: show info + balance; if not found: open registration dialog.

**Payment:** validate amount > 0, amount ≤ current balance → deduct balance → insert transaction row (type='사용').

**Recharge:** validate amount > 0 → add to balance → insert transaction row (type='충전').

**Admin stats SQL:**
```sql
SELECT
    SUM(CASE WHEN type='충전' THEN amount ELSE 0 END) AS total_recharged,
    SUM(CASE WHEN type='사용' THEN amount ELSE 0 END) AS total_used
FROM transactions
WHERE created_at BETWEEN :start AND :end;
```

## Exception Handling Requirements

All of these must be handled explicitly — do not let them surface as unhandled exceptions:
- Duplicate barcode on registration
- DB connection failure (auto-reconnect attempt, then error dialog)
- Negative or zero amount input
- Non-numeric input
- Insufficient balance (결제 시 잔액 부족)
- Unregistered card scanned

## Tech Stack

- **GUI:** PySide6 (Qt for Python) — desktop only, no web
- **DB:** SQLite3 via Python's built-in `sqlite3` module
- **Testing:** pytest
- **Python:** 3.9+
