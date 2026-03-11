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

    def __init__(self, *, schema: bool = False, show_alias: bool = False) -> None:
        """Initialize the extension.

        Parameters:
            schema: Whether to compute and store the JSON schema of models.
            show_alias: Whether to use `alias` as the field name in documentation.
                When enabled, fields with a `alias` will be keyed by that alias instead of their Python attribute name.
        """
        super().__init__()
        self._schema = schema
        self._show_alias = show_alias
        self._processed: set[str] = set()
        self._recorded: list[tuple[ObjectNode, Class]] = []

    def on_package(self, *, pkg: Module, **kwargs: Any) -> None:  # noqa: ARG002
        """Detect models once the whole package is loaded."""
        for node, cls in self._recorded:
            self._processed.add(cls.canonical_path)
            dynamic._process_class(
                node.obj,
                cls,
                processed=self._processed,
                schema=self._schema,
                show_alias=self._show_alias,
            )
        static._process_module(
            pkg,
            processed=self._processed,
            schema=self._schema,
            show_alias=self._show_alias,
        )

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
