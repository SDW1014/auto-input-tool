"""
탭 기반 마우스 자동 클릭 & 키보드 연타 프로그램

사용자 인터페이스를 탭으로 분리하여 기능별로 구분합니다.
"""
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ctypes

from src.core.mouse_position import get_mouse_position
from src.utils.admin_check import is_admin, run_as_admin
from src.gui.tabs.mouse_clicker_tab import MouseClickerTab
from src.gui.tabs.keyboard_tab import KeyboardTab
from src.gui.tabs.settings_tab import SettingsTab

class TabBasedApp:
    def __init__(self, root):
        try:
            # 기본 윈도우 설정
            self.root = root
            self.root.title("마우스 자동 클릭기 & 키보드 연타")
            self.root.geometry("520x700")  # 창 크기 설정
            self.root.resizable(False, False)
            
            # 창을 항상 맨 위에 표시
            self.root.attributes('-topmost', True)
            
            # 관리자 권한 확인
            if not is_admin():
                messagebox.showwarning("권한 필요", "이 프로그램은 관리자 권한이 필요합니다.\n프로그램을 다시 시작합니다.")
                run_as_admin()
                return
            
            # 스타일 설정
            self._setup_styles()
            
            # 탭 컨트롤 생성
            self.tab_control = ttk.Notebook(self.root)
            
            # 각 탭 생성
            self.mouse_tab = MouseClickerTab(self.tab_control)
            self.keyboard_tab = KeyboardTab(self.tab_control)
            self.settings_tab = SettingsTab(self.tab_control)
            
            # 탭 추가
            self.tab_control.add(self.mouse_tab.frame, text='마우스 자동 클릭')
            self.tab_control.add(self.keyboard_tab.frame, text='키보드 연타')
            self.tab_control.add(self.settings_tab.frame, text='설정')
            
            # 탭 컨트롤 배치
            self.tab_control.pack(expand=1, fill="both")
            
            # 앱이 종료될 때 정리 작업을 위한 프로토콜 설정
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # 전역 단축키 설정
            self._setup_global_hotkeys()
            
            # 마우스 위치 추적 시작
            self._start_mouse_tracking()
            
            print("GUI: 탭 기반 애플리케이션 초기화 완료")
            
        except Exception as e:
            print(f"GUI: 애플리케이션 초기화 중 오류: {e}")
            import traceback
            traceback.print_exc()
            try:
                messagebox.showerror("오류", f"프로그램 초기화 중 오류가 발생했습니다.\n{str(e)}")
            except:
                print("GUI: 메시지박스 표시 실패")
    
    def _setup_styles(self):
        """스타일 설정"""
        try:
            style = ttk.Style()
            style.configure("TButton", font=("맑은 고딕", 12))  # 버튼 폰트 크기 증가
            style.configure("TLabel", font=("맑은 고딕", 11))   # 라벨 폰트 크기 증가
            style.configure("Title.TLabel", font=("맑은 고딕", 16, "bold"))  # 제목 라벨 스타일
            style.configure("Green.TLabel", foreground="green", font=("맑은 고딕", 12, "bold"))
            style.configure("Red.TLabel", foreground="red", font=("맑은 고딕", 12, "bold"))
            style.configure("Large.TButton", font=("맑은 고딕", 14))  # 큰 버튼 스타일
            
            # 노트북(탭) 스타일 설정
            style.configure("TNotebook", font=("맑은 고딕", 12))
            style.configure("TNotebook.Tab", font=("맑은 고딕", 12, "bold"), padding=[10, 5])
        except Exception as e:
            print(f"GUI: 스타일 설정 중 오류: {e}")
    
    def _start_mouse_tracking(self):
        """마우스 위치 추적 시작"""
        # 마우스 위치 업데이트 함수
        def update_mouse_position():
            try:
                if hasattr(self.mouse_tab, 'update_position'):
                    x, y = get_mouse_position()
                    self.mouse_tab.update_position(x, y)
                self.root.after(100, update_mouse_position)  # 100ms마다 업데이트
            except Exception as e:
                print(f"마우스 위치 추적 중 오류: {e}")
        
        # 마우스 위치 추적 시작
        update_mouse_position()
    
    def _setup_global_hotkeys(self):
        """전역 단축키 설정"""
        try:
            # 마우스 탭의 단축키 설정
            if hasattr(self.mouse_tab, 'setup_hotkeys'):
                self.mouse_tab.setup_hotkeys()
            
            # 키보드 탭의 단축키 설정
            if hasattr(self.keyboard_tab, 'setup_hotkeys'):
                self.keyboard_tab.setup_hotkeys()
        except Exception as e:
            print(f"전역 단축키 설정 중 오류: {e}")
    
    def on_closing(self):
        """앱 종료 시 정리 작업"""
        try:
            print("앱 종료 요청됨 - 정리 시작...")
            
            # 마우스 탭 정리
            if hasattr(self.mouse_tab, 'cleanup'):
                self.mouse_tab.cleanup()
            
            # 키보드 탭 정리
            if hasattr(self.keyboard_tab, 'cleanup'):
                self.keyboard_tab.cleanup()
            
            # 스레드 종료를 위한 짧은 대기
            print("정리 완료 대기...")
            time.sleep(0.2)
            print("앱 종료 준비 완료")
        except Exception as e:
            print(f"앱 종료 처리 중 오류: {e}")
        finally:
            self.root.destroy() 