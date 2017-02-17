# :tokyo_tower: tokyo :tokyo_tower:

The [godzillops](https://github.com/statmuse/godzillops) chat bot runtime (assorted chat platform).

## Working Platforms

* Text interface

## Planned Platforms

* Slack
  * [python-slackclient](https://github.com/slackhq/python-slackclient) is required for this platform.

## Configure Platform Settings

Configure tokyo by editing the `config.py` file accordingly (set the appropriate values for your chat platform, etc.)
  * You can also edit a file `config_private.py` which is a gitignore'd file but, if it exists, is used in place of config.py.

## Running

```
$> virtualenv --python /usr/local/bin/python3 .venv
$> .venv/bin/python main.py
```
