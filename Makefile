.PHONY: help test

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

clean: ## delete all *.retry files
	find . -name '*.retry' -delete

build: ## build docker file
	docker build -t lynis-bridge .

run: ## run detached prod with gunicorn
	docker run -d --rm --network host -e SSL=yes -e DATABASE_HOST="127.0.0.1" -e DATABASE_USER=m -e DATABASE_PASSWORD=nomysql1 lynis-bridge:latest ./prod.sh

dev: ## run interactive
	docker run -ti --rm --network host -e DATABASE_HOST="127.0.0.1" -e DATABASE_USER=m -e DATABASE_PASSWORD=nomysql1 lynis-bridge:latest python3 main.py
