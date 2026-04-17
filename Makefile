include $(PWD)/.env
export

REGISTRY=10.11.0.9:5000

build: lock clean linter

clean:
	rm -rf dist

lock:
	poetry lock

test: 
	poetry run pytest --ff --cov=admiral --cov-report=term:skip-covered --cov-report=html -vvv

profile: 
	poetry run pytest --profile-svg

linter:
	poetry run black .
	poetry run isort --atomic .

pypi: clean lock linter test
	poetry build && poetry publish
