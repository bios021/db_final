# app/models/student.py
from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Unit(Base):
    __tablename__ = "UNITS"
    
    unit_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unit_name: Mapped[str] = mapped_column(String(20), nullable=False)
    college_id: Mapped[Optional[int]] = mapped_column(ForeignKey("UNITS.unit_id"))

class Student(Base):
    __tablename__ = "STUDENTS"
    
    student_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_name: Mapped[str] = mapped_column(String(20), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False) # Hash 密碼長度建議加大
    unit_id: Mapped[int] = mapped_column(ForeignKey("UNITS.unit_id"), nullable=False)
    enrollment_year: Mapped[int] = mapped_column(Integer, nullable=False)

    # 關聯
    unit: Mapped["Unit"] = relationship()
