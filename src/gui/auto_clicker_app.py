"""
마우스 자동 클릭기 GUI 모듈

마우스 자동 클릭기의 그래픽 사용자 인터페이스를 제공합니다.
"""
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ctypes
import keyboard  # 전역 키보드 후킹을 위한 모듈 추가

from src.core.mouse_position import get_mouse_position
from src.core.mouse_click import click_at_position
from src.core.keyboard_control import keyboard_controller
from src.utils.admin_check import is_admin, run_as_admin

class AutoClickerApp:
    def __init__(self, root):
        try:
            # 기본 윈도우 설정
            self.root = root
            self.root.title("마우스 자동 클릭기 & 키보드 연타")
            self.root.geometry("500x700")  # 창 크기 더 증가
            self.root.resizable(False, False)
            
            # 초기 변수 설정
            self.running = False  # 클릭 실행 여부
            self.click_interval = 0.1  # 클릭 간격 (초)
            self.current_x = 0  # 현재 마우스 X 좌표
            self.current_y = 0  # 현재 마우스 Y 좌표
            self.click_count = 0  # 클릭 횟수
            
            # UI 관련 변수들 초기화
            self.key_buttons = {}  # 가상 키보드 버튼 저장
            self.position_label = None  # 마우스 위치 표시 라벨
            self.interval_label = None  # 클릭 간격 표시 라벨
            self.status_label = None  # 상태 표시 라벨
            self.click_counter = None  # 클릭 카운터 표시 라벨
            self.key_repeat_btn = None  # 키보드 연속 입력 버튼
            self.key_repeat_status = None  # 키보드 연속 입력 상태 라벨
            self.start_btn = None  # 마우스 클릭 시작 버튼
            self.tooltip_label = None  # 툴팁 라벨
            self.temp_message_label = None  # 임시 메시지 라벨
            self._msg_timer_id = None  # 메시지 타이머 ID
            self.debug_status = None  # 디버그 상태 라벨
            self.test_key_entry = None  # 키 테스트 입력 필드
            
            # 프로세스 관련 플래그
            self.is_processing_hotkey = False  # 핫키 처리 중 플래그
            
            # 창을 항상 맨 위에 표시
            self.root.attributes('-topmost', True)
            
            # 관리자 권한 확인
            if not is_admin():
                messagebox.showwarning("권한 필요", "이 프로그램은 관리자 권한이 필요합니다.\n프로그램을 다시 시작합니다.")
                run_as_admin()
                return
            
            # 스타일 설정
            self._setup_styles()
            
            # GUI 구성
            self.create_widgets()
            
            # 타이머 시작
            self._start_timers()
            
            # 키보드 이벤트 설정
            self._setup_keyboard_hooks()
            
            # 앱이 종료될 때 단축키 해제를 위한 프로토콜 설정
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            print("GUI: 애플리케이션 초기화 완료")
            
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
        except Exception as e:
            print(f"GUI: 스타일 설정 중 오류: {e}")
    
    def _start_timers(self):
        """애플리케이션 타이머 시작"""
        try:
            # 마우스 위치 추적 타이머
            self.track_mouse_position()
            
            # 활성 키 갱신 타이머
            self.update_active_keys_timer()
        except Exception as e:
            print(f"GUI: 타이머 시작 중 오류: {e}")
    
    def on_closing(self):
        """앱 종료 시 단축키 해제 및 정리"""
        try:
            print("앱 종료 요청됨 - 정리 시작...")
            
            # 모든 키보드 후킹 해제 시도
            try:
                print("키보드 후킹 해제 중...")
                keyboard.unhook_all()  # 모든 단축키 해제
            except Exception as e:
                print(f"키보드 후킹 해제 중 오류: {e}")
                
            # 클릭 중지
            if self.running:
                print("자동 클릭 중지 중...")
                self.running = False  # 클릭 중단
                
            # 모든 키 반복 중지 시도
            try:
                print("키 반복 중지 중...")
                # 키보드 모드 비활성화
                keyboard_controller.reset_all_states()  # 전체 초기화로 변경
                
                # 추가로 모든 키 직접 해제
                for key in "abcdefghijklmnopqrstuvwxyz0123456789":
                    try:
                        keyboard.release(key)
                    except:
                        pass
            except Exception as e:
                print(f"키 반복 중지 중 오류: {e}")
                
            # 스레드 종료를 위한 짧은 대기
            print("정리 완료 대기...")
            time.sleep(0.2)
            print("앱 종료 준비 완료")
        except Exception as e:
            print(f"앱 종료 처리 중 오류: {e}")
        finally:
            self.root.destroy()
    
    def create_widgets(self):
        # 스크롤 가능한 캔버스 생성
        main_canvas = tk.Canvas(self.root)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=main_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 캔버스와 스크롤바 연결
        main_canvas.configure(yscrollcommand=scrollbar.set)
        main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        
        # 메인 프레임 생성
        main_frame = ttk.Frame(main_canvas, padding=15)
        main_canvas.create_window((0, 0), window=main_frame, anchor="nw", width=485)
        
        # 앱 제목
        title_label = ttk.Label(
            main_frame, 
            text="마우스 자동 클릭 & 키보드 연타 프로그램", 
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 15))
        
        # 현재 마우스 위치 표시
        position_frame = ttk.LabelFrame(main_frame, text="현재 마우스 위치", padding=10)
        position_frame.pack(fill=tk.X, pady=5)
        
        self.position_label = ttk.Label(position_frame, text="X: 0, Y: 0", font=("맑은 고딕", 12))
        self.position_label.pack(pady=5)
        
        # 클릭 간격 설정
        interval_frame = ttk.LabelFrame(main_frame, text="클릭 간격 설정", padding=10)
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
        
        # 상태 표시
        status_frame = ttk.LabelFrame(main_frame, text="작동 상태", padding=10)
        status_frame.pack(fill=tk.X, pady=8)
        
        self.status_label = ttk.Label(status_frame, text="정지됨", style="Red.TLabel", font=("맑은 고딕", 12))
        self.status_label.pack(pady=5)
        
        self.click_counter = ttk.Label(status_frame, text="클릭 횟수: 0", font=("맑은 고딕", 12))
        self.click_counter.pack(pady=5)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # 버튼 생성
        self.start_btn = ttk.Button(button_frame, text="마우스 자동 클릭 시작", 
                                   command=self.toggle_clicking,
                                   style="Large.TButton")
        self.start_btn.pack(fill=tk.X, pady=3, ipady=5)  # 버튼 높이 늘림
        
        # 가상 키보드 UI - 먼저 배치
        # 키보드 연속 입력 상태 프레임
        key_repeat_frame = ttk.LabelFrame(main_frame, text="키보드 연속 입력", padding=10)
        key_repeat_frame.pack(fill=tk.X, pady=8)
        
        key_status_frame = ttk.Frame(key_repeat_frame)
        key_status_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(key_status_frame, text="상태:", font=("맑은 고딕", 12)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.key_repeat_status = ttk.Label(
            key_status_frame, 
            text="비활성화", 
            style="Red.TLabel",
            font=("맑은 고딕", 14, "bold")
        )
        self.key_repeat_status.pack(side=tk.LEFT)
        
        # 반복 속도 설정 프레임 추가
        speed_frame = ttk.Frame(key_repeat_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="반복 속도:", font=("맑은 고딕", 11)).pack(side=tk.LEFT, padx=(0, 10))
        
        # 속도 버튼 그룹
        speeds = [("느림", 1), ("중간", 2), ("빠름", 3), ("매우 빠름", 4)]
        self.speed_buttons = []
        self.speed_var = tk.IntVar(value=3)  # 기본값: 빠름
        
        for text, value in speeds:
            btn = ttk.Radiobutton(
                speed_frame, 
                text=text,
                variable=self.speed_var,
                value=value,
                command=self._update_repeat_speed
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.speed_buttons.append(btn)
        
        # 초기 속도 설정
        keyboard_controller.set_repeat_speed(self.speed_var.get())
        
        self.key_repeat_btn = ttk.Button(key_repeat_frame, text="키보드 연속 입력 활성화 (F7)",
                                       command=self.toggle_key_repeat,
                                       style="Large.TButton")
        self.key_repeat_btn.pack(fill=tk.X, pady=5, ipady=5)  # 버튼 높이 늘림

        # 도움말 텍스트 - 키보드 연속 입력에 대한 안내
        key_help_frame = ttk.Frame(key_repeat_frame, padding=5)
        key_help_frame.pack(fill=tk.X, pady=5)
        
        key_help_label = ttk.Label(
            key_help_frame, 
            text="1) 아래에서 사용할 키를 선택하세요 (녹색으로 표시)",
            font=("맑은 고딕", 11, "bold"), 
            foreground="#555555"
        )
        key_help_label.pack(pady=2, anchor="w")
        
        key_help_label2 = ttk.Label(
            key_help_frame, 
            text="2) F7 키로 키보드 모드를 활성화하세요",
            font=("맑은 고딕", 11, "bold"), 
            foreground="#008800"
        )
        key_help_label2.pack(pady=2, anchor="w")
        
        key_help_label3 = ttk.Label(
            key_help_frame, 
            text="3) 실제 키보드에서 해당 키를 누르고 있는 동안 연속 입력됩니다",
            font=("맑은 고딕", 11, "bold"), 
            foreground="#000088"
        )
        key_help_label3.pack(pady=2, anchor="w")
        
        key_help_label4 = ttk.Label(
            key_help_frame, 
            text="4) 키를 떼면 연속 입력이 중단됩니다",
            font=("맑은 고딕", 11, "bold"), 
            foreground="#880000"
        )
        key_help_label4.pack(pady=2, anchor="w")
        
        # 가상 키보드 UI
        keyboard_frame = ttk.LabelFrame(
            main_frame, 
            text="가상 키보드", 
            padding=15
        )
        keyboard_frame.pack(fill=tk.X, pady=15)
        
        # 가상 키보드 구성
        self.create_virtual_keyboard(keyboard_frame)
        
        # 키보드 단축키 안내
        shortcuts_frame = ttk.LabelFrame(main_frame, text="키보드 단축키 (전역)", padding=10)
        shortcuts_frame.pack(fill=tk.X, pady=10)
        
        shortcuts_text = "F6: 마우스 클릭 시작/중지\nF7: 키보드 연속 입력 활성화/비활성화\nF8: 카운터 초기화"
        shortcuts_label = ttk.Label(shortcuts_frame, text=shortcuts_text, font=("맑은 고딕", 11))
        shortcuts_label.pack(pady=5)
        
        # 디버깅 영역 추가
        debug_frame = ttk.LabelFrame(main_frame, text="디버깅 도구", padding=10)
        debug_frame.pack(fill=tk.X, pady=5)
        
        debug_buttons = ttk.Frame(debug_frame)
        debug_buttons.pack(fill=tk.X, pady=5)
        
        # 상태 확인 버튼
        status_btn = ttk.Button(debug_buttons, text="키보드 상태 확인",
                               command=self._check_keyboard_status)
        status_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # 강제 초기화 버튼
        reset_keys_btn = ttk.Button(debug_buttons, text="키 상태 강제 초기화",
                                   command=self._force_reset_keys)
        reset_keys_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)
        
        # 추가 디버깅 버튼 행
        debug_buttons2 = ttk.Frame(debug_frame)
        debug_buttons2.pack(fill=tk.X, pady=5)
        
        # 모든 키 해제 버튼
        release_all_btn = ttk.Button(debug_buttons2, text="모든 키 해제",
                                    command=self._release_all_keys)
        release_all_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # 전체 상태 초기화 버튼
        reset_all_btn = ttk.Button(debug_buttons2, text="전체 상태 초기화",
                                  command=self._reset_all_states)
        reset_all_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)
        
        # 상태 표시 영역
        self.debug_status = ttk.Label(debug_frame, text="", font=("맑은 고딕", 9))
        self.debug_status.pack(fill=tk.X, pady=5)
        
        # 기타 기능 버튼
        reset_btn = ttk.Button(main_frame, text="카운터 초기화",
                              command=self.reset_counter)
        reset_btn.pack(fill=tk.X, pady=5)
    
    def create_virtual_keyboard(self, parent):
        """가상 키보드 UI 생성"""
        # 키보드 레이아웃 정의
        keyboard_layout = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm']
        ]
        
        # 키보드 타이틀 라벨 추가
        keyboard_title = ttk.Label(
            parent, 
            text="클릭하여 사용할 키를 선택하세요 (녹색 = 활성화)", 
            font=("맑은 고딕", 10, "bold"),
            foreground="#444444"
        )
        keyboard_title.pack(pady=(0, 5), anchor="w")
        
        # 가상 키보드 테스트 버튼 추가
        keyboard_test_frame = ttk.Frame(parent)
        keyboard_test_frame.pack(fill=tk.X, pady=2)
        
        test_label = ttk.Label(
            keyboard_test_frame, 
            text="키 직접 테스트:", 
            font=("맑은 고딕", 9)
        )
        test_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.test_key_entry = ttk.Entry(keyboard_test_frame, width=5, font=("맑은 고딕", 9))
        self.test_key_entry.pack(side=tk.LEFT, padx=5)
        self.test_key_entry.insert(0, "a")
        
        test_key_btn = ttk.Button(
            keyboard_test_frame, 
            text="키 입력 테스트", 
            command=self._test_key_press,
            width=15
        )
        test_key_btn.pack(side=tk.LEFT, padx=5)
        
        # 가상 키보드 컨테이너 (테두리를 위한 프레임)
        keyboard_container = tk.Frame(parent, borderwidth=2, relief=tk.RAISED, bg="#dddddd", padx=3, pady=3)
        keyboard_container.pack(fill=tk.X, padx=5, pady=5)
        
        # 행별로 키보드 버튼 생성
        for row_idx, row in enumerate(keyboard_layout):
            row_frame = tk.Frame(keyboard_container, bg="#dddddd")
            row_frame.pack(fill=tk.X, pady=2)
            
            # 행에 따른 오프셋 조정 (키보드 모양 유지를 위해)
            if row_idx == 1:
                offset = 10
            elif row_idx == 2:
                offset = 18
            elif row_idx == 3:
                offset = 28
            else:
                offset = 0
                
            # 오프셋 적용
            if offset > 0:
                spacer = tk.Frame(row_frame, width=offset, bg="#dddddd")
                spacer.pack(side=tk.LEFT)
            
            # 버튼 생성
            for key in row:
                # 일반 스타일의 버튼 생성
                key_btn = tk.Button(
                    row_frame, 
                    text=key.upper(), 
                    width=3,  # 버튼 가로 크기 줄임
                    height=1,  # 버튼 세로 크기 줄임
                    font=("맑은 고딕", 11, "bold"),  # 폰트 크기 조정
                    relief=tk.RAISED,
                    bd=2,
                    bg="#f0f0f0",
                    activebackground="#e0e0e0",
                    cursor="hand2",  # 마우스 커서 변경
                    command=lambda k=key: self.toggle_key_active(k)
                )
                key_btn.pack(side=tk.LEFT, padx=2, pady=2)  # 간격 줄임
                
                # 버튼 객체 저장
                self.key_buttons[key] = key_btn
                
                # 키 버튼에 툴팁 힌트 추가
                self._add_key_tooltip(key_btn, f"'{key.upper()}' 키 활성화/비활성화")
    
    def _add_key_tooltip(self, widget, text):
        """위젯에 마우스 오버 툴팁 추가"""
        def enter(event):
            try:
                # 툴팁 생성
                if not hasattr(self, 'tooltip_label') or not self.tooltip_label:
                    self.tooltip_label = ttk.Label(
                        self.root,
                        text=text,
                        background="#ffffcc",
                        relief=tk.SOLID,
                        borderwidth=1,
                        font=("맑은 고딕", 9),
                        padding=2
                    )
                else:
                    self.tooltip_label.config(text=text)
                
                # 툴팁 위치 계산 및 표시
                x, y, _, _ = widget.bbox("insert")
                x += widget.winfo_rootx() + 25
                y += widget.winfo_rooty() + 20
                self.tooltip_label.place(x=x, y=y)
            except Exception as e:
                print(f"툴팁 표시 오류: {e}")
        
        def leave(event):
            try:
                # 툴팁 숨기기
                if hasattr(self, 'tooltip_label') and self.tooltip_label:
                    self.tooltip_label.place_forget()
            except Exception as e:
                print(f"툴팁 숨기기 오류: {e}")
        
        # 이벤트 바인딩
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def toggle_key_active(self, key):
        """가상 키보드 버튼 클릭 시 키 활성화 상태 전환"""
        # 키 상태 토글
        is_active = keyboard_controller.toggle_key(key)
        
        # 버튼 스타일 업데이트
        if is_active:
            self.key_buttons[key].config(bg="#a0ffa0", relief=tk.SUNKEN)  # 활성화: 녹색
            
            # 활성화시 테스트 입력창에 해당 키 설정
            self.test_key_entry.delete(0, tk.END)
            self.test_key_entry.insert(0, key)
            
            # 모드가 이미 활성화되어 있다면 자동으로 테스트 실행
            if keyboard_controller.is_mode_active():
                print(f"GUI: 키 '{key}' 활성화 후 자동 테스트 시도")
                self.root.after(100, self._test_key_press)
        else:
            self.key_buttons[key].config(bg="#f0f0f0", relief=tk.RAISED)  # 비활성화: 기본 색상
        
        # 활성화 상태일 때 도움말 설명
        if is_active:
            self.show_temp_message(f"키 '{key.upper()}' 활성화: F7로 모드 활성화 후 실제 키보드의 '{key.upper()}' 키를 누르세요", 3000)
        else:
            self.show_temp_message(f"키 '{key.upper()}' 비활성화", 2000)
    
    def show_temp_message(self, message, duration=2000):
        """임시 메시지를 표시하고 일정 시간 후 삭제"""
        try:
            # 이전 메시지 타이머 취소
            if hasattr(self, '_msg_timer_id') and self._msg_timer_id:
                self.root.after_cancel(self._msg_timer_id)
                
            # 메시지 레이블이 없으면 생성
            if not hasattr(self, 'temp_message_label') or not self.temp_message_label:
                self.temp_message_label = ttk.Label(
                    self.root, 
                    text=message,
                    foreground="blue",
                    font=("맑은 고딕", 10),
                    anchor="center"
                )
                self.temp_message_label.place(relx=0.5, rely=0.97, anchor="center")
            else:
                # 기존 메시지 업데이트
                self.temp_message_label.config(text=message)
                self.temp_message_label.place(relx=0.5, rely=0.97, anchor="center")
                
            # 타이머 설정
            self._msg_timer_id = self.root.after(duration, self._hide_temp_message)
        except Exception as e:
            print(f"임시 메시지 표시 중 오류: {e}")
    
    def _hide_temp_message(self):
        """임시 메시지 숨기기"""
        try:
            if hasattr(self, 'temp_message_label') and self.temp_message_label:
                self.temp_message_label.place_forget()
            self._msg_timer_id = None
        except Exception as e:
            print(f"임시 메시지 숨기기 중 오류: {e}")
    
    def update_key_button_styles(self):
        """활성화된 키에 따라 버튼 스타일 업데이트"""
        try:
            # 새로운 컨트롤러 API 사용
            enabled_keys = keyboard_controller.get_enabled_keys()
            
            for key, button in self.key_buttons.items():
                if key in enabled_keys:
                    is_pressed = keyboard_controller.is_key_pressed(key)
                    is_repeating = keyboard_controller.is_key_repeating(key)
                    
                    if is_pressed and is_repeating:
                        # 현재 누르고 있고 반복 중인 키 - 파란색
                        button.config(bg="#80c0ff", relief=tk.SUNKEN, fg="black", font=("맑은 고딕", 11, "bold"))
                    else:
                        # 활성화되었지만 누르고 있지 않은 키 - 녹색
                        button.config(bg="#a0ffa0", relief=tk.SUNKEN, fg="black", font=("맑은 고딕", 11, "normal"))
                else:
                    # 비활성화된 키 - 기본 색상
                    button.config(bg="#f0f0f0", relief=tk.RAISED, fg="black", font=("맑은 고딕", 11, "normal"))
            
            # GUI 업데이트를 강제로 처리
            self.root.update_idletasks()
        except Exception as e:
            print(f"GUI: 버튼 스타일 업데이트 중 오류: {e}")
            import traceback
            traceback.print_exc()
        
    def track_mouse_position(self):
        """마우스 위치 업데이트"""
        try:
            x, y = get_mouse_position()
            self.current_x, self.current_y = x, y
            self.position_label.config(text=f"X: {x}, Y: {y}")
        except Exception as e:
            print(f"마우스 위치 추적 오류: {e}")
        
        # 100ms마다 업데이트
        self.root.after(100, self.track_mouse_position)
    
    def toggle_clicking(self):
        """클릭 시작/중지 전환"""
        self.running = not self.running
        
        if self.running:
            self.start_btn.config(text="마우스 자동 클릭 중지")
            self.status_label.config(text="작동 중", style="Green.TLabel")
            # 클릭 스레드 시작
            self.click_thread = threading.Thread(target=self.auto_click)
            self.click_thread.daemon = True
            self.click_thread.start()
        else:
            self.start_btn.config(text="마우스 자동 클릭 시작")
            self.status_label.config(text="정지됨", style="Red.TLabel")
    
    def toggle_key_repeat(self):
        """키보드 연속 입력 모드 활성화/비활성화 (버튼에서 호출)"""
        try:
            if not self.is_processing_hotkey:
                print("DEBUG: 키보드 모드 토글 버튼 클릭됨")
                self.is_processing_hotkey = True
                
                # 먼저 UI 상태 업데이트 (사용자 피드백)
                self.key_repeat_status.config(text="처리 중...", foreground="orange")
                self.key_repeat_btn.config(state="disabled")
                self.root.update_idletasks()
                
                # 지연 처리로 변경 - 직접 호출하지 않고 이벤트 큐에 넣기
                print("DEBUG: 키보드 모드 토글 - 이벤트 큐에 처리 함수 등록")
                self.root.after(10, self._process_toggle_key_repeat)
        except Exception as e:
            print(f"DEBUG: 토글 버튼 처리 중 오류: {e}")
            import traceback
            traceback.print_exc()
            self.is_processing_hotkey = False
            
            # 오류 발생 시 UI 복원
            self.key_repeat_status.config(text="오류", foreground="red")
            self.key_repeat_btn.config(state="normal")

    def _process_toggle_key_repeat(self):
        """토글 처리"""
        try:
            # 로그 출력 강화
            print("DEBUG: 키보드 모드 토글 처리 시작")
            
            # 현재 상태 확인
            current_state = keyboard_controller.is_mode_active()
            print(f"DEBUG: 현재 모드 상태: {current_state}")
            
            # 안정적인 처리를 위해 키보드 훅 일시 중지 시도
            try:
                print("DEBUG: 키보드 훅 일시 중지")
                keyboard.unhook_all()
            except Exception as e:
                print(f"DEBUG: 키보드 훅 중지 오류: {e}")
            
            # 모든 키 강제 해제 
            try:
                print("DEBUG: 모드 전환 전 모든 키 해제 시도")
                keyboard_controller.reset_all_states()
            except Exception as e:
                print(f"DEBUG: 키 해제 중 오류: {e}")
            
            # 토글 명령 실행
            try:
                print(f"DEBUG: 모드 토글 시도 - 현재 상태: {current_state} -> {not current_state}")
                if current_state:
                    # 비활성화
                    result = keyboard_controller.enable_mode(False)
                    print(f"DEBUG: 모드 비활성화 결과: {result}")
                else:
                    # 활성화
                    result = keyboard_controller.enable_mode(True)
                    print(f"DEBUG: 모드 활성화 결과: {result}")
                    
                # 현재 상태 다시 확인
                new_state = keyboard_controller.is_mode_active()
                print(f"DEBUG: 모드 토글 후 상태: {new_state}")
            except Exception as e:
                print(f"DEBUG: 모드 토글 실행 오류: {e}")
                import traceback
                traceback.print_exc()
                
                # 오류 발생 시 모드는 비활성화 상태로 강제 설정
                keyboard_controller.enable_mode(False)
                new_state = False
            
            # 키보드 훅 다시 설정
            try:
                print("DEBUG: 키보드 훅 재설정")
                self._setup_keyboard_hooks()
            except Exception as e:
                print(f"DEBUG: 키보드 훅 재설정 오류: {e}")
            
            # UI 업데이트
            self.update_repeat_status(new_state)
            self.update_key_button_styles()
            
            # 버튼 상태 복원
            self.key_repeat_btn.config(state="normal")
            
            # 상태 메시지 표시
            if new_state:
                self.show_temp_message("키보드 연속 입력 모드가 활성화되었습니다", 3000)
            else:
                self.show_temp_message("키보드 연속 입력 모드가 비활성화되었습니다", 3000)
            
        except Exception as e:
            print(f"DEBUG: 모드 토글 처리 오류: {e}")
            import traceback
            traceback.print_exc()
            
            # 오류 발생 시 UI 복원
            self.key_repeat_status.config(text="오류", foreground="red")
            self.key_repeat_btn.config(state="normal")
            
            # 모드 강제 비활성화
            try:
                keyboard_controller.reset_all_states()
            except:
                pass
        finally:
            # 무조건 플래그 해제
            print("DEBUG: 키보드 모드 토글 처리 완료")
            self.is_processing_hotkey = False
    
    def update_repeat_status(self, active):
        """연속 입력 모드 상태 업데이트"""
        print(f"DEBUG: UI 상태 업데이트 - 모드 활성화 상태: {active}")
        if active:
            self.key_repeat_btn.config(text="키보드 연속 입력 비활성화 (F7)")
            self.key_repeat_status.config(text="활성화", style="Green.TLabel")
        else:
            self.key_repeat_btn.config(text="키보드 연속 입력 활성화 (F7)")
            self.key_repeat_status.config(text="비활성화", style="Red.TLabel")
    
    def update_active_keys_timer(self):
        """활성 키 상태 주기적 업데이트"""
        try:
            self.update_key_button_styles()
            self.root.after(200, self.update_active_keys_timer)  # 200ms마다 갱신
        except Exception as e:
            print(f"활성 키 업데이트 중 오류: {e}")
            # 오류 발생 시에도 타이머 계속 실행
            self.root.after(500, self.update_active_keys_timer)
    
    def auto_click(self):
        """자동 클릭 실행"""
        while self.running:
            try:
                click_at_position(self.current_x, self.current_y)
                self.click_count += 1
                self.click_counter.config(text=f"클릭 횟수: {self.click_count}")
                time.sleep(self.click_interval)
            except Exception as e:
                print(f"클릭 오류: {e}")
                time.sleep(0.5)
    
    def increase_interval(self):
        """클릭 간격 증가"""
        self.click_interval += 0.1
        self.interval_label.config(text=f"{self.click_interval:.1f}초")
    
    def decrease_interval(self):
        """클릭 간격 감소"""
        if self.click_interval > 0.1:
            self.click_interval -= 0.1
            self.interval_label.config(text=f"{self.click_interval:.1f}초")
    
    def reset_counter(self):
        """클릭 카운터 초기화"""
        self.click_count = 0
        self.click_counter.config(text=f"클릭 횟수: {self.click_count}") 
    
    # 안전한 단축키 핸들러들 (GUI 스레드에서 실행하도록)
    def safe_toggle_clicking(self):
        """F6 단축키를 위한 안전한 토글 처리"""
        if not self.is_processing_hotkey:
            self.is_processing_hotkey = True
            self.root.after(50, self._process_toggle_clicking)
    
    def _process_toggle_clicking(self):
        """GUI 스레드에서 실행되는 클릭 토글 처리"""
        try:
            self.toggle_clicking()
        except Exception as e:
            print(f"클릭 토글 처리 중 오류: {e}")
        finally:
            # 처리 완료 후 플래그 해제
            self.is_processing_hotkey = False
    
    def safe_reset_counter(self):
        """F8 단축키를 위한 안전한 카운터 초기화 처리"""
        if not self.is_processing_hotkey:
            self.is_processing_hotkey = True
            self.root.after(50, self._process_reset_counter)
    
    def _process_reset_counter(self):
        """GUI 스레드에서 실행되는 카운터 초기화 처리"""
        try:
            self.reset_counter()
            print("GUI: 클릭 카운터 초기화 완료")
        except Exception as e:
            print(f"카운터 초기화 중 오류: {e}")
        finally:
            # 처리 완료 후 플래그 해제
            self.is_processing_hotkey = False
    
    def safe_toggle_key_repeat(self):
        """F7 단축키를 위한 안전한 토글 처리"""
        try:
            # 이미 처리 중이면 무시
            if self.is_processing_hotkey:
                print("DEBUG: 이미 핫키 처리 중 - 무시됨")
                return
            
            # 처리 중 플래그 설정
            self.is_processing_hotkey = True
            print("DEBUG: F7 키 감지됨 - 모드 토글 시작")
            
            # 먼저 UI 상태 업데이트 (사용자 피드백)
            self.key_repeat_status.config(text="처리 중...", foreground="orange")
            self.key_repeat_btn.config(state="disabled")
            self.root.update_idletasks()  # UI 즉시 업데이트
            
            # 안전한 지연 시간 적용하여 메인 스레드에서 처리
            try:
                # 짧은 대기 후 처리 (10ms -> 100ms)
                print("DEBUG: F7 - 이벤트 큐에 토글 처리 등록")
                self.root.after(100, self._process_toggle_key_repeat)
            except Exception as e:
                print(f"DEBUG: after 메소드 호출 오류: {e}")
                # 오류 발생 시 플래그 해제
                self.is_processing_hotkey = False
                # UI 복원
                self.key_repeat_status.config(text="오류", foreground="red")
                self.key_repeat_btn.config(state="normal")
        except Exception as e:
            print(f"DEBUG: F7 단축키 처리 오류: {e}")
            import traceback
            traceback.print_exc()
            # 오류 발생 시 플래그 해제
            self.is_processing_hotkey = False
            # UI 복원
            self.key_repeat_status.config(text="오류", foreground="red")
            self.key_repeat_btn.config(state="normal")
    
    def _setup_keyboard_hooks(self):
        """키보드 이벤트 훅 설정"""
        try:
            print("DEBUG: 키보드 이벤트 설정 시작")
            
            # 기존 훅 제거 (중복 방지)
            try:
                keyboard.unhook_all()
                print("DEBUG: 기존 키보드 훅 제거됨")
            except Exception as e:
                print(f"DEBUG: 기존 키보드 훅 제거 실패: {e}")
            
            # 단축키 시도 전 짧은 대기 (안정성 위해)
            time.sleep(0.1)
            
            # F7 키는 모드 토글용 - 직접 등록 방식 사용
            try:
                keyboard.add_hotkey('f7', lambda: self.root.after(1, self.safe_toggle_key_repeat))
                print("DEBUG: F7 키 핫키 등록 성공")
            except Exception as e:
                print(f"DEBUG: F7 키 등록 실패: {e}")
                # 대체 방법으로 시도
                try:
                    keyboard.on_press_key('f7', lambda e: self.root.after(1, self.safe_toggle_key_repeat))
                    print("DEBUG: F7 키 대체 방식으로 등록 성공")
                except Exception as ex:
                    print(f"DEBUG: F7 키 대체 등록 실패: {ex}")
            
            # 기타 단축키와 키 이벤트 후킹 등록 (간소화)
            try:
                self._register_hotkey('f6', self.safe_toggle_clicking)
                self._register_hotkey('f8', self.safe_reset_counter)
                self._setup_key_hooks()
            except Exception as e:
                print(f"DEBUG: 기타 키 이벤트 설정 오류: {e}")
            
            print("DEBUG: 키보드 이벤트 설정 완료")
        except Exception as e:
            print(f"DEBUG: 키보드 이벤트 설정 중 오류: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", "키보드 이벤트 설정에 실패했습니다.")
    
    def _check_keyboard_status(self):
        """키보드 컨트롤러 상태 확인 (디버깅용)"""
        try:
            # 컨트롤러의 상태 정보 가져오기
            status = keyboard_controller.get_status_info()
            
            # 상태 정보 포맷팅
            status_text = f"모드 활성화: {status['mode_active']}\n"
            status_text += f"활성화된 키: {', '.join(status['enabled_keys']) if status['enabled_keys'] else '없음'}\n"
            status_text += f"눌린 키: {', '.join(status['pressed_keys'].keys()) if status['pressed_keys'] else '없음'}\n"
            status_text += f"활성 스레드 수: {status['active_threads']}"
            
            # UI 업데이트
            self.debug_status.config(text=status_text)
            
            # 콘솔에도 출력
            keyboard_controller.print_status()
            
            # 현재 상태에 따라 키보드 상태 UI 업데이트
            self.update_repeat_status(status['mode_active'])
            self.update_key_button_styles()
            
            # 임시 메시지
            self.show_temp_message("키보드 상태 업데이트 완료", 2000)
        except Exception as e:
            print(f"키보드 상태 확인 오류: {e}")
            self.debug_status.config(text=f"오류 발생: {str(e)}")
    
    def _force_reset_keys(self):
        """키 상태 강제 초기화 (디버깅용)"""
        try:
            print("GUI: 키 상태 강제 초기화 시작")
            
            # 기존 키보드 훅 제거
            try:
                keyboard.unhook_all()
                print("GUI: 키보드 훅 모두 제거")
            except Exception as e:
                print(f"GUI: 키보드 훅 제거 실패: {e}")
            
            # 모드 비활성화
            keyboard_controller.reset_all_states()
            
            # 키 이벤트 다시 설정
            self._setup_keyboard_hooks()
            
            # 상태 확인
            self._check_keyboard_status()
            
            # 임시 메시지
            self.show_temp_message("키 상태 강제 초기화 완료", 2000)
        except Exception as e:
            print(f"GUI: 키 상태 강제 초기화 오류: {e}")
            import traceback
            traceback.print_exc()
            self.debug_status.config(text=f"초기화 오류: {str(e)}")
    
    def _release_all_keys(self):
        """모든 키 해제 (디버깅용)"""
        try:
            print("GUI: 모든 키 해제 시작")
            
            # 사용 가능한 모든 키에 대해 해제 시도
            for key in "abcdefghijklmnopqrstuvwxyz0123456789":
                try:
                    print(f"GUI: 키 '{key}' 해제 시도")
                    keyboard.release(key)
                except:
                    pass
            
            # 키보드 컨트롤러의 눌림 상태 초기화
            for key in keyboard_controller.get_enabled_keys():
                if keyboard_controller.is_key_pressed(key):
                    # 직접 해제 이벤트 발생
                    print(f"GUI: 키 '{key}' 강제 해제 이벤트 발생")
                    keyboard_controller.handle_key_release(key)
            
            # 상태 업데이트
            self.update_key_button_styles()
            
            # 임시 메시지
            self.show_temp_message("모든 키 해제 완료", 2000)
            
            # 상태 표시
            self._check_keyboard_status()
        except Exception as e:
            print(f"GUI: 모든 키 해제 오류: {e}")
            self.debug_status.config(text=f"키 해제 오류: {str(e)}")
    
    def _reset_all_states(self):
        """전체 상태 초기화 (디버깅용)"""
        try:
            print("GUI: 전체 상태 초기화 시작")
            
            # 키보드 컨트롤러 상태 초기화
            keyboard_controller.reset_all_states()
            
            # 추가로 모든 키 직접 해제
            try:
                for key in "abcdefghijklmnopqrstuvwxyz0123456789":
                    keyboard.release(key)
                    time.sleep(0.005)  # 짧은 간격으로 해제
                
                # 잠시 대기 후 다시 해제 (안전성 강화)
                time.sleep(0.05)
                for key in "abcdefghijklmnopqrstuvwxyz0123456789":
                    keyboard.release(key)
            except Exception as e:
                print(f"GUI: 키 직접 해제 오류: {e}")
            
            # 키보드 훅 재설정
            try:
                keyboard.unhook_all()
                time.sleep(0.1)  # 잠시 대기 후 재설정
                self._setup_keyboard_hooks()
            except Exception as e:
                print(f"GUI: 키보드 훅 재설정 오류: {e}")
            
            # UI 업데이트
            self.update_repeat_status(False)
            self.update_key_button_styles()
            
            # 상태 표시
            self._check_keyboard_status()
            
            # 임시 메시지
            self.show_temp_message("전체 상태 초기화 완료", 2000)
        except Exception as e:
            print(f"GUI: 전체 상태 초기화 오류: {e}")
            self.debug_status.config(text=f"초기화 오류: {str(e)}")
            
    def _test_key_press(self):
        """입력한 키를 직접 테스트"""
        try:
            # 입력 필드에서 키 가져오기
            key = self.test_key_entry.get().strip().lower()
            
            if not key:
                self.show_temp_message("테스트할 키를 입력하세요", 2000)
                return
                
            # 첫 문자만 사용
            key = key[0]
            
            print(f"GUI: 키 '{key}' 테스트 시도")
            
            # 키가 활성화되어 있는지 확인
            if not keyboard_controller.is_key_enabled(key):
                # 자동으로 키 활성화
                keyboard_controller.enable_key(key)
                self.show_temp_message(f"키 '{key.upper()}'가 활성화되지 않아 자동으로 활성화했습니다", 2000)
                self.update_key_button_styles()
            
            # 모드가 활성화되어 있는지 확인
            if not keyboard_controller.is_mode_active():
                # 자동으로 모드 활성화
                keyboard_controller.enable_mode(True)
                self.update_repeat_status(True)
                self.show_temp_message("키보드 모드가 자동으로 활성화되었습니다", 2000)
            
            # 테스트 키 눌림 시뮬레이션 - 직접 반복 스레드 시작 시도
            print(f"GUI: 키 '{key}' 반복 시작 시도")
            if keyboard_controller.handle_key_press(key):
                print(f"GUI: 키 '{key}' 반복 시작 성공")
                self.show_temp_message(f"키 '{key.upper()}' 테스트 성공 - 반복 시작됨", 2000)
                self.update_key_button_styles()
            else:
                print(f"GUI: 키 '{key}' 반복 시작 실패")
                self.show_temp_message(f"키 '{key.upper()}' 테스트 실패", 2000)
                
            # 상태 정보 확인
            keyboard_controller.print_status()
                
        except Exception as e:
            print(f"GUI: 키 테스트 중 오류: {e}")
            self.show_temp_message(f"키 테스트 오류: {str(e)}", 2000)
    
    def _update_repeat_speed(self):
        """키 반복 속도 설정 업데이트"""
        try:
            speed = self.speed_var.get()
            keyboard_controller.set_repeat_speed(speed)
            self.show_temp_message(f"키 반복 속도가 변경되었습니다: {['느림', '중간', '빠름', '매우 빠름'][speed-1]}")
        except Exception as e:
            print(f"반복 속도 설정 오류: {e}") 

    def _register_hotkey(self, key, callback):
        """단축키 등록 헬퍼 함수"""
        try:
            keyboard.add_hotkey(key, callback)
            print(f"GUI: 단축키 '{key}' 등록 성공")
            return True
        except Exception as e:
            print(f"GUI: 단축키 '{key}' 등록 실패: {e}")
            return False 

    def _setup_key_hooks(self):
        """숫자와 알파벳 키 이벤트 후킹"""
        try:
            print("GUI: 키 이벤트 후킹 시작")
            
            # 숫자 키 (0-9)
            for i in range(10):
                key = str(i)
                self._bind_key_events(key)
                print(f"GUI: 키 '{key}' 이벤트 후킹 완료")
            
            # 알파벳 키 (a-z)
            for c in "abcdefghijklmnopqrstuvwxyz":
                self._bind_key_events(c)
                print(f"GUI: 키 '{c}' 이벤트 후킹 완료")
            
            print("GUI: 키 이벤트 후킹 완료")
        except Exception as e:
            print(f"GUI: 키 이벤트 후킹 오류: {e}")
            
    def _bind_key_events(self, key):
        """키별 이벤트 바인딩 함수 - 클로저 문제 해결"""
        try:
            # 기존에 등록된 핸들러가 있으면 제거
            try:
                keyboard.unhook_key(key)
            except:
                pass
                
            # 키 눌림 이벤트
            keyboard.on_press_key(
                key, 
                lambda e, k=key: self.root.after(1, lambda: self._on_key_event(k, True)),
                suppress=False  # 시스템 이벤트 가로채지 않음
            )
            
            # 키 해제 이벤트 - 직접 콜백에서 처리
            keyboard.on_release_key(
                key, 
                lambda e, k=key: self._on_key_release_direct(k),
                suppress=False  # 시스템 이벤트 가로채지 않음
            )
        except Exception as e:
            print(f"GUI: 키 '{key}' 이벤트 바인딩 오류: {e}")
            
    def _on_key_event(self, key, is_press):
        """통합 키 이벤트 처리 함수"""
        try:
            # 이벤트 로깅
            action = "눌림" if is_press else "해제"
            print(f"GUI: 키 '{key}' {action} 이벤트 감지")
            
            # 키가 활성화되지 않았거나 모드가 비활성화면 무시
            if not keyboard_controller.is_mode_active():
                print(f"GUI: 키 '{key}' {action} 무시 - 모드 비활성화")
                return
            
            # 활성화된 키가 아니면 무시
            if not keyboard_controller.is_key_enabled(key):
                print(f"GUI: 키 '{key}' {action} 무시 - 활성화되지 않은 키")
                return

            # 키보드 컨트롤러 상태 확인 (디버깅용)
            if is_press:
                print(f"GUI: 키 '{key}' 눌림 처리 전 상태 - 모드: {keyboard_controller.is_mode_active()}")
                
                # 이미 눌려있고 반복 중이면 무시
                if keyboard_controller.is_key_pressed(key) and keyboard_controller.is_key_repeating(key):
                    print(f"GUI: 키 '{key}' 이미 눌려있고 반복 중 - 무시")
                    return
            
            # 키 상태에 따라 처리
            result = False
            if is_press:
                # 눌림 상태가 아니거나 반복 중이 아닐 때만 처리
                if not keyboard_controller.is_key_pressed(key) or not keyboard_controller.is_key_repeating(key):
                    print(f"GUI: 키 '{key}' 반복 처리 시작 시도")
                    result = keyboard_controller.handle_key_press(key)
                    print(f"GUI: 키 '{key}' 반복 처리 결과: {result}")
                    if result:
                        print(f"GUI: 키 '{key}' 눌림 처리 성공")
                    else:
                        print(f"GUI: 키 '{key}' 눌림 처리 실패")
            else:
                # 해제는 _on_key_release_direct 함수에서 처리
                pass
            
            # 상태 변경 시 UI 업데이트 (메인 스레드에서 안전하게 실행)
            if result:
                # GUI 업데이트 시간이 너무 길어지면 키 입력에 영향을 줄 수 있으므로
                # 더 짧은 대기 시간으로 설정
                self.root.after(1, self.update_key_button_styles)
        except Exception as e:
            print(f"GUI: 키 이벤트 처리 오류 ({key}, {'눌림' if is_press else '해제'}): {e}")
            import traceback
            traceback.print_exc()
            
    def _on_key_release_direct(self, key):
        """키 해제 이벤트 직접 처리 (UI 스레드와 분리)"""
        try:
            print(f"GUI: 키 '{key}' 해제 이벤트 감지 (직접)")
            
            # 모드가 비활성화 상태면 무시
            if not keyboard_controller.is_mode_active():
                print(f"GUI: 키 '{key}' 해제 무시 - 모드 비활성화")
                return
            
            # 활성화된 키가 아니면 무시
            if not keyboard_controller.is_key_enabled(key):
                print(f"GUI: 키 '{key}' 해제 무시 - 활성화되지 않은 키")
                return
            
            # 약간 지연 후 키 해제 처리 (키가 짧게 눌렸다 떼어진 경우 처리 개선)
            time.sleep(0.01)
            
            # 키 해제 직접 처리
            print(f"GUI: 키 '{key}' 해제 처리 시도")
            result = keyboard_controller.handle_key_release(key)
            print(f"GUI: 키 '{key}' 해제 처리 결과: {result}")
            
            # 키보드에서 직접 해제 추가
            try:
                keyboard.release(key)
                time.sleep(0.01)
                keyboard.release(key)  # 두 번 해제하여 안정성 확보
                print(f"GUI: 키 '{key}' 직접 해제 완료")
            except Exception as e:
                print(f"GUI: 키 '{key}' 직접 해제 실패: {e}")
            
            # UI 업데이트는 메인 스레드에서
            if result:
                print(f"GUI: 키 '{key}' 해제 처리 성공 (직접)")
                self.root.after(1, self.update_key_button_styles)
        except Exception as e:
            print(f"GUI: 키 해제 직접 처리 오류 ({key}): {e}")
            import traceback
            traceback.print_exc()
            # 오류 발생 시에도 키 해제 시도
            try:
                keyboard.release(key)
            except:
                pass 