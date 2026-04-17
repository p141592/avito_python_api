# Repository Guidelines

## Project Structure & Module Organization

The package lives in `avito/`. Current modules are small and flat:

- `avito/client/` contains the API client entry point.
- `avito/settings.py` loads credentials from environment variables.
- `avito/messages/` is the start of domain-specific models.
- `docs/` stores Avito API reference payloads and examples in JSON/Markdown.

Keep new code inside the `avito/` package and group it by API area (`ads/`, `messenger/`, `orders/`) as described in `STYLEGUIDE.md`. Avoid adding raw integration logic to `__init__.py`.

## Build, Test, and Development Commands

- `poetry install` installs runtime and developer dependencies.
- `poetry run python -m avito` runs the package entry point if you add CLI behavior.
- `poetry build` builds the wheel and source distribution.
- `make pypi` builds and publishes the package to PyPI.

There is no dedicated local server or demo app in this repository. Treat `poetry build` as the minimum release validation step.

## Coding Style & Naming Conventions

Target Python is `3.12` and dependency management is handled by Poetry. Follow `STYLEGUIDE.md` for architectural rules:

- Use 4-space indentation and full type annotations on public code.
- Prefer clear domain models over loose `dict` payloads.
- Keep HTTP, auth, mapping, and settings concerns separated.
- Use `snake_case` for functions/modules, `PascalCase` for classes, and uppercase names for environment variables such as `AVITO_CLIENT_ID`.

`STYLEGUIDE.md` prefers dataclasses for domain models; use `pydantic-settings` only at configuration boundaries.

## Testing Guidelines

Automated tests are not set up yet. Add new tests under `tests/` with `test_*.py` names and mirror the package structure, for example `tests/client/test_client.py`.

When adding behavior, include at least one regression test and run it with `poetry run pytest` once `pytest` is added to the project. For API-facing changes, cover auth failures, retry behavior, and response mapping.

## Commit & Pull Request Guidelines

Recent commits use short, imperative summaries in Russian, for example `Подготовка к разработке`. Keep commit subjects concise, specific, and focused on one change.

Pull requests should include:

- a short description of the behavioral change;
- linked issue or task when available;
- notes about new environment variables, endpoints, or publishing impact;
- sample request/response snippets when API behavior changes.
