from collections import OrderedDict

from marshmallow import Schema, fields

from app.models import NumericQuestion, ScaleQuestion, SortQuestion, CloseEndedQuestion, CurrencyQuestion
from app.engine.convert import format_quantity, format_value


class UnitField(fields.Field):
    def _serialize(self, value, attr, obj):
        return format_quantity(value)


class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    type = fields.String()


def question_schema_serialization_disambiguation(base_object, _):
    class_to_schema = {
        NumericQuestion.__name__: NumericQuestionSchema,
        ScaleQuestion.__name__: ScaleQuestionSchema,
        SortQuestion.__name__: SortQuestionSchema,
        CloseEndedQuestion.__name__: CloseEndedQuestionSchema,
        CurrencyQuestion.__name__: CurrencySchema
    }
    try:
        return class_to_schema[base_object.__class__.__name__]()
    except KeyError:
        pass

    raise TypeError("Could not detect type.")


# close ended

class CloseEndedAnswerSchema(Schema):
    answer = fields.Function(lambda obj: format_value(obj.unit, obj.value))
    explanation = ""  # not critical, maybe implement later
    correct = fields.Boolean()


class CloseEndedQuestionSchema(QuestionSchema):
    question = fields.String(attribute="question_en")
    answers = fields.Nested(CloseEndedAnswerSchema, many=True, attribute="answers")


# numeric

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


# sort

class SortAnswerSchema(Schema):
    title = fields.Function(lambda obj: format_value(obj.unit, obj.value))
    correctPosition = fields.Integer(attribute="correct_pos")
    presentedPosition = fields.Integer(attribute="presented_pos")
    errorExplanation = ""  # not critical, maybe implement later


class SortQuestionSchema(QuestionSchema):
    question = fields.Method("get_question")
    topDescription = fields.Function(lambda obj: obj.min_label)
    bottomDescription = fields.Function(lambda obj: obj.max_label)
    answers = fields.Nested(SortAnswerSchema, many=True, attribute="sorted_answers")

    @staticmethod
    def get_question(obj):
        return "Sort from {} to {}".format(obj.min, obj.max)


# currency

class CurrencySchema(Schema):
    fromValue = fields.Float(attribute="from_value")
    fromCurrency = UnitField(attribute="from_unit")
    toUnit = UnitField(attribute="to_unit")
    toValue = fields.Float(attribute="to_value")
    tolerance = "20"
    available_notes = fields.Method("get_available_notes")
    correct_notes = fields.Method("get_correct_notes")

    @staticmethod
    def get_available_notes(obj):
        return OrderedDict([(1, 5), (5, 5), (10, 10), (100, 5), (500, 5), (1000, 5)])

    @staticmethod
    def get_correct_notes(obj):
        notes = CurrencySchema.get_available_notes(obj)
        remaining_value = obj.to_value
        correct_notes = []

        for value, count in reversed(list(notes.items())):
            for i in range(count):
                if value <= remaining_value:
                    remaining_value -= value
                    correct_notes.append(value)
                else:
                    break

        return list(reversed(correct_notes[:8]))

