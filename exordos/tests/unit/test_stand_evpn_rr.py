#    Copyright 2026 Genesis Corporation.
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

"""The ``--evpn-rr-address`` / ``--evpn-peer-prefix`` bootstrap flags carry the
route-reflector overrides for a multi-hypervisor realm. The stand is delivered
to the core as ``{"stand": dataclasses.asdict(stand)}`` and the core reads
``spec["stand"]["evpn_rr_address"]`` / ``["evpn_peer_prefixes"]`` — so the flags
must land under exactly those keys."""

import dataclasses
import ipaddress

from exordos.stand import models as stand_models


def _stand(**overrides):
    return stand_models.Stand.single_bootstrap_stand(
        image="core.raw",
        image_uri="http://repo/core.raw",
        core_ip=ipaddress.IPv4Address("192.168.100.2"),
        network=stand_models.Network(
            name="main", cidr=ipaddress.IPv4Network("192.168.100.0/24")
        ),
        boot_network=stand_models.Network(
            name="boot", cidr=ipaddress.IPv4Network("172.16.0.0/24")
        ),
        **overrides,
    )


def test_evpn_rr_overrides_reach_the_delivered_spec():
    spec = dataclasses.asdict(
        _stand(
            evpn_rr_address="10.20.0.24",
            evpn_peer_prefixes=["10.20.0.0/22"],
        )
    )
    assert spec["evpn_rr_address"] == "10.20.0.24"
    assert spec["evpn_peer_prefixes"] == ["10.20.0.0/22"]


def test_evpn_rr_overrides_default_to_empty():
    spec = dataclasses.asdict(_stand())
    assert spec["evpn_rr_address"] is None
    assert spec["evpn_peer_prefixes"] == []


def _with_hypervisor(**hyper):
    stand = _stand()
    stand.hypervisors.append(
        stand_models.Hypervisor(
            network_type="network",
            network="main",
            connection_uri="qemu+tcp://192.168.100.1/system",
            **hyper,
        )
    )
    return stand


def test_a_stand_that_asked_for_no_ovs_says_nothing_about_it():
    """A hypervisor's block reaches the core as a machine pool's
    `driver_spec`, and a core that does not know a key in it refuses the
    *whole* spec: measured on a released 0.2.9 core, which died in
    `apply_startup_db` with `ParseError: (Unknown fields: {'ovs': False})`
    and never finished bootstrapping. A default that is sent is not a
    default -- it is this CLI telling an older core about a feature it does
    not have."""
    spec = _with_hypervisor().as_spec()

    assert "ovs" not in spec["hypervisors"][0]


def test_an_ovs_hypervisor_still_says_so():
    spec = _with_hypervisor(ovs=True).as_spec()

    assert spec["hypervisors"][0]["ovs"] is True
