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

"""Tests for the `extension` module."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest
from griffe import Extensions, temporary_inspected_package, temporary_visited_package

from griffe_pydantic._internal.extension import PydanticExtension

if TYPE_CHECKING:
    from mkdocstrings_handlers.python import PythonHandler


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
        search_sys_path=analysis == "dynamic",
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

        # Both analysis modes must collect fields, including inherited ones.
        fields = package.classes["ExampleModel"].extra["griffe_pydantic"]["fields"]()
        assert set(fields) == {
            "parent_field",
            "field_without_default",
            "field_plain_with_validator",
            "field_with_validator_and_alias",
            "field_with_constraints_and_description",
        }


@pytest.mark.parametrize("analysis", ["static", "dynamic"])
def test_collect_field_metadata(analysis: str, python_handler: PythonHandler) -> None:
    """Collect field metadata that can be rendered by the model template."""
    code = """
    from pydantic import BaseModel, Field

    class Model(BaseModel):
        required: int
        name: str = Field(default="example", description="The model's name.")
        optional: str | None = None
        items: list[int] = []
    """

    loader = {"static": temporary_visited_package, "dynamic": temporary_inspected_package}[analysis]
    with loader(
        "field_metadata",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension()),
        search_sys_path=analysis == "dynamic",
    ) as package:
        model = package["Model"]
        fields = model.extra["griffe_pydantic"]["fields"]()

        # Required fields have no default; explicit defaults keep their Python representation.
        assert set(fields) == {"required", "name", "optional", "items"}
        assert fields["required"].value is None
        assert fields["name"].value == "'example'"
        assert fields["optional"].value == "None"
        assert str(fields["items"].value) == "[]"

        # Collected fields must retain their types, descriptions, and owning class.
        assert str(fields["required"].annotation) == "int"
        assert str(fields["name"].annotation) == "str"
        assert str(fields["optional"].annotation) == "str | None"
        assert str(fields["items"].annotation) == "list[int]"
        assert fields["name"].docstring.value == "The model's name."
        assert fields["name"].parent is model
        assert fields["name"].path == "field_metadata.Model.name"

        # The model template renders every field annotation.
        python_handler.render(model, python_handler.get_options({}))


@pytest.mark.parametrize("analysis", ["static", "dynamic"])
def test_exclude_non_field_attributes(analysis: str) -> None:
    """Keep ordinary attributes out of the model's field collection."""
    code = """
    from typing import ClassVar
    from pydantic import BaseModel, ConfigDict, PrivateAttr

    class Ignored:
        pass

    class Mixin:
        inherited: int = 1
        ignored = Ignored()

        def __init__(self):
            self.inherited_instance_only: int = 2

    class Model(BaseModel, Mixin):
        model_config = ConfigDict(extra="allow", ignored_types=(Ignored,))
        field: str
        class_variable: ClassVar[int] = 3
        ignored = Ignored()
        _private: str = PrivateAttr(default="secret")
        _implicit_private: str = "secret"

        def __init__(self, **data):
            super().__init__(**data)
            self.instance_only: int = 4
            self.unannotated_instance = 5
            self.ignored_after_init: int = 6

        ignored_after_init = Ignored()

        @property
        def property_value(self) -> str:
            return self.field
    """

    loader = {"static": temporary_visited_package, "dynamic": temporary_inspected_package}[analysis]
    with loader(
        "non_field_attributes",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension()),
        search_sys_path=analysis == "dynamic",
    ) as package:
        # Annotated fields inherited from ordinary classes remain valid fields.
        fields = package["Model"].extra["griffe_pydantic"]["fields"]()
        assert set(fields) == {"field", "inherited"}

        # Unannotated model configuration must still be collected separately.
        assert package["Model"].extra["griffe_pydantic"]["config"]["extra"] == "allow"


def test_class_fields_assigned_in_init() -> None:
    """Assignments in constructors must not hide fields declared on the class."""
    code = """
    from pydantic import BaseModel

    class Parent(BaseModel):
        inherited: int

    class Model(Parent):
        before: int

        def __init__(self, **data):
            super().__init__(**data)
            self.before = 1
            self.after: int = 2
            self.instance_only: int = 3
            self.inherited = 4

        after: int
    """

    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension()),
    ) as package:
        # Declaration order must not affect whether an attribute is a field.
        fields = package["Model"].extra["griffe_pydantic"]["fields"]()
        assert set(fields) == {"before", "after", "inherited"}

        # Constructor assignments do not change defaults or the origin of inherited fields.
        assert all(field.value is None for field in fields.values())
        assert fields["inherited"].canonical_path == "package.Parent.inherited"


@pytest.mark.parametrize("analysis", ["static", "dynamic"])
def test_inherited_and_overridden_fields(analysis: str) -> None:
    """Keep inherited fields and collect subclass overrides independently."""
    code = """
    from pydantic import BaseModel, Field

    class Parent(BaseModel):
        inherited: str = Field(default="parent", description="An inherited field.")
        overridden: int = 1

    class Child(Parent):
        overridden: str = "child"
        own: bool = False
    """

    loader = {"static": temporary_visited_package, "dynamic": temporary_inspected_package}[analysis]
    with loader(
        "field_inheritance",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension()),
        search_sys_path=analysis == "dynamic",
    ) as package:
        parent_fields = package["Parent"].extra["griffe_pydantic"]["fields"]()
        child_fields = package["Child"].extra["griffe_pydantic"]["fields"]()

        # Inherited fields keep their defining class and description.
        assert set(child_fields) == {"inherited", "overridden", "own"}
        assert child_fields["inherited"].is_alias
        assert child_fields["inherited"].canonical_path == "field_inheritance.Parent.inherited"
        assert child_fields["inherited"].docstring.value == "An inherited field."

        # An override must not change the parent model's field metadata.
        assert child_fields["overridden"].canonical_path == "field_inheritance.Child.overridden"
        assert str(child_fields["overridden"].annotation) == "str"
        assert child_fields["overridden"].value == "'child'"
        assert str(parent_fields["overridden"].annotation) == "int"
        assert parent_fields["overridden"].value == "1"


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


def test_ignoring_properties() -> None:
    """Properties are not fields and must be ignored."""
    code = """
    from pydantic import BaseModel, field

    class Base(BaseModel):
        @property
        def a(self) -> int:
            return 0

    class Model(Base):
        b: int = field(default=1)
    """
    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False)),
    ) as package:
        assert "pydantic-field" not in package["Model.a"].labels


def test_process_non_model_base_class_fields() -> None:
    """Fields in a non-model base class must be processed."""
    code = """
    from pydantic import BaseModel, field

    class A:
        a: int = 0

    class B(BaseModel, A):
        b: int = 1
    """
    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False)),
    ) as package:
        assert "pydantic-field" in package["B.a"].labels


def test_annotated_fields() -> None:
    """Test the extension with annotated fields."""
    code = """
    from pydantic import BaseModel, Field
    from typing import Annotated

    class Model(BaseModel):
        a: Annotated[int, Field(description="Some description.")]
        b: Annotated[int, Field(description="Another description.")] = 1
    """
    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False)),
    ) as package:
        assert package["Model.a"].is_attribute
        assert package["Model.b"].is_attribute
        assert "pydantic-field" in package["Model.a"].labels
        assert "pydantic-field" in package["Model.b"].labels
        assert package["Model.a"].docstring.value == "Some description."
        assert package["Model.b"].docstring.value == "Another description."
        # Check that annotation is the actual type, not Annotated[...]
        assert str(package["Model.a"].annotation) == "int"
        assert str(package["Model.b"].annotation) == "int"


def test_ignore_private_attrs() -> None:
    """Test the extension ignores private attributes."""
    code = """
    from pydantic import BaseModel, PrivateAttr

    class Model(BaseModel):
        field: str
        _private: str = PrivateAttr(default="secret")
    """
    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False)),
    ) as package:
        assert "pydantic-field" in package["Model.field"].labels
        assert "pydantic-field" not in package["Model._private"].labels


def test_ignore_private_attrs_annotated() -> None:
    """Test the extension ignores private attributes with Annotated syntax."""
    code = """
    from pydantic import BaseModel, PrivateAttr
    from typing import Annotated

    class Model(BaseModel):
        field: str
        _private: Annotated[str, PrivateAttr(default="secret")]
    """
    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False)),
    ) as package:
        assert "pydantic-field" in package["Model.field"].labels
        assert "pydantic-field" not in package["Model._private"].labels


def test_field_description_with_dedent() -> None:
    """Test that field descriptions wrapped in textwrap.dedent() are extracted."""
    code = """
    from textwrap import dedent
    from pydantic import BaseModel, Field

    class Model(BaseModel):
        field1: int = Field(
            description=dedent('''
                This is a multiline description.
                With multiple lines.
            ''')
        )
        field2: str = Field(default="test", description=dedent("Single line dedented."))
    """
    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False)),
    ) as package:
        assert package["Model.field1"].is_attribute
        assert "pydantic-field" in package["Model.field1"].labels
        assert package["Model.field1"].docstring is not None
        assert "This is a multiline description." in package["Model.field1"].docstring.value
        assert "With multiple lines." in package["Model.field1"].docstring.value

        assert package["Model.field2"].is_attribute
        assert "pydantic-field" in package["Model.field2"].labels
        assert package["Model.field2"].docstring is not None
        assert package["Model.field2"].docstring.value == "Single line dedented."


def test_field_description_with_cleandoc() -> None:
    """Test that field descriptions wrapped in inspect.cleandoc() are extracted."""
    code = """
    from inspect import cleandoc
    from pydantic import BaseModel, Field

    class Model(BaseModel):
        field1: int = Field(
            description=cleandoc('''
                This is a multiline description.
                With multiple lines.
            ''')
        )
        field2: str = Field(default="test", description=cleandoc("Single line cleandoc."))
    """
    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False)),
    ) as package:
        assert package["Model.field1"].is_attribute
        assert "pydantic-field" in package["Model.field1"].labels
        assert package["Model.field1"].docstring is not None
        assert "This is a multiline description." in package["Model.field1"].docstring.value
        assert "With multiple lines." in package["Model.field1"].docstring.value

        assert package["Model.field2"].is_attribute
        assert "pydantic-field" in package["Model.field2"].labels
        assert package["Model.field2"].docstring is not None
        assert package["Model.field2"].docstring.value == "Single line cleandoc."


def test_field_description_with_annotated_and_dedent() -> None:
    """Test that field descriptions with Annotated and dedent() are extracted."""
    code = """
    from textwrap import dedent
    from pydantic import BaseModel, Field
    from typing import Annotated

    class Model(BaseModel):
        field1: Annotated[int, Field(
            description=dedent('''
                This is a multiline description.
                With multiple lines.
            ''')
        )]
    """
    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False)),
    ) as package:
        assert package["Model.field1"].is_attribute
        assert "pydantic-field" in package["Model.field1"].labels
        assert package["Model.field1"].docstring is not None
        assert "This is a multiline description." in package["Model.field1"].docstring.value
        assert "With multiple lines." in package["Model.field1"].docstring.value


def test_typing_extensions_annotated_fields() -> None:
    """Test the extension with fields annotated through `typing_extensions`."""
    code = """
    from pydantic import BaseModel, Field
    import typing_extensions as te

    class Model(BaseModel):
        a: te.Annotated[int, Field(description="Some description.", le=10)]
        b: te.Annotated[int, Field(description="Another description.")] = 1
    """
    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False)),
    ) as package:
        assert "pydantic-field" in package["Model.a"].labels
        assert "pydantic-field" in package["Model.b"].labels
        assert package["Model.a"].docstring.value == "Some description."
        assert package["Model.b"].docstring.value == "Another description."
        # The `Annotated` wrapper is unwrapped, leaving the actual type.
        assert str(package["Model.a"].annotation) == "int"
        assert str(package["Model.b"].annotation) == "int"
        # Constraints declared inside `Annotated` are collected too.
        assert package["Model.a"].extra["griffe_pydantic"]["constraints"] == {"le": "10"}


def test_serialize_by_alias_disabled_static() -> None:
    """Test that without serialize_by_alias, static analysis uses Python attribute names."""
    code = """
    from pydantic import BaseModel, Field

    class Model(BaseModel):
        internal_name: str = Field(default="test", serialization_alias="external_name")
        regular_field: int = Field(default=42)
    """
    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False, serialize_by_alias=False)),
    ) as package:
        fields = package["Model"].extra["griffe_pydantic"]["fields"]()
        assert "internal_name" in fields
        assert "regular_field" in fields
        assert "external_name" not in fields


@pytest.mark.parametrize("analysis", ["static", "dynamic"])
def test_serialize_by_alias_enabled(analysis: str) -> None:
    """Test that serialize_by_alias extension setting uses serialization_alias as the field name."""
    code = """
    from pydantic import BaseModel, Field

    class Model(BaseModel):
        internal_name: str = Field(default="test", serialization_alias="external_name")
        regular_field: int = Field(default=42)
    """
    loader = {"static": temporary_visited_package, "dynamic": temporary_inspected_package}[analysis]
    with loader(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(PydanticExtension(schema=False, serialize_by_alias=True)),
        search_sys_path=analysis == "dynamic",
    ) as package:
        model = package["Model"]
        assert model.labels == {"pydantic-model"}

        fields = model.extra["griffe_pydantic"]["fields"]()
        assert "internal_name" not in fields
        assert "regular_field" in fields
        assert "external_name" in fields
