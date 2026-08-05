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

build_docker:
	 docker build --no-cache --progress=plain -t exordos .

build_binary:
	 tox -e bin

cli_docs:
	tox -e cli_docs

mdlint:
	markdownlint-cli2 --config .markdownlint.yaml "**/*.md" "#node_modules" "#!.venv" "#!.tox" "#!.opencode" "#!.claude" --fix

build_element:
	./dist/exordos build -i $(SSH_KEY) -f ../$(ELEMENT_PATH) -o ../$(ELEMENT_PATH)/output

push_element:
	./dist/exordos repo push -t my_push_name -f --latest ../$(ELEMENT_PATH) -e ../$(ELEMENT_PATH)/output

install_element:
	./dist/exordos e e install $(ELEMENT_NAME)

list_elements:
	./dist/exordos e e d $(ELEMENT_NAME)

bootstrap:
	./dist/exordos bootstrap -i ../exordos_core/output -f -m core --admin-password admin --cidr 10.20.0.0/22 --ssh-public-key $(SSH_KEY)

find_ascii:
	grep -rnP "#.*[^\x00-\x7f]" ./exordos

define_resource:
	./dist/exordos e e define $(ELEMENT_NAME)

validate_element:
	./dist/exordos e m validate $(ELEMENT_NAME)

add_ssh_keys:
	./dist/exordos secret ssh_keys add --current-realm --target_public_key $(SSH_KEY)

add_ssh_keys_element:
	./dist/exordos secret ssh_keys add --element $(ELEMENT_NAME) --target_public_key $(SSH_KEY)

clear_ssh_keys:
	./dist/exordos secret ssh_keys clear -y

create_ecosystem_realm:
	./dist/exordos -u jdoe@corp.com -p 12345678 realms a -n example --admin-password 12345678 --core-version 0.2.5

list_ecosystem_realms:
	./dist/exordos -u jdoe@corp.com -p 12345678 realms l

delete_ecosystem_realm:
	./dist/exordos -u jdoe@corp.com -p 12345678 realms d example

limits:
	./dist/exordos limits l

add_limit:
	./dist/exordos limits add -p 11111113-bc70-4760-9fbf-9fcfe40da329 -r secret_ssh_keys -l 1

add_limit_field:
	./dist/exordos limits add -p 11111113-bc70-4760-9fbf-9fcfe40da329 -r nodes -f cores -l 1

clear_limits:
	./dist/exordos limits clear -y

user_info:
	./dist/exordos iam users info jdoe

introspect:
	./dist/exordos iam introspect

role_permissions:
	./dist/exordos iam permissions role newcomer
