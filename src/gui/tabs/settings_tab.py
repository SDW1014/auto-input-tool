"""
설정 탭

애플리케이션 설정 및 정보를 제공하는 탭 UI 구현
"""
import tkinter as tk
from tkinter import ttk
import sys
import webbrowser
import platform
import ctypes

class SettingsTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding=15)
        
        # UI 구성
        self._create_widgets()
    
    def _create_widgets(self):
        # 탭 제목
        title_label = ttk.Label(
            self.frame, 
            text="설정 및 정보", 
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 15))
        
        # 앱 정보
        info_frame = ttk.LabelFrame(self.frame, text="프로그램 정보", padding=10)
        info_frame.pack(fill=tk.X, pady=8)
        
        ttk.Label(info_frame, text="마우스 자동 클릭 & 키보드 연타 프로그램", font=("맑은 고딕", 12, "bold")).pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="버전: 1.5.0 (탭 UI 업데이트)", font=("맑은 고딕", 11)).pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="© 2024 자동화 도구 개발팀", font=("맑은 고딕", 11)).pack(anchor=tk.W, pady=2)
        
        # 시스템 정보
        system_frame = ttk.LabelFrame(self.frame, text="시스템 정보", padding=10)
        system_frame.pack(fill=tk.X, pady=8)
        
        ttk.Label(system_frame, text=f"OS: {platform.system()} {platform.release()}", font=("맑은 고딕", 11)).pack(anchor=tk.W, pady=2)
        ttk.Label(system_frame, text=f"Python: {sys.version.split()[0]}", font=("맑은 고딕", 11)).pack(anchor=tk.W, pady=2)
        
        admin_status = "O (관리자 권한)" if ctypes.windll.shell32.IsUserAnAdmin() else "X (일반 권한)"
        ttk.Label(system_frame, text=f"관리자 권한: {admin_status}", font=("맑은 고딕", 11)).pack(anchor=tk.W, pady=2)
        
        # 도움말
        help_frame = ttk.LabelFrame(self.frame, text="도움말", padding=10)
        help_frame.pack(fill=tk.X, pady=8)
        
        help_text = "• 마우스 자동 클릭: 마우스 위치에서 자동으로 클릭을 반복합니다.\n"
        help_text += "• 키보드 연타: 선택한 키를 자동으로 반복해서 입력합니다.\n"
        help_text += "• 단축키를 사용하여 빠르게 기능을 활성화/비활성화할 수 있습니다."
        
        help_label = ttk.Label(
            help_frame, 
            text=help_text,
            font=("맑은 고딕", 11),
            justify=tk.LEFT,
            wraplength=450
        )
        help_label.pack(anchor=tk.W, pady=5)
        
        # 알림 섹션
        notice_frame = ttk.LabelFrame(self.frame, text="주의사항", padding=10)
        notice_frame.pack(fill=tk.X, pady=8)
        
        notice_text = "이 프로그램은 게임이나 작업 자동화에 사용될 수 있지만, "
        notice_text += "일부 프로그램이나 게임에서는 자동화 도구 사용이 금지될 수 있습니다. "
        notice_text += "항상 해당 서비스의 이용약관을 확인하세요."
        
        notice_label = ttk.Label(
            notice_frame, 
            text=notice_text,
            font=("맑은 고딕", 11),
            justify=tk.LEFT,
            wraplength=450
        )
        notice_label.pack(anchor=tk.W, pady=5)
        
        # 개발자 정보 및 링크
        dev_frame = ttk.LabelFrame(self.frame, text="개발자 정보", padding=10)
        dev_frame.pack(fill=tk.X, pady=8)
        
        # GitHub 링크 버튼
        github_button = ttk.Button(
            dev_frame,
            text="GitHub 저장소 방문",
            command=lambda: webbrowser.open("https://github.com/")
        )
        github_button.pack(fill=tk.X, pady=5)
        
        # 피드백 이메일 버튼
        email_button = ttk.Button(
            dev_frame,
            text="이메일로 피드백 보내기",
            command=lambda: webbrowser.open("mailto:example@example.com")
        )
        email_button.pack(fill=tk.X, pady=5)
        
        # 앱 설정
        settings_frame = ttk.LabelFrame(self.frame, text="앱 설정", padding=10)
        settings_frame.pack(fill=tk.X, pady=8)
        
        # 시작 시 항상 위에 표시 체크박스
        self.topmost_var = tk.BooleanVar(value=True)
        topmost_check = ttk.Checkbutton(
            settings_frame,
            text="항상 다른 창 위에 표시",
            variable=self.topmost_var,
            command=self._toggle_topmost
        )
        topmost_check.pack(anchor=tk.W, pady=5)
    
    def _toggle_topmost(self):
        """항상 위에 표시 토글"""
        # 앱의 루트 창에 속성 적용
        if self.parent.master:
            self.parent.master.attributes('-topmost', self.topmost_var.get()) 