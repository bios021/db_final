# app/models/__init__.py
from app.core.database import Base
from app.models.student import Unit, Student
from app.models.course import Subject, Course, StdCourseHistory
from app.models.rule import Rule, Condition, ConditionCourse

