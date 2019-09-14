# Eos Lighting System
eos_master_group = "eos_master_group"
eos_scene_item_prefix = "eos_"
eos_scene_item_suffix = "_scene"
eos_reload_item_name = "eos_reinit"
eos_global_settings = {
    "switch": {
        "soft": {
            "state": "OFF"
        },
        "bright": {
            "state": "ON"
        },
        "fader": {
            "state_above": "ON",
            "state_below": "OFF"
        }
    },
    "dimmer": {
        "state_low": 255,
        "on": {
            "state": 255
        },
        "soft": {
            "state_low": 64
        },
        "fader": {
            "state_high": 255,
            "state_low": 0
        }
    },
    "color": {
        "on": {
            "state": [20,65,100]
        },
        "soft": {
            "state_low": 25
        },
        "fader": {
            "state_high": 100,
            "state_low": 0
        }
    },
    "fader": {
        "level_threshold": 50,
        "level_high": 100,
        "level_low": 0,
    },
    "soft": {
        "level_high": 300,
        "level_low": 100
    },
    "bright": {
        "level_high": 500,
        "level_low": 300
    },
}
