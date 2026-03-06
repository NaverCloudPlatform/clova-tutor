include ../.env
export

PYTHON = uv run python -m
SCRIPT = scripts.upload_problem_db

URL ?= http://localhost:8000
FILE ?= scripts/problem.json
INDEX ?= Problem_opensource

.PHONY: build up down db_save db_apply freeze pr re proto test-api test-unit test upload upload-local sync problem_sync init

%:
	@:

build:
	@echo "Start Docker container..."
	docker-compose -f docker-compose-local.yml up -d --build

up:
	docker-compose -f docker-compose-local.yml up -d

down:
	docker-compose -f docker-compose-local.yml down

re:
	$(MAKE) down
	$(MAKE) build

db_save:
	@commit_message="$(word 2, $(MAKECMDGOALS))"; \
	if [ -z "$$commit_message" ]; then \
		echo "Usage: make db_save \"commit message\""; \
		exit 1; \
	fi; \
	alembic revision --autogenerate -m "$$commit_message"

db_apply:
	uv run alembic upgrade head

proto:
	@chmod +x ./scripts/gen_proto.sh
	@./scripts/gen_proto.sh proto src/common/infra/grpc/grpc_stubs

test-api:
	uv run pytest -n 3 -s tests/api -v

test-unit:
	@env | grep MYSQL_
	uv run pytest -n 3 -s tests/unit -v

test: test-api test-unit

upload:
	$(PYTHON) $(SCRIPT)

upload-args:
	$(PYTHON) $(SCRIPT) --url $(URL) --file $(FILE) --yes

upload-local:
	$(PYTHON) $(SCRIPT) --url http://localhost:8000 --file scripts/problem.json --yes

sync:
	$(PYTHON) $(SCRIPT) --url $(URL) --file $(FILE) --index $(INDEX)

problem_sync:
	@echo "🚀 업로드 및 동기화 시작..."
	$(MAKE) upload URL=$(URL) FILE=$(FILE)
	$(MAKE) sync URL=$(URL) FILE=$(FILE) INDEX=$(INDEX)

init:
	uv sync --all-groups
	$(MAKE) db_apply
	$(MAKE) upload-local

	