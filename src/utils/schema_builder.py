from __future__ import annotations

from typing import Any, Dict, Tuple, Type

from pydantic import BaseModel, create_model


def is_json_schema(obj: Dict[str, Any]) -> bool:
    return obj.get("type") == "object" and isinstance(obj.get("properties"), dict)


def infer_field_type(value: Any):
    # Primitive and nested inference used when an example dict is provided
    if isinstance(value, bool):
        return (bool, ...)
    if isinstance(value, int):
        return (int, ...)
    if isinstance(value, float):
        return (float, ...)
    if isinstance(value, str):
        return (str, ...)
    if value is None:
        return (type(None), ...)
    if isinstance(value, list):
        # Simplistic: assume homogeneous list of strings/ints/floats/bools/objects
        if len(value) == 0:
            return (list, ...)
        first = value[0]
        if isinstance(first, dict):
            nested_model = create_model_from_example(first)
            return (list[nested_model], ...)
        if isinstance(first, bool):
            return (list[bool], ...)
        if isinstance(first, int):
            return (list[int], ...)
        if isinstance(first, float):
            return (list[float], ...)
        if isinstance(first, str):
            return (list[str], ...)
        return (list, ...)
    if isinstance(value, dict):
        nested_model = create_model_from_example(value)
        return (nested_model, ...)
    # Fallback to string
    return (str, ...)


def create_model_from_example(example: Dict[str, Any]) -> Type[BaseModel]:
    fields: Dict[str, Tuple[Any, Any]] = {}
    for key, val in example.items():
        fields[key] = infer_field_type(val)
    dynamic = create_model("DynamicModel", **fields)  # type: ignore[arg-type]
    print(dynamic.model_json_schema())
    return dynamic


def create_model_from_json_schema(schema: Dict[str, Any]) -> Type[BaseModel]:
    if not is_json_schema(schema):
        raise ValueError("Provided schema is not a supported JSON Schema object with type=object.")

    properties: Dict[str, Any] = schema.get("properties", {})
    required = set(schema.get("required", []))
    fields: Dict[str, Tuple[Any, Any]] = {}

    for key, prop in properties.items():
        ptype = prop.get("type")
        default_required = ... if key in required else None

        if ptype == "string":
            fields[key] = (str, default_required)
        elif ptype == "integer":
            fields[key] = (int, default_required)
        elif ptype == "number":
            fields[key] = (float, default_required)
        elif ptype == "boolean":
            fields[key] = (bool, default_required)
        elif ptype == "object":
            nested = create_model_from_json_schema(prop)
            fields[key] = (nested, default_required)
        elif ptype == "array":
            items = prop.get("items", {})
            item_type = items.get("type")
            if item_type == "string":
                fields[key] = (list[str], default_required)
            elif item_type == "integer":
                fields[key] = (list[int], default_required)
            elif item_type == "number":
                fields[key] = (list[float], default_required)
            elif item_type == "boolean":
                fields[key] = (list[bool], default_required)
            elif item_type == "object":
                nested_item = create_model_from_json_schema(items)
                fields[key] = (list[nested_item], default_required)
            else:
                fields[key] = (list, default_required)
        else:
            fields[key] = (str, default_required)

    dynamic = create_model("DynamicSchemaModel", **fields)  # type: ignore[arg-type]
    return dynamic


def build_pydantic_model(structure: Dict[str, Any]) -> Type[BaseModel]:
    """Build a Pydantic model from either a JSON Schema or an example dictionary."""
    if is_json_schema(structure):
        return create_model_from_json_schema(structure)
    if isinstance(structure, dict):
        return create_model_from_example(structure)
    raise ValueError("`structure` must be a JSON Schema object or an example dictionary.")

