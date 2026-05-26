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
import qrcode
import qrcode.constants
import rich_click as click


def print_qr(uri: str) -> None:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_L, border=1
    )
    qr.add_data(uri)
    qr.make(fit=True)
    white = "\033[0;37;47m  "
    black = "\033[0;37;40m  "
    reset = "\033[0m"
    click.echo(white * (qr.modules_count + 2) + reset)
    for row in qr.modules:
        click.echo(white + "".join(black if cell else white for cell in row) + white + reset)
    click.echo(white * (qr.modules_count + 2) + reset)
