SHELL := bash
ELEMENT_NAME = empty
ELEMENT_PATH = exordos_empty
PROJECT_ID = 11111111-1111-1111-1111-111111111111
DBAAS_INSTANCE_UUID = 22222222-2222-2222-2222-222222222222
DBAAS_INSTANCE_NAME = mypg
DBAAS_VERSION = pg18
DBAAS_USER_UUID = 33333333-3333-3333-3333-333333333333
DBAAS_USER_NAME = myuser
DBAAS_DATABASE_UUID = 44444444-4444-4444-4444-444444444444
DBAAS_DATABASE_NAME = mydb
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
	./dist/exordos repo push -j 4 -t exordos_repo -f --latest ../$(ELEMENT_PATH) -e ../$(ELEMENT_PATH)/output

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

reset_password:
	./dist/exordos iam u reset_password dae92b97-ee63-4376-9743-f735120ea7db --new-password 123456789


# DBaaS commands
list_dbaas_versions:
	./dist/exordos dbaas versions list

show_dbaas_version:
	./dist/exordos dbaas versions show $(DBAAS_VERSION)

list_dbaas_instances:
	./dist/exordos dbaas instances list

show_dbaas_instance:
	./dist/exordos dbaas instances show $(DBAAS_INSTANCE_UUID)

add_dbaas_instance:
	./dist/exordos dbaas instances add -u $(DBAAS_INSTANCE_UUID) -p $(PROJECT_ID) -n $(DBAAS_INSTANCE_NAME) -v $(DBAAS_VERSION) --cpu 2 --ram 2048 --disk-size 16 --nodes-number 1 --sync-replica-number 1

update_dbaas_instance:
	./dist/exordos dbaas instances update $(DBAAS_INSTANCE_UUID) --cpu 4 --ram 4096 --disk-size 32

delete_dbaas_instance:
	./dist/exordos dbaas instances delete $(DBAAS_INSTANCE_UUID) -y

list_dbaas_users:
	./dist/exordos dbaas users list --instance-uuid $(DBAAS_INSTANCE_UUID)

show_dbaas_user:
	./dist/exordos dbaas users show $(DBAAS_USER_UUID) --instance-uuid $(DBAAS_INSTANCE_UUID)

add_dbaas_user:
	./dist/exordos dbaas users add -u $(DBAAS_USER_UUID) -p $(PROJECT_ID) -i $(DBAAS_INSTANCE_UUID) -n $(DBAAS_USER_NAME) --password 12345678

update_dbaas_user:
	./dist/exordos dbaas users update $(DBAAS_USER_UUID) -i $(DBAAS_INSTANCE_UUID) --password 87654321

delete_dbaas_user:
	./dist/exordos dbaas users delete $(DBAAS_USER_UUID) --instance-uuid $(DBAAS_INSTANCE_UUID) -y

list_dbaas_databases:
	./dist/exordos dbaas databases list --instance-uuid $(DBAAS_INSTANCE_UUID)

show_dbaas_database:
	./dist/exordos dbaas databases show $(DBAAS_DATABASE_UUID) --instance-uuid $(DBAAS_INSTANCE_UUID)

add_dbaas_database:
	./dist/exordos dbaas databases add -u $(DBAAS_DATABASE_UUID) -p $(PROJECT_ID) -i $(DBAAS_INSTANCE_UUID) -n $(DBAAS_DATABASE_NAME) --owner $(DBAAS_USER_NAME)

update_dbaas_database:
	./dist/exordos dbaas databases update $(DBAAS_DATABASE_UUID) -i $(DBAAS_INSTANCE_UUID) --owner $(DBAAS_USER_NAME)

delete_dbaas_database:
	./dist/exordos dbaas databases delete $(DBAAS_DATABASE_UUID) --instance-uuid $(DBAAS_INSTANCE_UUID) -y
