from marshmallow import Schema, fields

from app.models import NumericQuestion, ScaleQuestion


class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    type = fields.String()


class NumericQuestionSchema(QuestionSchema):
    imagePath = fields.String()


class ScaleQuestionSchema(QuestionSchema):
    task_en = fields.String()


def question_schema_serialization_disambiguation(base_object, _):
    class_to_schema = {
        NumericQuestion.__name__: NumericQuestionSchema,
        ScaleQuestion.__name__: ScaleQuestionSchema
    }
    try:
        return class_to_schema[base_object.__class__.__name__]()
    except KeyError:
        pass

    raise TypeError("Could not detect type. "
                    "Did not have a base or a length. "
                    "Are you sure this is a shape?")