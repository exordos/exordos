#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

from unittest import mock

from exordos.cmd.compute.hypervisors import commands


def _installed(install):
    """The package names an `apt-get install` run was given."""
    names = []
    for call in install.call_args_list:
        for packages in call.args[:1]:
            names.extend(packages)
    return names


def test_configure_sdn_installs_ovs_and_br_int():
    """The overlay data plane needs OVS running and `br-int` present before
    libvirt can plug a guest tap into it."""
    with mock.patch.object(commands, "run_command") as run:
        commands._configure_sdn()

    calls = [c.args[0] for c in run.call_args_list]
    assert ["systemctl", "enable", "--now", "openvswitch-switch"] in calls
    assert ["ovs-vsctl", "--may-exist", "add-br", "br-int"] in calls


def test_install_sdn_brings_the_packages_the_overlay_needs():
    with mock.patch.object(commands, "_apt_install") as install:
        commands._install_sdn_packages()

    assert "openvswitch-switch" in _installed(install)


def test_a_hypervisor_without_an_overlay_is_not_given_one():
    """`init` prepares any hypervisor, `init --sdn` prepares one that will
    wire an overlay. An installation with no overlay has no use for an Open
    vSwitch daemon, a `br-int` bridge or a C toolchain, and on a mirror
    without `openvswitch-switch` installing them would fail `init` before
    libvirt was even configured."""
    with mock.patch.object(commands, "_apt_install") as install:
        commands._install_packages()

    packages = _installed(install)
    assert "qemu-system-x86" in packages, "init still prepares a hypervisor"
    for sdn_only in ("openvswitch-switch", "build-essential", "python3-dev"):
        assert sdn_only not in packages
