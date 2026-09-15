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

from exordos.common import table


class TestFillTable:
    def test_callable_field_returning_a_bool_is_rendered(self) -> None:
        fields_map = {
            "Ephemeral": lambda e: e["ephemeral"],
        }

        result = table.fill_table([{"ephemeral": False}], fields_map)

        assert list(result.columns[0].cells) == ["False"]

    def test_callable_field_returning_an_int_is_rendered(self) -> None:
        fields_map = {
            "Total": lambda e: e["total"],
        }

        result = table.fill_table([{"total": 100}], fields_map)

        assert list(result.columns[0].cells) == ["100"]
