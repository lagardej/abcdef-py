SHELL := /bin/bash
.PHONY: ci fmt-check lint types test format mutate install

ci:
	@mkdir -p logs
	@$(MAKE) fmt-check lint types test 2>&1 | tee logs/ci.log; exit $${PIPESTATUS[0]}

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
	@mkdir -p logs
	uv run pytest --gremlins 2>&1 | tee logs/gremlins.log; exit ${PIPESTATUS[0]}

install:
	@for hook in scripts/hooks/*; do \
		name=$$(basename $$hook); \
		chmod +x $$hook; \
		ln -sf "$(CURDIR)/$$hook" ".git/hooks/$$name"; \
		echo "Installed hook: $$name"; \
	done
