@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

echo ============================================================
echo  GiftCardSys - Windows 32bit EXE 빌드 스크립트
echo  대상: Python 3.8 32bit + PyQt5 + PyInstaller
echo ============================================================
echo.

:: ── Python 3.8 32비트 인터프리터 탐색 ──────────────────────────────
set PY38=

:: 우선순위 순으로 탐색
for %%P in (
    "C:\Python38-32\python.exe"
    "C:\Python38\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python38-32\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python38\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python38-32\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python38\python.exe"
) do (
    if exist %%P (
        set PY38=%%P
        goto :found
    )
)

:: py 런처로 시도
where py >nul 2>&1
if %ERRORLEVEL% == 0 (
    py -3.8-32 --version >nul 2>&1
    if %ERRORLEVEL% == 0 (
        set PY38=py -3.8-32
        goto :found
    )
)

echo [오류] Python 3.8 32비트를 찾을 수 없습니다.
echo.
echo  설치 방법:
echo   1. https://www.python.org/downloads/release/python-3815/ 접속
echo   2. "Windows installer (32-bit)" 다운로드 및 설치
echo   3. 설치 경로 예: C:\Python38-32
echo.
pause
exit /b 1

:found
echo [확인] Python 인터프리터: %PY38%

:: 실제로 32비트인지 검증
%PY38% -c "import struct, sys; bits=struct.calcsize('P')*8; print(f'  Python {sys.version[:6]}, {bits}bit'); exit(0 if bits==32 else 1)"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [오류] 위 Python이 64비트입니다. 32비트 Python 3.8이 필요합니다.
    pause
    exit /b 1
)
echo.

:: ── 패키지 설치 ────────────────────────────────────────────────────
echo [1/3] 패키지 설치 중...
%PY38% -m pip install --upgrade pip >nul 2>&1
%PY38% -m pip install -r requirements.txt pyinstaller==6.3.0
if %ERRORLEVEL% NEQ 0 (
    echo [오류] 패키지 설치 실패.
    pause
    exit /b 1
)
echo       완료.
echo.

:: ── PyInstaller 버전 확인 ───────────────────────────────────────────
echo [2/3] 빌드 환경 확인...
%PY38% -m PyInstaller --version
echo.

:: ── EXE 빌드 ────────────────────────────────────────────────────────
echo [3/3] EXE 빌드 중... (수 분 소요될 수 있습니다)
%PY38% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --name GiftCardSys ^
    --add-data "img;img" ^
    --add-data "config;config" ^
    --hidden-import PyQt5.QtCore ^
    --hidden-import PyQt5.QtGui ^
    --hidden-import PyQt5.QtWidgets ^
    --hidden-import PyQt5.QtSvg ^
    --hidden-import PyQt5.QtXml ^
    main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [오류] 빌드 실패. 위 오류 메시지를 확인하세요.
    pause
    exit /b 1
)

:: ── ZIP 패키징 ──────────────────────────────────────────────────────
if not exist "dist\release" mkdir "dist\release"
powershell -Command "Compress-Archive -Path 'dist\GiftCardSys' -DestinationPath 'dist\release\GiftCardSys-windows32.zip' -Force"

echo.
echo ============================================================
echo  빌드 완료!
echo  EXE 위치 : dist\GiftCardSys\GiftCardSys.exe
echo  ZIP 위치 : dist\release\GiftCardSys-windows32.zip
echo ============================================================
pause
