"""
키보드 연타 탭

키보드 연속 입력 기능을 제공하는 탭 UI 구현
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
import keyboard

from src.core.keyboard_control import keyboard_controller

class KeyboardTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding=15)
        
        # 초기 변수 설정
        self.active_keys = set()  # 활성화된 키
        self.is_repeating = False  # 키 반복 중 여부
        self.is_processing_hotkey = False  # 핫키 처리 중 플래그
        self.key_buttons = {}  # 가상 키보드 버튼 저장
        self.repeat_speed = 0.1  # 기본 반복 속도 (초)
        
        # UI 구성
        self._create_widgets()
    
    def _create_widgets(self):
        # 탭 제목
        title_label = ttk.Label(
            self.frame, 
            text="키보드 연타", 
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 15))
        
        # 가상 키보드
        keyboard_frame = ttk.LabelFrame(self.frame, text="가상 키보드", padding=10)
        keyboard_frame.pack(fill=tk.X, pady=8)
        
        self._create_virtual_keyboard(keyboard_frame)
        
        # 반복 속도 설정
        speed_frame = ttk.LabelFrame(self.frame, text="반복 속도 설정", padding=10)
        speed_frame.pack(fill=tk.X, pady=8)
        
        speed_control = ttk.Frame(speed_frame)
        speed_control.pack(fill=tk.X, pady=5)
        
        ttk.Button(speed_control, text="-", width=4, 
                  command=self._decrease_speed).pack(side=tk.LEFT, padx=5)
        
        self.speed_label = ttk.Label(speed_control, text=f"{self.repeat_speed:.1f}초", font=("맑은 고딕", 12))
        self.speed_label.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        ttk.Button(speed_control, text="+", width=4,
                  command=self._increase_speed).pack(side=tk.RIGHT, padx=5)
        
        # 상태 표시
        status_frame = ttk.LabelFrame(self.frame, text="상태", padding=10)
        status_frame.pack(fill=tk.X, pady=8)
        
        self.key_repeat_status = ttk.Label(
            status_frame, 
            text="준비됨", 
            style="Green.TLabel"
        )
        self.key_repeat_status.pack(pady=5)
        
        # 시작/중지 버튼
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, pady=15)
        
        self.key_repeat_btn = ttk.Button(
            control_frame,
            text="키보드 연타 시작 (F7)",
            style="Large.TButton",
            command=self.toggle_key_repeat
        )
        self.key_repeat_btn.pack(fill=tk.X, ipady=10)
        
        # 키 테스트 영역
        test_frame = ttk.LabelFrame(self.frame, text="키 테스트", padding=10)
        test_frame.pack(fill=tk.X, pady=8)
        
        test_entry_frame = ttk.Frame(test_frame)
        test_entry_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(test_entry_frame, text="테스트할 키:").pack(side=tk.LEFT, padx=5)
        
        self.test_key_entry = ttk.Entry(test_entry_frame, width=10)
        self.test_key_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        ttk.Button(test_entry_frame, text="테스트", 
                  command=self._test_key_press).pack(side=tk.RIGHT, padx=5)
        
        # 단축키 안내
        hotkey_frame = ttk.LabelFrame(self.frame, text="단축키 안내", padding=10)
        hotkey_frame.pack(fill=tk.X, pady=8)
        
        ttk.Label(hotkey_frame, text="F7: 키보드 연타 시작/중지", font=("맑은 고딕", 11)).pack(anchor=tk.W, pady=2)
        ttk.Label(hotkey_frame, text="F8: 모든 키 초기화", font=("맑은 고딕", 11)).pack(anchor=tk.W, pady=2)
    
    def _create_virtual_keyboard(self, parent):
        """가상 키보드 UI 생성"""
        # 키보드 레이아웃
        layouts = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
            ["z", "x", "c", "v", "b", "n", "m"]
        ]
        
        # 키보드 프레임 생성
        keyboard_container = ttk.Frame(parent)
        keyboard_container.pack(pady=5)
        
        # 각 행의 키 생성
        for row_idx, row in enumerate(layouts):
            row_frame = ttk.Frame(keyboard_container)
            row_frame.pack(pady=2)
            
            # 첫 번째 행 외에는 약간의 오프셋 적용
            offset = 0
            if row_idx == 2:  # a, s, d, ... 행
                offset = 10
            elif row_idx == 3:  # z, x, c, ... 행
                offset = 25
            
            # 오프셋 적용을 위한 더미 프레임
            if offset > 0:
                ttk.Frame(row_frame, width=offset).pack(side=tk.LEFT)
            
            # 해당 행의 키 버튼 생성
            for key in row:
                key_btn = ttk.Button(
                    row_frame, 
                    text=key.upper(),
                    width=4,
                    command=lambda k=key: self.toggle_key_active(k)
                )
                key_btn.pack(side=tk.LEFT, padx=1, pady=1)
                self.key_buttons[key] = key_btn
                
                # 툴팁 추가
                self._add_key_tooltip(key_btn, f"'{key.upper()}' 키 활성화/비활성화")
    
    def _add_key_tooltip(self, widget, text):
        """위젯에 툴팁 추가"""
        tooltip_label = None
        
        def enter(event):
            nonlocal tooltip_label
            # 툴팁 위치 계산
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # 툴팁 생성
            tooltip_label = tk.Toplevel(widget)
            tooltip_label.wm_overrideredirect(True)  # 창 테두리 제거
            tooltip_label.wm_geometry(f"+{x}+{y}")  # 위치 설정
            
            # 프레임에 라벨 추가
            tooltip_frame = ttk.Frame(tooltip_label, borderwidth=1, relief="solid")
            tooltip_frame.pack(ipadx=3, ipady=2)
            
            ttk.Label(
                tooltip_frame, 
                text=text,
                justify=tk.LEFT,
                font=("맑은 고딕", 10),
                background="#FFFFD0",
                relief="solid",
                borderwidth=0
            ).pack()
        
        def leave(event):
            nonlocal tooltip_label
            if tooltip_label:
                tooltip_label.destroy()
                tooltip_label = None
        
        # 이벤트 바인딩
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def toggle_key_active(self, key):
        """키 활성화/비활성화 토글"""
        if key in self.active_keys:
            # 이미 활성화된 키 비활성화
            self.active_keys.remove(key)
            self.key_buttons[key].state(["!pressed"])
        else:
            # 키 활성화
            self.active_keys.add(key)
            self.key_buttons[key].state(["pressed"])
        
        # 키 상태 업데이트
        self._update_button_styles()
    
    def toggle_key_repeat(self):
        """키 반복 준비 상태 토글"""
        # 반복 모드 토글
        self.is_repeating = not self.is_repeating
        
        if self.is_repeating:
            # 활성화된 키가 없으면 알림
            if not self.active_keys:
                print("키보드 연타 준비 실패: 활성화된 키가 없습니다.")
                from tkinter import messagebox
                messagebox.showinfo("알림", "키보드 연타를 시작하려면 먼저 키를 활성화해주세요.")
                self.is_repeating = False
                return
                
            print(f"키보드 연타 모드 활성화: {list(self.active_keys)}")
            self.key_repeat_btn.config(text="키보드 연타 모드 중지 (F7)")
            self.key_repeat_status.config(text="준비됨 - 키 입력 대기 중", style="Red.TLabel")
            
            # 키 이벤트 핸들러 등록
            for key in self.active_keys:
                try:
                    # 키 눌림/해제 이벤트 핸들러 등록
                    keyboard.on_press_key(key, lambda e, k=key: self._on_key_press(k), suppress=False)
                    keyboard.on_release_key(key, lambda e, k=key: self._on_key_release(k), suppress=False)
                    print(f"키 '{key}' 이벤트 핸들러 등록됨")
                except Exception as e:
                    print(f"키 '{key}' 이벤트 핸들러 등록 실패: {e}")
        else:
            print("키보드 연타 모드 비활성화")
            self.key_repeat_btn.config(text="키보드 연타 모드 시작 (F7)")
            self.key_repeat_status.config(text="준비됨", style="Green.TLabel")
            
            # 모든 키 반복 중지 및 이벤트 핸들러 제거
            keyboard_controller.stop_all_repeats()
            
            # 이벤트 핸들러 제거
            for key in self.active_keys:
                try:
                    keyboard.unhook_key(key)
                except:
                    pass
    
    def _on_key_press(self, key):
        """키 눌림 이벤트 핸들러"""
        if not self.is_repeating or key not in self.active_keys:
            return
            
        print(f"키 '{key}' 눌림 감지됨 - 연타 시작")
        # 키 연타 시작
        keyboard_controller.start_key_repeat(key, self.repeat_speed)
    
    def _on_key_release(self, key):
        """키 해제 이벤트 핸들러"""
        if not self.is_repeating or key not in self.active_keys:
            return
            
        print(f"키 '{key}' 해제 감지됨 - 연타 중지")
        # 키 연타 중지
        keyboard_controller.stop_key_repeat(key)
    
    def _update_button_styles(self):
        """버튼 스타일 업데이트"""
        for key, button in self.key_buttons.items():
            if key in self.active_keys:
                button.state(["pressed"])
            else:
                button.state(["!pressed"])
    
    def _increase_speed(self):
        """반복 속도 증가 (간격 감소)"""
        self.repeat_speed = round(max(self.repeat_speed - 0.05, 0.05), 2)
        self.speed_label.config(text=f"{self.repeat_speed:.2f}초")
        self._update_repeat_speed()
    
    def _decrease_speed(self):
        """반복 속도 감소 (간격 증가)"""
        self.repeat_speed = round(min(self.repeat_speed + 0.05, 1.0), 2)
        self.speed_label.config(text=f"{self.repeat_speed:.2f}초")
        self._update_repeat_speed()
    
    def _update_repeat_speed(self):
        """반복 중인 키 속도 업데이트"""
        if self.is_repeating:
            for key in self.active_keys:
                keyboard_controller.update_repeat_speed(key, self.repeat_speed)
    
    def _test_key_press(self):
        """키 테스트"""
        key = self.test_key_entry.get().strip().lower()
        if not key:
            return
            
        try:
            # 키 누름 (0.1초 후 해제)
            keyboard.press(key)
            self.frame.after(100, lambda: keyboard.release(key))
        except Exception as e:
            print(f"키 테스트 중 오류: {e}")
    
    def safe_toggle_key_repeat(self):
        """스레드 안전한 키 반복 토글"""
        if self.is_processing_hotkey:
            return
            
        self.is_processing_hotkey = True
        self.frame.after(0, self._process_toggle_key_repeat)
    
    def _process_toggle_key_repeat(self):
        """키 반복 토글 처리 (메인 스레드)"""
        try:
            self.toggle_key_repeat()
        finally:
            self.is_processing_hotkey = False
    
    def safe_reset_all_keys(self):
        """스레드 안전한 모든 키 초기화"""
        if self.is_processing_hotkey:
            return
            
        self.is_processing_hotkey = True
        self.frame.after(0, self._process_reset_all_keys)
    
    def _process_reset_all_keys(self):
        """모든 키 초기화 처리 (메인 스레드)"""
        try:
            # 이전에 활성화된 모든 키 비활성화
            for key in list(self.active_keys):
                self.toggle_key_active(key)
                
            # 키보드 컨트롤러 초기화
            keyboard_controller.reset_all_states()
            
            # 반복 중이었다면 상태 업데이트
            if self.is_repeating:
                self.is_repeating = False
                self.key_repeat_btn.config(text="키보드 연타 시작 (F7)")
                self.key_repeat_status.config(text="준비됨", style="Green.TLabel")
        finally:
            self.is_processing_hotkey = False
    
    def setup_hotkeys(self):
        """전역 단축키 설정"""
        try:
            # F7: 키보드 연타 시작/중지
            keyboard.add_hotkey('f7', self.safe_toggle_key_repeat, suppress=True)
            
            # F8: 모든 키 초기화
            keyboard.add_hotkey('f8', self.safe_reset_all_keys, suppress=True)
            
            print("키보드 연타 탭 단축키 설정 완료")
        except Exception as e:
            print(f"단축키 설정 중 오류: {e}")
    
    def cleanup(self):
        """탭 정리 작업"""
        # 키 반복 중지
        if self.is_repeating:
            keyboard_controller.stop_all_repeats()
            
        # 모든 키 초기화
        keyboard_controller.reset_all_states()
            
        try:
            # 단축키 해제
            keyboard.unhook_key('f7')
            keyboard.unhook_key('f8')
        except Exception as e:
            print(f"단축키 해제 중 오류: {e}") 