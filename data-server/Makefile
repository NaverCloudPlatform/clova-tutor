.PHONY: build up down freeze re

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

freeze:
	pip freeze > requirements.txt

pr:
	python scripts/create-pr.py