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

