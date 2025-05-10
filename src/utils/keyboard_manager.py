"""
키보드 단축키 관리 모듈

전역 키보드 단축키를 등록하고 관리하는 기능을 제공합니다.
"""
import keyboard

class KeyboardManager:
    """
    전역 키보드 단축키 관리 클래스
    """
    def __init__(self):
        """
        KeyboardManager 초기화
        """
        self.registered_hotkeys = []
    
    def register_hotkey(self, key, callback):
        """
        단축키 등록

        Args:
            key (str): 등록할 키 (예: 'f6', 'ctrl+alt+p')
            callback (function): 키가 눌렸을 때 실행할 콜백 함수
        """
        try:
            keyboard.add_hotkey(key, callback)
            self.registered_hotkeys.append(key)
            print(f"단축키 등록 성공: {key}")
        except Exception as e:
            print(f"단축키 등록 실패 ({key}): {e}")
    
    def unregister_hotkey(self, key):
        """
        단축키 해제

        Args:
            key (str): 해제할 키
        """
        try:
            keyboard.remove_hotkey(key)
            if key in self.registered_hotkeys:
                self.registered_hotkeys.remove(key)
            print(f"단축키 해제 성공: {key}")
        except Exception as e:
            print(f"단축키 해제 실패 ({key}): {e}")
    
    def unregister_all(self):
        """
        모든 단축키 해제
        """
        try:
            keyboard.unhook_all()
            self.registered_hotkeys = []
            print("모든 단축키 해제 성공")
        except Exception as e:
            print(f"단축키 해제 실패: {e}") 