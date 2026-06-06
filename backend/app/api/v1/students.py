# app/api/v1/students.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.v1.auth import get_current_student_id
from app.models.course import StdCourseHistory

router = APIRouter()

@router.get("/me/courses")
async def get_my_courses(
    # 檢查 Token 並吐出學號
    current_student_id: int = Depends(get_current_student_id),
    # 開啟資料庫連線
    db: AsyncSession = Depends(get_db) 
):
    """
    獲取當前登入學生的所有修課紀錄
    """
    # 執行非同步 SQL 查詢
    # 這裡使用了 selectinload，讓 SQLAlchemy 一併把關聯的 COURSES 表拉出來
    stmt = (
        select(StdCourseHistory)
        .where(StdCourseHistory.student_id == current_student_id)
        .options(selectinload(StdCourseHistory.course)) 
    )
    
    result = await db.execute(stmt)
    histories = result.scalars().all()

    # 如果沒撈到資料，會給提示
    if not histories:
        return {"message": "目前還沒有任何修課紀錄哦！", "data": []}

    # 整理成 JSON 格式準備回傳給前端
    courses_data = []
    for h in histories:
        courses_data.append({
            "semester": h.semester,
            "course_name": h.course.course_name, # 例如："資料庫系統" 或 "自然語言處理"
            "credits": h.course.credits,
            "grade": h.grade
        })
        
    return {
        "student_id": current_student_id,
        "total_courses": len(courses_data),
        "data": courses_data
    }
