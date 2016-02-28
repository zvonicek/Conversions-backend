from marshmallow import Schema, fields, post_load
from marshmallow_polyfield import PolyField

from app.models.Task import TaskRunQuestion
from app.schemas.Question import question_schema_serialization_disambiguation


class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    identifier = fields.String()
    name = fields.String()


class TaskRunQuestionSchema(Schema):
    question = PolyField(serialization_schema_selector=question_schema_serialization_disambiguation)

    @post_load
    def make_object(self, data):
        return TaskRunQuestion(
            data.get("question")
        )


class TaskRunSchema(Schema):
    id = fields.Int(dump_only=True)
    task = fields.Nested(TaskSchema)
    questions = fields.Nested(TaskRunQuestionSchema, many=True, only=('question'))


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

taskrun_schema = TaskRunSchema()