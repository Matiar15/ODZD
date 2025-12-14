ruff_check:
	uv run ruff check --fix

ruff_format:
	uv run ruff format

mypy:
	uv run mypy .

lint: ruff_check ruff_format mypy
