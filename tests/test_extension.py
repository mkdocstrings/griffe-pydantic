"""Tests for the `extension` module."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest
from griffe import Extensions, temporary_inspected_package, temporary_visited_package

from griffe_pydantic._internal.extension import PydanticExtension

if TYPE_CHECKING:
    from mkdocstrings_handlers.python.handler import PythonHandler


code = """
    from pydantic import field_validator, ConfigDict, BaseModel, Field


    class ExampleParentModel(BaseModel):
        '''An example parent model.'''
        parent_field: str = Field(..., description="Parent field.")


    class ExampleModel(ExampleParentModel):
        '''An example child model.'''

        model_config = ConfigDict(frozen=False)

        field_without_default: str
        '''Shows the *[Required]* marker in the signature.'''

        field_plain_with_validator: int = 100
        '''Show standard field with type annotation.'''

        field_with_validator_and_alias: str = Field("FooBar", alias="BarFoo", validation_alias="BarFoo")
        '''Shows corresponding validator with link/anchor.'''

        field_with_constraints_and_description: int = Field(
            default=5, ge=0, le=100, description="Shows constraints within doc string."
        )

        @field_validator("field_with_validator_and_alias", "field_plain_with_validator", mode="before")
        @classmethod
        def check_max_length_ten(cls, v):
            '''Show corresponding field with link/anchor.'''
            if len(v) >= 10:
                raise ValueError("No more than 10 characters allowed")
            return v

        def regular_method(self):
            pass


    class RegularClass(object):
        regular_attr = 1
"""


@pytest.mark.parametrize("analysis", ["static", "dynamic"])
def test_extension(analysis: str) -> None:
    """Test the extension."""
    loader = {"static": temporary_visited_package, "dynamic": temporary_inspected_package}[analysis]
    with loader(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=True)),
    ) as package:
        assert package

        assert "ExampleParentModel" in package.classes
        assert package.classes["ExampleParentModel"].labels == {"pydantic-model"}

        assert "ExampleModel" in package.classes
        assert package.classes["ExampleModel"].labels == {"pydantic-model"}

        config = package.classes["ExampleModel"].extra["griffe_pydantic"]["config"]
        assert config == {"frozen": False}

        schema = package.classes["ExampleModel"].extra["griffe_pydantic"]["schema"]
        assert schema.startswith('{\n  "description"')


def test_imported_models() -> None:
    """Test the extension with imported models."""
    with temporary_visited_package(
        "package",
        modules={
            "__init__.py": "from ._private import MyModel\n\n__all__ = ['MyModel']",
            "_private.py": "from pydantic import BaseModel\n\nclass MyModel(BaseModel):\n    field1: str\n    '''Some field.'''\n",
        },
        extensions=Extensions(PydanticExtension(schema=False)),
    ) as package:
        assert package["MyModel"].labels == {"pydantic-model"}
        assert package["MyModel.field1"].labels == {"pydantic-field"}


def test_rendering_model_config_using_configdict(python_handler: PythonHandler) -> None:
    """Test the extension with model config using ConfigDict."""
    code = """
    from pydantic import BaseModel, ConfigDict, Field

    class Model(BaseModel):
        usage: str | None = Field(
            None,
            description="Some description.",
            example="Some example.",
        )
        model_config = ConfigDict(
            json_schema_extra={
                "example": {
                    "usage": "Some usage.",
                    "limitations": "Some limitations.",
                    "billing": "Some value.",
                    "notice_period": "Some value.",
                }
            }
        )
    """
    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False)),
    ) as package:
        python_handler.render(package["Model"], python_handler.get_options({}))  # Assert no errors.


def test_not_crashing_on_dynamic_field_description(caplog: pytest.LogCaptureFixture) -> None:
    """Test the extension with dynamic field description."""
    code = """
    import pydantic

    desc = "xyz"

    class TestModel(pydantic.BaseModel):
        abc: str = pydantic.Field(description=desc)
    """
    with (
        caplog.at_level(logging.DEBUG),
        temporary_visited_package(
            "package",
            modules={"__init__.py": code},
            extensions=Extensions(PydanticExtension(schema=False)),
        ),
    ):
        assert any(
            record.levelname == "DEBUG" and "field 'package.TestModel.abc' as literal" in record.message
            for record in caplog.records
        )


def test_ignore_classvars() -> None:
    """Test the extension ignores class variables."""
    code = """
    from pydantic import BaseModel
    from typing import ClassVar

    class Model(BaseModel):
        field: str
        class_var: ClassVar[int] = 1
    """
    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False)),
    ) as package:
        assert "pydantic-field" not in package["Model.class_var"].labels
        assert "class-attribute" in package["Model.class_var"].labels


def test_wildcard_field_validator() -> None:
    """Test field validator that works on all fields."""
    code = """
    from pydantic import BaseModel, field_validator

    class Schema(BaseModel):
        a: int
        b: int

        @field_validator('*', mode='before')
        @classmethod
        def set_if_none(cls, v: Any, info):
            ...
    """
    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False)),
    ) as package:
        validator = package["Schema.set_if_none"]
        assert validator.labels == {"pydantic-validator"}
        assert validator in package["Schema.a"].extra["griffe_pydantic"]["validators"]
        assert validator in package["Schema.b"].extra["griffe_pydantic"]["validators"]
