from collections import OrderedDict

from flask import logging, url_for
from marshmallow import Schema, fields, post_load, pre_load
from marshmallow_polyfield import PolyField

from app.engine.utils import get_tolerance
from app.models import NumericQuestion, ScaleQuestion, SortQuestion, CloseEndedQuestion, CurrencyQuestion, TextHint, \
    Hint
from app.engine.convert import format_unit, format_value, format_number
from app.serialization.Hint import TextHintSchema, task_schema_serialization_disambiguation


class UnitField(fields.Field):
    def _serialize(self, value, attr, obj):
        return format_unit(value)


class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    targetTime = fields.Function(lambda obj: obj.expected_time())
    type = fields.String()
    hint = PolyField(serialization_schema_selector=task_schema_serialization_disambiguation)

    def handle_error(self, exc, data):
        logger = logging.getLogger('logger')
        logger.error(exc.messages)

    @post_load
    def make_object(self, data):
        return Hint(
            data.get("hint")
        )

    @staticmethod
    def get_image_path(obj):
        if obj.image_name:
            return url_for('static', filename='tasks_img/'+obj.image_name+'.png')
        else:
            return None


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
    explanation = None  # not critical, maybe implement later
    correct = fields.Boolean()


class CloseEndedQuestionSchema(QuestionSchema):
    question = fields.Method('get_question')
    answers = fields.Nested(CloseEndedAnswerSchema, many=True, attribute="answers")
    imagePath = fields.Method("get_image_path")

    @staticmethod
    def get_question(obj):
        if obj.question_type == "estimate_height":
            return "Which is a better estimate for the height of a {}?".format(obj.question_en)
        elif obj.question_type == "estimate_length":
            return "Which is a better estimate for the length of a {}?".format(obj.question_en)
        elif obj.question_type == "estimate_distance":
            return "Which is a better estimate for the distance {}?".format(obj.question_en)
        else:
            return obj.question_en

# numeric

class NumericQuestionSchema(QuestionSchema):
    fromValue = fields.Float(attribute="from_value")
    fromUnit = UnitField(attribute="from_unit")
    toUnit = UnitField(attribute="to_unit")
    toValue = fields.Float(attribute="to_value")
    tolerance = fields.Function(lambda obj: get_tolerance(obj.to_unit, obj.to_value))
    imagePath = fields.Method("get_image_path")


class ScaleQuestionSchema(QuestionSchema):
    question = fields.Method("get_task")
    fromValue = fields.Float(attribute="from_value")
    fromUnit = UnitField(attribute="from_unit")
    toUnit = UnitField(attribute="to_unit")
    correctValue = fields.Float(attribute="to_value")
    correctTolerance = fields.Function(lambda obj: get_tolerance(obj.to_unit, obj.scale_max - obj.scale_min))
    scaleMin = fields.Float(attribute="scale_min")
    scaleMax = fields.Float(attribute="scale_max")

    @staticmethod
    def get_task(obj):
        return "Convert {} {} to {}".format(format_number(obj.from_value), format_unit(obj.from_unit), format_unit(obj.to_unit))


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
    tolerance = fields.Function(lambda obj: get_tolerance(obj.to_unit, obj.to_value))
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