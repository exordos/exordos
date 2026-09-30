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

from io import StringIO

from rich.console import Console

from exordos.common import table as table_utils

UUID = "04ae8c93-a744-43fd-be24-94a9a9d1f0e2"
NAME = "dbaas-dp-6d7cc758-ea58-4ee5-b1c2-0123456789ab"


def _render(table, width: int) -> str:
    console = Console(file=StringIO(), width=width)
    console.print(table)
    return console.file.getvalue()


def _columns_text(output: str) -> list:
    # Folded values are split over lines, so join every column's lines
    rows = [
        line.strip("\u2502").split("\u2502")
        for line in output.splitlines()
        if line.startswith("\u2502")
    ]
    return ["".join(cell.strip() for cell in col) for col in zip(*rows)]


def test_fill_table_narrow_terminal_uuid_and_name_not_truncated():
    entities = [
        {
            "uuid": UUID,
            "name": NAME,
            "image": "https://repo.exordos.com/exordos/images/some-long-image",
            "status": "ACTIVE",
        }
    ]
    fields_map = {"UUID": "uuid", "Name": "name", "Image": "image", "Status": "status"}

    output = _render(table_utils.fill_table(entities, fields_map), width=120)

    columns = _columns_text(output)
    assert columns[0] == UUID
    assert columns[1] == NAME


def test_get_table_other_columns_wrap():
    table = table_utils.get_table("UUID", "Name", "Image")

    assert [c.overflow for c in table.columns] == ["fold", "fold", "ellipsis"]
    assert [c.no_wrap for c in table.columns] == [True, False, False]
    assert table.columns[2].min_width == len("Image")


def test_fill_table_80_columns_other_columns_visible():
    entities = [
        {
            "uuid": UUID,
            "name": NAME,
            "image": "https://repo.exordos.com/exordos/images/some-long-image",
            "status": "ACTIVE",
        }
    ]
    fields_map = {"UUID": "uuid", "Name": "name", "Image": "image", "Status": "status"}

    output = _render(table_utils.fill_table(entities, fields_map), width=80)

    assert "Image" in output
    assert "Status" in output
    columns = _columns_text(output)
    assert columns[0] == UUID
    assert columns[1] == NAME
