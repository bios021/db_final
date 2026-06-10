# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.students import router as students_router
from app.api.v1.graduation import router as grad_router

app = FastAPI(title="學分檢核系統 API")

# 設定 CORS (允許前端 localhost:3306 來串接)
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    #開 ["*"]配合壓力測試
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], # 允許所有方法 (GET, POST, etc.)
    allow_headers=["*"],
)

# 註冊登入相關 API：網址 /api/v1/auth/login
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

# 註冊學生專屬 API：網址 /api/v1/students/me/courses
app.include_router(students_router, prefix="/api/v1/students", tags=["Students"])

# 註冊學分審查 API：網址 /api/v1/graduation/audit
app.include_router(grad_router, prefix="/api/v1/graduation", tags=["Graduation Audit"])

@app.get("/")
async def root():
    return {"message": "Welcome to Graduation Audit API"}
