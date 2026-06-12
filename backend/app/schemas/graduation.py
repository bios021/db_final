# app/schemas/graduation.py

from pydantic import BaseModel
from typing import List, Optional

# 單一條件的進度 (例如：人文通識)
class ConditionSummary(BaseModel):
    condition_id: int
    condition_name: str
    required_credits: int
    max_admitted_credits: int
    earned_credits: int
    status: str # "COMPLETED" 或 "UNCOMPLETED"
    details: List[str] = [] # 具體修了哪些課



# 最終回傳給前端的畢業報告總表
class GraduationReportSchema(BaseModel):
    student_id: int
    is_graduable: bool
    total_required: int
    total_earned: int
    free_elective_credits: int
    summary_by_conditions: List[ConditionSummary]
    unmapped_courses: List[str] = []
    f_gened_credits: int
    h_major_credits: int
    k_failed_credits: int
