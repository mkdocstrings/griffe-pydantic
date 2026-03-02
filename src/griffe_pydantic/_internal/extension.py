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
from typing import TYPE_CHECKING, Any

from griffe import (
    Class,
    Extension,
    Module,
    get_logger,
)

from griffe_pydantic._internal import dynamic, static

if TYPE_CHECKING:
    from griffe import Attribute, Inspector, ObjectNode, Visitor


_logger = get_logger("griffe_pydantic")


class PydanticExtension(Extension):
    """Griffe extension for Pydantic."""

    def __init__(self, *, schema: bool = False, serialize_by_alias: bool = False) -> None:
        """Initialize the extension.

        Parameters:
            schema: Whether to compute and store the JSON schema of models.
            serialize_by_alias: Whether to use `serialization_alias` as the field name in documentation.
                When enabled, fields with a `serialization_alias` will be keyed by that alias instead of their Python attribute name.
        """
        super().__init__()
        self._schema = schema
        self._serialize_by_alias = serialize_by_alias
        self._processed: set[str] = set()
        self._recorded: list[tuple[ObjectNode, Class]] = []
        self._attribute_declarations: dict[str, Attribute | None] = {}

    def on_package(self, *, pkg: Module, **kwargs: Any) -> None:  # noqa: ARG002
        """Detect models once the whole package is loaded."""
        # Process bases first so inherited fields can remain aliases to their definitions.
        for node, cls in sorted(self._recorded, key=lambda item: len(item[0].obj.__mro__)):
            self._processed.add(cls.canonical_path)
            dynamic._process_class(node.obj, cls, processed=self._processed, schema=self._schema, serialize_by_alias=self._serialize_by_alias)

        static._process_module(
            pkg,
            processed=self._processed,
            declarations=self._attribute_declarations,
            schema=self._schema,
            serialize_by_alias=self._serialize_by_alias,
        )

    def on_attribute_instance(
        self,
        *,
        node: ast.AST | ObjectNode,
        attr: Attribute,
        agent: Visitor | Inspector,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Record whether static attributes are declared on a class or in its constructor."""
        if not isinstance(node, ast.AST):
            return
        if agent.current.is_class:
            # An annotation copied from an earlier self assignment is not a class annotation.
            if (
                isinstance(node, ast.Assign)
                and attr.name != "model_config"
                and self._attribute_declarations.get(attr.canonical_path, attr) is None
            ):
                return
            self._attribute_declarations[attr.canonical_path] = attr
        elif agent.current.is_function and agent.current.name == "__init__":
            # Keep any class declaration that preceded the constructor assignment.
            self._attribute_declarations.setdefault(attr.canonical_path, None)

    def on_class_instance(self, *, node: ast.AST | ObjectNode, cls: Class, **kwargs: Any) -> None:  # noqa: ARG002
        """Detect and prepare Pydantic models."""
        # Prevent running during static analysis.
        if isinstance(node, ast.AST):
            return

        try:
            import pydantic  # noqa: PLC0415
        except ImportError:
            _logger.warning("could not import pydantic - models will not be detected")
            return

        if issubclass(node.obj, pydantic.BaseModel):
            self._recorded.append((node, cls))
