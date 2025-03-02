"""Griffe extension for Pydantic."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING, Any

from griffe import (
    Class,
    Extension,
    Module,
    get_logger,
)

from griffe_pydantic import dynamic, static

if TYPE_CHECKING:
    from griffe import ObjectNode


logger = get_logger(__name__)


class PydanticExtension(Extension):
    """Griffe extension for Pydantic."""

    def __init__(self, *, schema: bool = False) -> None:
        """Initialize the extension.

        Parameters:
            schema: Whether to compute and store the JSON schema of models.
        """
        super().__init__()
        self.schema = schema
        self.processed: set[str] = set()
        self.recorded: list[tuple[ObjectNode, Class]] = []

    def on_package_loaded(self, *, pkg: Module, **kwargs: Any) -> None:  # noqa: ARG002
        """Detect models once the whole package is loaded."""
        for node, cls in self.recorded:
            self.processed.add(cls.canonical_path)
            dynamic.process_class(node.obj, cls, processed=self.processed, schema=self.schema)
        static.process_module(pkg, processed=self.processed, schema=self.schema)

    def on_class_instance(self, *, node: ast.AST | ObjectNode, cls: Class, **kwargs: Any) -> None:  # noqa: ARG002
        """Detect and prepare Pydantic models."""
        # Prevent running during static analysis.
        if isinstance(node, ast.AST):
            return

        try:
            import pydantic
        except ImportError:
            logger.warning("could not import pydantic - models will not be detected")
            return

        if issubclass(node.obj, pydantic.BaseModel):
            self.recorded.append((node, cls))
