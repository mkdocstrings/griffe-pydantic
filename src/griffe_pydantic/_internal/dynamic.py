# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2023, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from __future__ import annotations

import ast
from inspect import formatannotation
from typing import TYPE_CHECKING

from griffe import (
    Alias,
    Attribute,
    Class,
    Docstring,
    Function,
    Kind,
    get_logger,
    safe_get_annotation,
)

from griffe_pydantic._internal import common

if TYPE_CHECKING:
    from collections.abc import Callable

    from pydantic import BaseModel
    from pydantic.fields import FieldInfo


_logger = get_logger("griffe_pydantic")


def _process_attribute(obj: FieldInfo, attr: Attribute, cls: Class, *, processed: set[str]) -> None:
    """Handle Pydantic fields."""
    from pydantic_core import PydanticUndefined  # noqa: PLC0415

    if attr.canonical_path in processed:
        return
    processed.add(attr.canonical_path)

    attr.labels = {"pydantic-field"}
    attr.value = None if obj.default is PydanticUndefined else repr(obj.default)

    # Runtime annotations must become Griffe expressions before templates can render them.
    annotation = formatannotation(obj.annotation)
    try:
        annotation_node = ast.parse(annotation, mode="eval").body
    except SyntaxError:
        attr.annotation = annotation
    else:
        attr.annotation = safe_get_annotation(annotation_node, parent=cls)

    constraints = {}
    for constraint in common._field_constraints:
        if (value := getattr(obj, constraint, None)) is not None:
            constraints[constraint] = value
    attr.extra[common._self_namespace]["constraints"] = constraints
    attr.extra[common._mkdocstrings_namespace]["template"] = "pydantic_field.html.jinja"

    # Pydantic has already applied the shared alias and direction-specific overrides.
    for name in ("validation_alias", "serialization_alias"):
        if (alias := getattr(obj, name)) is not None:
            attr.extra[common._self_namespace][name] = alias

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


def _process_class(obj: type[BaseModel], cls: Class, *, processed: set[str], schema: bool = False) -> None:
    """Detect and prepare Pydantic models."""
    common._process_class(cls)
    cls.extra[common._self_namespace]["config"] = obj.model_config
    if schema:
        try:
            cls.extra[common._self_namespace]["schema"] = common._json_schema(obj)
        except Exception as exc:  # noqa: BLE001
            # Schema generation can fail and raise Pydantic errors.
            _logger.debug("Failed to generate schema for %s: %s", cls.path, exc)

    # Pydantic removes fields from the class namespace, so ordinary inspection misses them.
    for name, field_info in obj.model_fields.items():
        member = cls.all_members.get(name)
        if member is None or member.kind is not Kind.ATTRIBUTE or (member.is_alias and name in obj.__annotations__):
            member = Attribute(name=name, analysis="dynamic")
            cls.set_member(name, member)
        elif isinstance(member, Alias):
            member = member.final_target
        _process_attribute(field_info, member, cls, processed=processed)  # ty: ignore[invalid-argument-type]

    for member in cls.all_members.values():
        if member.kind is Kind.FUNCTION:
            _process_function(getattr(obj, member.name), member, cls, processed=processed)  # ty: ignore[invalid-argument-type]
