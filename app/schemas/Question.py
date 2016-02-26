from marshmallow import Schema, fields

from app.models import NumericQuestion, ScaleQuestion
from app.engine.convert import convert, format_quantity


class UnitField(fields.Field):
    def _serialize(self, value, attr, obj):
        return format_quantity(value)


class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    type = fields.String()


class NumericQuestionSchema(QuestionSchema):
    fromValue = fields.Float(attribute="from_value")
    fromUnit = UnitField(attribute="from_unit")
    toUnit = UnitField(attribute="to_unit")
    toValue = fields.Float(attribute="to_value")
    minCorrectValue = fields.Method("get_min_correct_val")
    maxCorrectValue = fields.Method("get_min_correct_val")
    imagePath = fields.String()

    @staticmethod
    def get_min_correct_val(obj):
        return obj.toValue

    @staticmethod
    def get_max_correct_val(obj):
        return obj.toValue


class ScaleQuestionSchema(QuestionSchema):
    task = fields.Method("get_task")
    fromValue = fields.Float(attribute="from_value")
    fromUnit = UnitField(attribute="from_unit")
    toUnit = UnitField(attribute="to_unit")
    correctValue = fields.Float(attribute="to_value")
    correctTolerance = 42
    scaleMin = fields.Function(lambda obj: obj.to_value - obj.scale_min)
    scaleMax = fields.Function(lambda obj: obj.to_value + obj.scale_max)

    @staticmethod
    def get_task(obj):
        return "Convert {:d} {} to {}".format(obj.from_value, format_quantity(obj.from_unit), format_quantity(obj.to_unit))


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