from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Risk DSS FastAPI 서버가 정상 작동 중입니다 🚀"}

@app.get("/apikey")
def show_key():
    # 실제 운영에서는 이 엔드포인트는 절대 만들면 안 돼! 테스트용이야
    return {"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}
