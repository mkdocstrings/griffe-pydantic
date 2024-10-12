# griffe-pydantic

[![ci](https://github.com/mkdocstrings/griffe-pydantic/workflows/ci/badge.svg)](https://github.com/mkdocstrings/griffe-pydantic/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://mkdocstrings.github.io/griffe-pydantic/)
[![pypi version](https://img.shields.io/pypi/v/griffe-pydantic.svg)](https://pypi.org/project/griffe-pydantic/)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-708FCC.svg?style=flat)](https://gitpod.io/#https://github.com/mkdocstrings/griffe-pydantic)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://app.gitter.im/#/room/#griffe-pydantic:gitter.im)

[Griffe](https://mkdocstrings.github.io/griffe/) extension for [Pydantic](https://github.com/pydantic/pydantic).

## Installation

```bash
pip install griffe-pydantic
```

## Usage

### Command-line

```bash
griffe dump mypackage -e griffe_pydantic
```

See [command-line usage in Griffe's documentation](https://mkdocstrings.github.io/griffe/extensions/#on-the-command-line).

### Python

```python
import griffe

griffe.load(
    "mypackage",
    extensions=griffe.load_extensions(
        [{"griffe_pydantic": {"schema": True}}]
    )
)
```

See [programmatic usage in Griffe's documentation](https://mkdocstrings.github.io/griffe/extensions/#programmatically).

### MkDocs

```yaml title="mkdocs.yml"
plugins:
- mkdocstrings:
    handlers:
      python:
        options:
          extensions:
          - griffe_pydantic:
              schema: true
```


See [MkDocs usage in Griffe's documentation](https://mkdocstrings.github.io/griffe/extensions/#in-mkdocs).
