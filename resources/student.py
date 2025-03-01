from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from schemas import StudentSchema,BlocklistSchema
from models import StudentModel, BlocklistModel
from flask_jwt_extended import create_access_token, jwt_required, get_jwt


blp = Blueprint("students", __name__, description="Operations on students")


@blp.route('/signup')
class StudentSignUp(MethodView):
    @blp.arguments(StudentSchema)
    def post(self, new_student):
        new_student["password"] = pbkdf2_sha256.hash(new_student["password"])
        student = StudentModel(**new_student)

        try:
            db.session.add(student)
            db.session.commit()
        except IntegrityError:
            abort(400, message="User already exists, login instead.")
        except SQLAlchemyError as e:
            print(f"SQLAlchemy Error: {e}")
            abort(500, message="An error occurred while registering user.")

        access_token = create_access_token(identity=str(student.id))
        return {"student_id": student.id, "access_token": access_token}, 201
    

@blp.route('/login')
class StudentLogin(MethodView):
    @blp.arguments(StudentSchema(only=("email", "password")))
    def post(self, student_data):
        student = StudentModel.query.filter(
            StudentModel.email == student_data["email"]
        ).first()

        if student and pbkdf2_sha256.verify(student_data["password"], student.password):
            access_token = create_access_token(identity=str(student.id))
            return {"student_id": student.id, "access_token": access_token}, 200
        
        abort(401, message="Invalid credentials.")


@blp.route('/students/<int:student_id>')
class Student(MethodView):
    @jwt_required()
    @blp.response(200, StudentSchema)
    def get(self, student_id):
        student = StudentModel.query.get_or_404(student_id)
        return student, 200


@blp.route('/logout')
class StudentLogout(MethodView):
    @jwt_required()
    @blp.response(200, BlocklistSchema)
    def post(self):
        jti = get_jwt()["jti"]
        blocked_token = BlocklistModel(blocked=jti)

        try:
            db.session.add(blocked_token)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while logging out.")

        return blocked_token, 200
    

@blp.route('/check-auth')
class CheckAuth(MethodView):
    @jwt_required()
    @blp.response(200)
    def get(self):
        return "Authorized", 200