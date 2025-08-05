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
- **`on_package_loaded`** – Detect models once the whole package is loaded.

### on_class_instance

```
on_class_instance(
    *, node: AST | ObjectNode, cls: Class, **kwargs: Any
) -> None

```

Detect and prepare Pydantic models.

### on_package_loaded

```
on_package_loaded(*, pkg: Module, **kwargs: Any) -> None

```

Detect models once the whole package is loaded.

## get_templates_path

```
get_templates_path() -> Path

```

Return the templates directory path.

## common

Deprecated. Import from `griffe_pydantic` directly instead.

## dynamic

Deprecated. Import from `griffe_pydantic` directly instead.

## extension

Deprecated. Import from `griffe_pydantic` directly instead.

## static

Deprecated. Import from `griffe_pydantic` directly instead.
