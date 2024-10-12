"""Griffe extension for Pydantic."""

from __future__ import annotations

import ast
import sys
from typing import TYPE_CHECKING

from griffe import (
    Alias,
    Attribute,
    Class,
    Docstring,
    Expr,
    ExprCall,
    ExprKeyword,
    ExprName,
    Function,
    Module,
    dynamic_import,
    get_logger,
)

from griffe_pydantic import common

if TYPE_CHECKING:
    from pathlib import Path


logger = get_logger(__name__)


def inherits_pydantic(cls: Class) -> bool:
    """Tell whether a class inherits from a Pydantic model.

    Parameters:
        cls: A Griffe class.

    Returns:
        True/False.
    """
    for base in cls.bases:
        if isinstance(base, (ExprName, Expr)):
            base = base.canonical_path  # noqa: PLW2901
        if base in {"pydantic.BaseModel", "pydantic.main.BaseModel"}:
            return True

    return any(inherits_pydantic(parent_class) for parent_class in cls.mro())


def pydantic_field_validator(func: Function) -> ExprCall | None:
    """Return a function's `pydantic.field_validator` decorator if it exists.

    Parameters:
        func: A Griffe function.

    Returns:
        A decorator value (Griffe expression).
    """
    for decorator in func.decorators:
        if isinstance(decorator.value, ExprCall) and decorator.callable_path == "pydantic.field_validator":
            return decorator.value
    return None


def process_attribute(attr: Attribute, cls: Class, *, processed: set[str]) -> None:
    """Handle Pydantic fields."""
    if attr.canonical_path in processed:
        return
    processed.add(attr.canonical_path)

    kwargs = {}
    if isinstance(attr.value, ExprCall):
        kwargs = {
            argument.name: argument.value for argument in attr.value.arguments if isinstance(argument, ExprKeyword)
        }

        if (
            attr.value.function.canonical_path == "pydantic.Field"
            and len(attr.value.arguments) >= 1
            and not isinstance(attr.value.arguments[0], ExprKeyword)
            and attr.value.arguments[0] != "..."  # handle Field(...), i.e. no default
        ):
            kwargs["default"] = attr.value.arguments[0]

    elif attr.value is not None:
        kwargs["default"] = attr.value

    if attr.name == "model_config":
        cls.extra[common.self_namespace]["config"] = kwargs
        return

    attr.labels = {"pydantic-field"}
    attr.value = kwargs.get("default", None)
    constraints = {kwarg: value for kwarg, value in kwargs.items() if kwarg not in {"default", "description"}}
    attr.extra[common.self_namespace]["constraints"] = constraints

    # Populate docstring from the field's `description` argument.
    if not attr.docstring and (docstring := kwargs.get("description", None)):
        attr.docstring = Docstring(ast.literal_eval(docstring), parent=attr)  # type: ignore[arg-type]


def process_function(func: Function, cls: Class, *, processed: set[str]) -> None:
    """Handle Pydantic field validators."""
    if func.canonical_path in processed:
        return
    processed.add(func.canonical_path)

    if isinstance(func, Alias):
        logger.warning(f"cannot yet process {func}")
        return

    if decorator := pydantic_field_validator(func):
        fields = [ast.literal_eval(field) for field in decorator.arguments if isinstance(field, str)]
        common.process_function(func, cls, fields)


def process_class(cls: Class, *, processed: set[str], schema: bool = False) -> None:
    """Finalize the Pydantic model data."""
    if cls.canonical_path in processed:
        return

    if not inherits_pydantic(cls):
        return

    processed.add(cls.canonical_path)

    common.process_class(cls)

    if schema:
        import_path: Path | list[Path] = cls.package.filepath
        if isinstance(import_path, list):
            import_path = import_path[-1]
        if import_path.name == "__init__.py":
            import_path = import_path.parent
        import_path = import_path.parent
        try:
            true_class = dynamic_import(cls.path, import_paths=[import_path, *sys.path])
        except ImportError:
            logger.debug(f"Could not import class {cls.path} for JSON schema")
            return
        cls.extra[common.self_namespace]["schema"] = common.json_schema(true_class)

    for member in cls.all_members.values():
        if isinstance(member, Attribute):
            process_attribute(member, cls, processed=processed)
        elif isinstance(member, Function):
            process_function(member, cls, processed=processed)
        elif isinstance(member, Class):
            process_class(member, processed=processed, schema=schema)


def process_module(
    mod: Module,
    *,
    processed: set[str],
    schema: bool = False,
) -> None:
    """Handle Pydantic models in a module."""
    if mod.canonical_path in processed:
        return
    processed.add(mod.canonical_path)

    for cls in mod.classes.values():
        process_class(cls, processed=processed, schema=schema)

    for submodule in mod.modules.values():
        process_module(submodule, processed=processed, schema=schema)
