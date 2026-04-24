#!/usr/bin/env python3
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


APP_NAME = "GiftCardSys"
ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build"
PYI_CONFIG_DIR = ROOT / ".pyinstaller"
ICON_PNG = ROOT / "img" / "logo1.png"
ICON_ICO = ROOT / "img" / "logo1.ico"
ICON_ICNS = ROOT / "img" / "logo1.icns"


def run(cmd: List[str]) -> None:
    subprocess.run(cmd, check=True, cwd=ROOT)


def clean() -> None:
    for path in (DIST_DIR, BUILD_DIR):
        if path.exists():
            shutil.rmtree(path)
    PYI_CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def convert_icon(system: str) -> Optional[Path]:
    if not ICON_PNG.exists():
        print(f"아이콘 파일 없음: {ICON_PNG} — 아이콘 없이 빌드합니다.")
        return None

    try:
        from PIL import Image
    except ImportError:
        print("Pillow 미설치 — 아이콘 없이 빌드합니다. (pip install Pillow)")
        return None

    img = Image.open(ICON_PNG).convert("RGBA")

    if system == "windows":
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(ICON_ICO, format="ICO", sizes=sizes)
        print(f"아이콘 변환 완료: {ICON_ICO}")
        return ICON_ICO

    if system == "darwin":
        # PyInstaller는 macOS에서 PNG도 허용
        print(f"macOS 빌드 — PNG 아이콘 사용: {ICON_PNG}")
        return ICON_PNG

    return None


def pyinstaller_build() -> None:
    system = platform.system().lower()
    data_sep = ";" if system == "windows" else ":"
    os.environ["PYINSTALLER_CONFIG_DIR"] = str(PYI_CONFIG_DIR)

    icon_path = convert_icon(system)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name", APP_NAME,
        "--add-data", f"img{data_sep}img",
        "--add-data", f"config{data_sep}config",
    ]

    if icon_path:
        cmd += ["--icon", str(icon_path)]

    # PyQt5 필수 hidden imports
    for mod in [
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "PyQt5.QtWidgets",
        "PyQt5.QtSvg",
        "PyQt5.QtXml",
    ]:
        cmd += ["--hidden-import", mod]

    cmd.append("main.py")
    run(cmd)


def package_output() -> None:
    system = platform.system().lower()
    release_dir = DIST_DIR / "release"
    release_dir.mkdir(parents=True, exist_ok=True)

    if system == "darwin":
        app_bundle = DIST_DIR / f"{APP_NAME}.app"
        if not app_bundle.exists():
            raise RuntimeError(f"앱 번들을 찾을 수 없습니다: {app_bundle}")
        dmg_path = DIST_DIR / f"{APP_NAME}-installer.dmg"
        dmg_staging = DIST_DIR / "dmg"
        if dmg_staging.exists():
            shutil.rmtree(dmg_staging)
        dmg_staging.mkdir(parents=True, exist_ok=True)
        shutil.copytree(app_bundle, dmg_staging / app_bundle.name, dirs_exist_ok=True)
        app_link = dmg_staging / "Applications"
        if app_link.exists() or app_link.is_symlink():
            app_link.unlink()
        app_link.symlink_to("/Applications")

        try:
            run([
                "hdiutil", "create",
                "-volname", APP_NAME,
                "-srcfolder", str(dmg_staging),
                "-ov", "-format", "UDZO",
                str(dmg_path),
            ])
            print(f"설치 파일 생성: {dmg_path}")
        except Exception:
            print("DMG 생성에 실패했습니다. .app 번들은 정상 생성되었습니다.")
        return

    if system == "windows":
        target = DIST_DIR / APP_NAME
        if not target.exists():
            raise RuntimeError(f"실행 폴더를 찾을 수 없습니다: {target}")
        archive = release_dir / f"{APP_NAME}-windows"
        shutil.make_archive(str(archive), "zip", root_dir=target.parent, base_dir=target.name)
        print(f"설치용 zip 생성: {archive}.zip")
        return

    target = DIST_DIR / APP_NAME
    if not target.exists():
        raise RuntimeError(f"실행 폴더를 찾을 수 없습니다: {target}")
    archive = release_dir / f"{APP_NAME}-linux.tar.gz"
    run(["tar", "-czf", str(archive), "-C", str(target.parent), target.name])
    print(f"배포 파일 생성: {archive}")


def main() -> None:
    clean()
    pyinstaller_build()
    package_output()
    print("완료: dist 폴더를 확인하세요.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"빌드 실패: {exc}")
        sys.exit(1)
