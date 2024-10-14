
check-coverage:
	poetry run pytest --cov-branch --cov=app/ --cov-report=xml tests/

check-poetry:
	poetry check --lock

check-quality:
	poetry run ruff check app/ tests/

check-tests:
	poetry run pytest tests/

check-types:
	poetry run mypy app/ tests/

checkers: check-coverage check-poetry check-quality check-types