# app/models/rule.py

from sqlalchemy import String, Integer, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Rule(Base):
    __tablename__ = "RULE"
    
    rule_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_name: Mapped[str] = mapped_column(String(40), nullable=False)
    unit_id: Mapped[int] = mapped_column(ForeignKey("UNITS.unit_id"), nullable=False)
    enrollment_year: Mapped[int] = mapped_column(Integer, nullable=False)
    required_credits: Mapped[int] = mapped_column(Integer, nullable=False)

class Condition(Base):
    __tablename__ = "CONDITION"
    
    condition_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    condition_name: Mapped[str] = mapped_column(String(50), nullable=False)
    rule_id: Mapped[int] = mapped_column(ForeignKey("RULE.rule_id"), nullable=False)
    required_credits: Mapped[int] = mapped_column(Integer, nullable=False)
    max_admitted_credits: Mapped[int] = mapped_column(Integer, nullable=False)

class ConditionCourse(Base):
    __tablename__ = "CONDITION_COURSE"

    condition_id: Mapped[int] = mapped_column(ForeignKey("CONDITION.condition_id"), primary_key=True)
    course_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    semester: Mapped[int] = mapped_column(Integer, primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ['course_id', 'semester'],
            ['COURSES.course_id', 'COURSES.semester']
        ),
    )
