.PHONY: format lint test ci

format:
	black .
	isort .

lint:
	black --check .
	isort --check-only .

test:
	pytest -q

ci: lint test
