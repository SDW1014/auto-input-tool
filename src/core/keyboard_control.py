"""
키보드 연속 입력 모듈

키보드 키를 연속으로 입력하는 기능을 제공합니다.
"""
import time
import threading
import keyboard
import traceback

# 키보드 컨트롤러 클래스
class KeyboardController:
    def __init__(self):
        # 기본 상태
        self.mode_active = False     # 전체 모드 활성화 상태
        self.enabled_keys = set()    # 활성화된 키 목록
        self.pressed_keys = {}       # 각 키별 눌림 상태 {키: 눌림여부}
        self.active_threads = {}     # 각 키별 스레드 {키: 스레드}
        self.stop_signals = {}       # 각 키별 종료 신호 {키: 이벤트}
        
        # 키 반복 설정 - 더 안정적인 값으로 조정
        self.press_delay = 0.02      # 키 누름 지속 시간 (초)
        self.release_delay = 0.02    # 키 해제 지속 시간 (초)
        
        # 안정성 설정
        self.retry_delay = 0.05      # 키 입력 실패 시 재시도 간격 (증가)
        self.min_cycle_time = 0.01   # 최소 사이클 타임 (증가)
        self.max_retries = 2         # 최대 재시도 횟수 (감소)
        
        # 디버깅 설정
        self.debug_mode = True       # 디버깅 모드 활성화
        
        # 스레드 안전 락
        self.lock = threading.RLock()  # 재진입 가능한 락으로 변경
        
        # 키 입력 상태 확인용 타이머
        self.watchdog_timer = None
        self.watchdog_interval = 0.5  # 0.5초마다 상태 확인
        
        # 초기화 로그
        self._log("초기화 완료")
        
        # 워치독 타이머 시작
        self._start_watchdog()
    
    def _log(self, message):
        """디버깅 로그 출력"""
        if self.debug_mode:
            print(f"[KeyboardController] {message}")
    
    def _start_watchdog(self):
        """워치독 타이머 시작 - 키 상태를 주기적으로 확인하여 문제 감지 및 수정"""
        def watchdog_worker():
            while True:
                try:
                    # 모드가 활성화된 경우에만 검사
                    if self.mode_active:
                        with self.lock:
                            # 활성 스레드 확인
                            for key in list(self.active_threads.keys()):
                                # 스레드가 죽었는데 키가 눌린 상태로 남아있는지 확인
                                if not self.active_threads[key].is_alive() and self.pressed_keys.get(key, False):
                                    self._log(f"워치독: 키 {key}의 스레드가 죽었지만 눌린 상태로 감지됨, 상태 초기화")
                                    self.pressed_keys[key] = False
                                    self._clean_key_state(key)
                                
                                # 키가 눌려있지 않은데 스레드가 살아있는지 확인
                                if not self.pressed_keys.get(key, False) and key in self.active_threads:
                                    self._log(f"워치독: 키 {key}가 눌려있지 않은데 스레드가 활성 상태, 스레드 종료")
                                    self._stop_key_repeat(key)
                    
                    # 실제 키보드 상태와 내부 상태 동기화 확인
                    for key in self.enabled_keys:
                        # 키보드 라이브러리를 통해 실제 키 상태 확인
                        try:
                            is_physically_pressed = keyboard.is_pressed(key)
                            internal_state = self.pressed_keys.get(key, False)
                            
                            # 불일치 감지 및 수정
                            if not is_physically_pressed and internal_state:
                                self._log(f"워치독: 키 {key}가 실제로는 눌려있지 않은데 내부 상태는 눌림, 상태 수정")
                                self.handle_key_release(key)
                        except:
                            pass
                except Exception as e:
                    self._log(f"워치독 오류: {e}")
                
                # 일정 간격으로 실행
                time.sleep(self.watchdog_interval)
        
        # 워치독 스레드 시작
        self.watchdog_timer = threading.Thread(target=watchdog_worker, daemon=True)
        self.watchdog_timer.start()
    
    def enable_mode(self, enable=True):
        """모드 활성화/비활성화"""
        try:
            with self.lock:
                old_state = self.mode_active
                
                # 상태가 같으면 아무것도 하지 않음
                if old_state == enable:
                    return old_state
                
                # 상태 변경
                self.mode_active = enable
                self._log(f"모드 {'활성화됨' if enable else '비활성화됨'}")
                
                # 비활성화 시 모든 반복 중지 및 상태 초기화
                if not enable:
                    self._stop_all_repeats()
                    
                    # 모든 키 눌림 상태 초기화
                    active_keys = list(self.pressed_keys.keys())
                    for key in active_keys:
                        self.pressed_keys[key] = False
                        try:
                            keyboard.release(key)  # 실제 키 상태도 해제
                        except:
                            pass
                else:
                    # 활성화 시 모든 키 상태 초기화
                    active_keys = list(self.enabled_keys)
                    for key in active_keys:
                        self.pressed_keys[key] = False
                        try:
                            keyboard.release(key)  # 실제 키 상태도 해제
                        except:
                            pass
                
                return old_state
        except Exception as e:
            self._log(f"모드 {'활성화' if enable else '비활성화'} 중 오류: {e}")
            traceback.print_exc()
            return not enable  # 오류 시 요청한 상태의 반대를 반환
    
    def toggle_mode(self):
        """모드 토글"""
        current = self.is_mode_active()
        return self.enable_mode(not current)
    
    def is_mode_active(self):
        """모드 활성화 상태 확인"""
        return self.mode_active
    
    def enable_key(self, key):
        """키 활성화"""
        with self.lock:
            if key not in self.enabled_keys:
                self.enabled_keys.add(key)
                self.pressed_keys[key] = False
                self._log(f"키 '{key}' 활성화됨")
                return True
            return False
    
    def disable_key(self, key):
        """키 비활성화"""
        with self.lock:
            if key in self.enabled_keys:
                # 반복 중이면 중지
                if key in self.active_threads:
                    self._stop_key_repeat(key)
                
                # 상태 제거
                self.enabled_keys.remove(key)
                if key in self.pressed_keys:
                    del self.pressed_keys[key]
                
                # 키 상태 초기화
                try:
                    keyboard.release(key)
                except:
                    pass
                
                self._log(f"키 '{key}' 비활성화됨")
                return True
            return False
    
    def toggle_key(self, key):
        """키 활성화 상태 토글"""
        if key in self.enabled_keys:
            return not self.disable_key(key)
        else:
            return self.enable_key(key)
    
    def get_enabled_keys(self):
        """활성화된 키 목록 반환"""
        return list(self.enabled_keys)
    
    def is_key_enabled(self, key):
        """키 활성화 상태 확인"""
        return key in self.enabled_keys
    
    def is_key_pressed(self, key):
        """키 눌림 상태 확인"""
        return self.pressed_keys.get(key, False)
    
    def is_key_repeating(self, key):
        """키 반복 중인지 확인"""
        return key in self.active_threads and self.active_threads[key].is_alive()
    
    def _clean_key_state(self, key):
        """키 상태 정리 - 모든 관련 상태를 초기화"""
        try:
            # 키 해제
            keyboard.release(key)
            
            # 스레드 목록에서 제거
            if key in self.active_threads:
                del self.active_threads[key]
            
            # 종료 신호 목록에서 제거
            if key in self.stop_signals:
                del self.stop_signals[key]
                
        except Exception as e:
            self._log(f"키 상태 정리 중 오류: {e}")
    
    def handle_key_press(self, key):
        """키 눌림 처리"""
        try:
            # 모드가 비활성화면 무시
            if not self.mode_active:
                return False

            # 키가 활성화되어 있는지 확인
            if key not in self.enabled_keys:
                return False

            with self.lock:
                # 이미 눌린 상태이고 스레드가 정상 작동 중이면 무시
                if self.pressed_keys.get(key, False) and key in self.active_threads:
                    if self.active_threads[key].is_alive():
                        return False
                    else:
                        # 스레드가 죽어있으면 상태 초기화 후 재시작
                        self._log(f"키 {key}의 스레드가 죽어 있음, 상태 초기화 후 재시작")
                        self._clean_key_state(key)
                        self.pressed_keys[key] = False
                        time.sleep(0.05)  # 더 긴 지연으로 안정성 확보

                # 눌림 상태 업데이트
                self.pressed_keys[key] = True

                # 반복 시작
                success = self._start_key_repeat(key)
                if not success:
                    self._log(f"키 {key} 반복 시작 실패, 상태 초기화")
                    self.pressed_keys[key] = False
                    self._clean_key_state(key)
                return success

        except Exception as e:
            self._log(f"키 눌림 처리 중 오류: {e}")
            traceback.print_exc()
            return False

    def handle_key_release(self, key):
        """키 해제 처리"""
        try:
            # 모드가 비활성화면 무시
            if not self.mode_active:
                return False

            # 키가 활성화되어 있는지 확인
            if key not in self.enabled_keys:
                return False
            
            with self.lock:
                # 키 눌림 상태 업데이트
                self.pressed_keys[key] = False
                
                # 반복 중지
                if key in self.active_threads:
                    self._stop_key_repeat(key)
                
                # 키 상태 확실히 초기화
                self._clean_key_state(key)
                return True
            
        except Exception as e:
            self._log(f"키 해제 처리 중 오류: {e}")
            traceback.print_exc()
            return False
    
    def _start_key_repeat(self, key):
        """키 반복 시작"""
        try:
            # 이미 실행 중인 스레드가 있으면 중지
            if key in self.active_threads:
                self._stop_key_repeat(key)
                time.sleep(0.05)  # 더 긴 지연으로 안정성 확보
            
            # 종료 신호 객체 생성
            stop_signal = threading.Event()
            self.stop_signals[key] = stop_signal
            
            # 스레드 생성
            thread = threading.Thread(
                target=self._key_repeat_worker,
                args=(key, stop_signal),
                daemon=True,
                name=f"KeyRepeat_{key}"
            )
            
            # 스레드를 활성 스레드 목록에 추가
            self.active_threads[key] = thread
            
            # 스레드 시작
            thread.start()
            return True
                
        except Exception as e:
            self._log(f"키 반복 시작 실패: {e}")
            traceback.print_exc()
            return False
    
    def _stop_key_repeat(self, key):
        """키 반복 중지"""
        try:
            # 종료 신호 전송
            if key in self.stop_signals:
                self.stop_signals[key].set()
            
            # 키 해제
            try:
                keyboard.release(key)
            except:
                pass
            
            # 스레드 종료 대기 (최대 0.1초)
            if key in self.active_threads:
                try:
                    self.active_threads[key].join(0.1)
                except:
                    pass
            
            # 스레드 목록에서 제거
            if key in self.active_threads:
                del self.active_threads[key]
            if key in self.stop_signals:
                del self.stop_signals[key]
            
            return True
        except Exception as e:
            self._log(f"키 반복 중지 중 오류: {e}")
            traceback.print_exc()
            return False
    
    def _stop_all_repeats(self):
        """모든 키 반복 중지"""
        keys = list(self.active_threads.keys())
        for key in keys:
            self._stop_key_repeat(key)
    
    def _key_repeat_worker(self, key, stop_signal):
        """키 반복 작업 스레드"""
        try:
            # 재실행 방지를 위한 마지막 실행 시간 기록
            last_executed = time.time()
            retry_count = 0
            
            # 종료 신호가 올 때까지 반복
            while not stop_signal.is_set() and self.pressed_keys.get(key, False) and self.mode_active:
                # 키 상태 재확인 - 중요한 안정성 체크
                if not self.pressed_keys.get(key, False) or stop_signal.is_set() or not self.mode_active:
                    break
                
                current_time = time.time()
                # 너무 빠른 실행 방지 (최소 간격 보장)
                if current_time - last_executed < self.min_cycle_time:
                    time.sleep(0.002)  # 짧게 대기
                    continue
                
                try:
                    # 키 입력
                    keyboard.press(key)
                    time.sleep(self.press_delay)
                    keyboard.release(key)
                    time.sleep(self.release_delay)
                    
                    # 성공적으로 실행됨을 기록
                    last_executed = time.time()
                    retry_count = 0  # 성공 시 재시도 카운트 초기화
                except Exception as e:
                    # 개별 키 입력 실패 시 재시도
                    retry_count += 1
                    self._log(f"키 {key} 입력 실패, 재시도 중 ({retry_count}/{self.max_retries}): {e}")
                    
                    # 키 상태 강제 초기화 시도
                    try:
                        keyboard.release(key)
                    except:
                        pass
                        
                    # 최대 재시도 횟수 초과 시 중단
                    if retry_count >= self.max_retries:
                        self._log(f"키 {key} 최대 재시도 횟수 초과, 스레드 종료")
                        break
                    else:
                        time.sleep(self.retry_delay)
                
                # 종료 조건 다시 확인
                if stop_signal.is_set() or not self.pressed_keys.get(key, False) or not self.mode_active:
                    break
        except Exception as e:
            self._log(f"키 반복 스레드 오류: {e}")
            traceback.print_exc()
        finally:
            # 항상 키 해제 및 상태 정리
            try:
                keyboard.release(key)
            except:
                pass
    
    def set_repeat_speed(self, speed_level=2):
        """키 반복 속도 설정 (1=느림, 2=중간, 3=빠름, 4=매우 빠름)"""
        with self.lock:
            if speed_level == 1:  # 느림
                self.press_delay = 0.03
                self.release_delay = 0.03
            elif speed_level == 2:  # 중간 (기본)
                self.press_delay = 0.02
                self.release_delay = 0.02
            elif speed_level == 3:  # 빠름
                self.press_delay = 0.01
                self.release_delay = 0.01
            elif speed_level == 4:  # 매우 빠름
                self.press_delay = 0.005
                self.release_delay = 0.005
            else:
                # 기본값 (중간)
                self.press_delay = 0.02
                self.release_delay = 0.02
            return True

    def get_status_info(self):
        """현재 컨트롤러 상태 정보 반환 (디버깅용)"""
        with self.lock:
            status = {
                "mode_active": self.mode_active,
                "enabled_keys": list(self.enabled_keys),
                "active_threads": len(self.active_threads),
                "pressed_keys": {k: v for k, v in self.pressed_keys.items() if v is True},
                "press_delay": self.press_delay,
                "release_delay": self.release_delay
            }
        return status
    
    def print_status(self):
        """현재 상태 콘솔 출력 (디버깅용)"""
        status = self.get_status_info()
        self._log("==== 현재 상태 ====")
        self._log(f"모드 활성화: {status['mode_active']}")
        self._log(f"활성화된 키: {status['enabled_keys']}")
        self._log(f"눌린 키: {status['pressed_keys']}")
        self._log(f"활성 스레드 수: {status['active_threads']}")
        self._log(f"반복 간격: {status['press_delay']}초 / {status['release_delay']}초")
        self._log("===================")

    def reset_all_states(self):
        """모든 키 상태 초기화 (디버깅용)"""
        with self.lock:
            # 모드 비활성화
            self.mode_active = False
            
            # 모든 스레드 종료
            self._stop_all_repeats()
            
            # 모든 키 해제
            for key in "abcdefghijklmnopqrstuvwxyz0123456789":
                try:
                    keyboard.release(key)
                except:
                    pass
            
            # 상태 초기화
            self.active_threads.clear()
            self.stop_signals.clear()
            
            # 눌림 상태 초기화
            for key in self.pressed_keys:
                self.pressed_keys[key] = False
                
            return True

# 전역 인스턴스
keyboard_controller = KeyboardController() 