"""
마우스 자동 클릭 프로그램 진입점

프로그램 실행을 위한 메인 파일입니다.
"""
import tkinter as tk
import traceback
import sys
from src.gui.tab_based_app import TabBasedApp

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = TabBasedApp(root)
        print("[메인] 애플리케이션 초기화 완료")
        root.mainloop()
    except Exception as e:
        print(f"[오류] 프로그램 실행 중 예외 발생: {e}")
        traceback.print_exc()
        sys.exit(1) 