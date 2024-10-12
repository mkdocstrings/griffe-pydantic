"""Griffe extension for Pydantic."""

from __future__ import annotations

import json
from functools import partial
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griffe import Attribute, Class, Function
    from pydantic import BaseModel

self_namespace = "griffe_pydantic"
mkdocstrings_namespace = "mkdocstrings"

field_constraints = {
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
    return {name: attr for name, attr in cls.members.items() if "pydantic-field" in attr.labels}  # type: ignore[misc]


def _model_validators(cls: Class) -> dict[str, Function]:
    return {name: func for name, func in cls.members.items() if "pydantic-validator" in func.labels}  # type: ignore[misc]


def json_schema(model: type[BaseModel]) -> str:
    """Produce a model schema as JSON.

    Parameters:
        model: A Pydantic model.

    Returns:
        A schema as JSON.
    """
    return json.dumps(model.model_json_schema(), indent=2)


def process_class(cls: Class) -> None:
    """Set metadata on a Pydantic model.

    Parameters:
        cls: The Griffe class representing the Pydantic model.
    """
    cls.labels.add("pydantic-model")
    cls.extra[self_namespace]["fields"] = partial(_model_fields, cls)
    cls.extra[self_namespace]["validators"] = partial(_model_validators, cls)
    cls.extra[mkdocstrings_namespace]["template"] = "pydantic_model.html.jinja"


def process_function(func: Function, cls: Class, fields: Sequence[str]) -> None:
    """Set metadata on a Pydantic validator.

    Parameters:
        cls: A Griffe function representing the Pydantic validator.
    """
    func.labels = {"pydantic-validator"}
    targets = [cls.members[field] for field in fields]

    func.extra[self_namespace].setdefault("targets", [])
    func.extra[self_namespace]["targets"].extend(targets)
    for target in targets:
        target.extra[self_namespace].setdefault("validators", [])
        target.extra[self_namespace]["validators"].append(func)
