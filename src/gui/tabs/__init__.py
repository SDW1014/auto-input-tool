"""
탭 UI 모듈 패키지

애플리케이션의 각 기능별 탭 UI를 제공하는 모듈들을 포함합니다.
"""
from src.gui.tabs.mouse_clicker_tab import MouseClickerTab
from src.gui.tabs.keyboard_tab import KeyboardTab
from src.gui.tabs.settings_tab import SettingsTab

__all__ = ['MouseClickerTab', 'KeyboardTab', 'SettingsTab'] 