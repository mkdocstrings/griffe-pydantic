from __future__ import annotations

import json
from functools import partial
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griffe import Attribute, Class, Function
    from pydantic import BaseModel

_self_namespace = "griffe_pydantic"
_mkdocstrings_namespace = "mkdocstrings"

_field_constraints = {
    "gt",
    "ge",
    "lt",
    "le",
    "multiple_of",
    "min_length",
    "max_length",
    "pattern",
    "allow_inf_nan",
    "max_digits",
    "decimal_place",
}


def _model_fields(cls: Class) -> dict[str, Attribute]:
    """Get model fields, using serialization_alias when configured.

    Parameters:
        cls: The Griffe class representing the Pydantic model.

    Returns:
        A dictionary of field name to Attribute, using serialization_alias as keys when appropriate.
    """
    fields = {name: attr for name, attr in cls.all_members.items() if "pydantic-field" in attr.labels}

    ext_namespace = cls.extra.get(_self_namespace, {})
    serialize_by_alias = ext_namespace.get("serialize_by_alias", False)

    if not serialize_by_alias:
        return fields  # ty: ignore[invalid-return-type]

    # Re-key fields with their serialization_alias if present.
    # For dynamic analysis, Pydantic fields don't appear as labeled members so we fall back
    # to _pydantic_model_fields (populated from model_fields in dynamic._process_class).
    pydantic_fields = ext_namespace.get("_pydantic_model_fields", {})
    source = fields or dict.fromkeys(pydantic_fields)
    remapped_fields = {}
    for name, attr in source.items():
        if attr is not None:
            serialization_alias = attr.extra.get(_self_namespace, {}).get("serialization_alias")
        else:
            field_info = pydantic_fields.get(name)
            serialization_alias = getattr(field_info, "serialization_alias", None) if field_info else None
        remapped_fields[serialization_alias or name] = attr
    return remapped_fields


def _model_validators(cls: Class) -> dict[str, Function]:
    return {name: func for name, func in cls.all_members.items() if "pydantic-validator" in func.labels}  # ty: ignore[invalid-return-type]


def _json_schema(model: type[BaseModel]) -> str:
    """Produce a model schema as JSON.

    Parameters:
        model: A Pydantic model.

    Returns:
        A schema as JSON.
    """
    return json.dumps(model.model_json_schema(), indent=2)


def _process_class(cls: Class, *, serialize_by_alias: bool = False) -> None:
    """Set metadata on a Pydantic model.

    Parameters:
        cls: The Griffe class representing the Pydantic model.
        serialize_by_alias: Whether to use serialization_alias as the field name.
    """
    cls.labels.add("pydantic-model")
    cls.extra[_self_namespace]["serialize_by_alias"] = serialize_by_alias
    cls.extra[_self_namespace]["fields"] = partial(_model_fields, cls)
    cls.extra[_self_namespace]["validators"] = partial(_model_validators, cls)
    cls.extra[_mkdocstrings_namespace]["template"] = "pydantic_model.html.jinja"


def _process_function(func: Function, cls: Class, fields: Sequence[str]) -> None:
    """Set metadata on a Pydantic validator.

    Parameters:
        cls: A Griffe function representing the Pydantic validator.
    """
    func.labels = {"pydantic-validator"}
    if fields and fields[0] == "*":
        targets = [member for member in cls.all_members.values() if "pydantic-field" in member.labels]
    else:
        targets = [cls.all_members[field] for field in fields]

    func.extra[_self_namespace].setdefault("targets", [])
    func.extra[_self_namespace]["targets"].extend(targets)
    for target in targets:
        target.extra[_self_namespace].setdefault("validators", [])
        target.extra[_self_namespace]["validators"].append(func)
