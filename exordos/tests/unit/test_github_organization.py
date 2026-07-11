#    Copyright 2026 Genesis Corporation.
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

from exordos import constants
from exordos.infra.libvirt import libvirt


def test_github_release_url_uses_exordos_organization() -> None:
    assert (
        constants.GITHUB_RELEASES_URL
        == "https://api.github.com/repos/exordos/exordos/releases"
    )


def test_libvirt_metadata_namespace_uses_exordos_organization() -> None:
    assert 'xmlns:genesis="https://github.com/exordos"' in libvirt.domain_template
