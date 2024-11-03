# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [1.1.0](https://github.com/mkdocstrings/griffe-pydantic/releases/tag/1.1.0) - 2024-11-03

<small>[Compare with 1.0.0](https://github.com/mkdocstrings/griffe-pydantic/compare/1.0.0...1.1.0)</small>

### Features

- Also support `pydantic.model_validator` ([c83074d](https://github.com/mkdocstrings/griffe-pydantic/commit/c83074da16d529002793fb5ea27ccb80d35572ed) by Timothée Mazzucotelli). [Issue-4](https://github.com/mkdocstrings/griffe-pydantic/issues/4)

### Bug Fixes

- Don't crash on new config based on `ConfigDict` ([c23ba7c](https://github.com/mkdocstrings/griffe-pydantic/commit/c23ba7c490833bf7632607fa88020d5274e0822a) by Timothée Mazzucotelli). [Issue-6](https://github.com/mkdocstrings/griffe-pydantic/issues/6)
- Don't process class aliases, as real classes are processed at some point anyway ([24a10f7](https://github.com/mkdocstrings/griffe-pydantic/commit/24a10f7347949cfe9b4392f370913c4cadd5b437) by SimonBoothroyd). [Issue-8](https://github.com/mkdocstrings/griffe-pydantic/issues/8), [PR-7](https://github.com/mkdocstrings/griffe-pydantic/pull/7), Co-authored-by: Timothée Mazzucotelli <dev@pawamoy.fr>

### Code Refactoring

- Use new autoref elements instead of deprecated spans ([3e1020e](https://github.com/mkdocstrings/griffe-pydantic/commit/3e1020e347797dfffdfb82347f1878ccf4627ec8) by Timothée Mazzucotelli).

## [1.0.0](https://github.com/mkdocstrings/griffe-pydantic/releases/tag/1.0.0) - 2024-10-12

<small>[Compare with first commit](https://github.com/mkdocstrings/griffe-pydantic/compare/397ad6fb94b1d5b11e5cb25bdd7af473f73a396e...1.0.0)</small>

### Features

- Make the project public! ([b19ad56](https://github.com/mkdocstrings/griffe-pydantic/commit/b19ad561b8952c15b41cad833d4167af1bc2b20f) by Timothée Mazzucotelli).
