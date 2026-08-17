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

from io import StringIO
import typing as tp

from rich import print as rprint
from rich import print_json as rprint_json
from rich.console import Console
from rich.table import Table
import rich_click as click
import ruamel.yaml

SHOW_FIELDS = [
    "Field",
    "Value",
]


def dump_yaml_ruamel_to_str(data: tp.Union[dict, list]) -> str:
    loader = ruamel.yaml.YAML()
    loader.indent(sequence=4, offset=2)
    string_stream = StringIO()
    loader.dump(data, string_stream)
    output_str = string_stream.getvalue()
    string_stream.close()
    return output_str


def table_to_list_of_dicts(table: Table) -> tp.List[dict]:
    headers = [col.header.lower() for col in table.columns]
    rows_data = zip(*(col.cells for col in table.columns))
    return [dict(zip(headers, row)) for row in rows_data]


def get_table(*args, **kwargs) -> Table:
    table = Table(show_header=True, *args, **kwargs)
    return table


def fill_table(
    entities: tp.List[dict],
    fields_map: dict,
    fields: tp.Optional[tuple[str, ...]] = None,
):
    if entities:
        fields_map = {
            k: v for k, v in fields_map.items() if callable(v) or v in entities[0]
        }
    if fields:
        normalized_fields = {f.lower() for f in fields}
        fields_map = {
            k: v
            for k, v in fields_map.items()
            if k.lower() in normalized_fields
            or (isinstance(v, str) and v.lower() in normalized_fields)
        }
    table = get_table(*fields_map.keys())

    for entity in entities:
        table.add_row(
            *[
                str(entity[field.lower()]) if not callable(field) else field(entity)
                for field in fields_map.values()
            ]
        )

    return table


def print_table(
    table: Table,
    output: str = "table",
    msg: tp.Optional[str] = None,
    fg: tp.Optional[str] = None,
) -> None:
    if msg and output in ["table", "text"]:
        if fg:
            click.secho(msg, fg=fg)
        else:
            click.echo(msg)
        rprint(table)
    elif output == "json":
        data = table_to_list_of_dicts(table)
        rprint_json(data=data)
    elif output == "html":
        console = Console(file=StringIO(), record=True)
        console.print(table)
        data = console.export_html()
        click.echo(data)
    elif output == "yaml":
        objects = table_to_list_of_dicts(table)
        click.echo(dump_yaml_ruamel_to_str(objects))
    else:
        rprint(table)


def show_data(data: dict, output: str = "table", msg: tp.Optional[str] = None) -> None:
    table = get_table(*SHOW_FIELDS)
    for key, value in data.items():
        table.add_row(key, str(value))
    print_table(table, output, msg)
