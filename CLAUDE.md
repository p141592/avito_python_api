# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make test          # run all tests
make typecheck     # mypy strict check on avito/
make lint          # ruff check
make fmt           # ruff format
make check         # test → typecheck → lint → build (full gate)
make build         # poetry build

# single test
poetry run pytest tests/test_facade.py::test_name
```

## Architecture

**Entry point**: `avito/client.py` — `AvitoClient` is the single public facade. It exposes factory methods (`account()`, `ad()`, `chat()`, etc.) that return domain objects.

**Layers** (strict separation, no mixing):

| Layer | Location | Responsibility |
|---|---|---|
| `AvitoClient` | `avito/client.py` | Public facade, factory methods |
| `SectionClient` | `avito/<domain>/client.py` | HTTP calls for one API section |
| `Transport` | `avito/core/transport.py` | httpx, retries, error mapping, token injection |
| `AuthProvider` | `avito/auth/provider.py` | Token cache, refresh, 401 handling |
| `Mapper` | `avito/<domain>/mappers.py` | JSON → typed dataclass |
| Config | `avito/config.py`, `avito/auth/settings.py` | `AvitoSettings`, `AuthSettings` |

**Domain packages** follow a uniform structure: `__init__.py`, `domain.py` (DomainObject subclass), `client.py` (SectionClient), `models.py` (frozen dataclasses), `mappers.py`, optional `enums.py`.

**Public models** are `@dataclass(slots=True, frozen=True)`, inherit `SerializableModel` (provides `to_dict()` / `model_dump()`), and never expose transport fields.

**Exceptions** live in `avito/core/exceptions.py`. `AvitoError` is the base. HTTP codes map to specific types: 401→`AuthenticationError`, 403→`AuthorizationError`, 429→`RateLimitError`, etc. These two are siblings, not parent/child.

**Pagination**: `PaginatedList[T]` is lazy. First page loads on creation; subsequent pages load on iteration. `materialize()` loads all pages.

**Testing**: `tests/fake_transport.py` provides `FakeTransport` — inject it instead of real HTTP. Tests are Arrange/Act/Assert, one scenario per test. Test names describe behavior, not the method under test.

## API coverage and inventory

`docs/avito/api/` contains Swagger/OpenAPI specs (23 documents, 204 operations) — the authoritative source of truth for all API contracts.

`docs/avito/inventory.md` is the canonical mapping of every API operation to its SDK domain object and public method. Before implementing any new method, check the inventory to find:
- which `пакет_sdk` and `доменный_объект` it belongs to
- the expected `публичный_метод_sdk`, request/response type names
- whether the operation is deprecated (`deprecated: да` → wrap in a legacy domain object)

**When adding a new API method**: add it to the `## Операции` table in `docs/avito/inventory.md` (between the `operations-table:start/end` markers) following the existing format.

All 204 operations from the specs must be covered. A missing method is a defect.

## STYLEGUIDE.md — strict compliance is mandatory

`STYLEGUIDE.md` is a normative document. All code changes **must** comply with it. When there is a conflict between any consideration and the STYLEGUIDE, the STYLEGUIDE takes priority.

The most critical prohibitions that must never be violated:

- Mixing layers: transport/auth/parsing/domain logic in one class.
- Returning `dict` or `Any` from public methods.
- Using `resource_id` instead of concrete names (`item_id`, `order_id`).
- Annotating `list[T]` where `PaginatedList[T]` is returned at runtime.
- Making `AuthenticationError` a subclass of `AuthorizationError` (or vice versa).
- Writing error messages in mixed languages (Russian only).
- Injecting methods via `setattr`/`globals()` at runtime.
- Duplicating behavior through two different public methods without deprecation.
- Leaking internal-layer request-DTOs into public signatures.
- Adding dead code: unused imports, type aliases, TypeVars.

## Key conventions (from STYLEGUIDE.md)

- All public methods return typed SDK models, never raw `dict`.
- Field names are concrete: `item_id`, `user_id` — never `resource_id`.
- Public method arguments are primitives or domain models — internal request-DTOs must not leak out.
- Write-operations that accept `dry_run: bool = False` must build the same payload in both modes; with `dry_run=True` transport must not be called.
- `Any` is forbidden except at JSON boundary layers (with a local comment).
- Error messages are written in Russian only — no mixed languages.
- No dynamic method injection (`setattr`, `globals()` patching).
- `PaginatedList[T]` annotation must match runtime — never annotate as `list[T]` if you return `PaginatedList[T]`.
- `AuthenticationError` (401) and `AuthorizationError` (403) must not be in an inheritance relation.
- Dead code (unused imports, aliases, TypeVars) must be removed.
- Request-objects of the internal layer must not appear in public domain-method signatures.
