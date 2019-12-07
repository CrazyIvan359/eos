# Eos Change Log

## Development

* **Fixed**
  * Some log messages being sent to non-existant logger `critical`.

## 0.2.4

* **Fixed**
  * Motion source rule not being removed on reload.

## 0.2.3

* **Fixed**
  * Bug introduced in `0.2.2` where event scene would be used for all groups
    when doing recursive updates.
  * Scene changed rule would pass scene item to `update_group` but it expects
    a group.

## 0.2.2

* **Changed**
  * Clean up and reduce the amount of logging.

* **Fixed**
  * Use event command or state when applying scene changes or updates.

## 0.2.1

* **Changed**
  * Moved `290_eos.py` script to `eos` folder.

* **Fixed**
  * Editor crashing with `literal_eval` `SyntaxError`.
  * Editor crashing with `KeyError` when selecting `Configure Group`.

## 0.2.0

* **Added**
  * Scene alias setting that allows you to provide the name of a
    different scene to evaluate. Allows multiple scene names to reuse the same
    settings.

* **Changed**
  * Editor now prompts for `configuration.py` location.

## 0.1.1

* **Added**
  * Log Eos version on startup.
  * Scene item changed rule. Previously only *received command* events
    would trigger a scene update and propagate the scene to group children. Now
    you can change the a scene item's state and it will trigger a scene update,
    but will **not** propagate the scene change to group children.

* **Changed**
  * Group settings are now inheritted recursively from parent
    groups. Editor shows the source group name if it's not the current group.
  * Values from `configuration.py` are reloaded when Eos is
    reinitialized.

## 0.1.0

Initial Beta release
