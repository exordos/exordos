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
from __future__ import annotations

import dataclasses
import ipaddress
import random
import re
import typing as tp
import uuid


@dataclasses.dataclass
class Port:
    mac: str
    ip: ipaddress.IPv4Address | None = None

    @classmethod
    def from_spec(cls, spec: dict[str, tp.Any]) -> Port:
        spec = spec.copy()
        spec["ip"] = (
            ipaddress.IPv4Address(spec["ip"]) if spec["ip"] is not None else None
        )
        return cls(**spec)

    @classmethod
    def gen_mac(cls) -> str:
        return (
            "52:54:00:"
            f"{random.randint(0, 255):02x}:"
            f"{random.randint(0, 255):02x}:"
            f"{random.randint(0, 255):02x}"
        )

    @classmethod
    def port_with_random_mac(cls) -> Port:
        return cls(mac=cls.gen_mac(), ip=None)


@dataclasses.dataclass
class Network:
    name: str
    cidr: ipaddress.IPv4Network
    dhcp: bool = False

    # Is an user's network bridge
    managed_network: bool = True

    @classmethod
    def dummy(cls) -> Network:
        return cls(
            name="dummy",
            cidr=ipaddress.IPv4Network("0.0.0.0/24"),
            managed_network=False,
        )

    @property
    def is_dummy(self) -> bool:
        return self.name == "dummy"

    @classmethod
    def from_spec(cls, spec: dict[str, tp.Any]) -> Network:
        spec = spec.copy()
        spec["cidr"] = ipaddress.IPv4Network(spec["cidr"])
        return cls(**spec)


@dataclasses.dataclass
class Disk:
    size: int
    label: str = ""

    def uuid(self, node_uuid: uuid.UUID) -> uuid.UUID:
        return uuid.uuid5(node_uuid, self.label)

    @classmethod
    def from_spec(cls, spec: dict[str, tp.Any]) -> Disk:
        return cls(**spec)


@dataclasses.dataclass
class Node:
    uuid: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    name: str = "exordos-node"
    memory: int = 1024
    cores: int = 1
    disks: list[Disk] = dataclasses.field(default_factory=lambda: [Disk(size=10)])
    image: str | None = None
    image_uri: str | None = None
    ports: list[Port] = dataclasses.field(default_factory=list)

    @classmethod
    def from_spec(cls, spec: dict[str, tp.Any]) -> Node:
        spec = spec.copy()
        spec["disks"] = [Disk.from_spec(d) for d in spec.pop("disks", [])]
        spec["ports"] = [Port.from_spec(p) for p in spec.pop("ports", [])]
        return cls(**spec)


@dataclasses.dataclass
class Bootstrap(Node):
    name: str = "exordos-bootstrap"
    # Two disks for the bootstrap, one for the root and one for the data
    disks: list[Disk] = dataclasses.field(
        default_factory=lambda: [
            Disk(size=10, label="root-volume"),
            Disk(size=10, label="data"),
        ]
    )

    @classmethod
    def from_node(cls, node: Node) -> Bootstrap:
        return cls(**dataclasses.asdict(node))


@dataclasses.dataclass
class Hypervisor:
    network_type: str
    network: str
    connection_uri: str
    storage_pool: str = "default"
    kind: str = "libvirt"
    # Required by the "exordos_local_hyper" kind: the node uuid of the
    # local universal agent (LocalPoolAgentDriver) this pool is pinned to.
    node: str | None = None
    # Required by the "exordos_local_hyper" kind: the node encryption key
    # (base64) already written to the local agent's disk, so the core
    # stores the same key instead of generating a mismatched one.
    private_key: str | None = None
    machine_prefix: str = "vm-"
    # None = default boot chain (stock ROM -> undionly.kpxe over the
    # core's TFTP), which works with any guest RAM size. The custom Seed
    # OS iPXE ROM hangs at "initialising devices" with >2048 MiB guests.
    iface_rom_file: str | None = None
    # OVS-backed hypervisor (SDN): overlay ports of guests plug into the
    # host's br-int. Requires openvswitch + the SDN agent on the host
    # (the exordos-realm image ships both).
    #
    # `None` rather than `False` so that a stand which was not asked for an
    # OVS hypervisor says nothing about one: the spec goes to the core as
    # the pool's `driver_spec`, and a core that does not know the field
    # refuses to parse the whole spec -- `ParseError: (Unknown fields:
    # {'ovs': False})`, on an installation that never asked for any of
    # this. Dropped from the rendered spec by `as_spec` below.
    ovs: bool | None = None

    @classmethod
    def from_spec(cls, spec: dict[str, tp.Any]) -> Hypervisor:
        return cls(**spec)

    def is_valid(self, network: Network) -> bool:
        match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", self.connection_uri)
        if not match:
            # Perhaps it's a domain name
            return True

        ip_str = match.group(0)
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            return False

        return network.cidr.overlaps(ipaddress.ip_network(ip))


@dataclasses.dataclass
class Stand:
    # Main network of the installation. After bootstrap
    # procedure a node will be connected to this network.
    network: Network
    # Network used for the bootstrapping procedure.
    # It's an isolated private network.
    boot_network: Network
    bootstraps: list[Bootstrap]
    baremetals: list[Node]
    hypervisors: list[Hypervisor] = dataclasses.field(default_factory=list)
    name: str = "dev-stand"
    # SDN route-reflector overrides for a multi-hypervisor realm: the extra
    # hypervisors live outside the nested core's network and reach the RR
    # through the control node's flat address (Border forwards 179). Empty
    # leaves the core node's own IP and just the installation network.
    evpn_rr_address: str | None = None
    evpn_peer_prefixes: list[str] = dataclasses.field(default_factory=list)

    def as_spec(self) -> dict[str, tp.Any]:
        """The stand as it goes onto the config drive.

        `asdict`, minus what was never asked for. A hypervisor's block
        reaches the core as a machine pool's `driver_spec`, and a core that
        does not know a key in it refuses the *whole* spec rather than the
        key -- `ParseError: (Unknown fields: {'ovs': False})`, on a
        bootstrap that never mentioned an overlay. So an option nobody set
        is not sent at all, which is also the only thing this CLI can do
        about a core older than itself.
        """
        spec = dataclasses.asdict(self)
        for hypervisor in spec.get("hypervisors") or []:
            if hypervisor.get("ovs") is None:
                hypervisor.pop("ovs", None)
        return spec

    def is_valid(self) -> bool:
        if self.network.is_dummy or not self.bootstraps:
            return False

        if all(b.image is None for b in self.bootstraps):
            return False

        # Overlapping networks put the same subnet on both core interfaces,
        # so replies leave via the isolated boot network and are lost.
        if not self.boot_network.is_dummy and self.network.cidr.overlaps(
            self.boot_network.cidr
        ):
            return False

        for h in self.hypervisors:
            if not h.is_valid(self.network):
                return False

        return True

    def has_bootstrap_image(self) -> bool:
        return any(b.image for b in self.bootstraps)

    def set_bootstrap_image(self, image: str):
        for b in self.bootstraps:
            b.image = image

    @classmethod
    def single_bootstrap_stand(
        cls,
        image: str,
        image_uri: str,
        core_ip: ipaddress.IPv4Address,
        network: Network,
        boot_network: Network,
        cores: int = 1,
        memory: int = 1024,
        disks: list[int] | None = None,
        name: str = "dev-stand",
        bootstrap_name: str = "bootstrap",
        hypervisors: tp.Collection[Hypervisor] = (),
        evpn_rr_address: str | None = None,
        evpn_peer_prefixes: tp.Collection[str] = (),
    ) -> Stand:
        ports = [
            Port(mac=Port.gen_mac(), ip=core_ip),
            Port(mac=Port.gen_mac()),
        ]
        if disks is None:
            disks = [
                Disk(size=10, label="root-volume"),
                Disk(size=10, label="data"),
            ]
        else:
            if len(disks) != 2:
                raise ValueError("Core node requires exactly 2 disks!")
            disks = [
                Disk(size=int(disks[0]), label="root-volume"),
                Disk(size=int(disks[1]), label="data"),
            ]

        return cls(
            name=name,
            network=network,
            boot_network=boot_network,
            bootstraps=[
                Bootstrap(
                    name=bootstrap_name,
                    image=image,
                    image_uri=image_uri,
                    cores=cores,
                    memory=memory,
                    disks=disks,
                    ports=ports,
                )
            ],
            baremetals=[],
            hypervisors=list(hypervisors),
            evpn_rr_address=evpn_rr_address,
            evpn_peer_prefixes=list(evpn_peer_prefixes),
        )

    @classmethod
    def empty_stand(
        cls,
        name: str = "dev-stand",
        network: Network | None = None,
        boot_network: Network | None = None,
    ) -> Stand:
        if network is None:
            network = Network.dummy()

        if boot_network is None:
            boot_network = Network.dummy()

        return cls(
            name=name,
            bootstraps=[],
            baremetals=[],
            network=network,
            boot_network=boot_network,
            hypervisors=[],
        )

    @classmethod
    def from_spec(cls, spec: dict[str, tp.Any]) -> Stand:
        spec = spec.copy()
        bootstraps = [Bootstrap.from_spec(b) for b in spec.pop("bootstraps", [])]
        baremetals = [Node.from_spec(n) for n in spec.pop("baremetals", [])]

        if "network" not in spec:
            network = Network.dummy()
        else:
            network = Network.from_spec(spec.pop("network"))

        if "boot_network" not in spec:
            boot_network = Network.dummy()
        else:
            boot_network = Network.from_spec(spec.pop("boot_network"))

        return cls(
            bootstraps=bootstraps,
            baremetals=baremetals,
            network=network,
            boot_network=boot_network,
            hypervisors=[Hypervisor.from_spec(h) for h in spec.pop("hypervisors", [])],
            **spec,
        )
