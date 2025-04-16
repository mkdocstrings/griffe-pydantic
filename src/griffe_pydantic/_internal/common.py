from __future__ import annotations

import importlib
import json
import sys
from functools import partial
from typing import TYPE_CHECKING

from griffe import get_logger

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griffe import Attribute, Class, Function
    from pydantic import BaseModel

_DEFAULT_BASES = (
    "pydantic.BaseModel",
    "pydantic.main.BaseModel",
    "pydantic_settings.BaseSettings",
    "pydantic_settings.main.BaseSettings",
    "sqlmodel.SQLModel",
    "sqlmodel.main.SQLModel",
)


_self_namespace = "griffe_pydantic"
_mkdocstrings_namespace = "mkdocstrings"
_logger = get_logger(__name__)

_field_constraints = {
    "gt",
    "ge",
    "lt",
    "le",
    "multiple_of",
    "min_length",
    "max_length",
    "pattern",
    "allow_inf_nan",
    "max_digits",
    "decimal_place",
}


def _model_fields(cls: Class) -> dict[str, Attribute]:
    return {name: attr for name, attr in cls.all_members.items() if "pydantic-field" in attr.labels}  # type: ignore[misc]


def _model_validators(cls: Class) -> dict[str, Function]:
    return {name: func for name, func in cls.all_members.items() if "pydantic-validator" in func.labels}  # type: ignore[misc]


def _json_schema(model: type[BaseModel]) -> str:
    """Produce a model schema as JSON.

    Parameters:
        model: A Pydantic model.

    Returns:
        A schema as JSON.
    """
    return json.dumps(model.model_json_schema(), indent=2)


def _process_class(cls: Class) -> None:
    """Set metadata on a Pydantic model.

    Parameters:
        cls: The Griffe class representing the Pydantic model.
    """
    cls.labels.add("pydantic-model")
    cls.extra[_self_namespace]["fields"] = partial(_model_fields, cls)
    cls.extra[_self_namespace]["validators"] = partial(_model_validators, cls)
    cls.extra[_mkdocstrings_namespace]["template"] = "pydantic_model.html.jinja"


def _process_function(func: Function, cls: Class, fields: Sequence[str]) -> None:
    """Set metadata on a Pydantic validator.

    Parameters:
        cls: A Griffe function representing the Pydantic validator.
    """
    func.labels = {"pydantic-validator"}
    if fields and fields[0] == "*":
        targets = [member for member in cls.all_members.values() if "pydantic-field" in member.labels]
    else:
        targets = [cls.all_members[field] for field in fields]

    func.extra[_self_namespace].setdefault("targets", [])
    func.extra[_self_namespace]["targets"].extend(targets)
    for target in targets:
        target.extra[_self_namespace].setdefault("validators", [])
        target.extra[_self_namespace]["validators"].append(func)


def _import_from_name(name: str) -> type[BaseModel]:
    """Given a fully-qualified `package.module.Class` name, return the imported class."""
    module_name, _, class_name = name.rpartition(".")
    module = sys.modules.get(module_name, importlib.import_module(module_name))
    try:
        return getattr(module, class_name)
    except AttributeError as e:
        raise AttributeError(f"No class {class_name} in module {module}") from e


def _import_bases(names: tuple[str, ...]) -> tuple[type[BaseModel], ...]:
    """Import a set of bases from fully-qualified `package.module.Class` names.

    Does not raise for import errors,
    since we don't expect all possible bases to be present.
    """
    bases = []
    for name in names:
        try:
            bases.append(_import_from_name(name))
        except ImportError:
            # fine, we expect some of the defaults to fail, we only care if we have none
            _logger.debug("Could not import %s", name)

    return tuple(bases)
