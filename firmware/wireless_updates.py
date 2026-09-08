"""Opt-in WebREPL for application updates on the always-online S2 demo."""


def start(config):
    if config.get("hardware_profile") != "s2-demo" or config.get("transport", "direct") != "direct":
        return False
    try:
        import webrepl_cfg
    except ImportError:
        return False
    except Exception:
        print("Wireless updates disabled: unreadable private WebREPL configuration")
        return False
    password = getattr(webrepl_cfg, "PASS", None)
    if (not isinstance(password, str) or not 4 <= len(password) <= 9
            or any(ord(c) < 33 or ord(c) > 126 for c in password)):
        print("Wireless updates disabled: invalid private WebREPL configuration")
        return False
    try:
        import webrepl
        webrepl.start(password=password)
    except Exception:
        # Do not expose configuration values in exception output.
        print("Wireless updates unavailable; check WebREPL support over USB")
        return False
    print("Wireless application updates enabled on port 8266")
    return True
