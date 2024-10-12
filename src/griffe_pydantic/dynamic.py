"""Griffe extension for Pydantic."""

from __future__ import annotations

from typing import TYPE_CHECKING

from griffe import (
    Attribute,
    Class,
    Docstring,
    Function,
    get_logger,
)
from pydantic.fields import FieldInfo

from griffe_pydantic import common

if TYPE_CHECKING:
    from griffe import ObjectNode

logger = get_logger(__name__)


def process_attribute(node: ObjectNode, attr: Attribute, cls: Class) -> None:
    """Handle Pydantic fields."""
    if attr.name == "model_config":
        cls.extra[common.self_namespace]["config"] = node.obj
        return

    if not isinstance(node.obj, FieldInfo):
        return

    attr.labels = {"pydantic-field"}
    attr.value = node.obj.default
    constraints = {}
    for constraint in common.field_constraints:
        if (value := getattr(node.obj, constraint, None)) is not None:
            constraints[constraint] = value
    attr.extra[common.self_namespace]["constraints"] = constraints

    # Populate docstring from the field's `description` argument.
    if not attr.docstring and (docstring := node.obj.description):
        attr.docstring = Docstring(docstring, parent=attr)


def process_function(node: ObjectNode, func: Function, cls: Class) -> None:
    """Handle Pydantic field validators."""
    if dec_info := getattr(node.obj, "decorator_info", None):
        common.process_function(func, cls, dec_info.fields)


def process_class(node: ObjectNode, cls: Class) -> None:
    """Detect and prepare Pydantic models."""
    common.process_class(cls)
    cls.extra[common.self_namespace]["schema"] = common.json_schema(node.obj)
