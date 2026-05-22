SHELL := bash
ELEMENT_NAME = empty
ELEMENT_PATH = exordos_empty
ifeq ($(SSH_KEY),)
	SSH_KEY = ~/.ssh/id_rsa.pub
endif

all: help

help:
	@echo "build_core       - build exordos core"
	@echo "bootstrap        - bootstrap exordos core"

mdlint:
	markdownlint-cli2 --config .markdownlint.yaml "**/*.md" "#node_modules" --fix

build_element:
	./dist/exordos build -i $(SSH_KEY) -f ../$(ELEMENT_PATH)

push_element:
	./dist/exordos repo push -t my_push_name -f --latest ../$(ELEMENT_PATH) -e ../$(ELEMENT_PATH)/output -c ./exordos/repo/exordos_repo_proxy.yaml

deploy_element:
	./dist/exordos deploy ../$(ELEMENT_PATH)

bootstrap:
	./dist/exordos bootstrap -i ../exordos_core/output/inventory.json -f -m core --admin-password admin --cidr 10.20.0.0/22 --settings

repo_init:
	./dist/exordos repo init -c ./exordos/repo/exordos_repo_proxy.yaml

repo_list:
	./dist/exordos repo list -c ./exordos/repo/exordos_repo_proxy.yaml

repo_delete:
	./dist/exordos repo delete -c ./exordos/repo/exordos_repo_proxy.yaml

build_inventory:
	./dist/exordos build-inventory /tmp/proxy_repo/exordos-elements

find_ascii:
	grep -rnP "#.*[^\x00-\x7f]" ./exordos

define_resource:
	./dist/exordos e e define $(ELEMENT_NAME)

add_ssh_key:
	./dist/exordos secret ssh_keys add --realm --target_public_key $(SSH_KEY)
