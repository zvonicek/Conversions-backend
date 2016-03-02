from marshmallow import Schema, fields

from app.models import ScaleHint, TextHint


class HintSchema(Schema):
    type = fields.String()


def task_schema_serialization_disambiguation(base_object, _):
    class_to_schema = {
        ScaleHint.__name__: ScaleHintSchema,
        TextHint.__name__: TextHintSchema,
    }
    try:
        return class_to_schema[base_object.__class__.__name__]()
    except KeyError:
        pass

    raise TypeError("Could not detect type.")


class ScaleHintSchema(HintSchema):
    topUnit = fields.String()
    topMin = fields.Float()
    topMax = fields.Float()
    bottomUnit = fields.String()
    bottomMin = fields.Float()
    bottomMax = fields.Float()


class TextHintSchema(HintSchema):
    text = fields.String()