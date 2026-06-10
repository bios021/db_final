# app/api/v1/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.models.student import Student
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter()
security_scheme = HTTPBearer() # FastAPI 內建的 Bearer Token 守門員

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """學生登入 API：驗證成功後發放 Token"""
    # 1. 到資料庫搜尋該學號
    stmt = select(Student).where(Student.student_id == login_data.student_id)
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="學號或密碼錯誤")

    # 2. 比對密碼
    if not verify_password(login_data.password, student.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="學號或密碼錯誤")

    # 3. 成功則簽發 Token，將學號包進 "sub" (Subject) 欄位中
    access_token = create_access_token(data={"sub": str(student.student_id)})
    return TokenResponse(access_token=access_token)

    # login test
    # print("學號:", login_data.student_id)
    # print("密碼:", login_data.password)
    # print("驗證結果:", verify_password(login_data.password, student.password))


async def get_current_student_id(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> int:
    """
    這是安全性依賴項 (Dependency)。
    未來任何 API 只要加了這個當參數，前端就必須在 Header 帶上 Token 才能存取。
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認證失敗，請重新登入",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解密 Token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        student_id_str: str = payload.get("sub")
        if student_id_str is None:
            raise credentials_exception
        return int(student_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

