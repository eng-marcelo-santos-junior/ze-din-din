.PHONY: build up down logs shell psql migrate migration test test-cov lint

# ── Docker ──────────────────────────────────────────────────────────────────

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f web

# ── Flask shell / DB ────────────────────────────────────────────────────────

shell:
	docker compose exec web flask shell

psql:
	docker compose exec db psql -U zedindin -d zedindin_dev

# ── Migrations ──────────────────────────────────────────────────────────────

migrate-init:
	docker compose exec web flask db init

migrate:
	docker compose exec web flask db upgrade

migration:
	docker compose exec web flask db migrate -m "$(msg)"

# ── Tests ────────────────────────────────────────────────────────────────────

test:
	docker compose exec web pytest -v

test-cov:
	docker compose exec web pytest --cov=app --cov-report=term-missing -v

# ── Code quality ─────────────────────────────────────────────────────────────

lint:
	docker compose exec web ruff check app tests
	docker compose exec web black --check app tests
	docker compose exec web isort --check-only app tests

format:
	docker compose exec web black app tests
	docker compose exec web isort app tests
