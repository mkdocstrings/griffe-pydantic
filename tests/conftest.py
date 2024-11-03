"""Configuration for the pytest test suite."""

import pytest
from markdown import Markdown
from mkdocstrings_handlers.python.handler import PythonHandler


@pytest.fixture(name="python_handler")
def fixture_python_handler() -> PythonHandler:
    """Return a PythonHandler instance."""
    handler = PythonHandler("python", "material")
    handler.update_env(md=Markdown(extensions=["toc"]), config={})
    handler.env.filters["convert_markdown"] = lambda *args, **kwargs: str(args) + str(kwargs)
    return handler
