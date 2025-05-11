"""
마우스 자동 클릭기 빌드 스크립트

실행 파일(.exe) 생성을 위한 cx_Freeze 빌드 스크립트입니다.
"""
import sys
import os
from cx_Freeze import setup, Executable

# 빌드 옵션
build_exe_options = {
    "packages": ["tkinter", "pyautogui", "ctypes", "keyboard"],
    "includes": ["src"],
    "include_files": ["mouse_icon.ico"],
    "excludes": [],
    "build_exe": "build_output",  # 빌드 출력 디렉토리
}

# 실행 파일 옵션
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # GUI 애플리케이션 (콘솔 창 없음)

# 실행 파일 설정
executables = [
    Executable(
        script="main.py",  # 메인 파일
        base=base,
        target_name="마우스자동클릭기.exe",  # 출력 파일 이름
        icon="mouse_icon.ico",
        shortcut_name="마우스 자동 클릭기",  # 바로가기 이름
        shortcut_dir="DesktopFolder",  # 바탕화면에 바로가기 생성
        uac_admin=True,  # 관리자 권한으로 실행 요청
    )
]

# 설정
setup(
    name="마우스 자동 클릭기 & 키보드 연타",
    version="1.5.0",  # 탭 기반 UI 업데이트
    description="마우스 자동 클릭 및 키보드 연속 입력 프로그램",
    options={"build_exe": build_exe_options},
    executables=executables
)

print("빌드가 완료되었습니다. build_output 폴더를 확인하세요.")
print("실행 방법: build_output/마우스자동클릭기.exe (관리자 권한으로 실행해주세요)") 