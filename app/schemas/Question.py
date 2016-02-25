from marshmallow import Schema, fields

from app.models import NumericQuestion, ScaleQuestion
from app.engine.convert import convert


class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    type = fields.String()


class NumericQuestionSchema(QuestionSchema):
    fromValue = fields.Float(attribute="from_value")
    fromUnit = fields.String(attribute="from_unit")
    toUnit = fields.String(attribute="to_unit")
    toValue = fields.Method("get_to_value")
    minCorrectValue = fields.Method("get_min_correct_val")
    maxCorrectValue = fields.Method("get_min_correct_val")
    imagePath = fields.String()

    @staticmethod
    def get_to_value(obj):
        return convert(obj.from_unit, obj.from_value, obj.to_unit).magnitude

    @staticmethod
    def get_min_correct_val(obj):
        return obj.toValue

    @staticmethod
    def get_max_correct_val(obj):
        return obj.toValue


class ScaleQuestionSchema(QuestionSchema):
    task = fields.Method("get_task")
    fromValue = fields.Integer(attribute="from_value")
    fromUnit = fields.String(attribute="from_unit")
    toUnit = fields.String(attribute="to_unit")
    correctValue = fields.Method("get_to_value")
    correctTolerance = 42
    scaleMin = fields.Float(attribute="scale_min")
    scaleMax = fields.Float(attribute="scale_max")

    @staticmethod
    def get_task(obj):
        pass

    @staticmethod
    def get_to_value(obj):
        return convert(obj.from_unit, obj.from_value, obj.to_unit).magnitude


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