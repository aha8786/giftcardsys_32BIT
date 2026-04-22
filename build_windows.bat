@echo off
chcp 65001 > nul

echo [GiftCardSys] Windows EXE Build Start

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo Installing packages...
pip install -r requirements.txt pyinstaller
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)

echo Building...
python scripts\build_release.py

if %ERRORLEVEL% == 0 (
    echo.
    echo Build succeeded!
    echo EXE location : dist\GiftCardSys\GiftCardSys.exe
    echo Release ZIP  : dist\release\GiftCardSys-windows.zip
) else (
    echo.
    echo Build failed. Check the error messages above.
)

pause
