# -*- coding: utf-8 -*-
"""리소스 파일(이미지 등) 경로 헬퍼.

일반 Python 실행 / PyInstaller onedir / PyInstaller onefile 모두에서
img/ 같은 리소스 폴더를 찾을 수 있도록 후보 경로를 순서대로 검사한다.

변경 이력:
- PyInstaller 6.x onedir 모드는 데이터 파일을 dist/<APP>/_internal/<resource>로 옮기므로,
  단순 상대경로 또는 __file__ 기준 ../../img 가 동작하지 않는 문제를 해결.
"""
import os
import sys


_HERE = os.path.dirname(os.path.abspath(__file__))
# 일반 실행에서는 src/ 위가 프로젝트 루트
_PROJECT_ROOT = os.path.dirname(_HERE)


def _candidate_bases():
    bases = []
    # PyInstaller (onefile/onedir 모두 _MEIPASS 노출)
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        bases.append(meipass)
    # 일반 실행 — 프로젝트 루트
    bases.append(_PROJECT_ROOT)
    # PyInstaller onedir 안전망 — exe 폴더, exe/_internal
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        bases.append(exe_dir)
        bases.append(os.path.join(exe_dir, "_internal"))
    # cwd 안전망 (사용자가 다른 폴더에서 실행했을 때)
    bases.append(os.getcwd())
    # 중복 제거 (순서 유지)
    seen = set()
    uniq = []
    for b in bases:
        if b and b not in seen:
            seen.add(b)
            uniq.append(b)
    return uniq


def resource_path(relative):
    # type: (str) -> str
    """리소스의 절대 경로를 반환. 존재하는 첫 후보, 없으면 첫 번째 후보 경로(caller가 처리)."""
    rel = relative.replace("\\", "/").lstrip("/")
    parts = rel.split("/")
    for base in _candidate_bases():
        candidate = os.path.join(base, *parts)
        if os.path.exists(candidate):
            return candidate
    # 못 찾았으면 첫 번째 후보로 fallback (Qt이 빈 QPixmap 처리)
    return os.path.join(_candidate_bases()[0], *parts)
