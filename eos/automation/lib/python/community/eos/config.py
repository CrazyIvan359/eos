"""
Eos Lighting

Config value loader
"""
# Copyright (c) 2020 Eos Lighting contributors
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

from community.eos import log
from community.eos.constants import *
from community.eos import constants

import sys, copy, collections

__all__ = ["load"]


def _get_conf_value(name, valid_types=None, default=None):
    """Gets ``name`` from configuration.

    Returns ``default`` if not present or not one of types in ``valid_types``
    """
    # importing here so we can reload each time and catch any updates the user may have made
    try:
        import configuration

        reload(configuration)
    except:
        return default

    if hasattr(configuration, name):
        value = getattr(configuration, name)
        if valid_types is None or isinstance(value, valid_types):
            log.debug(
                "Got '{name}': '{value}' from configuration".format(
                    name=name, value=value
                )
            )
            return value
        else:
            log.error(
                "Configuration value for '{name}' is type '{type}', must be one of {valid_types}".format(
                    name=name, type=type(value), valid_types=valid_types
                )
            )
            return default
    else:
        log.debug(
            "No value for '{name}' specified in configuration, using default '{value}'".format(
                name=name, value=default
            )
        )
        return default


def update_dict(d, u):
    """
    Recursively update dict ``d`` with dict ``u``
    """
    for k in u:
        dv = d.get(k, {})
        if not isinstance(dv, collections.Mapping):
            d[k] = u[k]
        elif isinstance(u[k], collections.Mapping):
            d[k] = update_dict(dv, u[k])
        else:
            d[k] = u[k]
    return d


def load():
    this = sys.modules[__name__]
    this.master_group_name = _get_conf_value(CONF_KEY_MASTER_GROUP, str, "")
    this.scene_item_prefix = _get_conf_value(CONF_KEY_SCENE_PREFIX, str, "")
    this.scene_item_suffix = _get_conf_value(CONF_KEY_SCENE_SUFFIX, str, "")
    this.reinit_item_name = _get_conf_value(CONF_KEY_REINIT_ITEM, str, "")
    this.log_trace = _get_conf_value(CONF_KEY_LOG_TRACE, None, False)
    this.global_settings = update_dict(
        copy.deepcopy(constants._global_settings),
        _get_conf_value(CONF_KEY_GLOBAL_SETTINGS, dict, {}),
    )
