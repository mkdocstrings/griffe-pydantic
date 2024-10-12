"""Tests for the `extension` module."""

from __future__ import annotations

from griffe import Extensions, temporary_visited_package

from griffe_pydantic.extension import PydanticExtension

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


def test_extension() -> None:
    """Test the extension."""
    with temporary_visited_package(
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
        assert config == {"frozen": "False"}

        schema = package.classes["ExampleModel"].extra["griffe_pydantic"]["schema"]
        assert schema.startswith('{\n  "description"')
