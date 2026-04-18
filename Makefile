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

release: patch
	poetry publish
