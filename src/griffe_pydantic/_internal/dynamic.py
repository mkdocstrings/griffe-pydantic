from __future__ import annotations

from typing import Any, Callable

from griffe import (
    Attribute,
    Class,
    Docstring,
    Function,
    Kind,
    get_logger,
)
from pydantic.fields import FieldInfo

from griffe_pydantic._internal import common

_logger = get_logger(__name__)


def _process_attribute(obj: Any, attr: Attribute, cls: Class, *, processed: set[str]) -> None:
    """Handle Pydantic fields."""
    if attr.canonical_path in processed:
        return
    processed.add(attr.canonical_path)
    if attr.name == "model_config":
        cls.extra[common._self_namespace]["config"] = obj
        return

    if not isinstance(obj, FieldInfo):
        return

    attr.labels = {"pydantic-field"}
    attr.value = obj.default
    constraints = {}
    for constraint in common._field_constraints:
        if (value := getattr(obj, constraint, None)) is not None:
            constraints[constraint] = value
    attr.extra[common._self_namespace]["constraints"] = constraints

    # Populate docstring from the field's `description` argument.
    if not attr.docstring and (docstring := obj.description):
        attr.docstring = Docstring(docstring, parent=attr)


def _process_function(obj: Callable, func: Function, cls: Class, *, processed: set[str]) -> None:
    """Handle Pydantic field validators."""
    if func.canonical_path in processed:
        return
    processed.add(func.canonical_path)
    if dec_info := getattr(obj, "decorator_info", None):
        common._process_function(func, cls, dec_info.fields)


def _process_class(obj: type, cls: Class, *, processed: set[str], schema: bool = False) -> None:
    """Detect and prepare Pydantic models."""
    common._process_class(cls)
    if schema:
        cls.extra[common._self_namespace]["schema"] = common._json_schema(obj)
    for member in cls.all_members.values():
        kind = member.kind
        if kind is Kind.ATTRIBUTE:
            _process_attribute(getattr(obj, member.name), member, cls, processed=processed)  # type: ignore[arg-type]
        elif kind is Kind.FUNCTION:
            _process_function(getattr(obj, member.name), member, cls, processed=processed)  # type: ignore[arg-type]
