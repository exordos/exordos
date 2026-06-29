#    Copyright 2025 Genesis Corporation.
#
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import ipaddress
import os
import typing as tp

PKG_NAME = "exordos"
GITHUB_RELEASES_URL = f"https://api.github.com/repos/infraguys/{PKG_NAME}/releases"
EXORDOS_REPO_URL = "https://repo.exordos.com"
ELEMENT_REPO_PATH = "exordos-elements"
ELEMENT_REPO_URL = f"{EXORDOS_REPO_URL}/{ELEMENT_REPO_PATH}"
LIBVIRT_DEF_POOL_PATH = "/var/lib/libvirt/images"
DEF_GEN_CFG_FILE_NAME = "exordos.yaml"
DEF_GEN_WORK_DIR_NAME = "exordos"
DEF_GEN_OUTPUT_DIR_NAME = "output"
RC_BRANCHES = ("master", "main")
ENCRYPTED_EXTENSION = ".encrypted"
EP_BACKUP_DRIVERS = "exordos.backup.drivers"
EP_REPO_DRIVERS = "exordos.repo.drivers"
GB_SHIFT = 30

# IAM constants
DEFAULT_IAM_TTL = 15 * 60
DEFAULT_IAM_REFRESH_TTL = 60 * 60
DEFAULT_IAM_SCOPE = "profile"

# ENV vars
ENV_GEN_DEV_KEYS = "GEN_DEV_KEYS"

# Types
ImageProfileType = tp.Literal["ubuntu_24", "exordos_base", "exordos_base_minimal"]
ImageFormatType = tp.Literal["raw", "qcow2", "gz", "zst"]
NetType = tp.Literal["network", "bridge"]
VersionSuffixType = tp.Literal["latest", "none", "element"]
DomainState = tp.Literal["all", "inactive", "state-paused"]
NodeType = tp.Literal["bootstrap", "baremetal"]

ENV_FILE_FORMAT = tp.Literal["json", "env"]

MANIFEST_COLLECTION = "/v1/em/manifests/"
ELEMENT_COLLECTION = "/v1/em/elements/"
SERVICE_COLLECTION = "/v1/em/services/"
RESOURCE_COLLECTION = "/v1/em/resources/"
IMPORTS_COLLECTION = "/v1/em/imports/"
EXPORTS_COLLECTION = "/v1/em/exports/"

PROFILE_COLLECTION = "/v1/vs/profiles/"
VALUE_COLLECTION = "/v1/vs/values/"
VARIABLE_COLLECTION = "/v1/vs/variables/"

CERTIFICATE_COLLECTION = "/v1/secret/certificates/"
PASSWORD_COLLECTION = "/v1/secret/passwords/"
SSH_KEY_COLLECTION = "/v1/secret/ssh_keys/"
RSA_KEY_COLLECTION = "/v1/secret/rsa_keys/"

NODE_COLLECTION = "/v1/compute/nodes/"
HYPERVISOR_COLLECTION = "/v1/compute/hypervisors/"
SET_COLLECTION = "/v1/compute/sets/"

USER_COLLECTION = "/v1/iam/users/"
IDP_COLLECTION = "/v1/iam/idp/"
CLIENT_COLLECTION = "/v1/iam/clients/"
ORGANIZATION_COLLECTION = "/v1/iam/organizations/"
PROJECT_COLLECTION = "/v1/iam/projects/"
ROLE_COLLECTION = "/v1/iam/roles/"
PERMISSION_COLLECTION = "/v1/iam/permissions/"
ROLE_BINDING_COLLECTION = "/v1/iam/role_bindings/"
PERMISSION_BINDING_COLLECTION = "/v1/iam/permission_bindings/"

CONFIG_COLLECTION = "/v1/config/configs/"

DOMAIN_COLLECTION = "/v1/dns/domains/"
RECORD_COLLECTION = "/v1/dns/domains/{domain_uuid}/records/"


LB_COLLECTION = "/v1/network/lb/"
BACKEND_POOL_COLLECTION = "/v1/network/lb/{lb_uuid}/backend_pools/"
VHOST_COLLECTION = "/v1/network/lb/{lb_uuid}/vhosts/"
ROUTE_COLLECTION = "/v1/network/lb/{lb_uuid}/vhosts/{vhost_uuid}/routes/"

# Cli
CONFIG_DIR = "~/.exordos"
CONFIG_FILE = os.path.expanduser(f"{CONFIG_DIR}/exordosctl.yaml")
LAST_CHECK_FILE = os.path.expanduser(f"{CONFIG_DIR}/exordosctl.last_version_check")
BOOTSTRAP_USER = "ubuntu"
UPDATE_CHECK_INTERVAL = 60 * 60  # 1 hour in seconds

CORE_ELEMENT = "core"
BASE_ELEMENTS = [CORE_ELEMENT, "ecosystem_realm"]

DEFAULT_TABLE_FORMAT = "table"
TABLE_FORMATS = ["json", "html", DEFAULT_TABLE_FORMAT, "yaml"]

GC_CIDR = ipaddress.IPv4Network("10.20.0.0/22")
GC_BOOT_CIDR = ipaddress.IPv4Network("10.30.0.0/24")
GC_ADDRESS = ipaddress.IPv4Address("10.20.0.1")
