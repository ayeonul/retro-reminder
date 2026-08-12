# Reminder

Windows용 개인 일정 리마인더, 연락처 및 메모 관리 애플리케이션입니다.

## 구성

- `backend/`: FastAPI 및 SQLite 백엔드
- `frontend/`: Vue 3 UI 프로젝트 위치
- `scripts/`: 패키징 및 개발 보조 스크립트
- `tests/`: 자동화 테스트

## 개발 실행

```powershell
conda run -n reminder uvicorn app.main:app --app-dir backend --reload
```

서버 실행 후 `http://127.0.0.1:8000/api/health`에서 상태를 확인할 수 있습니다.

## 프론트엔드 준비 상태

Node.js/npm이 현재 시스템 PATH에서 확인되지 않아 Vue CLI 프로젝트는 아직 생성하지 않았습니다. Node.js 설치 또는 PATH 설정 후 `frontend/`에 Vue 3 프로젝트를 생성합니다.

