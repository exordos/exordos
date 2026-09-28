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

"""The default IAM client a bootstrapped core gets."""

from exordos.clients import base as base_client
from exordos.cmd.stand import commands


def test_a_stand_gets_a_generated_client_secret():
    first = commands._iam_default_client_settings()
    again = commands._iam_default_client_settings()

    assert first["default_client_id"] == "Exordos"
    assert first["default_client_secret"] != again["default_client_secret"]


def test_a_managed_realm_gets_the_client_the_cli_logs_in_with():
    iam = commands._iam_default_client_settings(well_known=True)

    assert iam["default_client_uuid"] == "00000000-0000-0000-0000-000000000000"
    assert iam["default_client_id"] == base_client.DEFAULT_CLIENT_ID
    assert iam["default_client_secret"] == base_client.DEFAULT_CLIENT_SECRET
