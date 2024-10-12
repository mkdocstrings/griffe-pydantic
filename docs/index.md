---
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

```python exec="1" result="python"
print('--8<-- "docs/examples/model_ext.py"')
```

///

/// tab | Without extension

::: model_noext.ExampleModel
    options:
      heading_level: 3

///


/// tab | With extension

::: model_ext.ExampleModel
    options:
      heading_level: 3
      extensions:
      - griffe_pydantic

///
