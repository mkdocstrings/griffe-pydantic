from __future__ import annotations

import ast
from typing import TYPE_CHECKING, Any

from griffe import (
    Class,
    Extension,
    Module,
    get_logger,
)

from griffe_pydantic._internal import common, dynamic, static

if TYPE_CHECKING:
    from griffe import ObjectNode


_logger = get_logger(__name__)


class PydanticExtension(Extension):
    """Griffe extension for Pydantic."""

    def __init__(
        self,
        *,
        schema: bool = False,
        bases: tuple[str, ...] | list[str] = common._DEFAULT_BASES,
        include_bases: tuple[str, ...] | list[str] | None = None,
    ) -> None:
        """Initialize the extension.

        Parameters:
            schema: Whether to compute and store the JSON schema of models.
            bases: Tuple of complete `package.module.Class` references to base classes that should be considered
                pydantic models. Declaring this *replaces* the default bases.
            include_bases: *Additional* base classes to consider as pydantic models, including the defaults.
        """
        super().__init__()
        self._schema = schema
        self._bases = tuple(bases)
        if include_bases:
            self._bases += tuple(include_bases)
        self._processed: set[str] = set()
        self._recorded: list[tuple[ObjectNode, Class]] = []

    def on_package_loaded(self, *, pkg: Module, **kwargs: Any) -> None:  # noqa: ARG002
        """Detect models once the whole package is loaded."""
        for node, cls in self._recorded:
            self._processed.add(cls.canonical_path)
            dynamic._process_class(node.obj, cls, processed=self._processed, schema=self._schema)
        static._process_module(pkg, processed=self._processed, schema=self._schema, bases=self._bases)

    def on_class_instance(self, *, node: ast.AST | ObjectNode, cls: Class, **kwargs: Any) -> None:  # noqa: ARG002
        """Detect and prepare Pydantic models."""
        # Prevent running during static analysis.
        if isinstance(node, ast.AST):
            return

        bases = common._import_bases(self._bases)
        if not bases:
            _logger.warning(
                "could not import any expected model base - models will not be detected. \nexpected: %s",
                self._bases,
            )
            return

        if issubclass(node.obj, bases):
            self._recorded.append((node, cls))
