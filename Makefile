SHELL := bash
ELEMENT_NAME = empty
ELEMENT_PATH = exordos_empty
ifeq ($(SSH_KEY),)
	SSH_KEY = ~/.ssh/id_rsa.pub
endif

all: help

help:
	@echo "help             - show this help"

mdlint:
	markdownlint-cli2 --config .markdownlint.yaml "**/*.md" "#node_modules" "#!.venv" "#!.tox" --fix

bin:
	tox -e bin

find_ascii:
	grep -rnP "#.*[^\x00-\x7f]" ./exordos

build_element:
	./dist/exordos build -i $(SSH_KEY) -f ../$(ELEMENT_PATH) -o ../$(ELEMENT_PATH)/output

push_element:
	./dist/exordos repo push -t my_push_name -f --latest ../$(ELEMENT_PATH) -e ../$(ELEMENT_PATH)/output

install_element:
	./dist/exordos e e install $(ELEMENT_NAME)

list_elements:
	./dist/exordos e e l

bootstrap:
	./dist/exordos bootstrap -i ../exordos_core/output -f -m core --admin-password admin --cidr 10.20.0.0/22 --settings

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

limits:
	./dist/exordos quota limits l

add_limit:
	./dist/exordos quota limits add -p 11111113-bc70-4760-9fbf-9fcfe40da329 -r secret_ssh_keys -l 1

clear_limits:
	./dist/exordos quota limits clear -y

reservations:
	./dist/exordos quota reservations l

reservations_summary:
	./dist/exordos quota reservations summary