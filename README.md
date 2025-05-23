# 마우스 자동 클릭 & 키보드 연속 입력 프로그램

현재 마우스 위치에서 자동으로 클릭을 수행하고, 키보드 키를 연속으로 입력하는 프로그램입니다.

## 주요 기능

- 관리자 권한으로 실행되어 모든 프로그램에서 동작 가능
- 전역 단축키(F6, F7, F8)로 어떤 창에서든 제어 가능
- 마우스 클릭 간격 조절 기능 (0.1초 단위)
- 클릭 횟수 카운터
- 현재 마우스 위치 실시간 표시
- **키보드 연속 입력 기능** - 숫자 및 문자 키를 누르면 자동으로 연속 입력
- **3개의 탭으로 구성된 UI** - 사용 목적에 따라 쉽게 전환 가능

## 설치 방법

1. 필요한 라이브러리 설치:
```
pip install -r requirements.txt
```

## 사용 방법

### 프로그램 실행
```
python main.py
```
프로그램은 자동으로 관리자 권한을 요청합니다. 관리자 권한 요청 창이 나타나면 '예'를 클릭하세요.

### 키보드 단축키 사용법

1. **F6: 자동 클릭 시작/중지**
   - 어떤 창이 활성화되어 있어도 작동합니다.
   - 클릭 기능을 빠르게 켜거나 끌 때 사용하세요.
   - 게임이나 다른 프로그램에 집중하면서도 자동 클릭을 제어할 수 있습니다.

2. **F7: 키보드 연속 입력 활성화/비활성화**
   - 활성화하면 숫자나 문자 키를 눌렀을 때 자동으로 연속 입력됩니다.
   - 키를 누르는 동안 계속 해당 키가 입력됩니다.
   - 활성화 상태에서는 여러 키를 동시에 누를 수 있습니다.

3. **F8: 클릭 카운터 초기화**
   - 지금까지 수행한 클릭 횟수를 0으로 초기화합니다.
   - 새로운 작업을 시작할 때 사용하세요.
   - 이 키 역시 어떤 창이 활성화되어 있어도 작동합니다.

### UI 탭 구성

프로그램은 3개의 탭으로 구성되어 있어 사용 목적에 맞게 쉽게 전환할 수 있습니다:

1. **마우스 자동 클릭 탭**
   - 현재 마우스 위치 표시
   - 클릭 간격 설정 (0.1초 단위 조절)
   - 클릭 횟수 카운터
   - 시작/중지 버튼
   - 마우스 버튼 선택 (왼쪽/오른쪽/휠)
   - 클릭 타입 선택 (싱글/더블)

2. **키보드 연타 탭**
   - 키보드 연속 입력 활성화/비활성화
   - 현재 활성화된 키 표시
   - 연타 간격 설정
   - 자주 사용하는 키 바로 선택 기능
   - 멀티 키 동시 입력 지원

3. **설정 탭**
   - 프로그램 실행 옵션 설정
   - 시각적 피드백 설정
   - 소리 알림 설정
   - 단축키 커스터마이징
   - 프로그램 정보 및 도움말

### GUI 화면 설명

- **현재 마우스 위치**: 실시간으로 마우스 좌표를 보여줍니다.
- **클릭 간격 설정**: +/- 버튼으로 클릭 간격을 0.1초 단위로 조절할 수 있습니다.
- **작동 상태**: 자동 클릭이 작동 중인지 표시합니다.
- **클릭 횟수**: 지금까지 수행한 클릭 횟수를 보여줍니다.
- **키보드 연속 입력**: 연속 입력 기능의 활성화 여부와 현재 활성화된 키를 표시합니다.
- **시작/중지 버튼**: 클릭하여 자동 클릭을 시작하거나 중지합니다.
- **키보드 연속 입력 버튼**: 클릭하여 키보드 연속 입력 기능을 활성화하거나 비활성화합니다.
- **단축키 도움말**: 단축키 사용법에 대한 자세한 정보를 제공합니다.

## EXE 파일로 빌드하기

실행 파일(.exe)로 변환하려면 다음 단계를 따르세요:

1. cx_Freeze 설치 확인:
```
pip install cx-Freeze
```

2. 빌드 실행:
```
python build_exe.py build
```

3. 'build_output' 폴더에서 생성된 '마우스자동클릭기.exe' 파일을 찾으세요.
4. 해당 파일을 **관리자 권한으로 실행**하세요.

## 프로젝트 구조

```
마우스 자동 클릭기/
├── src/                     # 소스 코드 패키지
│   ├── __init__.py
│   ├── core/                # 핵심 기능
│   │   ├── __init__.py
│   │   ├── mouse_position.py
│   │   ├── mouse_click.py
│   │   └── keyboard_control.py
│   ├── gui/                 # GUI 관련
│   │   ├── __init__.py
│   │   ├── tab_based_app.py # 탭 기반 메인 애플리케이션
│   │   ├── auto_clicker_app.py # 레거시 코드(참조용)
│   │   └── tabs/            # 각 탭 구현
│   │       ├── __init__.py
│   │       ├── mouse_clicker_tab.py
│   │       ├── keyboard_tab.py
│   │       └── settings_tab.py
│   └── utils/               # 유틸리티
│       ├── __init__.py
│       └── admin_check.py
├── main.py                  # 메인 진입점
├── build_exe.py             # EXE 빌드 스크립트
├── requirements.txt         # 의존성 패키지
├── mouse_icon.ico           # 프로그램 아이콘
└── README.md                # 이 문서
```

## 주의사항

- 이 프로그램은 관리자 권한으로 실행되어야 합니다.
- 일부 게임이나 보안 프로그램에서는 자동 클릭이나 키보드 입력이 제한될 수 있습니다.
- 매크로 사용이 금지된 게임이나 프로그램에서 사용하면 계정 제재를 받을 수 있습니다. 