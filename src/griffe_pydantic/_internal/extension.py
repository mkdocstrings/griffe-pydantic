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

    def __init__(
        self,
        *,
        schema: bool = False,
        extra_bases: list[str] | None = None,
    ) -> None:
        """Initialize the extension.

        Parameters:
            schema: Whether to compute and store the JSON schema of models.
            extra_bases: Additional base classes to detect as Pydantic models.
        """
        super().__init__()
        self._schema = schema
        self._extra_bases = extra_bases or []
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
            )
        self._recorded.clear()
        static._process_module(
            pkg,
            processed=self._processed,
            schema=self._schema,
            extra_bases=self._extra_bases,
        )

    def on_class_instance(
        self,
        *,
        node: ast.AST | ObjectNode,
        cls: Class,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Detect and prepare Pydantic models."""
        # Prevent running during static analysis.
        if isinstance(node, ast.AST):
            return

        try:
            import pydantic  # noqa: PLC0415
        except ImportError:
            _logger.warning("could not import pydantic - models will not be detected")
            return

        # Check if it's a standard Pydantic model
        if issubclass(node.obj, pydantic.BaseModel):
            self._recorded.append((node, cls))
            return

        # Check if it's a subclass of any extra base classes
        for extra_base in self._extra_bases:
            try:
                # Import the extra base class
                parts = extra_base.split(".")
                module_name = ".".join(parts[:-1])
                class_name = parts[-1]

                if module_name:
                    import importlib  # noqa: PLC0415

                    module = importlib.import_module(module_name)
                    base_class = getattr(module, class_name)
                else:
                    # Handle case where only class name is provided (in current module)
                    base_class = globals().get(class_name)
                    if base_class is None:
                        continue

                if base_class and issubclass(node.obj, base_class):
                    try:
                        # Verify that this extra base ultimately inherits from BaseModel
                        if issubclass(base_class, pydantic.BaseModel):
                            self._recorded.append((node, cls))
                            return
                        _logger.debug(f"Extra base class {extra_base} does not inherit from pydantic.BaseModel")
                    except TypeError:
                        # issubclass() can raise TypeError if base_class is not a class
                        _logger.debug(f"Extra base {extra_base} is not a valid class for issubclass check")
                        continue
            except (ImportError, AttributeError):
                # Skip if we can't import or resolve the extra base
                _logger.debug(f"Could not resolve extra base class: {extra_base}")
                continue
            except TypeError:
                # issubclass() with node.obj failed
                _logger.debug(f"Could not check inheritance from extra base class: {extra_base}")
                continue
