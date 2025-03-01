from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from schemas import StudentSchema, AssignmentSchema, BlocklistSchema
from models import StudentModel, AssignmentModel, BlocklistModel
from flask_jwt_extended import jwt_required
from models.assignment import AssignmentStatus


blp = Blueprint("assignments", __name__, description="Operations on assignments")


@blp.route('/students/<int:student_id>/assignments')
class Assignments(MethodView):
    @jwt_required()
    @blp.arguments(AssignmentSchema)
    @blp.response(201, AssignmentSchema)
    def post(self, new_assignment, student_id):
        student = StudentModel.query.get_or_404(student_id)
        assignment = AssignmentModel(**new_assignment)
        assignment.student_id = student_id

        try:
            db.session.add(assignment)
            db.session.commit()
        except SQLAlchemyError as e:
            print(f"SQLAlchemy Error: {e}")
            abort(500, message="An error occurred while adding assignment.")

        return assignment, 201
    

@blp.route('/students/<int:student_id>/assignments/<int:assignment_id>')
class Assignment(MethodView):
    @jwt_required()
    @blp.response(200, AssignmentSchema)
    def get(self, student_id, assignment_id):
        assignment = AssignmentModel.query.filter(
            AssignmentModel.student_id == student_id,
            AssignmentModel.id == assignment_id
        ).first_or_404()

        return assignment

    @jwt_required()
    @blp.arguments(AssignmentSchema)
    @blp.response(200, AssignmentSchema)
    def put(self, new_assignment, student_id, assignment_id):
        assignment = AssignmentModel.query.filter(
            AssignmentModel.student_id == student_id,
            AssignmentModel.id == assignment_id
        ).first_or_404()

        for key, value in new_assignment.items():
            setattr(assignment, key, value)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            print(f"SQLAlchemy Error: {e}")
            abort(500, message="An error occurred while updating assignment.")

        return assignment

    @jwt_required()
    @blp.response(204)
    def delete(self, student_id, assignment_id):
        assignment = AssignmentModel.query.filter(
            AssignmentModel.student_id == student_id,
            AssignmentModel.id == assignment_id
        ).first_or_404()

        try:
            db.session.delete(assignment)
            db.session.commit()
        except SQLAlchemyError as e:
            print(f"SQLAlchemy Error: {e}")
            abort(500, message="An error occurred while deleting assignment")
            
        return None, 204
    

@blp.route('/students/<int:student_id>/assignments/<int:assignment_id>/submit')
class AssignmentSubmission(MethodView):
    @jwt_required()
    @blp.response(200, AssignmentSchema)
    def post(self, student_id, assignment_id):
        assignment = AssignmentModel.query.filter(
            AssignmentModel.student_id == student_id,
            AssignmentModel.id == assignment_id
        ).first_or_404()

        assignment.status = AssignmentStatus.COMPLETED
        db.session.commit()

        return assignment