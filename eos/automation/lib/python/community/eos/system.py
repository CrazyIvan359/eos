"""
Eos Lighting

System init and uninit
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

from community import eos
from community.eos import log, config
from community.eos.update import update_eos
from community.eos.util import *
from community.eos.constants import *

from core.jsr223.scope import scriptExtension

ruleRegistry = scriptExtension.get("ruleRegistry")
# from core import osgi
# ruleEngine = osgi.get_service("org.openhab.core.automation.RuleManager") or osgi.get_service("org.eclipse.smarthome.automation.RuleManager")
from core.rules import rule
from core.triggers import when
from core.utils import validate_item
from core.metadata import get_value
from core.log import log_traceback

__all__ = ["init", "uninit"]


@log_traceback
def init(
    rule_reinit,
    rule_scene_command,
    rule_scene_changed,
    rule_light_update,
    rule_level_source_update,
    rule_motion_source_changed,
):
    """Initialize Eos.

    This creates a rule with triggers for the scene item in
    ``configuration.eos_master_group`` and any descendants that are a
    ``GroupItem`` and contain a scene item to update members when they receive
    an update.
    """

    def _gen_triggers_for_sources(config):
        all_items_valid = True
        for key in config:
            if isinstance(config[key], dict):
                all_items_valid = all_items_valid and _gen_triggers_for_sources(
                    config[key]
                )
            elif key == META_KEY_LEVEL_SOURCE:
                item = validate_item(config[key])
                if item is not None:
                    if item.name not in levelTriggers:
                        levelTriggers[item.name] = when(
                            "Item {name} received update".format(name=item.name)
                        )
                        log.debug(
                            "Added '{key}' received update trigger for '{level}'".format(
                                level=item.name, key=key
                            )
                        )
                else:
                    log.error(
                        "Failed to add '{key}' trigger for '{level}', item does not exist".format(
                            level=config[key], key=key
                        )
                    )
                    all_items_valid = False
            elif key == META_KEY_MOTION_SOURCE:
                item = validate_item(config[key])
                if item is not None:
                    if item.name not in motionTriggers:
                        motionTriggers[item.name] = when(
                            "Item {name} changed".format(name=item.name)
                        )
                        log.debug(
                            "Added '{key}' changed trigger for '{level}'".format(
                                level=item.name, key=key
                            )
                        )
                else:
                    log.error(
                        "Failed to add '{key}' trigger for '{level}', item does not exist".format(
                            level=config[key], key=key
                        )
                    )
                    all_items_valid = False
        return all_items_valid

    def _gen_triggers_for_group(group):
        if str(get_value(group.name, META_NAME_EOS)).lower() in META_STRING_FALSE:
            log.info("Found group '{group}' but it is disabled".format(name=group.name))
        else:
            log.debug("Scanning group '{group}'".format(group=group.name))
            itemScene = get_scene_item(group)
            if itemScene:
                # add scene triggers
                when("Item {name} received command".format(name=itemScene.name))(
                    rule_scene_command
                )
                when("Item {name} changed".format(name=itemScene.name))(
                    rule_scene_changed
                )
                log.debug(
                    "Added triggers for scene item '{name}' in '{group}'".format(
                        name=itemScene.name, group=group.name
                    )
                )
                # gen triggers for Level and Motion sources in metadata
                _gen_triggers_for_sources(
                    get_metadata(group.name, META_NAME_EOS).get("configuration", {})
                )
                # add lights triggers
                for light in get_light_items(group):
                    if (
                        str(get_value(light.name, META_NAME_EOS)).lower()
                        in META_STRING_FALSE
                    ):
                        log.info(
                            "Found light '{name}' in '{group}' but it is disabled".format(
                                name=light.name, group=group.name
                            )
                        )
                    else:
                        _gen_triggers_for_sources(
                            get_metadata(light.name, META_NAME_EOS).get(
                                "configuration", {}
                            )
                        )
                        when("Item {name} received update".format(name=light.name))(
                            rule_light_update
                        )
                        log.debug(
                            "Added light received update trigger for '{name}' in '{group}'".format(
                                name=light.name, group=group.name
                            )
                        )
                # recurse into groups
                for group in get_group_items(group):
                    _gen_triggers_for_group(group)
            else:
                log.warn(
                    "Group '{group}' will be ignored because it has no scene item".format(
                        group=group.name
                    )
                )

    log.info("Eos Version {} initializing...".format(eos.__version__))

    config.load()

    if not config.master_group_name:
        log.error(
            "No '{name}' specified in configuration".format(name=CONF_KEY_MASTER_GROUP)
        )
        log.error("Eos failed to initialize")
        return

    if not config.scene_item_prefix and not config.scene_item_suffix:
        log.error(
            "Must specify at least one of '{prefix}' or '{suffix}' in configuration".format(
                prefix=CONF_KEY_SCENE_PREFIX, suffix=CONF_KEY_SCENE_SUFFIX
            )
        )
        log.error("Eos failed to initialize")
        return

    master_group_item = validate_item(config.master_group_name)
    if not master_group_item:
        log.error(
            "Master group item '{group}' does not exist".format(
                group=config.master_group_name
            )
        )
        log.error("Eos failed to initialize")
        return
    elif not isinstance(master_group_item, itemtypesGroup):
        log.error(
            "Master group item '{group}' is not a GroupItem".format(
                group=config.master_group_name
            )
        )
        log.error("Eos failed to initialize")
        return
    if not get_scene_item(master_group_item):
        log.error(
            "Could not validate master scene item in '{group}'".format(
                group=config.master_group_name
            )
        )
        log.error("Eos failed to initialize")
        return

    for objRule in [
        objRule
        for objRule in ruleRegistry.getAll()
        if objRule.name
        in [
            RULE_REINIT_NAME,
            RULE_SCENE_COMMAND_NAME,
            RULE_SCENE_CHANGED_NAME,
            RULE_LIGHT_NAME,
            RULE_LEVEL_SOURCE_NAME,
            RULE_MOTION_SOURCE_NAME,
        ]
    ]:
        log.debug(
            "Removing existing {rule} with UID '{uid}'".format(
                rule=objRule.name, uid=objRule.UID
            )
        )
        ruleRegistry.remove(objRule.UID)
        # try: ruleRegistry.remove(objRule.UID)
        # except:
        #    log.error("Failed to delete {rule} with UID '{uid}', attempting to disable".format(rule=objRule.name, uid=objRule.UID))
        #    ruleEngine.setEnabled(objRule.UID, False)

    # if we are reinit-ing {rule}.triggers will be 'None' and cause errors
    if hasattr(rule_reinit, "triggers"):
        delattr(rule_reinit, "triggers")
    if hasattr(rule_scene_command, "triggers"):
        delattr(rule_scene_command, "triggers")
    if hasattr(rule_scene_changed, "triggers"):
        delattr(rule_scene_changed, "triggers")
    if hasattr(rule_light_update, "triggers"):
        delattr(rule_light_update, "triggers")
    if hasattr(rule_level_source_update, "triggers"):
        delattr(rule_level_source_update, "triggers")
    if hasattr(rule_motion_source_changed, "triggers"):
        delattr(rule_motion_source_changed, "triggers")

    # add rule to reload Eos if item exists
    if config.reinit_item_name:
        when("Item {name} received command ON".format(name=config.reinit_item_name))(
            rule_reinit
        )
        rule(RULE_REINIT_NAME, RULE_REINIT_DESC)(rule_reinit)
        if hasattr(rule_reinit, "UID"):
            log.debug(
                "Created {rule} with UID '{uid}'".format(
                    rule=RULE_REINIT_NAME, uid=rule_reinit.UID
                )
            )
        else:
            log.error("Failed to create {rule}".format(rule=RULE_REINIT_NAME))

    # generate triggers for all scene, light, level source, and motion source items
    levelTriggers = {}
    motionTriggers = {}
    _gen_triggers_for_sources(config.global_settings)
    _gen_triggers_for_group(master_group_item)

    if hasattr(rule_light_update, "triggers"):  # do not proceed if there are no lights
        # create scene command rule
        rule(RULE_SCENE_COMMAND_NAME, RULE_SCENE_COMMAND_DESC)(rule_scene_command)
        if hasattr(rule_scene_command, "UID"):
            log.debug(
                "Created {rule} with UID '{uid}'".format(
                    rule=RULE_SCENE_COMMAND_NAME, uid=rule_scene_command.UID
                )
            )
        else:
            log.error("Failed to create {rule}".format(rule=RULE_SCENE_COMMAND_NAME))
            log.error("Eos failed to initialize")
            return

        # create scene changed rule
        rule(RULE_SCENE_CHANGED_NAME, RULE_SCENE_CHANGED_DESC)(rule_scene_changed)
        if hasattr(rule_scene_changed, "UID"):
            log.debug(
                "Created {rule} with UID '{uid}'".format(
                    rule=RULE_SCENE_CHANGED_NAME, uid=rule_scene_changed.UID
                )
            )
        else:
            log.error("Failed to create {rule}".format(rule=RULE_SCENE_CHANGED_NAME))
            log.error("Eos failed to initialize")
            return

        # create light received update rule
        rule(RULE_LIGHT_NAME, RULE_LIGHT_DESC)(rule_light_update)
        if hasattr(rule_light_update, "UID"):
            log.debug(
                "Created {rule} with UID '{uid}'".format(
                    rule=RULE_LIGHT_NAME, uid=rule_light_update.UID
                )
            )
        else:
            log.error("Failed to create {rule}".format(rule=RULE_LIGHT_NAME))
            log.error("Eos failed to initialize")
            return

        # add triggers for each Level Source item and create rule if any exist
        for key in levelTriggers:
            levelTriggers[key](rule_level_source_update)
        if hasattr(rule_level_source_update, "triggers"):
            rule(RULE_LEVEL_SOURCE_NAME, RULE_LEVEL_SOURCE_DESC)(
                rule_level_source_update
            )
            if hasattr(rule_level_source_update, "UID"):
                log.debug(
                    "Created {rule} with UID '{uid}'".format(
                        rule=RULE_LEVEL_SOURCE_NAME, uid=rule_level_source_update.UID
                    )
                )
            else:
                log.error("Failed to create {rule}".format(rule=RULE_LEVEL_SOURCE_NAME))
                log.error("Eos failed to initialize")
                return

        # add triggers for each Motion Source item and create rule if any exist
        for key in motionTriggers:
            motionTriggers[key](rule_motion_source_changed)
        if hasattr(rule_motion_source_changed, "triggers"):
            rule(RULE_MOTION_SOURCE_NAME, RULE_MOTION_SOURCE_DESC)(
                rule_motion_source_changed
            )
            if hasattr(rule_motion_source_changed, "UID"):
                log.debug(
                    "Created {rule} with UID '{uid}'".format(
                        rule=RULE_MOTION_SOURCE_NAME, uid=rule_motion_source_changed.UID
                    )
                )
            else:
                log.error(
                    "Failed to create {rule}".format(rule=RULE_MOTION_SOURCE_NAME)
                )
                log.error("Eos failed to initialize")
                return

    else:
        log.warn("No lights found")

    log.info("Eos initialized")
    update_eos()


@log_traceback
def uninit():
    """Uninitialize Eos.

    This will remove the rules created by Eos when it is unloaded.
    """
    log.info("Eos uninitializing...")

    for objRule in [
        objRule
        for objRule in ruleRegistry.getAll()
        if objRule.name
        in [
            RULE_REINIT_NAME,
            RULE_SCENE_COMMAND_NAME,
            RULE_SCENE_CHANGED_NAME,
            RULE_LIGHT_NAME,
            RULE_LEVEL_SOURCE_NAME,
            RULE_MOTION_SOURCE_NAME,
        ]
    ]:
        log.info(
            "Removing {rule} with UID '{uid}'".format(
                rule=objRule.name, uid=objRule.UID
            )
        )
        ruleRegistry.remove(objRule.UID)
        # try: ruleRegistry.remove(objRule.UID)
        # except:
        #    log.error("Failed to delete {rule} with UID '{uid}', attempting to disable".format(rule=objRule.name, uid=objRule.UID))
        #    ruleEngine.setEnabled(objRule.UID, False)

    log.info("Eos uninitialized")
