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
    from griffe import ObjectNode


_logger = get_logger("griffe_pydantic")


class PydanticExtension(Extension):
    """Griffe extension for Pydantic."""

    def __init__(self, *, schema: bool = False) -> None:
        """Initialize the extension.

        Parameters:
            schema: Whether to compute and store the JSON schema of models.
        """
        super().__init__()
        self._schema = schema
        self._processed: set[str] = set()
        self._recorded: list[tuple[ObjectNode, Class]] = []

    def on_package(self, *, pkg: Module, **kwargs: Any) -> None:  # noqa: ARG002
        """Detect models once the whole package is loaded."""
        for node, cls in self._recorded:
            self._processed.add(cls.canonical_path)
            dynamic._process_class(node.obj, cls, processed=self._processed, schema=self._schema)
        static._process_module(pkg, processed=self._processed, schema=self._schema)

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
