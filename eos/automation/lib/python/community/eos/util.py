"""
Eos Lighting

Utilities
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

from community.eos import log, config
from community.eos.constants import *

from core.utils import validate_item
from core.metadata import get_value, get_metadata as core_get_metadata

from ast import literal_eval
import copy, collections

__all__ = [
    "resolve_type",
    "validate_item_name",
    "get_scene_item",
    "get_light_items",
    "get_group_items",
    "get_item_eos_group",
    "get_scene_for_item",
    "get_metadata",
    "update_dict",
    "build_data",
    "get_scene_setting",
    "get_scene_type",
]


def resolve_type(value):
    """Attempts to resolve the type of ``value``.

    It will return ``value`` as the python type if possible, otherwise will
    return value as string.
    """
    value = str(value).strip()
    if str(value).lower() == "true":
        return True
    elif str(value).lower() == "false":
        return False
    elif str(value).lower() == "none":
        return None
    else:
        # attempt to parse
        try:
            return literal_eval(value)
        except ValueError:
            pass
        # unparseable, return as str
        return value


def validate_item_name(name, prefix, suffix):
    """Verifies that ``name`` starts with ``prefix`` and ends with ``suffix``.

    Returns ``True`` or ``False``"""
    return name[: len(prefix)] == prefix and name[-len(suffix) :] == suffix


def get_scene_item(group):
    """Finds the scene item in a group.

    Returns the scene item or ``None`` if it does not find exactly one match.
    """
    if not group:
        return None
    items = [
        item
        for item in group.members
        if validate_item_name(
            item.name, config.scene_item_prefix, config.scene_item_suffix
        )
    ]
    if not items:
        if config.log_trace:
            log.debug(
                "Group '{group}' does not contain a scene item".format(group=group.name)
            )
        return None
    elif len(items) > 1 and "restore" in group.name.lower():
        # probably a restore on startup group, skip
        return None
    elif len(items) > 1:
        itemList = ""
        for item in items:
            itemList = "{list}'{name}', ".format(list=itemList, name=item.name)
        log.debug(
            "Group '{group}' contains more than one scene item. Each group can only have one scene item, please correct. ({list})".format(
                group=group.name, list=itemList[:-2]
            )
        )
        return None
    elif not isinstance(items[0], itemtypesScene):
        log.error(
            "Group '{group}' scene item '{name}' is not a StringItem".format(
                group=group.name, name=items[0].name
            )
        )
        return None
    else:
        if config.log_trace:
            log.debug(
                "Got scene item '{name}' for group '{group}'".format(
                    name=items[0].name, group=group.name
                )
            )
        return items[0]


def get_light_items(group):
    """Finds all light items in a group.

    Returns a list of valid Eos lights.
    """
    return (
        [
            item
            for item in group.members
            if not isinstance(item, itemtypesGroup)
            and isinstance(item, itemtypesLight)
            and item != get_scene_item(group)
            and resolve_type(get_value(item.name, META_NAME_EOS)) is not None
        ]
        if hasattr(group, "members")
        else []
    )


def get_group_items(group):
    """Finds all group items in a group.

    Returns a list of valid Eos groups.
    """
    return (
        [
            item
            for item in group.members
            if isinstance(item, itemtypesGroup) and get_scene_item(group) is not None
        ]
        if hasattr(group, "members")
        else []
    )


def get_item_eos_group(item):
    """Gets the Eos group from the item's groups.

    Returns the group item or ``None`` if it does not find exactly one match.
    """
    groups = [
        group for group in item.groupNames if get_scene_item(validate_item(group))
    ]
    if not groups:
        if item.name != config.master_group_name:
            log.error("No Eos group found for item '{name}'".format(name=item.name))
        return None
    elif len(groups) > 1:
        groupList = ""
        for group in groups:
            groupList = "{list}'{group}', ".format(list=groupList, group=group)
        log.error(
            "Item '{name}' is a memeber of more than one Eos group: {list}".format(
                name=item.name, list=groupList[:-2]
            )
        )
        log.error("Each item can only be a member of one Eos group, please correct.")
        return None
    else:
        if config.log_trace:
            log.debug(
                "Got Eos group '{group}' for item '{name}'".format(
                    group=groups[0], name=item.name
                )
            )
        return validate_item(groups[0])


def get_scene_for_item(item):
    """Returns the scene string applicable for ``item``.
    """
    scene_item = get_scene_item(get_item_eos_group(item))
    if (
        scene_item.name == config.master_group_name
        and str(scene_item.state).lower() == SCENE_PARENT
    ):
        # master group cannot inherit scene from parent, no parent
        # this is caused by invalid site configuration allowing master group scene
        # to be set to parent
        log.error(
            "Master group '{group}' scene item '{name}' is set to 'parent', this is an impossible state. Using '{scene}' scene instead".format(
                group=config.master_group_name, name=scene_item.name, scene=SCENE_MANUAL
            )
        )
        return SCENE_MANUAL
    elif str(scene_item.state).lower() == SCENE_PARENT:
        # group is set to inherit scene from parent
        return get_scene_for_item(get_item_eos_group(scene_item))
    elif isinstance(scene_item.state, typesUnDef):
        log.warn(
            "Scene item '{name}' is not set, using '{scene}' scene instead.".format(
                name=scene_item.name, scene=SCENE_MANUAL
            )
        )
        return SCENE_MANUAL
    else:
        return str(scene_item.state).lower()


def get_metadata(item_name, namespace):
    """
    Wrapper for ``get_metadata`` to translate to Python ``dict``.
    """

    def parse_config(config):
        value = copy.deepcopy(config)
        result = {}
        try:
            value = literal_eval(value)
        except:
            pass
        try:
            for key in value:
                result[str(key)] = parse_config(value[str(key)])
        except:
            if isinstance(value, basestring):
                value = str(value)
        if not value:
            if (
                str(type(value)) == "<type 'java.util.Collections$UnmodifiableMap'>"
                or str(type(value)) == "<type 'java.util.LinkedHashMap'>"
            ):
                value = {}
        return result or value

    metadata = core_get_metadata(item_name, namespace)
    return (
        {"value": metadata.value, "configuration": parse_config(metadata.configuration)}
        if metadata
        else {}
    )


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


def build_data(item):
    """
    Builds a dict of all item, group, and global settings to use when
    evaluating a scene.
    """

    def _get_parent_group_data(group):
        """
        Get all group ancestor's data, top level group settings are lowest priority
        """
        group_data = {}
        if get_item_eos_group(group):
            group_data = _get_parent_group_data(get_item_eos_group(group))
        group_data = update_dict(
            group_data, get_metadata(group.name, META_NAME_EOS).get("configuration", {})
        )
        return group_data

    data = {}
    data["item"] = get_metadata(item.name, META_NAME_EOS).get("configuration", {})
    data["group"] = _get_parent_group_data(get_item_eos_group(item))
    data["global"] = config.global_settings
    return data


def get_scene_setting(item, scene, key, data=None, max_depth=10):
    """
    Gets a setting value by searching:
    Scene in Item > Scene in Light Type in Group > Scene in Group >
    Scene in Light Type in Global > Scene in Global > Item >
    Light Type in Group > Group > Light Type in Global > Global
    """
    light_type = LIGHT_TYPE_MAP.get(item.type.lower(), None)
    item_data = data["item"]
    # if config.log_trace: log.debug("Got Item data for '{name}': {data}".format(name=item.name, data=item_data))
    group_data = data["group"]
    # if config.log_trace: log.debug("Got Group data for '{name}': {data}".format(name=get_item_eos_group(item).name, data=group_data))
    global_data = data["global"]
    # if config.log_trace: log.debug("Got Global data: {data}".format(name=light_type, data=global_data))
    value = None
    if (
        max_depth >= 1
        and 1 in META_KEY_DEPTH_MAP[key]
        and item_data.get(scene, {}).get(key, None) is not None
    ):
        source = "Scene in Item"
        value = item_data.get(scene, {}).get(key, None)
    elif (
        max_depth >= 2
        and 2 in META_KEY_DEPTH_MAP[key]
        and group_data.get(light_type, {}).get(scene, {}).get(key, None) is not None
    ):
        source = "Scene in Light Type in Group"
        value = group_data.get(light_type, {}).get(scene, {}).get(key, None)
    elif (
        max_depth >= 3
        and 3 in META_KEY_DEPTH_MAP[key]
        and group_data.get(scene, {}).get(key, None) is not None
    ):
        source = "Scene in Group"
        value = group_data.get(scene, {}).get(key, None)
    elif (
        max_depth >= 4
        and 4 in META_KEY_DEPTH_MAP[key]
        and global_data.get(light_type, {}).get(scene, {}).get(key, None) is not None
    ):
        source = "Scene in Light Type in Global"
        value = global_data.get(light_type, {}).get(scene, {}).get(key, None)
    elif (
        max_depth >= 5
        and 5 in META_KEY_DEPTH_MAP[key]
        and global_data.get(scene, {}).get(key, None) is not None
    ):
        source = "Scene in Global"
        value = global_data.get(scene, {}).get(key, None)
    elif (
        max_depth >= 6
        and 6 in META_KEY_DEPTH_MAP[key]
        and item_data.get(key, None) is not None
    ):
        source = "Item"
        value = item_data.get(key, None)
    elif (
        max_depth >= 7
        and 7 in META_KEY_DEPTH_MAP[key]
        and group_data.get(light_type, {}).get(key, None) is not None
    ):
        source = "Light Type in Group"
        value = group_data.get(light_type, {}).get(key, None)
    elif (
        max_depth >= 8
        and 8 in META_KEY_DEPTH_MAP[key]
        and group_data.get(key, None) is not None
    ):
        source = "Group"
        value = group_data.get(key, None)
    elif (
        max_depth >= 9
        and 9 in META_KEY_DEPTH_MAP[key]
        and global_data.get(light_type, {}).get(key, None) is not None
    ):
        source = "Light Type in Global"
        value = global_data.get(light_type, {}).get(key, None)
    elif (
        max_depth >= 10
        and 10 in META_KEY_DEPTH_MAP[key]
        and global_data.get(key, None) is not None
    ):
        source = "Global"
        value = global_data.get(key, None)
    else:
        if config.log_trace:
            log.debug(
                "No value found for key '{key}' for scene '{scene}' for item '{name}' at depth {depth}".format(
                    key=key, scene=scene, name=item.name, depth=depth
                )
            )
        return None
    if config.log_trace:
        log.debug(
            "Got setting '{key}' for scene '{scene}' for item '{name}' from {source}: {value}".format(
                key=key, scene=scene, name=item.name, source=source, value=value
            )
        )
    return resolve_type(value)


def get_scene_type(item, scene, light_type, data=None):
    """
    Returns the scene type or ``None``.

    Scans depths 1-5 (scene settings) attempting to infer the scene type, if
    unable it then scans depths 6-10 (non scene specific settings) to infer
    scene type.
    """

    def _scan_settings(min_depth, max_depth):
        for depth in range(min_depth, max_depth + 1):
            if (
                get_scene_setting(
                    item, scene, META_KEY_STATE, data=data, max_depth=depth
                )
                is not None
            ):
                return SCENE_TYPE_FIXED
            elif light_type == LIGHT_TYPE_SWITCH:
                if (
                    get_scene_setting(
                        item,
                        scene,
                        META_KEY_LEVEL_THRESHOLD,
                        data=data,
                        max_depth=depth,
                    )
                    is not None
                ):
                    return SCENE_TYPE_THRESHOLD
            elif light_type in [LIGHT_TYPE_DIMMER, LIGHT_TYPE_COLOR]:
                if (
                    get_scene_setting(
                        item, scene, META_KEY_LEVEL_HIGH, data=data, max_depth=depth
                    )
                    is not None
                    or get_scene_setting(
                        item, scene, META_KEY_LEVEL_LOW, data=data, max_depth=depth
                    )
                    is not None
                ):
                    return SCENE_TYPE_SCALED
                elif max_depth < 5 and (
                    get_scene_setting(
                        item, scene, META_KEY_STATE_HIGH, data=data, max_depth=depth
                    )
                    is not None
                    or get_scene_setting(
                        item, scene, META_KEY_STATE_LOW, data=data, max_depth=depth
                    )
                    is not None
                ):
                    return SCENE_TYPE_SCALED
                elif (
                    get_scene_setting(
                        item,
                        scene,
                        META_KEY_LEVEL_THRESHOLD,
                        data=data,
                        max_depth=depth,
                    )
                    is not None
                ):
                    return SCENE_TYPE_THRESHOLD
        return None

    return _scan_settings(1, 5) or _scan_settings(6, 10)
