"""
관리자 권한 확인 모듈

프로그램이 관리자 권한으로 실행되었는지 확인하고, 
필요한 경우 관리자 권한으로 다시 실행하는 기능을 제공합니다.
"""
import sys
import ctypes
import os

def is_admin():
    """
    현재 프로그램이 관리자 권한으로 실행 중인지 확인합니다.
    
    Returns:
        bool: 관리자 권한으로 실행 중이면 True, 아니면 False
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """
    프로그램을 관리자 권한으로 다시 실행합니다.
    현재 프로세스는 종료합니다.
    """
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        " ".join(sys.argv),
        None,
        1  # SW_SHOWNORMAL
    )
    # 현재 프로세스 종료
    sys.exit(0) 