PYTHON	= uv run python
ARGS	?=

MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
             --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict

install:
	uv sync

# Exemplo: make run ARGS="search 'How to load a LoRA adapter?' --k 5"
run:
	$(PYTHON) -m src $(ARGS)

debug:
	$(PYTHON) -m pdb -m src $(ARGS)

clean:
	find . -path ./data -prune -o -path ./.venv -prune -o \
		-type d \( -name __pycache__ -o -name .mypy_cache -o -name .pytest_cache \) \
		-exec rm -rf {} +

lint:
	uv run flake8 .
	uv run mypy . $(MYPY_FLAGS)

lint-strict:
	uv run flake8 .
	uv run mypy . --strict
