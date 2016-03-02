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
    topUnit = fields.String(attribute="top_unit")
    topMin = fields.Float(attribute="top_min")
    topMax = fields.Float(attribute="top_max")
    bottomUnit = fields.String(attribute="bottom_unit")
    bottomMin = fields.Float(attribute="bottom_min")
    bottomMax = fields.Float(attribute="bottom_max")


class TextHintSchema(HintSchema):
    text = fields.String()