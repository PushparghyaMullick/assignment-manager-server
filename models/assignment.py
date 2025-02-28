from db import db
import enum

class AssignmentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class AssignmentModel(db.Model):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    problem_statement = db.Column(db.String(80), nullable=False)
    submission_link = db.Column(db.String(80), nullable=False)
    due_date_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(AssignmentStatus), nullable=False, default=AssignmentStatus.PENDING)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)

    student = db.relationship("StudentModel", back_populates="assignments")