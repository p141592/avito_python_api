-include $(PWD)/.env
export

REGISTRY=10.11.0.9:5000

check: test typecheck lint build

build: clean
	poetry build

clean:
	rm -rf dist

lock:
	poetry lock

test: 
	poetry run pytest

typecheck:
	poetry run mypy avito

profile: 
	poetry run pytest --profile-svg

fmt:
	poetry run ruff format .

lint:
	poetry run ruff check .

minor: check
	poetry version minor

patch: check
	poetry version patch

major: check
	poetry version major

release:
	poetry publish --no-interaction

docs-serve:
	poetry run mkdocs serve

docs-strict:
	poetry run mkdocs build --strict
	poetry run python scripts/check_readme_domain_coverage.py

docs-build: docs-strict

docs-report:
	poetry run python scripts/check_inventory_coverage.py --output inventory-coverage-report.json
	poetry run python scripts/check_spec_inventory_sync.py --output spec-inventory-report.json
	poetry run python scripts/check_reference_public_surface.py --output reference-public-report.json
	poetry run python scripts/check_public_docstrings.py --output docstring-contract-report.json
	poetry run python scripts/build_docs_quality_report.py

docs-check: docs-strict
	lychee --exclude "avito\.ru" --retry-wait-time 5 --max-retries 3 --timeout 30 site/
