# Eos Change Log

## 0.2.0

* __Changed__: Editor now prompts for `configuration.py` location.
* __Added__: Scene alias setting that allows you to provide the name of a
  different scene to evaluate. Allows multiple scene names to reuse the same
  settings.

## 0.1.1

* __Added__: Log Eos version on startup.
* __Added__: Scene item changed rule. Previously only *received command* events
  would trigger a scene update and propagate the scene to group children. Now
  you can change the a scene item's state and it will trigger a scene update,
  but will **not** propagate the scene change to group children.
* __Changed__: Group settings are now inheritted recursively from parent
  groups. Editor shows the source group name if it's not the current group.
* __Changed__: Values from `configuration.py` are reloaded when Eos is
  reinitialized.

## 0.1.0

* Initial Beta release
