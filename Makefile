ENV_FILE := .env
ENV := $(shell cat $(ENV_FILE))
run:
	$(ENV) poetry run python main.py

.PHONY: run
