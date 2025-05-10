"""
마우스 위치 모듈

현재 마우스 커서의 위치를 반환하는 기능을 제공합니다.
"""
import pyautogui

def get_mouse_position():
    """
    현재 마우스 커서의 위치 좌표(x, y)를 반환합니다.
    
    Returns:
        tuple: (x, y) 좌표
    """
    return pyautogui.position() 