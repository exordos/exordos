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
from __future__ import annotations

from unittest import mock

from click.testing import CliRunner
import pytest

from exordos import constants as c
from exordos.cmd.dns import dns_group
from exordos.common.cmd_context import ContextObject

UUID = "11111111-1111-1111-1111-111111111111"
RECORD_UUID = "22222222-2222-2222-2222-222222222222"


@pytest.mark.parametrize("command", ["info", "i"])
@pytest.mark.parametrize("output", ["table", "json", "yaml"])
@pytest.mark.parametrize("records_present", [True, False])
def test_info_cmd_shows_domain_and_records(command, output, records_present):
    domain = {"uuid": UUID, "name": "example.com"}
    records = (
        [{"uuid": RECORD_UUID, "name": "www", "type": "A", "record": ["192.0.2.1"]}]
        if records_present
        else []
    )
    client = mock.Mock()
    client.filter.side_effect = [[domain], records]
    with mock.patch(
        "exordos.cmd.dns.domains.commands.base_client.get_user_api_client",
        return_value=client,
    ):
        result = CliRunner().invoke(
            dns_group,
            ["domains", command, "example.com", "-o", output],
            obj=ContextObject(
                auth_data={},
                cfg_path=None,
                developer_key_path=None,
                cfg={},
                need_update=None,
            ),
        )

    assert result.exit_code == 0, result.output
    assert "example.com" in result.output
    assert ("192.0.2.1" in result.output) == records_present
    assert client.filter.call_args_list == [
        mock.call(c.DOMAIN_COLLECTION, name="example.com"),
        mock.call(c.RECORD_COLLECTION.format(domain_uuid=UUID)),
    ]
