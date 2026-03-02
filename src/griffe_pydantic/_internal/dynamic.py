from __future__ import annotations

from typing import TYPE_CHECKING, Any

from griffe import (
    Attribute,
    Class,
    Docstring,
    Function,
    Kind,
    get_logger,
)

from griffe_pydantic._internal import common

if TYPE_CHECKING:
    from collections.abc import Callable


_logger = get_logger("griffe_pydantic")


def _process_attribute(obj: Any, attr: Attribute, cls: Class, *, processed: set[str]) -> None:
    """Handle Pydantic fields."""
    from pydantic.fields import FieldInfo  # noqa: PLC0415

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

    # Store serialization_alias if present
    if obj.serialization_alias:
        attr.extra[common._self_namespace]["serialization_alias"] = obj.serialization_alias

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


def _process_class(
    obj: type,
    cls: Class,
    *,
    processed: set[str],
    schema: bool = False,
    serialize_by_alias: bool = False,
) -> None:
    """Detect and prepare Pydantic models."""
    common._process_class(cls, serialize_by_alias=serialize_by_alias)
    if schema:
        try:
            cls.extra[common._self_namespace]["schema"] = common._json_schema(obj)  # ty: ignore[invalid-argument-type]
        except Exception as exc:  # noqa: BLE001
            # Schema generation can fail and raise Pydantic errors.
            _logger.debug("Failed to generate schema for %s: %s", cls.path, exc)
    for member in cls.all_members.values():
        kind = member.kind
        if kind is Kind.ATTRIBUTE:
            _process_attribute(getattr(obj, member.name), member, cls, processed=processed)  # ty: ignore[invalid-argument-type]
        elif kind is Kind.FUNCTION:
            _process_function(getattr(obj, member.name), member, cls, processed=processed)  # ty: ignore[invalid-argument-type]

    # Also process Pydantic model fields directly from model_fields
    # These are FieldInfo objects that may not appear as regular member attributes
    if model_fields := getattr(obj, "model_fields", None):
        pydantic_fields = {}
        for field_name, field_info in model_fields.items():
            pydantic_fields[field_name] = field_info
            # If the field has a serialization_alias and serialize_by_alias is enabled,
            # we want to use the alias in the output
            if hasattr(field_info, "serialization_alias") and field_info.serialization_alias:
                from pydantic.fields import FieldInfo  # noqa: PLC0415

                if isinstance(field_info, FieldInfo):
                    # Create a synthetic field entry with the alias
                    # Store the FieldInfo in a place where _model_fields can access it
                    pass

        # Store model fields for later use
        cls.extra[common._self_namespace]["_pydantic_model_fields"] = pydantic_fields
