SHELL := bash
REPOSITORY := https://repository.genesis-core.tech
ifeq ($(SSH_KEY),)
	SSH_KEY = ~/.ssh/id_rsa.pub
endif

all: help

help:
	@echo "build_core       - build exordos core"
	@echo "bootstrap        - bootstrap exordos core"

mdlint:
	markdownlint-cli2 --config .markdownlint.yaml "**/*.md" "#node_modules" --fix

build_empty:
	./dist/exordos build -i $(SSH_KEY) -f ../genesis_empty -o ../genesis_empty/output --inventory --manifest-var repository=$(REPOSITORY)

push_empty:
	./dist/exordos repo push -t my_push_name -f --latest ../genesis_empty -e ../genesis_empty/output

bootstrap:
	./dist/exordos bootstrap -i ../exordos_core/output/inventory.json -f -m core --admin-password admin --cidr 10.20.0.0/22 --settings