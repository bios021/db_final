# app/api/v1/graduation.py

from fastapi import APIRouter, Depends
from app.schemas.graduation import GraduationReportSchema
from app.api.v1.auth import get_current_student_id

# 建立 Router
router = APIRouter()

@router.get("/audit", response_model=GraduationReportSchema)
async def mock_audit_graduation(current_student_id: int = Depends(get_current_student_id)):
    """
    這是 Mock API：目前不會真的去資料庫算學分，
    而是回傳假資料，讓前端可以先串接測試畫面。
    前端必須在 Header 帶上： Authorization: Bearer <後端給的Token>
    """
    return GraduationReportSchema(
        student_id=current_student_id,
        is_graduable=False,
        total_required=128,
        total_earned=15,
        summary_by_conditions=[
            {
                "condition_name": "人文通識",
                "required_credits": 6,
                "earned_credits": 3,
                "status": "UNCOMPLETED",
                "details": ["1121 哲學概論 (3學分)"]
            },
            {
                "condition_name": "系核心必修",
                "required_credits": 50,
                "earned_credits": 12,
                "status": "UNCOMPLETED",
                "details": ["1121 程式設計 (3學分)", "1121 微積分甲 (3學分)", "1122 資料結構 (3學分)"]
            }
        ],
        unmapped_courses=["1122 網球初級 (0學分)"]
    )
