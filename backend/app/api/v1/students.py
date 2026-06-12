# app/api/v1/students.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.api.v1.auth import get_current_student_id
from app.models.course import StdCourseHistory, Course

router = APIRouter()

@router.get("/me/courses")
async def get_my_courses(
    # 檢查 Token 並找出學號
    current_student_id: int = Depends(get_current_student_id),
    # 開啟資料庫連線
    db: AsyncSession = Depends(get_db) 
):
    """
    獲取當前登入學生的所有修課紀錄（動態資料庫正式版）
    """
    # 改用JOIN，直接透過 course_id 和 semester 把兩張表對齊
    stmt = (
        select(StdCourseHistory, Course)
        .join(
            Course, 
            (StdCourseHistory.course_id == Course.course_id) & 
            (StdCourseHistory.semester == Course.semester)
        )
        .where(StdCourseHistory.student_id == current_student_id)
    )
    
    result = await db.execute(stmt)
    # 因為同時撈了兩張表，這裡要用 .all() 拿出一對一的資料元組 (rows)
    rows = result.all()

    # 如果沒撈到資料，會給提示
    if not rows:
        return {"message": "目前還沒有任何修課紀錄哦！", "data": []}

    # 整理成 JSON 格式準備回傳給前端
    courses_data = []
    for h, c in rows:  # h 是歷史紀錄，c 是課程細節
        courses_data.append({
            "semester": h.semester,
            "course_name": c.course_name, # 從對齊的課程表撈出課名
            "credits": c.credits,         # 從對齊的課程表撈出學分
            "grade": h.grade
        })
        
    return {
        "student_id": current_student_id,
        "total_courses": len(courses_data),
        "data": courses_data
    }
