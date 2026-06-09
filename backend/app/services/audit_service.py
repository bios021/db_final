# app/services/audit_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.models.student import Student
from app.models.course import Course, StdCourseHistory
from app.models.rule import Rule, Condition, ConditionCourse

class GraduationAuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_audit(self, student_id: int):
        # ==========================================
        # Step 1: 撈取學生基本資料與適用的畢業規則 (RULE)
        # ==========================================
        stmt_student = select(Student).where(Student.student_id == student_id)
        result_student = await self.db.execute(stmt_student)
        student = result_student.scalar_one_or_none()
        
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到該學生資料")

        stmt_rules = select(Rule).where(
            Rule.unit_id == student.unit_id, 
            Rule.enrollment_year == student.enrollment_year
        )
        rules = (await self.db.execute(stmt_rules)).scalars().all()
        
        if not rules:
            return {"message": "該生目前沒有對應的畢業規則設定"}

        rule_ids = [r.rule_id for r in rules]

        # ==========================================
        # Step 2: 撈取該規則下的所有條件 (CONDITION) 與 課程對照表 (CONDITION_COURSE)
        # ==========================================
        stmt_cond = select(Condition).where(Condition.rule_id.in_(rule_ids))
        conditions = (await self.db.execute(stmt_cond)).scalars().all()
        
        # 建立 Condition 查詢字典: {condition_id: Condition物件}
        conditions_map = {c.condition_id: c for c in conditions}
        
        # 建立課程對應分類的字典: {(course_id, semester): condition_id}
        stmt_cc = select(ConditionCourse).where(ConditionCourse.condition_id.in_(conditions_map.keys()))
        cc_records = (await self.db.execute(stmt_cc)).scalars().all()
        course_to_cond = {(cc.course_id, cc.semester): cc.condition_id for cc in cc_records}

        # ==========================================
        # Step 3: 撈取學生修課歷史並進行「重複科目 (SUBJECT) 去重」
        # ==========================================
        stmt_history = (
            select(StdCourseHistory, Course)
            .join(Course, (StdCourseHistory.course_id == Course.course_id) & (StdCourseHistory.semester == Course.semester))
            .where(StdCourseHistory.student_id == student_id, StdCourseHistory.grade >= 60) # 只採計及格
            .order_by(StdCourseHistory.semester.asc()) # 依學期排序，先修先贏
        )
        history_records = (await self.db.execute(stmt_history)).all()

        unique_courses = {} # 格式: {subject_id: {"course": Course, "grade": int}}
        for history, course in history_records:
            sub_id = course.subject_id
            # 如果科目重複，保留成績較高的那次
            if sub_id in unique_courses:
                if history.grade > unique_courses[sub_id]["grade"]:
                    unique_courses[sub_id] = {"course": course, "grade": history.grade}
            else:
                unique_courses[sub_id] = {"course": course, "grade": history.grade}

        # ==========================================
        # Step 4: 執行學分累加與「超修分流 (max_admitted_credits)」演算法
        # ==========================================
        
        # 初始化審查報告結構
        audit_results = {
            cond_id: {
                "condition_name": c.condition_name,
                "required_credits": c.required_credits,
                "earned_credits": 0,
                "status": "UNCOMPLETED",
                "details": []
            } for cond_id, c in conditions_map.items()
        }
        
        free_elective_credits = 0 # 自由選修學分池
        unmapped_courses = []     # 記錄跑到自由選修的課程

        for data in unique_courses.values():
            course = data["course"]
            key = (course.course_id, course.semester)

            # 判斷這門課有沒有在規則籃子裡
            if key in course_to_cond:
                cond_id = course_to_cond[key]
                cond_meta = conditions_map[cond_id]
                max_credits = cond_meta.max_admitted_credits
                current = audit_results[cond_id]["earned_credits"]

                # 檢查是否超出該分類的採計上限
                if current + course.credits <= max_credits:
                    # 沒超修，全額採計
                    audit_results[cond_id]["earned_credits"] += course.credits
                    audit_results[cond_id]["details"].append(f"{course.course_name} ({course.credits}學分)")
                else:
                    # 超修了！計算能塞多少，剩下的溢出到自由選修
                    admitted = max_credits - current
                    excess = course.credits - admitted
                    
                    if admitted > 0:
                        audit_results[cond_id]["earned_credits"] += admitted
                        audit_results[cond_id]["details"].append(f"{course.course_name} (採計 {admitted} 學分, 溢出 {excess} 學分至選修)")
                    
                    free_elective_credits += excess
                    unmapped_courses.append(f"{course.course_name} (溢出的 {excess} 學分)")
            else:
                # 不在任何規則內的課，直接變自由選修
                free_elective_credits += course.credits
                unmapped_courses.append(f"{course.course_name} ({course.credits}學分)")

        # ==========================================
        # Step 5: 結算最終結果
        # ==========================================
        for res in audit_results.values():
            if res["earned_credits"] >= res["required_credits"]:
                res["status"] = "COMPLETED"

        total_required = sum(c.required_credits for c in conditions_map.values())
        # 總獲得學分 = 各條件獲得學分 + 自由選修學分
        total_earned = sum(r["earned_credits"] for r in audit_results.values()) + free_elective_credits
        # 是否可畢業：所有分類皆 COMPLETED
        is_graduable = all(r["status"] == "COMPLETED" for r in audit_results.values())

        return {
            "student_id": student_id,
            "is_graduable": is_graduable,
            "total_required": total_required,
            "total_earned": total_earned,
            "free_elective_credits": free_elective_credits,
            "summary_by_conditions": list(audit_results.values()),
            "unmapped_courses": unmapped_courses
        }
