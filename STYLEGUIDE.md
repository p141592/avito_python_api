# STYLEGUIDE

## Purpose

This document defines the unified development style for the Avito API Python SDK.
The library's goals:

- provide a clear and transparent public API;
- hide the technical details of authorization, retries, and data enrichment;
- return strictly typed objects of its own classes;
- maintain a clean package architecture organized by Avito API sections;
- ensure predictable behavior under unstable network conditions.

This document is normative. New modules and refactoring of existing code must comply with these rules.

## Core Principles

Principles are listed in descending priority order when they conflict.

- Code must be readable before it is compact.
- Explicit over implicit: every public contract is readable without knowledge of implementation details.
- Simple over complex: add abstraction only when there is no way around it.
- For each task there must be one obvious way — not two, not three.
- Errors must not pass silently: invalid state is detected as early as possible.
- The public API of the library must be simple; internal details must be encapsulated.
- Each layer is responsible for its own task only: transport, auth, API clients, domain models, mapping, errors.
- External code must not work with raw `dict[str, Any]` when a typed object can be returned instead.
- Exceptions must be explicit and domain-specific; no `assert False` for flow control.
- All network interaction is considered potentially unstable.
- Public SDK contracts are fixed explicitly and changed only deliberately.

## Target Package Architecture

Avito API sections are organized as packages. Recommended structure:

```text
avito/
  __init__.py
  client.py
  config.py
  auth/
    __init__.py
    models.py
    provider.py
    settings.py
  core/
    __init__.py
    transport.py
    retries.py
    exceptions.py
    types.py
    pagination.py
  accounts/
    __init__.py
    client.py
    models.py
    mappers.py
  ads/
    __init__.py
    client.py
    models.py
    enums.py
    mappers.py
  promotion/
    __init__.py
    client.py
    models.py
    enums.py
    mappers.py
  messenger/
    __init__.py
    client.py
    models.py
    enums.py
    mappers.py
  orders/
    __init__.py
    client.py
    models.py
    enums.py
    mappers.py
```

Rules:

- `core/` contains only shared infrastructure, with no logic specific to any API section.
- Each API section lives in its own package: `ads`, `messenger`, `orders`, `autoload`, etc.
- Only modules belonging to that section are allowed inside each section package.
- `avito/client.py` and `avito/__init__.py` contain only the high-level entry point and public exports.

## Public API

The public API must be object-oriented and obvious:

```python
client = AvitoClient(settings)
profile = client.account().get_self()
listing = client.ad(item_id=42, user_id=123).get()
stats = client.ad_stats(user_id=123).get_item_stats(item_ids=[42])
```

Rules:

- Methods must reflect domain actions, not HTTP details.
- `headers`, `token refresh`, `raw request payload` must not be exposed in the public API unless there is an explicit need.
- Public methods return domain models, collections of domain models, or typed result objects.
- Raw API responses are acceptable only in internal layers or in explicitly designated low-level methods.

### One Path Per Operation

For each operation in the public API there must be exactly one obvious way to perform it. If two different objects do the same thing, that is a design error.

- Duplicating behavior through different facades is forbidden: `ad().get_stats()` and `ad_stats().get_item_stats()` for the same dataset cannot coexist.
- If one method covers a specific case and another covers the general case, the specific one must be a wrapper around the general one, not an independent implementation.
- Type aliases (`Listing = AdItem`) without an explicit deprecation marker are forbidden: each public type must have one canonical name.

### What Constitutes the Public SDK Contract

The following are normatively part of the public contract:

- the `avito` package and its exports `AvitoClient`, `AvitoSettings`, `AuthSettings`;
- resource factory methods on `AvitoClient`, e.g. `account()`, `ad()`, `ad_stats()`, `promotion_order()`;
- public models from `avito.<domain>.models`;
- typed exceptions from `avito.core.exceptions`;
- the lazy pagination contract `PaginatedList`;
- stable serialization of public models via `to_dict()` and `model_dump()`;
- the safe diagnostic contract of `debug_info()`.

The following are normatively not part of the public contract:

- transport request/response shapes;
- internal mapper objects;
- `raw_payload`, transport-layer service dataclasses, and internal DTOs;
- the shape of the raw Avito API JSON response.

Internal changes are acceptable as long as public signatures, returned models, serialization, and exception types remain stable.

## Client Initialization

The user must have a simple path to the first working call.

Normatively supported ways to create a client (from simplest to most explicit):

```python
# 1. From environment variables
with AvitoClient.from_env() as avito:
    ...

# 2. Explicit credentials — required shortcut
with AvitoClient(client_id="...", client_secret="...") as avito:
    ...

# 3. Full configuration via settings
settings = AvitoSettings(auth=AuthSettings(client_id="...", client_secret="..."))
with AvitoClient(settings) as avito:
    ...
```

Rules:

- `AvitoClient` must accept `client_id` and `client_secret` directly without requiring an intermediate `AuthSettings` object.
- `AvitoClient.from_env()` is the official factory method for initializing from the environment.
- The nested `AvitoSettings → AuthSettings` path is acceptable as an explicit option but must not be the only one.

## Classes and Responsibilities

Required separation:

- `AvitoClient` — the root SDK facade.
- `SectionClient` classes — clients for specific API sections.
- `Transport` — HTTP request execution.
- `AuthProvider` — token acquisition and refresh.
- `Mapper` — JSON to domain model conversion.
- `Settings`/`Config` — SDK configuration.

Rules:

- One class, one explicit area of responsibility.
- Classes must not simultaneously handle HTTP, authorization, logging, and model transformation.
- "God object" classes containing logic for all API sections are forbidden.

## Dataclasses and Models

The primary model format for the SDK is `dataclass`.

Rules:

- Domain entities and response objects are described with `@dataclass(slots=True, frozen=True)` by default.
- If a model must be mutable, that must be a conscious exception and explicitly documented.
- Use concrete containers for lists: `list[Message]`, not just `list`.
- Use `T | None` for optional fields, not implicit defaults.
- Nested structures must also have their own typed dataclass models.
- Do not use `dict` as a substitute for a domain model.
- All public read/write methods return only normalized SDK models, not transport-layer objects.
- For stable public models, required and nullable fields must be explicitly defined.
- Each public model must provide uniform serialization via `to_dict()` and `model_dump()`.
- Serialization of public models must be JSON-compatible and recursive for nested SDK models.
- Transport/internal implementation fields are forbidden in public models.

Example:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class Message:
    id: str
    chat_id: str
    text: str | None
    created_at: datetime
```

## Domain Object Field Naming

Field names must precisely reflect what they store, without generalizations.

Rules:

- The abstract name `resource_id` is forbidden in domain objects. Use a concrete field name instead: `item_id`, `user_id`, `report_id`, `order_id`, etc.
- If a domain object takes multiple identifiers, each is declared as an explicit field with a domain-specific name.
- Field names in public models must not reflect HTTP details or upstream API JSON field names.

```python
# Correct
@dataclass(slots=True, frozen=True)
class Ad(DomainObject):
    item_id: int | None = None
    user_id: int | None = None

# Wrong
@dataclass(slots=True, frozen=True)
class Ad(DomainObject):
    resource_id: int | str | None = None  # unclear what is stored
    user_id: int | str | None = None
```

## Public Method Parameters

A public method must not require the user to construct internal SDK objects.

Rules:

- Public method arguments must be primitive types (`int`, `str`, `bool`, `float`) or well-known domain result models (not request objects).
- Request-DTOs used inside section clients must not appear in public domain method signatures.
- If a method requires a complex input object, it must accept its fields directly as keyword-only arguments.

```python
# Correct: primitives and keyword-only
def create_order(self, *, item_id: int, duration: int, price: int) -> PromotionActionResult:
    ...

# Wrong: internal request object leaks out
def create_order(self, *, items: list[BbipOrderItem]) -> PromotionActionResult:
    ...
```

## Fail-Fast and State Validation

Invalid object state must be detected as early as possible.

Rules:

- If a domain object cannot perform any operation without a specific identifier, that identifier must be validated at object creation time, not at the first method call.
- A factory method that creates an object in a knowingly incomplete state must return an object with a restricted interface (only the methods available without the ID), not an object with methods that fail at runtime.
- A configuration error (`ConfigurationError`) must be raised before the first HTTP request.
- Dates passed as parameters must accept `datetime` or a validated string format — a bare `str` without validation is not acceptable when the format matters.

## Pydantic and Validation

For this project `dataclass` is the standard for representing domain objects. `pydantic` must not be the foundational building block of the entire SDK model.

Acceptable uses of `pydantic`:

- reading configuration from the environment;
- validating complex external payloads at the system boundary, if it genuinely simplifies the code;
- prototyping before the final dataclass model exists.

Unacceptable uses:

- mixing `pydantic.BaseModel` and `dataclass` without a clear layer of responsibility;
- returning `BaseModel` as the primary public SDK format when a domain dataclass already exists.

## Typing and mypy

Strict typing is mandatory.

Rules:

- All functions, methods, class attributes, and return values must be annotated.
- `Any` is forbidden except in narrow boundary-layer locations with a local explanation.
- Use `mypy` in strict mode or as close to it as possible.
- Use `Protocol`, `TypeAlias`, `TypedDict` at boundaries where a dataclass is not yet applicable.
- JSON from an external API is first treated as a boundary type, then mapped to a dataclass.
- Do not return overly wide type unions such as `dict | list | str | None`.
- The return type annotation must precisely match the type of the value at runtime. If a method returns `PaginatedList`, the annotation must contain `PaginatedList`, not `list`.
- Dead code is not allowed: unused `TypeVar`s, imports, and aliases must be removed.

Minimum target `mypy` profile:

```toml
[tool.mypy]
python_version = "3.14"
strict = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_return_any = true
disallow_any_generics = true
no_implicit_optional = true
```

## HTTP and Transport Layer

All HTTP must go through a single transport layer.

Rules:

- Direct calls to `httpx.get()`/`httpx.post()` inside section clients are forbidden.
- Use `httpx.Client` or `httpx.AsyncClient` as an internal dependency of the transport layer.
- Timeouts are set explicitly.
- Authorization headers are injected by the transport/auth layer, not by business methods.
- URL construction, error handling, retries, and logging are concentrated in the transport.
- Transport details must not be part of public signatures, docstrings, or serialization.

Recommendation:

- Build a high-quality sync SDK first.
- The SDK is synchronous — this must be explicitly documented in the README and public API.
- An async version should be added as a separate layer, not mixed with sync in the same classes.

## Authorization

Authorization must be fully abstracted away from API methods.

Rules:

- API methods must not fetch tokens themselves.
- A separate `AuthProvider` must exist, responsible for token caching, refresh, and lifetime.
- On `401 Unauthorized`, the transport must initiate a controlled refresh rather than breaking the contract unpredictably.
- Authorization configuration is stored in `Settings`, not scattered throughout the code.

## Handling Unstable Connections

The network is unstable by default. This must be treated as part of the design.

Rules:

- The transport layer must have retries with a bounded number of attempts.
- Retries apply only to safe scenarios: timeout, connection errors, transient `5xx`, rate limiting under a clear policy.
- The retry policy must be centralized and configurable.
- Reasonable timeouts for connect/read/write are set on all requests.
- Errors after retry exhaustion are not suppressed; they are raised as domain exceptions.
- Retry logging must be informative but must not leak secrets.

Minimum expected entities:

- `RetryPolicy`
- `ApiTimeouts`
- `TransportError`
- `RateLimitError`
- `AuthorizationError`
- `UpstreamApiError`

## Errors and Exceptions

`assert` is not used to handle API errors.

Rules:

- A hierarchy of custom exceptions is created in `core/exceptions.py` for SDK errors.
- An error must contain at minimum: `operation`, HTTP status, Avito error code if present, a human-readable message, and safe metadata.
- `4xx` and `5xx` errors must be distinguished by type.
- Parsing errors and transport errors must be distinguished.
- Mapping of transport/HTTP/API errors to public SDK errors must be centralized.
- Secrets, tokens, and sensitive headers must be automatically sanitized in the message and metadata.
- An unknown upstream error must not leak out as a raw transport exception.
- All error messages are written in a single language — Russian. Mixing languages in error messages is forbidden.

Example hierarchy:

```python
class AvitoError(Exception): ...
class TransportError(AvitoError): ...
class ValidationError(AvitoError): ...
class AuthorizationError(AvitoError): ...     # 403: insufficient permissions
class AuthenticationError(AvitoError): ...    # 401: invalid credentials / token
class RateLimitError(AvitoError): ...
class ConflictError(AvitoError): ...
class UnsupportedOperationError(AvitoError): ...
class UpstreamApiError(AvitoError): ...
class ResponseMappingError(AvitoError): ...
```

`AuthenticationError` (401) and `AuthorizationError` (403) are semantically different errors; they must not be in an inheritance relationship. A user catching `AuthorizationError` must not unexpectedly receive authentication errors.

Normative mapping:

- `400` and `422` map to `ValidationError` when that matches the operation's contract;
- `401` maps to `AuthenticationError`;
- `403` maps to `AuthorizationError`;
- `409` maps to `ConflictError`;
- `429` maps to `RateLimitError`;
- an unsupported operation results in `UnsupportedOperationError`;
- all other unknown upstream errors map to `UpstreamApiError`.

## Mapping and Data Transformation

JSON from Avito is an external contract, not an internal application model.

Rules:

- Raw JSON responses are mapped in a dedicated layer.
- Data enrichment logic executes after transport but before returning the object to the user.
- Enrichment must be deterministic and must not break the original method contract.
- If enrichment is expensive or requires additional requests, it must be explicitly indicated in the API.
- Transformation of transport responses into public SDK models must be centralized.
- The same resource must always map to the same public type, regardless of upstream payload variations within the allowed range.
- Public docstrings and signatures must not require knowledge of the upstream JSON shape.

Recommendation:

- Use `mappers.py` inside each API section.
- Do not mix mapping with the HTTP call in the same method.

## Public Read Contracts

Read operations must be aligned in result shape, nullable behavior, and field naming.

Rules:

- `account().get_self()` returns `AccountProfile`;
- `ad().get(...)` returns `Listing`;
- `ad().list(...)` returns a collection or paginated result of `Listing`;
- `ad_stats().get_item_stats(...)` returns a collection of `ListingStats`;
- `ad_stats().get_calls_stats(...)` returns a collection of `CallStats`;
- `ad_stats().get_account_spendings(...)` returns `AccountSpendings` or another model fixed by the SDK contract;
- an empty or partially populated upstream payload must not break the read contract if the model allows `None` for missing values;
- consumer code must not need to know the raw Avito response structure to use read methods.

The following canonical types are normatively fixed for stable public read/write results:

- `AccountProfile`
- `Listing`
- `ListingStats`
- `CallStats`
- `AccountSpendings`
- `PromotionService`
- `PromotionOrder`
- `PromotionForecast`
- `PromotionActionResult`

## Promotion Write Contract

Officially supported promotion write operations must have a unified public contract.

Rules:

- Promotion write operations accept `dry_run: bool = False`;
- with `dry_run=True` the method must validate inputs, build the official request payload, not execute the write request, and return `PromotionActionResult` with status `preview` or `validated`;
- with `dry_run=False` the method must use the same payload builder, execute the write request, and return the same type `PromotionActionResult`;
- invalid input parameters must result in `ValidationError` before transport is called;
- `request_payload` in the result must correspond to the actual payload of the write call;
- identical inputs in `dry_run=True` and `dry_run=False` must produce the same payload.

Stable `PromotionActionResult` contract:

- `action`
- `target`
- `status`
- `applied`
- `request_payload`
- `warnings`
- `upstream_reference`
- `details`

At minimum the following operations must follow this contract:

- `bbip_promotion().create_order(...)`
- `ad_promotion().apply_vas(...)`
- `ad_promotion().apply_vas_package(...)`
- `ad_promotion().apply_vas_direct(...)`
- `trx_promotion().apply(...)`
- `trx_promotion().delete(...)`
- `target_action_pricing().update_manual(...)`
- `target_action_pricing().update_auto(...)`
- `target_action_pricing().delete(...)`

## Promotion Read Contract

Promotion surface read operations must return only stable public SDK models.

Rules:

- `promotion_order().list_services(...)` returns a collection of `PromotionService`;
- `promotion_order().list_orders(...)` returns a collection of `PromotionOrder`;
- `promotion_order().get_order_status(...)` returns a result per the fixed SDK contract;
- `bbip_promotion().get_suggests(...)` and `bbip_promotion().get_forecasts(...)` return stable SDK models, not transport shapes;
- `target_action_pricing().get_bids(...)` and `target_action_pricing().get_promotions_by_item_ids(...)` return stable SDK models;
- an empty upstream list is correctly returned as an empty SDK model collection;
- a partial upstream payload is correctly mapped into nullable fields of the public model.

## Naming

Rules:

- Package and module names: lowercase, short, and domain-specific.
- Class names: `PascalCase`.
- Function and method names: `snake_case`.
- Public method names must describe the business action: `get_item`, `list_messages`, `create_discount_campaign`.
- Use canonical domain names for public models, not internal transport aliases.
- Avoid abstract names like `utils`, `helpers`, `common2`, `manager2`.
- Generic identifier names are forbidden: `resource_id`, `entity_id`, `obj_id`. Use concrete names: `item_id`, `order_id`, `user_id`.

## Configuration

Rules:

- SDK configuration is isolated in a dedicated module: `config.py` or `settings.py`.
- `AvitoSettings` and `AuthSettings` are the official way to configure the SDK.
- SDK users must be able to pass `client_id` and `client_secret` directly to `AvitoClient` without creating intermediate objects.
- Environment variables are read in one place via `AvitoSettings.from_env()` and `AuthSettings.from_env()`.
- `AvitoClient.from_env()` is the official factory method for initializing the client from the environment.
- Resolution of process environment and `.env` must be deterministic and identical for all entry points.
- Process environment values take priority over `.env`.
- Supported environment variables and alias names must be documented and considered part of the stable config contract.
- Missing required configuration fields must be validated before the first HTTP request, via typed exceptions with clear messages.
- Error messages and metadata for configuration errors must not contain secret values.
- The number of allowed environment variable synonyms for a single field must be minimal. Generic names like `SECRET` or `TOKEN` must not be official aliases.

Example:

```python
@dataclass(slots=True, frozen=True)
class AuthSettings:
    client_id: str
    client_secret: str
    refresh_token: str | None = None


@dataclass(slots=True, frozen=True)
class AvitoSettings:
    auth: AuthSettings
    base_url: str = "https://api.avito.ru"
    user_id: int | None = None
    timeout_seconds: float = 10.0
```

Minimum expected config contract capabilities:

- `AvitoSettings.from_env()`;
- `AuthSettings.from_env()`;
- `AvitoClient.from_env()`;
- `AvitoClient(client_id=..., client_secret=...)`;
- explicit validation of required auth fields;
- safe `debug_info()` contract with no leakage of `client_secret`, access token, refresh token, or `Authorization` header.

## Pagination

The public behavior of lazy pagination must be fixed as part of the SDK contract.

Rules:

- list methods using lazy pagination return a result with a list-like `PaginatedList` collection in the `items` field;
- the type annotation for the `items` field must be `PaginatedList[T]`, not `list[T]` — the annotation must match the runtime;
- the first page may already be loaded at the time the result is obtained;
- reading the first `N` elements must not load all pages at once;
- iterating over the first `N` elements must execute only the necessary number of page requests;
- full materialization must be performed by an explicit call, e.g. `items.materialize()`;
- an empty collection must work without extra requests;
- an error on a subsequent page must propagate at the time that page is read;
- repeated access to already-loaded elements must not trigger a re-fetch if caching is declared part of the contract.

If additional utilities are needed on top of pagination, they must be part of the public SDK contract, not external helper functions.

## Serialization

Public SDK models must serialize safely and uniformly without external helpers.

Rules:

- each public model serializes via a standard SDK method;
- the serialization result must be JSON-compatible;
- nested public models must serialize recursively;
- nullable and optional fields serialize per the fixed contract rules;
- serialization must not expose transport objects, service references, or internal mapper fields;
- `to_dict()` and `model_dump()` must be explicitly declared in the class or inherited from an explicit mixin — dynamic method injection via `globals()` or `setattr` at runtime is forbidden;
- the presence of serialization methods must be visible in the class definition without tracking side-effect calls during module import.

## Logging

Rules:

- Logging must be structured and useful for diagnostics.
- `client_secret`, access token, refresh token, the full authorization header, and other secrets must not be logged.
- At info/debug level it is acceptable to log endpoint, attempt number, latency, status code, and operation name.
- SDK users must be able to disable or redirect logging.
- Diagnostic snapshots such as `debug_info()` must be safe by default.

## Docstrings and Comments

Rules:

- Public classes and methods must have short docstrings describing the contract.
- A public method docstring must describe the returned SDK model and behavior on nullable/empty cases.
- Comments are used only where the intent cannot be expressed in code.
- Comments must not duplicate what is obvious.

## Testing

### What to Test

A test exists to fix a technical decision or contract. A test is justified if without it, behavior that matters to the user or to the system can be broken unnoticed.

What is tested:

- **Public SDK contract**: factory method signatures, return types, behavior on empty and partial upstream payloads.
- **Error mapping**: each significant HTTP status must result in a strictly defined SDK exception type; secrets must not leak into metadata.
- **Auth flow**: token acquisition, refresh after 401, use of separate credentials for specialized endpoints.
- **Retry logic**: retries fire on allowed scenarios (timeout, 5xx, rate limit) and do not fire on disallowed ones (non-idempotent methods without explicit permission).
- **Pagination**: lazy loading reads only the necessary pages; an error on a subsequent page propagates at read time; an empty collection triggers no extra requests; full materialization loads all pages exactly once.
- **Serialization**: `to_dict()` / `model_dump()` returns a JSON-compatible structure; transport fields do not appear in the result; nested models serialize recursively.
- **Dry-run contract**: with `dry_run=True` transport is not called; the payload built in `dry_run` and in a real call is identical given the same inputs.
- **Configuration**: required fields are validated before the first HTTP request; process environment priority over `.env` is deterministic; secrets do not appear in `debug_info()`.
- **Data security**: secret values (tokens, `client_secret`, `Authorization` header) do not appear in error messages, metadata, or serialization output.

What is not tested:

- That a constructor accepts arguments and stores them in fields.
- That a dataclass contains a field of a certain type.
- That a function returns `None` when the input is `None`.
- That importing a module does not raise an exception.
- Logic fully implemented by a third-party library without customization.
- Code-to-documentation consistency: a test must not verify that a README, inventory, docstring, or comment describes the current behavior. Documentation is not a contract — it describes code, not the other way around. If documentation is outdated, update it; do not write a test to track it.
- The presence of a specific method or attribute via `hasattr`. That is a syntax check, not a behavior check. If a method is renamed, the calling code will break, not a `hasattr` test.

Criterion: if a test cannot be broken without violating a public contract or technical decision, the test is not needed.

### Test Architecture

Tests are divided by what they verify, not by which module they cover.

**Test levels:**

- **Contract tests** — verify that the public API returns expected types and structures given correct upstream payloads. Use fake transport. Do not depend on the network.
- **Error mapping tests** — verify that each HTTP status and upstream error shape results in the correct SDK exception type with the expected fields.
- **Integration-style tests** — verify end-to-end technical decisions: retry, auth refresh, pagination. Use a controlled fake transport with specified scenarios.
- **Security tests** — verify that secrets do not leak through any public path: errors, serialization, debug_info.

### Isolation

Tests do not make network calls. All HTTP is replaced by a controlled fake transport that:

- accepts a specified status and payload for each request;
- allows verifying whether a call was made, how many times, with which method and body;
- is used uniformly across all tests that verify the public API.

Section clients, domain objects, and transport are tested in isolation from each other.

### Test Structure

Each test verifies one aspect of behavior. Structure: Arrange / Act / Assert with no nested conditionals.

```python
def test_transport_retries_on_server_error_and_raises_after_exhaustion():
    # Arrange
    transport = FakeTransport(responses=[
        FakeResponse(status=500),
        FakeResponse(status=500),
        FakeResponse(status=500),
    ])

    # Act / Assert
    with pytest.raises(ServerError):
        transport.request_json("GET", "/some/path", context=ctx)

    assert transport.call_count == 3
```

Rules:

- Test names describe behavior, not the method under test: `test_transport_retries_on_server_error_and_raises_after_exhaustion`, not `test_transport_request`.
- One test, one scenario. Multiple `assert` statements are acceptable when they verify the same behavior from different angles.
- Parametrization is used for sets of equivalent inputs: different HTTP statuses, different error shapes, different upstream payload variants.
- Fixtures create only infrastructure (fake transport, settings); they must not hide test logic.

### Coverage of Mandatory Scenarios

**Error mapping** — must cover:

- 400, 401, 403, 404, 409, 422, 429, 5xx → the corresponding SDK exception type;
- secrets in `metadata` and error `headers` are replaced with `***`;
- an unknown status maps to `UpstreamApiError`, not a generic `Exception`.

**Auth flow** — must cover:

- successful token acquisition via `client_credentials`;
- automatic refresh after 401 exactly once;
- `AuthenticationError` after a failed refresh (second 401);
- credential isolation for separate token endpoints.

**Pagination** — must cover:

- partial iteration loads only the necessary pages;
- full materialization via `materialize()` loads everything exactly once;
- an empty first page triggers no additional requests;
- an error on a subsequent page propagates at read time, not at object creation.

**Dry-run** — must cover for each write method with `dry_run`:

- with `dry_run=True` transport receives no calls;
- the payload in `dry_run=True` and `dry_run=False` is identical given the same inputs;
- input validation in `dry_run=True` works the same as in `dry_run=False`.

**Serialization** — must cover:

- `to_dict()` returns only public fields with no transport objects;
- nested models serialize recursively;
- the result passes `json.dumps()` without exceptions.

## API Documentation and Contract Coverage

Avito API specifications are stored in the `docs/` directory as Swagger/OpenAPI files. This is the authoritative source of truth for all API contracts.

Rules:

- Before implementing any new method or model, consult the specification in `docs/`.
- The SDK must cover **all** API methods described in `docs/`. A method absent from the SDK but present in the specification is a defect.
- Public method signatures, model field names and types, allowed enum values, and nullable behavior must exactly match the contract in `docs/`.
- When there is a discrepancy between code and the specification in `docs/`, the specification takes priority.
- If the upstream API adds a new endpoint or changes an existing one, a corresponding SDK change is mandatory.
- Fields marked as required in the specification cannot be `T | None` in the public model without explicit justification.
- Enum values in the SDK must match the allowed values from the specification — arbitrary extension is forbidden.

## Imports and Dependencies

Rules:

- Use absolute imports within the package.
- Avoid circular dependencies between API section packages.
- Dependencies must be minimal.
- If the standard library solves the problem without loss of quality, a third-party library is not needed.

## What Must Not Exist in the Project

- Global token state without a controlled owner.
- Methods returning unstructured JSON in the main API.
- Mixing of transport, auth, parsing, and domain logic in one class.
- Unannotated public methods.
- Widespread use of `Any`.
- Error handling via `assert`.
- Hidden network side effects in properties and dataclasses.
- Leakage of transport-layer shapes and mapper details into public signatures and models.
- Implicit or undocumented config resolution through the environment.
- Abstract field names (`resource_id`) where a domain-specific name is known and unambiguous.
- Dynamic method injection into classes via `setattr`, patching via `globals()`, or other runtime magic.
- Two public methods doing the same thing without one of them being explicitly marked as deprecated.
- Type aliases without explicit deprecation.
- `list[T]` annotation where `PaginatedList[T]` is returned at runtime.
- `AuthenticationError` as a subclass of `AuthorizationError`: 401 and 403 are different errors.
- Error messages in mixed languages: all user-facing error text must be in one language.
- Generic environment aliases (`SECRET`, `TOKEN`) in the official config contract.
- Dead code: unused symbols, aliases, and imports.
- Internal-layer request objects in public domain method signatures.
