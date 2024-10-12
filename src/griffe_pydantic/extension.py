"""Griffe extension for Pydantic."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING, Any

from griffe import (
    Attribute,
    Class,
    Extension,
    Function,
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
        self.in_model: list[Class] = []
        self.processed: set[str] = set()

    def on_package_loaded(self, *, pkg: Module, **kwargs: Any) -> None:  # noqa: ARG002
        """Detect models once the whole package is loaded."""
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
            self.in_model.append(cls)
            dynamic.process_class(node, cls)
            self.processed.add(cls.canonical_path)

    def on_attribute_instance(self, *, node: ast.AST | ObjectNode, attr: Attribute, **kwargs: Any) -> None:  # noqa: ARG002
        """Handle Pydantic fields."""
        # Prevent running during static analysis.
        if isinstance(node, ast.AST):
            return
        if self.in_model:
            cls = self.in_model[-1]
            dynamic.process_attribute(node, attr, cls)
            self.processed.add(attr.canonical_path)

    def on_function_instance(self, *, node: ast.AST | ObjectNode, func: Function, **kwargs: Any) -> None:  # noqa: ARG002
        """Handle Pydantic field validators."""
        # Prevent running during static analysis.
        if isinstance(node, ast.AST):
            return
        if self.in_model:
            cls = self.in_model[-1]
            dynamic.process_function(node, func, cls)
            self.processed.add(func.canonical_path)

    def on_class_members(self, *, node: ast.AST | ObjectNode, cls: Class, **kwargs: Any) -> None:  # noqa: ARG002
        """Finalize the Pydantic model data."""
        # Prevent running during static analysis.
        if isinstance(node, ast.AST):
            return

        if self.in_model and cls is self.in_model[-1]:
            # Pop last class from the heap.
            self.in_model.pop()
