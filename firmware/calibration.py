"""Endpoint storage, separate from private Wi-Fi configuration."""
import json
import os
from control import validate_channel

FIELDS = ("pin", "on_us", "off_us", "neutral_us", "enabled", "calibrated")


def save_calibration(channels, path="calibration.json"):
    # Rename on the same filesystem: a failed write leaves the last save intact.
    values = [{key: channel.get(key) for key in FIELDS} for channel in channels]
    with open(path + ".tmp", "w") as stream:
        json.dump({"version": 1, "channels": values}, stream)
    os.rename(path + ".tmp", path)


def load_calibration(config, path="calibration.json"):
    try:
        with open(path) as stream:
            saved = json.load(stream)
    except OSError as error:
        if error.args and error.args[0] == 2:
            return
        raise
    if (not isinstance(saved, dict) or saved.get("version") != 1
            or not isinstance(saved.get("channels"), list)
            or len(saved["channels"]) != len(config["channels"])):
        raise ValueError("invalid calibration file")
    replacements = []
    for channel, values in zip(config["channels"], saved["channels"]):
        if (not isinstance(values, dict) or set(values) != set(FIELDS)
                or values["pin"] != channel["pin"]
                or type(values["enabled"]) is not bool
                or type(values["calibrated"]) is not bool):
            raise ValueError("invalid saved endpoints")
        replacement = dict(channel)
        replacement.update(values)
        validate_channel(replacement)
        replacements.append(replacement)
    config["channels"] = replacements
