---
title: Overview
hide:
- feedback
---

--8<-- "README.md"

<style>
  .mkdocstrings > h2,
  .mkdocstrings > h3,
  .mkdocstrings > h4,
  .mkdocstrings > h5,
  .mkdocstrings > h6 {
    display: none;
  }
</style>

## Examples

/// tab | Pydantic model

```python
--8<-- "examples/model_ext.py"
```

///

/// tab | Without extension

```md exec="true" updatetoc="false"
::: model_noext.ExampleModel
    options:
      heading_level: 3
      skip_local_inventory: true
```

///

/// tab | With extension

```md exec="true" updatetoc="false"
::: model_ext.ExampleModel
    options:
      heading_level: 3
      extensions:
      - griffe_pydantic
      skip_local_inventory: true
```

///

### Serialization Aliases

When the extension is configured with `serialize_by_alias=True`, fields with a `serialization_alias` will appear under their alias names in the documentation. This is useful for APIs where the serialized output uses different field names than the Python attribute names. See [Pydantic's alias documentation](https://docs.pydantic.dev/latest/concepts/alias/) for more information.

To enable this feature in your documentation configuration, configure the extension as follows:

```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          extensions:
            - griffe_pydantic:
                serialize_by_alias: true
```

/// tab | Pydantic model

```python
--8<-- "examples/model_serialize.py"
```

///

/// tab | Without alias

```md exec="true" updatetoc="false"
::: model_noserialize.UserModel
    options:
      heading_level: 4
      extensions:
      - griffe_pydantic: {serialize_by_alias: false}
      skip_local_inventory: true
```

///

/// tab | With alias

```md exec="true" updatetoc="false"
::: model_serialize.UserModel
    options:
      heading_level: 4
      extensions:
      - griffe_pydantic: {serialize_by_alias: true}
      skip_local_inventory: true
```

///

