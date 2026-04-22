#!/usr/bin/env bash
set -euo pipefail

APP_NAME="GiftCardSys"
SPEC_FILE="giftcardsys.spec"
DIST_DIR="dist"
BUILD_DIR="build"
PYI_CONFIG_DIR=".pyinstaller"
DMG_NAME="${APP_NAME}-installer"
ICON_PNG="img/logo.png"
ICONSET_DIR="${BUILD_DIR}/icon.iconset"
ICNS_PATH="${BUILD_DIR}/${APP_NAME}.icns"

if [[ "$OSTYPE" != "darwin"* ]]; then
  echo "이 스크립트는 macOS에서만 실행할 수 있습니다."
  exit 1
fi

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "PyInstaller가 없습니다. 먼저 설치하세요: pip install pyinstaller"
  exit 1
fi

ICON_PATH=""

if [[ -f "$ICON_PNG" ]]; then
  rm -rf "$ICONSET_DIR"
  mkdir -p "$ICONSET_DIR"

  sips -z 16 16 "$ICON_PNG" --out "${ICONSET_DIR}/icon_16x16.png" >/dev/null
  sips -z 32 32 "$ICON_PNG" --out "${ICONSET_DIR}/icon_16x16@2x.png" >/dev/null
  sips -z 32 32 "$ICON_PNG" --out "${ICONSET_DIR}/icon_32x32.png" >/dev/null
  sips -z 64 64 "$ICON_PNG" --out "${ICONSET_DIR}/icon_32x32@2x.png" >/dev/null
  sips -z 128 128 "$ICON_PNG" --out "${ICONSET_DIR}/icon_128x128.png" >/dev/null
  sips -z 256 256 "$ICON_PNG" --out "${ICONSET_DIR}/icon_128x128@2x.png" >/dev/null
  sips -z 256 256 "$ICON_PNG" --out "${ICONSET_DIR}/icon_256x256.png" >/dev/null
  sips -z 512 512 "$ICON_PNG" --out "${ICONSET_DIR}/icon_256x256@2x.png" >/dev/null
  sips -z 512 512 "$ICON_PNG" --out "${ICONSET_DIR}/icon_512x512.png" >/dev/null
  sips -z 1024 1024 "$ICON_PNG" --out "${ICONSET_DIR}/icon_512x512@2x.png" >/dev/null
  if iconutil -c icns "$ICONSET_DIR" -o "$ICNS_PATH"; then
    ICON_PATH="$ICNS_PATH"
  else
    echo "아이콘 변환 실패, 기본 아이콘으로 진행합니다."
  fi
fi

rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$PYI_CONFIG_DIR"
export PYINSTALLER_CONFIG_DIR="$PWD/$PYI_CONFIG_DIR"

if [[ -n "$ICON_PATH" ]]; then
  pyinstaller "$SPEC_FILE" --noconfirm --clean --icon "$ICON_PATH"
else
  pyinstaller "$SPEC_FILE" --noconfirm --clean
fi

APP_BUNDLE="${DIST_DIR}/${APP_NAME}.app"
if [[ ! -d "$APP_BUNDLE" ]]; then
  echo "앱 번들 생성 실패: ${APP_BUNDLE}"
  exit 1
fi

mkdir -p "${DIST_DIR}/dmg"
cp -R "$APP_BUNDLE" "${DIST_DIR}/dmg/"
ln -sfn /Applications "${DIST_DIR}/dmg/Applications"

rm -f "${DIST_DIR}/${DMG_NAME}.dmg"
hdiutil create \
  -volname "${APP_NAME}" \
  -srcfolder "${DIST_DIR}/dmg" \
  -ov \
  -format UDZO \
  "${DIST_DIR}/${DMG_NAME}.dmg" >/dev/null || {
    echo "DMG 생성 실패. 현재 환경에서 hdiutil 실행이 제한될 수 있습니다."
    echo "앱 번들은 정상 생성되었습니다: ${APP_BUNDLE}"
    exit 0
  }

echo "완료:"
echo "- 앱: ${APP_BUNDLE}"
echo "- 설치 파일: ${DIST_DIR}/${DMG_NAME}.dmg"
