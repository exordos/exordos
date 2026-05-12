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
	./dist/exordos build -i $(SSH_KEY) -f ../exordos_empty -o ../exordos_empty/output --manifest-var repository=$(REPOSITORY)

push_empty:
	./dist/exordos repo push -t my_push_name -f --latest ../exordos_empty -e ../exordos_empty/output

bootstrap:
	./dist/exordos bootstrap -i ../exordos_core/output/inventory.json -f -m core --admin-password admin --cidr 10.20.0.0/22 --settings

find_ascii:
	grep -rnP "#.*[^\x00-\x7f]" ./exordos
