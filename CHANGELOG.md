# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [1.2.0](https://github.com/mkdocstrings/griffe-pydantic/releases/tag/1.2.0) - 2026-01-13

<small>[Compare with 1.1.8](https://github.com/mkdocstrings/griffe-pydantic/compare/1.1.8...1.2.0)</small>

### Features

- Support Pydantic Field defined via Annotated ([5021332](https://github.com/mkdocstrings/griffe-pydantic/commit/502133277db3201e5003e229c914539bc0fc06fd) by Michele Dolfi). [Issue-37](https://github.com/mkdocstrings/griffe-pydantic/issues/37), [PR-46](https://github.com/mkdocstrings/griffe-pydantic/pull/46)

## [1.1.8](https://github.com/mkdocstrings/griffe-pydantic/releases/tag/1.1.8) - 2025-10-14

<small>[Compare with 1.1.7](https://github.com/mkdocstrings/griffe-pydantic/compare/1.1.7...1.1.8)</small>

### Bug Fixes

- Don't process module aliases (all modules eventually get processed) ([87ab586](https://github.com/mkdocstrings/griffe-pydantic/commit/87ab5866a03ed9b901b8e62ce8055edbeec7d3a9) by Timothée Mazzucotelli). [Issue-45](https://github.com/mkdocstrings/griffe-pydantic/issues/45)
- Prevent crashes while computing JSON schemas ([ec1b424](https://github.com/mkdocstrings/griffe-pydantic/commit/ec1b42404a2eecaab87041830f6e2c4176d18b80) by Timothée Mazzucotelli).

## [1.1.7](https://github.com/mkdocstrings/griffe-pydantic/releases/tag/1.1.7) - 2025-09-05

<small>[Compare with 1.1.6](https://github.com/mkdocstrings/griffe-pydantic/compare/1.1.6...1.1.7)</small>

### Build

- Depend on Griffe 1.14 ([08f955c](https://github.com/mkdocstrings/griffe-pydantic/commit/08f955c86c52cc48f32868ab87260b792139d0d2) by Timothée Mazzucotelli).

## [1.1.6](https://github.com/mkdocstrings/griffe-pydantic/releases/tag/1.1.6) - 2025-08-06

<small>[Compare with 1.1.5](https://github.com/mkdocstrings/griffe-pydantic/compare/1.1.5...1.1.6)</small>

### Bug Fixes

- Make Pydantic imports lazy ([5df7a47](https://github.com/mkdocstrings/griffe-pydantic/commit/5df7a47bfef9f32ca726957891659b40912bb036) by Timothée Mazzucotelli). [Issue-39](https://github.com/mkdocstrings/griffe-pydantic/issues/39)

## [1.1.5](https://github.com/mkdocstrings/griffe-pydantic/releases/tag/1.1.5) - 2025-08-05

<small>[Compare with 1.1.4](https://github.com/mkdocstrings/griffe-pydantic/compare/1.1.4...1.1.5)</small>

### Code Refactoring

- Rename logger to `griffe_pydantic` ([ad436b5](https://github.com/mkdocstrings/griffe-pydantic/commit/ad436b5a5202e9f599c1021ad16498791f19cbfb) by Timothée Mazzucotelli).
- Use DEBUG log level for unhandled objects ([1f33b32](https://github.com/mkdocstrings/griffe-pydantic/commit/1f33b320dc849a7525f740e82b5a5a869f9c0a36) by Martin Stancsics). [Issue-31](https://github.com/mkdocstrings/griffe-pydantic/issues/31), [PR-38](https://github.com/mkdocstrings/griffe-pydantic/pull/38)

## [1.1.4](https://github.com/mkdocstrings/griffe-pydantic/releases/tag/1.1.4) - 2025-03-26

<small>[Compare with 1.1.3](https://github.com/mkdocstrings/griffe-pydantic/compare/1.1.3...1.1.4)</small>

### Bug Fixes

- Don't process properties as fields ([2977b21](https://github.com/mkdocstrings/griffe-pydantic/commit/2977b2100c979998fa303292071ce7ad26edcb95) by Timothée Mazzucotelli). [Issue-29](https://github.com/mkdocstrings/griffe-pydantic/issues/29)

## [1.1.3](https://github.com/mkdocstrings/griffe-pydantic/releases/tag/1.1.3) - 2025-03-20

<small>[Compare with 1.1.2](https://github.com/mkdocstrings/griffe-pydantic/compare/1.1.2...1.1.3)</small>

### Bug Fixes

- Handle field validators targetting all fields with `"*"` ([449487f](https://github.com/mkdocstrings/griffe-pydantic/commit/449487faf7bd28f49daf0721c607c5f762831a4b) by Timothée Mazzucotelli). [Issue-22](https://github.com/mkdocstrings/griffe-pydantic/issues/22)
- Handle inherited fields ([c41a776](https://github.com/mkdocstrings/griffe-pydantic/commit/c41a776f63b60b4cf2a964b19b7ef0545f0b7872) by Timothée Mazzucotelli). [Issue-17](https://github.com/mkdocstrings/griffe-pydantic/issues/17)

### Code Refactoring

- Move code to internal API, update docs accordingly ([2f37b7e](https://github.com/mkdocstrings/griffe-pydantic/commit/2f37b7e3810498a632467a23999a7a69d05a84d6) by Timothée Mazzucotelli).
- Run dynamic analysis once package is loaded ([6e3ab4f](https://github.com/mkdocstrings/griffe-pydantic/commit/6e3ab4fcd6e758d1c7c8851a2b60780206bca137) by Timothée Mazzucotelli). [Issue-19](https://github.com/mkdocstrings/griffe-pydantic/issues/19)

## [1.1.2](https://github.com/mkdocstrings/griffe-pydantic/releases/tag/1.1.2) - 2025-02-18

<small>[Compare with 1.1.1](https://github.com/mkdocstrings/griffe-pydantic/compare/1.1.1...1.1.2)</small>

### Bug Fixes

- Use `set.discard` instead of `set.remove` to avoid key error ([2684be7](https://github.com/mkdocstrings/griffe-pydantic/commit/2684be718bfcb76b41d7ae92f8121f72034fd396) by Timothée Mazzucotelli). [Issue-26](https://github.com/mkdocstrings/griffe-pydantic/issues/26)

## [1.1.1](https://github.com/mkdocstrings/griffe-pydantic/releases/tag/1.1.1) - 2025-02-17

<small>[Compare with 1.1.0](https://github.com/mkdocstrings/griffe-pydantic/compare/1.1.0...1.1.1)</small>

### Bug Fixes

- Don't label `ClassVar`-annotated attributes as Pydantic fields ([0dbf958](https://github.com/mkdocstrings/griffe-pydantic/commit/0dbf958775ed488bda7f975ab3e3aadf4c71786b) by Miradil Zeynalli). [Issue-18](https://github.com/mkdocstrings/griffe-pydantic/issues/18), [PR-25](https://github.com/mkdocstrings/griffe-pydantic/pull/25), Co-authored-by: Timothée Mazzucotelli <dev@pawamoy.fr>
- Don't crash when trying to evaluate AST literals (field descriptions) ([b41bf46](https://github.com/mkdocstrings/griffe-pydantic/commit/b41bf463c44b9ed0b6cf6a7f10cb41d89477c926) by Timothée Mazzucotelli). [Issue-16](https://github.com/mkdocstrings/griffe-pydantic/issues/16)

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
