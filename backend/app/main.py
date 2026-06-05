from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, graduation # 假設的路由導入

app = FastAPI(title="學分檢核系統 API")

# 允許前端來源
origins = [
    "http://localhost:3000", # 前端開發 Port (可修改)
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # 允許所有方法 (GET, POST, etc.)
    allow_headers=["*"],
)
