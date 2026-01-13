# griffe_pydantic

griffe-pydantic package.

Griffe extension for Pydantic.

Modules:

- **`common`** – Deprecated. Import from griffe_pydantic directly instead.
- **`dynamic`** – Deprecated. Import from griffe_pydantic directly instead.
- **`extension`** – Deprecated. Import from griffe_pydantic directly instead.
- **`static`** – Deprecated. Import from griffe_pydantic directly instead.

Classes:

- **`PydanticExtension`** – Griffe extension for Pydantic.

Functions:

- **`get_templates_path`** – Return the templates directory path.

## PydanticExtension

```
PydanticExtension(*, schema: bool = False)
```

Bases: `Extension`

Griffe extension for Pydantic.

Parameters:

- **`schema`** (`bool`, default: `False` ) – Whether to compute and store the JSON schema of models.

Methods:

- **`on_class_instance`** – Detect and prepare Pydantic models.
- **`on_package`** – Detect models once the whole package is loaded.

Source code in `src/griffe_pydantic/_internal/extension.py`

```
def __init__(self, *, schema: bool = False) -> None:
    """Initialize the extension.

    Parameters:
        schema: Whether to compute and store the JSON schema of models.
    """
    super().__init__()
    self._schema = schema
    self._processed: set[str] = set()
    self._recorded: list[tuple[ObjectNode, Class]] = []
```

### on_class_instance

```
on_class_instance(
    *, node: AST | ObjectNode, cls: Class, **kwargs: Any
) -> None
```

Detect and prepare Pydantic models.

Source code in `src/griffe_pydantic/_internal/extension.py`

```
def on_class_instance(self, *, node: ast.AST | ObjectNode, cls: Class, **kwargs: Any) -> None:  # noqa: ARG002
    """Detect and prepare Pydantic models."""
    # Prevent running during static analysis.
    if isinstance(node, ast.AST):
        return

    try:
        import pydantic  # noqa: PLC0415
    except ImportError:
        _logger.warning("could not import pydantic - models will not be detected")
        return

    if issubclass(node.obj, pydantic.BaseModel):
        self._recorded.append((node, cls))
```

### on_package

```
on_package(*, pkg: Module, **kwargs: Any) -> None
```

Detect models once the whole package is loaded.

Source code in `src/griffe_pydantic/_internal/extension.py`

```
def on_package(self, *, pkg: Module, **kwargs: Any) -> None:  # noqa: ARG002
    """Detect models once the whole package is loaded."""
    for node, cls in self._recorded:
        self._processed.add(cls.canonical_path)
        dynamic._process_class(node.obj, cls, processed=self._processed, schema=self._schema)
    static._process_module(pkg, processed=self._processed, schema=self._schema)
```

## get_templates_path

```
get_templates_path() -> Path
```

Return the templates directory path.

Source code in `src/griffe_pydantic/__init__.py`

```
def get_templates_path() -> Path:
    """Return the templates directory path."""
    return Path(__file__).parent / "templates"
```

## common

Deprecated. Import from `griffe_pydantic` directly instead.

## dynamic

Deprecated. Import from `griffe_pydantic` directly instead.

## extension

Deprecated. Import from `griffe_pydantic` directly instead.

## static

Deprecated. Import from `griffe_pydantic` directly instead.
