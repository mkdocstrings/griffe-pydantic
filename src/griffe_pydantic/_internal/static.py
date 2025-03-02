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
    Kind,
    Module,
    dynamic_import,
    get_logger,
)

from griffe_pydantic._internal import common

if TYPE_CHECKING:
    from pathlib import Path


_logger = get_logger(__name__)


def _inherits_pydantic(cls: Class) -> bool:
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

    return any(_inherits_pydantic(parent_class) for parent_class in cls.mro())


def _pydantic_validator(func: Function) -> ExprCall | None:
    """Return a function's `pydantic.field_validator` decorator if it exists.

    Parameters:
        func: A Griffe function.

    Returns:
        A decorator value (Griffe expression).
    """
    for decorator in func.decorators:
        if isinstance(decorator.value, ExprCall) and decorator.callable_path in {
            "pydantic.field_validator",
            "pydantic.model_validator",
        }:
            return decorator.value
    return None


def _process_attribute(attr: Attribute, cls: Class, *, processed: set[str]) -> None:
    """Handle Pydantic fields."""
    if attr.canonical_path in processed:
        return
    processed.add(attr.canonical_path)

    # Presence of `class-attribute` label and absence of `instance-attribute` label
    # indicates that the attribute is annotated with `ClassVar` and should be ignored.
    if "class-attribute" in attr.labels and "instance-attribute" not in attr.labels:
        return

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
        config = {}
        for key, value in kwargs.items():
            if isinstance(value, str):
                try:
                    config[key] = ast.literal_eval(value)
                except ValueError:
                    config[key] = value
            else:
                config[key] = value
        cls.extra[common._self_namespace]["config"] = config
        return

    attr.labels.add("pydantic-field")
    attr.labels.discard("class-attribute")
    attr.labels.discard("instance-attribute")

    attr.value = kwargs.get("default", None)
    constraints = {kwarg: value for kwarg, value in kwargs.items() if kwarg not in {"default", "description"}}
    attr.extra[common._self_namespace]["constraints"] = constraints

    # Populate docstring from the field's `description` argument.
    if not attr.docstring and (docstring := kwargs.get("description", None)):
        try:
            attr.docstring = Docstring(ast.literal_eval(docstring), parent=attr)  # type: ignore[arg-type]
        except ValueError:
            _logger.debug(f"Could not parse description of field '{attr.path}' as literal, skipping")


def _process_function(func: Function, cls: Class, *, processed: set[str]) -> None:
    """Handle Pydantic field validators."""
    if func.canonical_path in processed:
        return
    processed.add(func.canonical_path)

    if isinstance(func, Alias):
        _logger.warning(f"cannot yet process {func}")
        return

    if decorator := _pydantic_validator(func):
        fields = [ast.literal_eval(field) for field in decorator.arguments if isinstance(field, str)]
        common._process_function(func, cls, fields)


def _process_class(cls: Class, *, processed: set[str], schema: bool = False) -> None:
    """Finalize the Pydantic model data."""
    if cls.canonical_path in processed:
        return

    if not _inherits_pydantic(cls):
        return

    processed.add(cls.canonical_path)

    common._process_class(cls)

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
            _logger.debug(f"Could not import class {cls.path} for JSON schema")
            return
        cls.extra[common._self_namespace]["schema"] = common._json_schema(true_class)

    for member in cls.all_members.values():
        kind = member.kind
        if kind is Kind.ATTRIBUTE:
            _process_attribute(member, cls, processed=processed)  # type: ignore[arg-type]
        elif kind is Kind.FUNCTION:
            _process_function(member, cls, processed=processed)  # type: ignore[arg-type]
        elif kind is Kind.CLASS:
            _process_class(member, processed=processed, schema=schema)  # type: ignore[arg-type]


def _process_module(
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
        # Don't process aliases, real classes will be processed at some point anyway.
        if not cls.is_alias:
            _process_class(cls, processed=processed, schema=schema)

    for submodule in mod.modules.values():
        _process_module(submodule, processed=processed, schema=schema)
