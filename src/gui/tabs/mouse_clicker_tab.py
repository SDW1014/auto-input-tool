"""
마우스 자동 클릭 탭

마우스 자동 클릭 기능을 제공하는 탭 UI 구현
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
import keyboard

from src.core.mouse_position import get_mouse_position
from src.core.mouse_click import click_at_position

class MouseClickerTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding=15)
        
        # 초기 변수 설정
        self.running = False  # 클릭 실행 여부
        self.click_interval = 0.1  # 클릭 간격 (초)
        self.current_x = 0  # 현재 마우스 X 좌표
        self.current_y = 0  # 현재 마우스 Y 좌표
        self.click_count = 0  # 클릭 횟수
        self.click_thread = None  # 클릭 스레드
        self.is_processing_hotkey = False  # 핫키 처리 중 플래그
        
        # UI 구성
        self._create_widgets()
    
    def _create_widgets(self):
        # 탭 제목
        title_label = ttk.Label(
            self.frame, 
            text="마우스 자동 클릭", 
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 15))
        
        # 현재 마우스 위치 표시
        position_frame = ttk.LabelFrame(self.frame, text="현재 마우스 위치", padding=10)
        position_frame.pack(fill=tk.X, pady=5)
        
        self.position_label = ttk.Label(position_frame, text="X: 0, Y: 0", font=("맑은 고딕", 12))
        self.position_label.pack(pady=5)
        
        # 클릭 간격 설정
        interval_frame = ttk.LabelFrame(self.frame, text="클릭 간격 설정", padding=10)
        interval_frame.pack(fill=tk.X, pady=8)
        
        interval_control = ttk.Frame(interval_frame)
        interval_control.pack(fill=tk.X, pady=5)
        
        decrease_btn = ttk.Button(interval_control, text="-", width=4, 
                                 command=self.decrease_interval)
        decrease_btn.pack(side=tk.LEFT, padx=5)
        
        self.interval_label = ttk.Label(interval_control, text=f"{self.click_interval:.1f}초", font=("맑은 고딕", 12))
        self.interval_label.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        increase_btn = ttk.Button(interval_control, text="+", width=4,
                                 command=self.increase_interval)
        increase_btn.pack(side=tk.RIGHT, padx=5)
        
        # 클릭 카운터
        counter_frame = ttk.LabelFrame(self.frame, text="클릭 카운터", padding=10)
        counter_frame.pack(fill=tk.X, pady=8)
        
        counter_control = ttk.Frame(counter_frame)
        counter_control.pack(fill=tk.X, pady=5)
        
        self.click_counter = ttk.Label(counter_control, text="0회", font=("맑은 고딕", 12))
        self.click_counter.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        reset_btn = ttk.Button(counter_control, text="초기화", 
                              command=self.reset_counter)
        reset_btn.pack(side=tk.RIGHT, padx=5)
        
        # 상태 표시
        status_frame = ttk.LabelFrame(self.frame, text="상태", padding=10)
        status_frame.pack(fill=tk.X, pady=8)
        
        self.status_label = ttk.Label(
            status_frame, 
            text="준비됨", 
            style="Green.TLabel"
        )
        self.status_label.pack(pady=5)
        
        # 시작/중지 버튼
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, pady=15)
        
        self.start_btn = ttk.Button(
            control_frame,
            text="자동 클릭 시작 (F6)",
            style="Large.TButton",
            command=self.toggle_clicking
        )
        self.start_btn.pack(fill=tk.X, ipady=10)
        
        # 단축키 안내
        hotkey_frame = ttk.LabelFrame(self.frame, text="단축키 안내", padding=10)
        hotkey_frame.pack(fill=tk.X, pady=8)
        
        ttk.Label(hotkey_frame, text="F6: 자동 클릭 시작/중지", font=("맑은 고딕", 11)).pack(anchor=tk.W, pady=2)
        ttk.Label(hotkey_frame, text="F9: 클릭 횟수 초기화", font=("맑은 고딕", 11)).pack(anchor=tk.W, pady=2)
    
    def update_position(self, x, y):
        """마우스 위치 업데이트"""
        self.current_x, self.current_y = x, y
        self.position_label.config(text=f"X: {x}, Y: {y}")
    
    def toggle_clicking(self):
        """자동 클릭 시작/중지"""
        self.running = not self.running
        
        if self.running:
            self.start_btn.config(text="자동 클릭 중지 (F6)")
            self.status_label.config(text="실행 중...", style="Red.TLabel")
            # 클릭 스레드 시작
            self.click_thread = threading.Thread(target=self.auto_click)
            self.click_thread.daemon = True
            self.click_thread.start()
        else:
            self.start_btn.config(text="자동 클릭 시작 (F6)")
            self.status_label.config(text="준비됨", style="Green.TLabel")
    
    def auto_click(self):
        """자동 클릭 스레드 함수"""
        while self.running:
            try:
                click_at_position(self.current_x, self.current_y)
                self.click_count += 1
                self.click_counter.config(text=f"{self.click_count}회")
                time.sleep(self.click_interval)
            except Exception as e:
                print(f"자동 클릭 중 오류: {e}")
                break
    
    def increase_interval(self):
        """클릭 간격 증가"""
        self.click_interval = round(min(self.click_interval + 0.1, 10.0), 1)
        self.interval_label.config(text=f"{self.click_interval:.1f}초")
    
    def decrease_interval(self):
        """클릭 간격 감소"""
        self.click_interval = round(max(self.click_interval - 0.1, 0.1), 1)
        self.interval_label.config(text=f"{self.click_interval:.1f}초")
    
    def reset_counter(self):
        """클릭 카운터 초기화"""
        self.click_count = 0
        self.click_counter.config(text="0회")
    
    def safe_toggle_clicking(self):
        """스레드 안전한 클릭 토글"""
        if self.is_processing_hotkey:
            return
            
        self.is_processing_hotkey = True
        self.frame.after(0, self._process_toggle_clicking)
    
    def _process_toggle_clicking(self):
        """토글 클릭 처리 (메인 스레드)"""
        try:
            self.toggle_clicking()
        finally:
            self.is_processing_hotkey = False
    
    def safe_reset_counter(self):
        """스레드 안전한 카운터 초기화"""
        if self.is_processing_hotkey:
            return
            
        self.is_processing_hotkey = True
        self.frame.after(0, self._process_reset_counter)
    
    def _process_reset_counter(self):
        """카운터 초기화 처리 (메인 스레드)"""
        try:
            self.reset_counter()
        finally:
            self.is_processing_hotkey = False
    
    def setup_hotkeys(self):
        """전역 단축키 설정"""
        try:
            # F6: 자동 클릭 시작/중지
            keyboard.add_hotkey('f6', self.safe_toggle_clicking, suppress=True)
            
            # F9: 클릭 횟수 초기화
            keyboard.add_hotkey('f9', self.safe_reset_counter, suppress=True)
            
            print("마우스 클릭 탭 단축키 설정 완료")
        except Exception as e:
            print(f"단축키 설정 중 오류: {e}")
    
    def cleanup(self):
        """탭 정리 작업"""
        # 클릭 중지
        if self.running:
            self.running = False  # 클릭 중단
            
        try:
            # 단축키 해제
            keyboard.unhook_key('f6')
            keyboard.unhook_key('f9')
        except Exception as e:
            print(f"단축키 해제 중 오류: {e}") 