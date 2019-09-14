"""
Eos Lighting

Contants used by all modules
"""

RULE_REINIT_NAME = "Eos Reload Rule"
RULE_REINIT_DESC = "This rule allows runtime reloading of the Eos System via a switch item"
RULE_SCENE_NAME = "Eos Scene Rule"
RULE_SCENE_DESC = "This rule is triggered when any Eos Scene item receives an update"
RULE_LIGHT_NAME = "Eos Light Rule"
RULE_LIGHT_DESC = "This rule is triggered when any Eos Light item receives an update"
RULE_LEVEL_SOURCE_NAME = "Eos Level Source Rule"
RULE_LEVEL_SOURCE_DESC = "This rule is triggered when any Level Source registered to an enabled Eos Light item receives an update"

CONF_KEY_MASTER_GROUP = "eos_master_group"
CONF_KEY_SCENE_PREFIX = "eos_scene_item_prefix"
CONF_KEY_SCENE_SUFFIX = "eos_scene_item_suffix"
CONF_KEY_SCENE_DEFAULTS = "eos_scene_defaults"
CONF_KEY_REINIT_ITEM = "eos_reload_item_name"

META_NAME_EOS = "eos"
META_KEY_LEVEL_SOURCE = "level_source"
META_KEY_LEVEL_THRESHOLD = "level_threshold"
META_KEY_LEVEL_HIGH = "level_high"
META_KEY_LEVEL_LOW = "level_low"
META_KEY_STATE = "state"
META_KEY_STATE_ABOVE = "state_above"
META_KEY_STATE_BELOW = "state_below"
META_KEY_STATE_HIGH = "state_high"
META_KEY_STATE_LOW = "state_low"
META_KEY_MOTION_SOURCE = "motion_source"
META_KEY_MOTION_ACTIVE = "motion_active"
META_KEY_MOTION_STATE = "motion_state"

LIGHT_TYPE_SWITCH = "switch"
LIGHT_TYPE_DIMMER = "dimmer"
LIGHT_TYPE_COLOR = "color"
LIGHT_TYPE_MAP = {"color": LIGHT_TYPE_COLOR, "dimmer": LIGHT_TYPE_DIMMER, "number": LIGHT_TYPE_DIMMER, "switch": LIGHT_TYPE_SWITCH}

SCENE_TYPE_FIXED = "fixed"
SCENE_TYPE_THRESHOLD = "threshold"
SCENE_TYPE_SCALED = "scaled"
SCENE_PARENT = "parent"
SCENE_MANUAL = "manual"
SCENE_ON = "on"
SCENE_OFF = "off"

try: from org.openhab.core.types import UnDefType as ohcUnDefType
except: ohcUnDefType = type(None)
try: from org.eclipse.smarthome.core.types import UnDefType as eshUnDefType
except: eshUnDefType = type(None)
try: from org.openhab.core.items import GroupItem as ohcGroupItem
except: ohcGroupItem = type(None)
try: from org.eclipse.smarthome.core.items import GroupItem as eshGroupItem
except: eshGroupItem = type(None)
try: from org.openhab.core.library.items import StringItem as ohcStringItem
except: ohcStringItem = type(None)
try: from org.eclipse.smarthome.core.library.items import StringItem as eshStringItem
except: eshStringItem = type(None)
try: from org.openhab.core.library.items import ColorItem as ohcColorItem
except: ohcColorItem = type(None)
try: from org.eclipse.smarthome.core.library.items import ColorItem as eshColorItem
except: eshColorItem = type(None)
try: from org.openhab.core.library.items import DimmerItem as ohcDimmerItem
except: ohcDimmerItem = type(None)
try: from org.eclipse.smarthome.core.library.items import DimmerItem as eshDimmerItem
except: eshDimmerItem = type(None)
try: from org.openhab.core.library.items import NumberItem as ohcNumberItem
except: ohcNumberItem = type(None)
try: from org.eclipse.smarthome.core.library.items import NumberItem as eshNumberItem
except: eshNumberItem = type(None)
try: from org.openhab.core.library.items import SwitchItem as ohcSwitchItem
except: ohcSwitchItem = type(None)
try: from org.eclipse.smarthome.core.library.items import SwitchItem as eshSwitchItem
except: eshSwitchItem = type(None)
typesUnDef = (ohcUnDefType, eshUnDefType)
itemtypesScene = (ohcStringItem, eshStringItem)
itemtypesLight = (ohcColorItem, eshColorItem, ohcDimmerItem, eshDimmerItem, ohcNumberItem, eshNumberItem, ohcSwitchItem, eshSwitchItem)
itemtypesSwitch = (ohcSwitchItem, eshSwitchItem)
itemtypesDimmer = (ohcColorItem, eshColorItem, ohcDimmerItem, eshDimmerItem, ohcNumberItem, eshNumberItem)
itemtypesColor = (ohcColorItem, eshColorItem)
itemtypesGroup = (ohcGroupItem, eshGroupItem)

__all__ = [
    "RULE_REINIT_NAME", "RULE_REINIT_DESC", "RULE_SCENE_NAME", "RULE_SCENE_DESC",
    "RULE_LIGHT_NAME", "RULE_LIGHT_DESC", "RULE_LEVEL_SOURCE_NAME", "RULE_LEVEL_SOURCE_DESC",

    "CONF_KEY_MASTER_GROUP", "CONF_KEY_SCENE_PREFIX", "CONF_KEY_SCENE_SUFFIX",
    "CONF_KEY_SCENE_DEFAULTS", "CONF_KEY_REINIT_ITEM",

    "META_NAME_EOS",
    "META_KEY_LEVEL_SOURCE", "META_KEY_LEVEL_THRESHOLD", "META_KEY_LEVEL_HIGH",
    "META_KEY_LEVEL_LOW", "META_KEY_STATE", "META_KEY_STATE_ABOVE", "META_KEY_STATE_BELOW",
    "META_KEY_STATE_HIGH", "META_KEY_STATE_LOW", "META_KEY_MOTION_SOURCE",
    "META_KEY_MOTION_ACTIVE", "META_KEY_MOTION_STATE",

    "LIGHT_TYPE_SWITCH", "LIGHT_TYPE_DIMMER", "LIGHT_TYPE_COLOR", "LIGHT_TYPE_MAP",

    "SCENE_TYPE_FIXED", "SCENE_TYPE_THRESHOLD", "SCENE_TYPE_SCALED", "SCENE_PARENT",
    "SCENE_MANUAL", "SCENE_ON", "SCENE_OFF",

    "typesUnDef",
    "itemtypesScene", "itemtypesLight", "itemtypesSwitch", "itemtypesDimmer",
    "itemtypesColor", "itemtypesGroup"
]