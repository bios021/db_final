# app/schemas/auth.py

from pydantic import BaseModel

class LoginRequest(BaseModel):
    student_id: int
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

