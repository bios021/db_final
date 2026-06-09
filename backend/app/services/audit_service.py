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
        # Step 1: 撈取學生基本資料與該生適用的所有畢業規則 (RULE)
        # ==========================================
        stmt_student = select(Student).where(Student.student_id == student_id)
        result_student = await self.db.execute(stmt_student)
        student = result_student.scalar_one_or_none()
        
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到該學生資料")

        # 一個學生可能同時適用多條規則（如：專業必修規則、專業群修規則、通識規則）
        stmt_rules = select(Rule).where(
            Rule.unit_id == student.unit_id, 
            Rule.enrollment_year == student.enrollment_year
        )
        rules = (await self.db.execute(stmt_rules)).scalars().all()
        
        if not rules:
            return {"message": "該生目前沒有對應的畢業規則設定"}

        rule_ids = [r.rule_id for r in rules]

        # ==========================================
        # Step 2: 撈取所有條件 (CONDITION) 與 課程對照表 (CONDITION_COURSE)
        # ==========================================
        stmt_cond = select(Condition).where(Condition.rule_id.in_(rule_ids))
        conditions = (await self.db.execute(stmt_cond)).scalars().all()
        
        # 建立 Condition 查詢字典: {condition_id: Condition物件}
        conditions_map = {c.condition_id: c for c in conditions}
        
        # 透過 Join COURSES 表格，直接找出畢業規則對應的科目 ID (subject_id)
        # 如此一來，不論學生在哪個學期重修，只要科目 ID 對得上，就能精準歸類！
        stmt_cc = (
            select(ConditionCourse, Course.subject_id)
            .join(Course, (ConditionCourse.course_id == Course.course_id) & (ConditionCourse.semester == Course.semester))
            .where(ConditionCourse.condition_id.in_(conditions_map.keys()))
        )
        cc_records = (await self.db.execute(stmt_cc)).all()
        
        # 建立科目與規則分類的對應字典: {subject_id: condition_id}
        subject_to_cond = {subject_id: cc.condition_id for cc, subject_id in cc_records}

        # ==========================================
        # Step 3: 撈取學生歷史修課紀錄，並執行「重複科目 (SUBJECT) 去重」
        # ==========================================
        stmt_history = (
            select(StdCourseHistory, Course)
            .join(Course, (StdCourseHistory.course_id == Course.course_id) & (StdCourseHistory.semester == Course.semester))
            .where(StdCourseHistory.student_id == student_id, StdCourseHistory.grade >= 60) # 嚴格把關：只採計及格分數
            .order_by(StdCourseHistory.semester.asc()) # 依學期順序由舊到新排序
        )
        history_records = (await self.db.execute(stmt_history)).all()

        unique_courses = {} # 格式: {subject_id: {"course": Course, "grade": int}}
        for history, course in history_records:
            sub_id = course.subject_id
            
            # 【核心去重邏輯】：如果科目重複修習，在 unique_courses 中只保留成績最高的那一次紀錄
            if sub_id in unique_courses:
                if history.grade > unique_courses[sub_id]["grade"]:
                    unique_courses[sub_id] = {"course": course, "grade": history.grade}
            else:
                unique_courses[sub_id] = {"course": course, "grade": history.grade}

        # ==========================================
        # Step 4: 核心迴圈：執行學分累加與「超修分流 (max_admitted_credits)」
        # ==========================================
        
        # 初始化各項條件的審查報告結構
        audit_results = {
            cond_id: {
                "condition_id": cond_id,
                "condition_name": c.condition_name,
                "required_credits": c.required_credits,
                "max_admitted_credits": c.max_admitted_credits,
                "earned_credits": 0,
                "status": "UNCOMPLETED",
                "details": []
            } for cond_id, c in conditions_map.items()
        }
        
        free_elective_credits = 0 # 自由選修學分池（外系選修或各分類超修溢出的學分）
        unmapped_courses = []     # 記錄最終流向自由選修的課程明細

        for data in unique_courses.values():
            course = data["course"]
            sub_id = course.subject_id

            # 檢查此科目是否屬於任何畢業門檻分類
            if sub_id in subject_to_cond:
                cond_id = subject_to_cond[sub_id]
                cond_meta = conditions_map[cond_id]
                max_credits = cond_meta.max_admitted_credits
                current = audit_results[cond_id]["earned_credits"]

                # A. 尚未超過該分類採計上限，全額認列
                if current + course.credits <= max_credits:
                    audit_results[cond_id]["earned_credits"] += course.credits
                    audit_results[cond_id]["details"].append(f"{course.course_name} ({course.credits} 學分)")
                
                # B. 加上這門課就爆了！執行超修分流
                else:
                    admitted = max_credits - current # 該分類還能塞多少學分
                    excess = course.credits - admitted # 溢位、多出來的學分
                    
                    if admitted > 0:
                        audit_results[cond_id]["earned_credits"] += admitted
                        audit_results[cond_id]["details"].append(
                            f"{course.course_name} (分類採計 {admitted} 學分, 溢出 {excess} 學分至選修)"
                        )
                    else:
                        audit_results[cond_id]["details"].append(
                            f"{course.course_name} (已達該分類上限，{course.credits} 學分全數溢出至選修)"
                        )
                    
                    # 將超修溢出的學分倒進自由選修池
                    free_elective_credits += excess
                    unmapped_courses.append(f"{course.course_name} (溢出的 {excess} 學分)")
            
            else:
                # C. 完全不在規則內的課（如跨系選修），直接計入自由選修
                free_elective_credits += course.credits
                unmapped_courses.append(f"{course.course_name} ({course.credits} 學分)")

        # ==========================================
        # Step 5: 結算最終畢業審查狀態
        # ==========================================
        for res in audit_results.values():
            if res["earned_credits"] >= res["required_credits"]:
                res["status"] = "COMPLETED"

        # 總要求學分 = 所有條件要求學分的總和
        total_required = sum(c.required_credits for c in conditions_map.values())
        
        # 總實得學分 = 各條件實得學分 + 自由選修學分
        total_earned = sum(r["earned_credits"] for r in audit_results.values()) + free_elective_credits
        
        # 是否可畢業：必須「所有門檻分類」皆達到 COMPLETED 狀態
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
