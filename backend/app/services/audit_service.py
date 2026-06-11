# app/services/audit_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func  # 新增這一行來使用資料庫的聚合函數 (如 Max)
from fastapi import HTTPException, status

from app.models.student import Unit, Student
from app.models.course import Course, StdCourseHistory
from app.models.rule import Rule, Condition, ConditionCourse

class GraduationAuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_audit(self, student_id: int):
        # ==========================================
        # Step 1: 撈取學生與單位資料
        # ==========================================
        stmt_student = select(Student).where(Student.student_id == student_id)
        student = (await self.db.execute(stmt_student)).scalar_one_or_none()
        
        if not student:
            raise HTTPException(status_code=404, detail="找不到該學生資料")

        stmt_units = select(Unit.unit_id).where(
            (Unit.unit_id == student.unit_id) | (Unit.college_id == student.unit_id)
        )
        related_unit_ids = (await self.db.execute(stmt_units)).scalars().all()

        # ==========================================
        # Step 2: 自動沿用最新舊制規則
        # ==========================================
        subq = (
            select(
                Rule.unit_id, 
                func.max(Rule.enrollment_year).label('max_year')
            )
            .where(Rule.unit_id.in_(related_unit_ids))
            .where(Rule.enrollment_year <= student.enrollment_year)
            .group_by(Rule.unit_id)
            .subquery()
        )

        stmt_rules = (
            select(Rule)
            .join(subq, (Rule.unit_id == subq.c.unit_id) & (Rule.enrollment_year == subq.c.max_year))
        )
        rules = (await self.db.execute(stmt_rules)).scalars().all()
        if not rules:
            return {"message": "該生目前沒有對應的畢業規則設定"}

        rules_map = {r.rule_id: r for r in rules}
        rule_ids = list(rules_map.keys())
        
        stmt_cond = select(Condition).where(Condition.rule_id.in_(rule_ids))
        conditions = (await self.db.execute(stmt_cond)).scalars().all()
        conditions_map = {c.condition_id: c for c in conditions}

        stmt_cc = (
            select(ConditionCourse, Course.subject_id)
            .join(Course, (ConditionCourse.course_id == Course.course_id) & (ConditionCourse.semester == Course.semester))
            .where(ConditionCourse.condition_id.in_(conditions_map.keys()))
        )
        cc_records = (await self.db.execute(stmt_cc)).all()
        subject_to_cond = {subject_id: cc.condition_id for cc, subject_id in cc_records}

        # ==========================================
        # Step 3: 撈取歷史成績，處理去重與當掉的課
        # ==========================================
        stmt_history = (
            select(StdCourseHistory, Course)
            .join(Course, (StdCourseHistory.course_id == Course.course_id) & (StdCourseHistory.semester == Course.semester))
            .where(StdCourseHistory.student_id == student_id)
            .order_by(StdCourseHistory.semester.asc())
        )
        history_records = (await self.db.execute(stmt_history)).all()

        unique_courses = {}
        failed_credits = 0

        for history, course in history_records:
            if history.grade < 60:
                failed_credits += course.credits
                continue

            term = history.semester % 10 
            dedup_key = f"{course.subject_id}_{term}"

            if dedup_key in unique_courses:
                if history.grade > unique_courses[dedup_key]["grade"]:
                    unique_courses[dedup_key] = {"course": course, "grade": history.grade}
            else:
                unique_courses[dedup_key] = {"course": course, "grade": history.grade}

        # ==========================================
        # Step 4: 裝載至你規定的 ConditionSummary 格式
        # ==========================================
        audit_results = {}
        for cond_id, c in conditions_map.items():
            # 🌟 核心攔截判斷：只要名稱包含人文、社會、自然，無視資料庫設定，強制覆蓋為 3~7 學分
            is_general_edu = any(kw in c.condition_name for kw in ['人文', '社會', '自然'])
            
            req_credits = 3 if is_general_edu else c.required_credits
            max_credits = 7 if is_general_edu else c.max_admitted_credits

            audit_results[cond_id] = {
                "condition_id": cond_id,
                "condition_name": c.condition_name,
                "required_credits": req_credits,
                "max_admitted_credits": max_credits,
                "earned_credits": 0,
                "status": "UNCOMPLETED",
                "details": []
            }
        
        free_elective_credits = 0
        unmapped_courses = []

        for data in unique_courses.values():
            course = data["course"]
            sub_id = course.subject_id

            if sub_id in subject_to_cond:
                cond_id = subject_to_cond[sub_id]
                cond_meta = conditions_map[cond_id]
                rule = rules_map[cond_meta.rule_id]

                is_gened = '通識' in rule.rule_name

                # 🌟 從 audit_results 讀取我們剛剛覆蓋的動態上限值，而不是原本的 cond_meta
                max_credits = audit_results[cond_id]["max_admitted_credits"]
                current = audit_results[cond_id]["earned_credits"]

                if current + course.credits <= max_credits:
                    audit_results[cond_id]["earned_credits"] += course.credits
                    audit_results[cond_id]["details"].append(f"{course.course_name} ({course.credits} 學分)")
                else:
                    admitted = max_credits - current
                    excess = course.credits - admitted
                    if admitted > 0:
                        audit_results[cond_id]["earned_credits"] += admitted
                        audit_results[cond_id]["details"].append(f"{course.course_name} (採計 {admitted} 學分, 溢出 {excess})")
                    else:
                        audit_results[cond_id]["details"].append(f"{course.course_name} (已達上限，{course.credits} 學分全溢出)")
                    
                    if not is_gened:
                        free_elective_credits += excess
                        unmapped_courses.append(f"{course.course_name} (群修溢出轉選修 {excess} 學分)")
                    else:
                        unmapped_courses.append(f"{course.course_name} (通識學分溢出，不採計 {excess} 學分)")
            else:
                free_elective_credits += course.credits
                unmapped_courses.append(f"{course.course_name} ({course.credits} 學分)")

        # ==========================================
        # Step 5: 結算通識上限與最終學分
        # ==========================================
        gened_cond_sum = 0
        major_cond_sum = 0
        
        for res in audit_results.values():
            # 判斷個別門檻是否達標
            if res["earned_credits"] >= res["required_credits"]:
                res["status"] = "COMPLETED"
                
            cond = conditions_map[res["condition_id"]]
            rule = rules_map[cond.rule_id]
            if '通識' in rule.rule_name:
                gened_cond_sum += res["earned_credits"]
            else:
                major_cond_sum += res["earned_credits"]

        # 處理總通識 (F) 最高 28 的限制
        f_gened_credits = min(gened_cond_sum, 28)
        gened_overflow = gened_cond_sum - f_gened_credits
        free_elective_credits += gened_overflow
        
        if gened_overflow > 0:
            unmapped_courses.append(f"通識學分溢出 ({gened_overflow} 學分)")

        gened_rule_completed = (f_gened_credits >= 28)
        audit_results_list = list(audit_results.values())
        
        audit_results_list.append({
            "condition_id": 9999, # 給予一個不重複的虛擬 ID
            "condition_name": "⚠️ 畢業總額管制：總通識學分需滿 28 分",
            "required_credits": 28,
            "max_admitted_credits": 28,
            "earned_credits": f_gened_credits,
            "status": "COMPLETED" if gened_rule_completed else "UNCOMPLETED",
            "details": [f"目前人文、社會、自然三大領域及及語文通識有效採計總和僅為 {f_gened_credits} 學分"]
        })

        # ==========================================
        # Step 6: 判定畢業資格
        # ==========================================
        total_required = sum(c.required_credits for c in conditions_map.values())
        total_earned = f_gened_credits + major_cond_sum + free_elective_credits
        
        # 條件 1: 所有 Condition 皆為 COMPLETED
        all_cond_completed = all(r["status"] == "COMPLETED" for r in audit_results.values())
        # 條件 2: 總學分 >= 124
        is_graduable = all_cond_completed and gened_rule_completed and (total_earned >= 124)
        return {
            "student_id": student_id,
            "is_graduable": is_graduable,
            "total_required": total_required,
            "total_earned": total_earned,
            "free_elective_credits": free_elective_credits,
            "summary_by_conditions": audit_results_list,
            "unmapped_courses": unmapped_courses,
            "f_gened_credits": f_gened_credits,
            "h_major_credits": major_cond_sum,
            "k_failed_credits": failed_credits
        }
