"""
Eos Lighting Metadata Editor
"""
# Copyright (c) 2020 Eos Lighting contributors
#
# The Eos Editor includes software from questionary (https://github.com/tmbo/questionary),
# under the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys

if sys.version_info[0] < 3:  # Python 2.x
    str = basestring
else:  # Python 3.x
    pass

import os, json
import requests as http
import click
from click import echo, clear

from constants import *
import menu
import utils
from rest.utils import validate_hostname, validate_item, update_item
from rest.metadata import get_value

master_group_name = ""
reinit_item_name = ""


def load_config(openhab_host):
    """Load Eos settings from ``{$OH_CONF}/automation/lib/python/configuration.py``
    """
    global master_group_name
    master_group_name = utils.get_conf_value(CONF_KEY_MASTER_GROUP, str)
    if not master_group_name:
        echo(
            "ERROR: No '{name}' specified in configuration".format(
                name=CONF_KEY_MASTER_GROUP
            ),
            err=True,
        )
        exit(1)

    if not utils.get_conf_value(
        CONF_KEY_SCENE_PREFIX, str, ""
    ) and not utils.get_conf_value(CONF_KEY_SCENE_SUFFIX, str, ""):
        echo(
            "ERROR: Must specify at least one of '{prefix}' or '{suffix}' in configuration".format(
                prefix=CONF_KEY_SCENE_PREFIX, suffix=CONF_KEY_SCENE_SUFFIX
            ),
            err=True,
        )
        exit(1)

    global reinit_item_name
    reinit_item_name = utils.get_conf_value(CONF_KEY_REINIT_ITEM)
    if reinit_item_name and validate_item(reinit_item_name, openhab_host) is None:
        echo(
            "WARNING: Eos reload item '{name}' does not exist".format(
                name=reinit_item_name
            ),
            err=True,
        )
        reinit_item_name = ""

    master_group_item = validate_item(master_group_name, openhab_host)
    if not master_group_item:
        echo(
            "ERROR: Master group item '{group}' does not exist".format(
                group=master_group_name
            )
        )
        exit(1)
    elif master_group_item["type"] not in utils.itemtypesGroup:
        echo(
            "ERROR: Master group item '{group}' is not a GroupItem".format(
                group=master_group_name
            )
        )
        exit(1)


def conf_file_exists(ctx, param, value):
    """
    Validate conf file exists
    """
    conf_file = "configuration.py"
    if value[-len(conf_file) :] != conf_file:
        value = os.path.join(value, conf_file)
    value = os.path.realpath(value)
    if os.path.isfile(value):
        return value
    else:
        raise click.BadParameter(
            "'configuration.py' not found at '{path}'".format(
                path=os.path.split(value)[0]
            )
        )


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("-s", "--openhab-host", "opt_openhab_host")
@click.option("-c", "--configuration", "opt_conf_path")
def eos_editor(ctx, opt_openhab_host, opt_conf_path):
    """
    Eos Item Metadata Editor

    If called with no command it will start in interactive mode.
    """
    if ctx.invoked_subcommand is None:
        live()


@eos_editor.command()
@click.option(
    "-s",
    "--openhab-host",
    "opt_openhab_host",
    prompt="Enter your openHAB server address",
    default="localhost:8080",
    callback=validate_hostname,
    help="openHAB server address",
)
@click.option(
    "-c",
    "--configuration",
    "opt_conf_path",
    prompt="Path to 'configuration.py'",
    default=utils.conf_path,
    callback=conf_file_exists,
    help="Helper Library 'configuration.py'",
)
def live(opt_openhab_host, opt_conf_path):
    """Interactive editing of all lights in Eos"""
    sys.modules[utils.__name__].conf_path = opt_conf_path
    load_config(opt_openhab_host)
    menu.menu_navigate(master_group_name, opt_openhab_host)


@eos_editor.command()
@click.option(
    "-s",
    "--openhab-host",
    "opt_openhab_host",
    prompt="Enter your openHAB server address",
    default="localhost:8080",
    callback=validate_hostname,
    help="openHAB server address",
)
@click.option(
    "-c",
    "--configuration",
    "opt_conf_path",
    prompt="Path to 'configuration.py'",
    default=utils.conf_path,
    callback=conf_file_exists,
    help="Helper Library 'configuration.py'",
)
@click.argument("arg_item_name")
def edit(opt_openhab_host, opt_conf_path, arg_item_name):
    """Edit a single light"""
    sys.modules[utils.__name__].conf_path = opt_conf_path
    load_config(opt_openhab_host)

    item = validate_item(arg_item_name, opt_openhab_host)
    item, data = menu.menu_eos(
        item,
        menu.build_data(item, opt_openhab_host),
        opt_openhab_host,
        6 if item["type"] in itemtypesGroup else 2,
        is_light=True if item["type"] in itemtypesLight else False,
        is_group=True if item["type"] in itemtypesGroup else False,
    ) or (None, None)
    if data:
        if not menu.save_metadata(item, opt_openhab_host, data):
            pass  # TODO something went wrong
        if item.get("editable", False):
            update_item(item, opt_openhab_host)
    del item, data

    clear()


if __name__ == "__main__":
    eos_editor()
