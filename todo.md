# STYLEGUIDE Compliance Action Plan

## Context Snapshot

Repository: `/Users/n.baryshnikov/Projects/avito_python_api`

User request: deep audit of project compliance with `STYLEGUIDE.md`, then preserve an action plan for fixing mismatches.

Current audit results:

- `poetry run python scripts/lint_architecture.py` passed: `errors=0`
- `poetry run mypy avito` passed
- `poetry run ruff check .` passed
- `poetry run python scripts/lint_swagger_bindings.py --strict` passed: 23 specs, 204 operations, bound 204, errors 0
- `poetry run pytest` passed: 2051 tests

Important context:

- `STYLEGUIDE.md` was updated to explicitly require Swagger-spec compliance tests and allow discovery/signature/schema introspection when it proves SDK-to-Swagger coverage.
- The audit found the project is broadly aligned with domain architecture v2, but several normative mismatches remain.
- Do not remove Swagger contract tests; they are now explicitly required by the guide.

## Action Plan

### 1. Synchronize Exception Contract

- Add explicit `attempt`, `method`, and `endpoint` fields to `AvitoError`.
- Populate these fields in `Transport._map_http_error()`.
- Pass `attempt` for retry exhaustion and transport-level exceptions.
- Keep existing `metadata` behavior for compatibility, but do not rely on metadata as the only public source of these fields.
- Update error mapping and security tests.

Relevant files:

- `avito/core/exceptions.py`
- `avito/core/transport.py`
- `tests/core/test_transport.py`
- `tests/core/test_authentication.py`
- `docs/site/reference/exceptions.md`

Verification:

```bash
poetry run pytest tests/core/test_transport.py tests/core/test_authentication.py
```

### 2. Add Per-Request Transport Debug Logging

- Emit a debug log for every real HTTP request/response.
- Include structured fields: `operation`, `endpoint`, `method`, `attempt`, `status`, `latency_ms`, `request_id`.
- Do not log body, secrets, auth headers, or idempotency keys.
- Keep retry logs, but align field naming with the standard set where possible.
- Add or update tests using `caplog`.

Relevant files:

- `avito/core/transport.py`
- `tests/core/test_transport.py`
- `docs/site/explanations/transport-and-retries.md`
- `docs/site/how-to/diagnostics-and-logging.md`

Verification:

```bash
poetry run pytest tests/core/test_transport.py
```

### 3. Fix Optional Positional Public Parameter

- Change `Account.get_balance(user_id=None, *, ...)` to `Account.get_balance(*, user_id=None, ...)`.
- Update call sites and documentation snippets if needed.
- Decide whether this is acceptable as a breaking public signature change. If not, document an explicit compatibility exception or deprecation path before changing.

Relevant files:

- `avito/accounts/domain.py`
- `tests/domains/accounts/test_accounts.py`
- `docs/site/how-to/account-profile.md`
- `README.md`

Verification:

```bash
poetry run pytest tests/domains/accounts/test_accounts.py tests/contracts/test_swagger_contracts.py
```

### 4. Resolve `AVITO_SECRET` Alias Policy

- `STYLEGUIDE.md` forbids generic env aliases like `SECRET` / `TOKEN`.
- Current official alias `AVITO_SECRET` conflicts with that rule.
- Preferred path:
  - keep it temporarily for backward compatibility;
  - emit a deprecation warning when it is used;
  - remove it from the official documented config contract;
  - add a `CHANGELOG.md` entry.
- Alternative path: add a documented exception to the guide, but that weakens the config rule.

Relevant files:

- `avito/auth/settings.py`
- `avito/_env.py`
- `tests/core/test_configuration.py`
- `README.md`
- `docs/site/reference/config.md`
- `docs/site/how-to/auth-and-config.md`
- `CHANGELOG.md`

Verification:

```bash
poetry run pytest tests/core/test_configuration.py
```

### 5. Validate Date/Time String Inputs

- Introduce shared validation/serialization helpers for date and datetime public inputs.
- Use the `ads` domain approach as a model: `date | datetime | str` plus ISO validation before transport.
- Review domains with public date-like `str` parameters:
  - `cpa`
  - `realty`
  - `jobs`
  - `messenger`
  - `orders`
- Invalid strings should raise `ValidationError` before transport.

Relevant examples:

- Good current pattern: `avito/ads/domain.py::_serialize_stats_date`
- Risk examples:
  - `avito/cpa/domain.py`
  - `avito/realty/domain.py`
  - `avito/jobs/domain.py`

Verification:

```bash
poetry run pytest tests/domains/cpa/test_cpa.py tests/domains/realty/test_realty.py tests/domains/jobs/test_jobs.py tests/domains/messenger/test_messenger.py tests/domains/orders/test_orders.py
```

### 6. Convert Closed Swagger Value Sets to Enums

- Identify public request/model fields where Swagger defines a closed set but SDK uses open `str`.
- Start with clear cases:
  - `orders.transition`
  - `jobs.billing_type`
  - `jobs.employment`
  - `jobs.schedule`
  - `jobs.experience`
  - `ads` spendings `grouping`
- Place enums next to the models that use them.
- Public method signatures should prefer enum types, optionally accepting corresponding string literals via internal normalization.
- Unknown upstream response values should map to `UNKNOWN` or typed fallback with warning.

Relevant files:

- `avito/orders/models.py`
- `avito/orders/domain.py`
- `avito/jobs/models.py`
- `avito/jobs/domain.py`
- `avito/ads/models.py`
- `avito/ads/domain.py`
- `docs/avito/api/*.json`

Verification:

```bash
poetry run mypy avito
poetry run pytest tests/domains/orders/test_orders.py tests/domains/jobs/test_jobs.py tests/domains/ads/test_ads.py
poetry run python scripts/lint_swagger_bindings.py --strict
```

### 7. Make Public Docstrings Reference-Ready

- Many public domain methods have short docstrings that do not describe all required contract details.
- For each public API method, document:
  - business action;
  - public arguments;
  - return SDK model;
  - pagination behavior, if any;
  - dry-run and idempotency behavior, if any;
  - `timeout` and `retry` overrides;
  - common SDK exceptions.
- Do not keep `Raises: AvitoError ...` as the only contract detail.
- This should be enforced by docs/static lint, not pytest.

Priority domains:

- `accounts`
- `ads`
- `promotion`
- `messenger`
- `tariffs`

Verification:

```bash
make docs-strict
```

### 8. Align Pytest Suite With Updated STYLEGUIDE

- Keep Swagger contract tests.
- Move non-behavioral documentation/style checks out of pytest.
- Review these tests:
  - `tests/contracts/test_docstring_contracts.py`
  - public-surface assertions in `tests/contracts/test_client_contracts.py`
  - non-Swagger linter unit tests in `tests/core/test_swagger_linter.py`
- Preserve tests that prove runtime behavior or Swagger contract coverage.
- Move pure style/doc checks to static linter or docs linter invoked from `make check`.

Verification:

```bash
poetry run pytest
poetry run python scripts/lint_architecture.py
make docs-strict
```

### 9. Extend Static Architecture Lint

- Add checks for issues discovered manually:
  - optional positional parameters in public domain methods;
  - public date-like `str` parameters without validation/serialization helper;
  - forbidden generic env aliases;
  - public exception fields required by the guide;
  - public docstring structure, if automatic enforcement is desired.
- Keep these in `scripts/lint_architecture.py` or a dedicated static/docs linter, not pytest.

Relevant files:

- `scripts/lint_architecture.py`
- `Makefile`

Verification:

```bash
poetry run python scripts/lint_architecture.py
make check
```

### 10. Final Gate

Run after the fixes are complete:

```bash
make swagger-lint
poetry run pytest
poetry run mypy avito
poetry run ruff check .
poetry run python scripts/lint_architecture.py
make docs-strict
make check
```

## Recommended Execution Order

1. Exception contract and transport logging.
2. `Account.get_balance` signature.
3. `AVITO_SECRET` alias policy.
4. Date/time validation.
5. Closed value-set enums.
6. Public docstrings.
7. Pytest/static-lint alignment.
8. Static lint expansion.
9. Final gate.

## Changelog

- 2026-05-03: Created plan from STYLEGUIDE compliance audit.
- 2026-05-03: Recorded current clean baseline: architecture lint, mypy, ruff, swagger-lint, and full pytest all pass.
- 2026-05-03: Noted that `STYLEGUIDE.md` now explicitly requires Swagger-spec compliance tests and permits contract-focused introspection for Swagger coverage.
