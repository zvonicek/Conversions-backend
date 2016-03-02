from collections import OrderedDict

from marshmallow import Schema, fields, post_load, pre_load
from marshmallow_polyfield import PolyField

from app.models import NumericQuestion, ScaleQuestion, SortQuestion, CloseEndedQuestion, CurrencyQuestion, TextHint, \
    Hint
from app.engine.convert import format_quantity, format_value, format_number
from app.serialization.Hint import TextHintSchema, task_schema_serialization_disambiguation


class UnitField(fields.Field):
    def _serialize(self, value, attr, obj):
        return format_quantity(value)


class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    type = fields.String()
    hint = PolyField(serialization_schema_selector=task_schema_serialization_disambiguation)

    @pre_load
    def format_numbers(self, in_data):
        in_data['fromValue'] = 5
        return in_data

    @post_load
    def make_object(self, data):
        return Hint(
            data.get("hint")
        )


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
    minCorrectValue = fields.Method("get_min_correct_val")  # temporary
    maxCorrectValue = fields.Method("get_max_correct_val")  # temporary
    imagePath = fields.String(attribute="image_path")

    @staticmethod
    def get_min_correct_val(obj):
        return obj.to_value

    @staticmethod
    def get_max_correct_val(obj):
        return obj.to_value


class ScaleQuestionSchema(QuestionSchema):
    question = fields.Method("get_task")
    fromValue = fields.Float(attribute="from_value")
    fromUnit = UnitField(attribute="from_unit")
    toUnit = UnitField(attribute="to_unit")
    correctValue = fields.Float(attribute="to_value")
    correctTolerance = fields.Constant(42)  # temporary
    scaleMin = fields.Function(lambda obj: obj.to_value - obj.scale_min)
    scaleMax = fields.Function(lambda obj: obj.to_value + obj.scale_max)

    @staticmethod
    def get_task(obj):
        return "Convert {} {} to {}".format(format_number(obj.from_value), format_quantity(obj.from_unit), format_quantity(obj.to_unit))


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
        return "Sort from {} to {}".format(obj.min_label, obj.max_label)


# currency

class CurrencySchema(QuestionSchema):
    fromValue = fields.Float(attribute="from_value")
    fromCurrency = UnitField(attribute="from_unit")
    toCurrency = UnitField(attribute="to_unit")
    toValue = fields.Float(attribute="to_value")
    tolerance = fields.Constant(42)  # temporary
    availableNotes = fields.Method("get_available_notes")
    correctNotes = fields.Method("get_correct_notes")

    @staticmethod
    def get_available_notes(obj):
        return [CurrencySchema.create_note(1, obj.to_unit, 5), CurrencySchema.create_note(5, obj.to_unit, 5),
                CurrencySchema.create_note(10, obj.to_unit, 10), CurrencySchema.create_note(100, obj.to_unit, 5),
                CurrencySchema.create_note(500, obj.to_unit, 5), CurrencySchema.create_note(1000, obj.to_unit, 5)]

    @staticmethod
    def get_correct_notes(obj):
        notes = CurrencySchema.get_available_notes(obj)
        remaining_value = obj.to_value
        correct_notes = []

        for note in reversed(list(notes)):
            for i in range(note["count"]):
                if note["value"] <= remaining_value:
                    remaining_value -= note["value"]
                    correct_notes.append(CurrencySchema.create_note(note["value"], obj.to_unit))
                else:
                    break

        return list(reversed(correct_notes[:8]))

    @staticmethod
    def create_note(value, currency, count=None):
        note = {"value": value, "currency": currency}
        if count is not None:
            note["count"] = count

        return note