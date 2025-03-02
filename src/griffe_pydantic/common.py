"""Deprecated. Import from `griffe_pydantic` directly instead."""

import warnings
from typing import Any

from griffe_pydantic._internal import common

# YORE: Bump 2: Remove file.


def __getattr__(name: str) -> Any:
    warnings.warn(
        "Importing from `griffe_pydantic.common` is deprecated. Import from `griffe_pydantic` directly instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    try:
        return getattr(common, name)
    except AttributeError:
        return getattr(common, name.removeprefix("_"))
