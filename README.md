# 픽셀 테마 메모 / 리마인더

안녕하세요!<br/>
프로그램의 배포는 처음입니다. 길지 않은 개발자 경력 중 배포되는 첫 프로그램이라니 왠지 감개가 무량합니다. 거의 파이썬만 할 줄 안다는 이유로 이런 UI가 붙은 무언가를 만들 생각은 못했는데 LLM의 발전이 참 빠르네요... <br/>
저는 베이퍼웨이브 혹은 win98 스타일 ui를 아주 좋아하는데, 문득 이런 스타일의 캘린더를 데스크탑 앱으로 만들면 좋겠다는 생각이 들어 만들게 되었습니다.<br/>
버그 제보는 언제나 환영합니다!

## Windows 배포 빌드

프로젝트 루트에서 아래 순서로 실행합니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-release.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\build-installer.ps1
```

첫 번째 명령은 Vue production 빌드와 PyInstaller 실행 파일 생성을 수행합니다. 두 번째 명령은 생성된 실행 파일을 Windows 설치 EXE로 묶습니다.

최종 설치 파일은 아래 경로에 생성됩니다.

```text
release\Reminder-Setup-<버전>.exe
```

새 버전을 배포할 때는 먼저 `installer/Reminder.iss`의 버전을 변경합니다.

```iss
#define MyAppVersion "0.1.1"
```

`AppId`는 기존 설치본을 업데이트로 인식하는 고정 식별자이므로 변경하지 않습니다.
