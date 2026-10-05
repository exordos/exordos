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

from rich import get_console
from rich import print as rprint
from rich import print_json as rprint_json
from rich.console import Console
from rich.table import Table
import rich_click as click

# Columns which are folded (never truncated); UUID is kept on one line
# unless the table does not fit the console otherwise (see fit_table_to_width)
NO_WRAP_COLUMNS = {"uuid"}
FOLD_COLUMNS = {"uuid", "name"}
# Keeps other columns visible on narrow terminals
MIN_WRAP_COLUMN_WIDTH = 6

SHOW_FIELDS = [
    "Field",
    "Value",
]


def dump_yaml_ruamel_to_str(data: tp.Union[dict, list]) -> str:
    import ruamel.yaml

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
    table = Table(*args, show_header=True, **kwargs)
    for column in table.columns:
        header = column.header.lower() if isinstance(column.header, str) else None
        if header in FOLD_COLUMNS:
            column.overflow = "fold"
            column.no_wrap = header in NO_WRAP_COLUMNS
        else:
            # Short columns (Cores, RAM, ...) must not be padded
            header_width = len(header) if header else MIN_WRAP_COLUMN_WIDTH
            column.min_width = min(header_width, MIN_WRAP_COLUMN_WIDTH)
    return table


def fit_table_to_width(table: Table, console: Console) -> None:
    """Relax column constraints until the table fits the console width."""

    def overflows() -> bool:
        max_width = console.width - table._extra_width
        options = console.options.update_width(max_width)
        return sum(table._calculate_column_widths(console, options)) > max_width

    # Fold UUID first, then drop min widths as the last resort
    if overflows():
        for column in table.columns:
            column.no_wrap = False
    if overflows():
        for column in table.columns:
            column.min_width = None


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
        fit_table_to_width(table, get_console())
        rprint(table)
    elif output == "json":
        data = table_to_list_of_dicts(table)
        rprint_json(data=data)
    elif output == "html":
        console = Console(file=StringIO(), record=True)
        fit_table_to_width(table, console)
        console.print(table)
        data = console.export_html()
        click.echo(data)
    elif output == "yaml":
        objects = table_to_list_of_dicts(table)
        click.echo(dump_yaml_ruamel_to_str(objects))
    else:
        fit_table_to_width(table, get_console())
        rprint(table)


def show_data(data: dict, output: str = "table", msg: tp.Optional[str] = None) -> None:
    table = get_table(*SHOW_FIELDS)
    for key, value in data.items():
        table.add_row(key, str(value))
    print_table(table, output, msg)
