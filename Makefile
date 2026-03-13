.PHONY: ci fmt-check lint types test format mutate install

ci: fmt-check lint types test

fmt-check:
	uv run ruff format --check .

lint:
	uv run ruff check .

types:
	uv run pyright

test:
	uv run pytest || [ $$? -eq 5 ]

format:
	uv run ruff format .

mutate:
	uv run pytest --gremlins

install:
	@for hook in scripts/hooks/*; do \
		name=$$(basename $$hook); \
		chmod +x $$hook; \
		ln -sf "$(CURDIR)/$$hook" ".git/hooks/$$name"; \
		echo "Installed hook: $$name"; \
	done
