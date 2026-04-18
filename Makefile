include $(PWD)/.env
export

REGISTRY=10.11.0.9:5000

build: test lock clean linter

clean:
	rm -rf dist

lock:
	poetry lock

test: 
	poetry run pytest

profile: 
	poetry run pytest --profile-svg

linter:
	poetry run ruff format .
	poetry run ruff check .

minor: build
	poetry version minor

patch: build
	poetry version patch

major: build
	poetry version major

release: patch
	poetry build && poetry publish
