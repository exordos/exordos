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

import ipaddress

import pytest

from exordos.stand import models


def _stand(main_cidr: str, boot_cidr: str) -> models.Stand:
    main = ipaddress.IPv4Network(main_cidr)
    return models.Stand.single_bootstrap_stand(
        image="core.qcow2",
        image_uri="https://example.com/core.qcow2",
        core_ip=main[2],
        network=models.Network(name="main", cidr=main),
        boot_network=models.Network(name="boot", cidr=ipaddress.IPv4Network(boot_cidr)),
    )


def test_disjoint_networks_are_valid() -> None:
    assert _stand("10.31.0.0/22", "10.30.0.0/24").is_valid()


@pytest.mark.parametrize(
    "boot_cidr",
    [
        "10.31.0.0/24",  # inside the main network
        "10.31.0.0/22",  # same as the main network
        "10.0.0.0/8",  # contains the main network
    ],
)
def test_overlapping_networks_are_invalid(boot_cidr: str) -> None:
    assert not _stand("10.31.0.0/22", boot_cidr).is_valid()
