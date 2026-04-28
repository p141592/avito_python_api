-include $(PWD)/.env
export

REGISTRY=10.11.0.9:5000
MKDOCS_ENV=DISABLE_MKDOCS_2_WARNING=true NO_MKDOCS_2_WARNING=1

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
	$(MKDOCS_ENV) poetry run mkdocs serve

docs-strict:
	$(MKDOCS_ENV) poetry run mkdocs build --strict
	poetry run python scripts/check_readme_domain_coverage.py
	poetry run pytest tests/docs/

docs-build: docs-strict

docs-report:
	poetry run python scripts/check_reference_public_surface.py --output reference-public-report.json
	poetry run python scripts/check_public_docstrings.py --output docstring-contract-report.json
	poetry run python scripts/check_changelog_sections.py --output changelog-sections-report.json
	poetry run python scripts/check_docs_examples.py --output reference-explanation-examples-report.json
	poetry run bandit -r avito -lll -f json -o bandit-report.json
	poetry run python scripts/build_docs_quality_report.py

docs-check: docs-strict
	ln -sfn . site/avito_python_api
	lychee --root-dir "$(PWD)/site" --exclude "avito\.ru" --exclude "^https://p141592\.github\.io/avito_python_api/" --retry-wait-time 5 --max-retries 3 --timeout 30 site/

qa-docs:
	poetry run pydocstyle \
		avito/client.py avito/config.py \
		avito/core/exceptions.py avito/core/pagination.py \
		avito/*/domain.py \
		avito/testing/fake_transport.py
	poetry run interrogate avito/ --fail-under=0 --quiet
