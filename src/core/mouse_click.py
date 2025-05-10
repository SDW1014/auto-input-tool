"""
마우스 클릭 모듈

시스템 레벨에서 마우스 클릭 기능을 제공합니다.
Windows API를 사용하여 관리자 권한으로 모든 애플리케이션에서 작동합니다.
"""
import pyautogui
import ctypes
import time
from ctypes import wintypes

# Windows API 상수
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

# Windows API 함수 설정
user32 = ctypes.WinDLL('user32', use_last_error=True)
user32.SetCursorPos.argtypes = [wintypes.INT, wintypes.INT]
user32.SetCursorPos.restype = wintypes.BOOL
user32.mouse_event.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.ULONG]

def click_at_position(x, y):
    """
    지정된 좌표(x, y)에서 마우스 왼쪽 버튼 클릭을 수행합니다.
    Windows API를 사용하여 시스템 레벨에서 작동합니다.
    
    Args:
        x (int): 클릭할 x 좌표
        y (int): 클릭할 y 좌표
    """
    # 방법 1: Windows API 사용 (관리자 권한 필요할 수 있음)
    try:
        # 커서 위치 설정
        user32.SetCursorPos(int(x), int(y))
        # 마우스 클릭 이벤트 발생
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.01)  # 짧은 지연
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    except Exception as e:
        # Windows API 실패 시 pyautogui 사용
        print(f"Windows API 클릭 실패, pyautogui 사용: {e}")
        pyautogui.click(x, y) 