# app/api/v1/graduation.py

from fastapi import APIRouter, Depends
from app.schemas.graduation import GraduationReportSchema
from app.api.v1.auth import get_current_student_id

try:
    from app.core.database import get_db
except ImportError:
    from app.database import get_db
    
# 建立 Router
router = APIRouter()

@router.get("/audit", response_model=GraduationReportSchema)
async def audit_graduation(
    current_student_id: int = Depends(get_current_student_id),
    db: AsyncSession = Depends(get_db)  # 🚀 透過依賴注入（Depends）取得資料庫連線
):
    """
    【畢業學分審查系統正式 API】
    安全防護：自動從前端帶過來的 JWT Token 中解析出目前登入學生的學號（防範越權查詢）。
    核心邏輯：從資料庫動態撈取該學生的修課紀錄、比對適用畢業規則、計算超修與分流，回傳最真實的審查報告。
    """
    # 1. 實例化畢業審查 Service，並把資料庫連線丟進去
    audit_service = GraduationAuditService(db)
    
    # 2. 呼叫大腦，傳入目前登入學生的學號開始計算
    audit_report = await audit_service.calculate_audit(current_student_id)
    
    # 3. 直接回傳計算完的字典，FastAPI 會自動幫你對齊 response_model=GraduationReportSchema 進行格式過濾與輸出
    return audit_report
    
"""
@router.get("/audit", response_model=GraduationReportSchema)
async def mock_audit_graduation(current_student_id: int = Depends(get_current_student_id)):
    
    這是 Mock API：目前不會真的去資料庫算學分，
    而是回傳假資料，讓前端可以先串接測試畫面。
    前端必須在 Header 帶上： Authorization: Bearer <後端給的Token>
    
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
"""
