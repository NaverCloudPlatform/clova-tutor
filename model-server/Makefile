.PHONY: build up down db_save db_apply freeze pr re proto setup

%:
	@:

build:
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
	alembic upgrade head

pr:
	python scripts/create-pr.py

proto:
	@chmod +x ./scripts/gen_proto.sh
	@./scripts/gen_proto.sh

setup:
	./src/assistant/setup.sh