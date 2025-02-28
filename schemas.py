from marshmallow import Schema, fields, validate


class PlainStudentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class PlainAssignmentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    problem_statement = fields.Str(required=True)
    submission_link = fields.Str(required=True)
    due_date_time = fields.DateTime(required=True)
    status = fields.Str(
        validate=validate.OneOf(["pending", "completed"]),
        dump_only=True  # Ensures it's correctly serialized
    )


class StudentSchema(PlainStudentSchema):
    assignments = fields.List(fields.Nested(PlainAssignmentSchema()), dump_only=True)


class AssignmentSchema(PlainAssignmentSchema):
    student_id = fields.Int(load_only=True)
    student = fields.Nested(PlainStudentSchema(), dump_only=True)


class BlocklistSchema(Schema):
    id = fields.Int(dump_only=True)
    blocked = fields.Str(required=True)