# app/models/course.py
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Subject(Base):
    __tablename__ = "SUBJECT"
    
    subject_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_name: Mapped[str] = mapped_column(String(50), nullable=False)

class Course(Base):
    __tablename__ = "COURSES"
    
    course_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    semester: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_name: Mapped[str] = mapped_column(String(50), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("SUBJECT.subject_id"), nullable=False)
    unit_id: Mapped[int] = mapped_column(ForeignKey("UNITS.unit_id"), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)

class StdCourseHistory(Base):
    __tablename__ = "STD_COURSE_HISTORY"
    
    student_id: Mapped[int] = mapped_column(ForeignKey("STUDENTS.student_id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    semester: Mapped[int] = mapped_column(Integer, primary_key=True)
    grade: Mapped[Optional[int]] = mapped_column(Integer)

    # 處理複合外鍵
    __table_args__ = (
        ForeignKeyConstraint(
            ['course_id', 'semester'],
            ['COURSES.course_id', 'COURSES.semester']
        ),
    )
