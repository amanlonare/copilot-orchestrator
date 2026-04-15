.PHONY: setup update lint test check clean session-clean db-flush

setup:
	uv venv
	uv sync --all-extras --dev
	uv run pre-commit install

update:
	uv sync --all-extras --dev

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy .

test:
	uv run pytest

check: lint test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

session-clean:
	@if [ -z "$(ID)" ]; then echo "Usage: make session-clean ID=<session_id>"; exit 1; fi
	docker exec copilot-orchestrator-redis redis-cli DEL session:$(ID)
	docker exec copilot-orchestrator-redis redis-cli eval "for _,k in ipairs(redis.call('keys','checkpoint:$(ID):*')) do redis.call('del',k) end" 0
	@echo "Session $(ID) cleaned in copilot-orchestrator-redis."

db-flush:
	docker exec copilot-orchestrator-redis redis-cli flushall
	@echo "copilot-orchestrator-redis database flushed."
