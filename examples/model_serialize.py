from pydantic import BaseModel, ConfigDict, Field


class UserModel(BaseModel):
    """A user model with serialization aliases.

    When the extension is configured with `show_as_alias=True`, fields with
    `alias` will appear under their alias names in the documentation.
    """

    model_config = ConfigDict(frozen=False)

    user_id: int = Field(alias="id")
    """Unique user identifier, serialized as 'id'."""

    full_name: str = Field(default="Anonymous", alias="name")
    """User's full name, serialized as 'name'."""

    email_address: str
    """User's email address."""

    is_active: bool = Field(default=True, alias="active")
    """Whether the user is active, serialized as 'active'."""
