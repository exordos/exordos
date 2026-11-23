#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

"""The boot network's own bridge: isolated, with the host on it."""

import ipaddress
from unittest import mock

from exordos.infra.libvirt import libvirt


def test_create_isolated_network_puts_the_host_on_it():
    """A hypervisor reaches the installation's boot API on this network, and
    an overlay guest netboots only by asking its hypervisor to fetch for it.
    Without an address of it the host cannot ask either."""
    with mock.patch.object(libvirt, "define_network") as define:
        libvirt.create_isolated_network(
            "boot-net", cidr=ipaddress.IPv4Network("10.30.0.0/24")
        )

    xml = define.call_args[0][1]
    assert '<ip address="10.30.0.1" netmask="255.255.255.0"/>' in xml
    # Still isolated: nothing is routed or translated out of it.
    assert "<forward" not in xml
    assert "<dhcp" not in xml


def test_create_isolated_network_without_a_cidr_stays_bare():
    """The shape every installation before this had, and the one a caller
    that names no addressing still gets."""
    with mock.patch.object(libvirt, "define_network") as define:
        libvirt.create_isolated_network("boot-net")

    xml = define.call_args[0][1]
    assert "<ip" not in xml
    assert "<forward" not in xml
