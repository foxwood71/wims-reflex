# run_backend.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "wims.wims:app",             # main.py의 app 객체
        host="0.0.0.0",         # 모든 IP에서 접근 가능
        port=8000,              # 원하는 포트로 설정
        reload=False,           # 개발용이면 True(핫리로드), 디버깅 시에는 False 권장
        log_level="debug"
    )