"""griffe-pydantic package.

Griffe extension for Pydantic.
"""

from __future__ import annotations

from pathlib import Path

from griffe_pydantic._internal.extension import PydanticExtension


def get_templates_path() -> Path:
    """Return the templates directory path."""
    return Path(__file__).parent / "templates"


__all__: list[str] = ["PydanticExtension", "get_templates_path"]
