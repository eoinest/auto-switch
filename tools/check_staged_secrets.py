"""Reject forced-added private files and known local credentials, without printing values."""
import base64
import json
from pathlib import Path
import subprocess
import sys


def git(*args, **kwargs):
    return subprocess.check_output(["git", *args], **kwargs)


def known_secrets(root):
    values = set()
    private = root / ".local" / "s2"
    password = private / "wifi-password.txt"
    if password.exists():
        value = password.read_text().rstrip("\r\n")
        if value and not value.startswith("REPLACE"):
            values.add(value)
    keys = private / "gateway-keys.json"
    if keys.exists():
        values.update(json.loads(keys.read_text()).values())
    for config in (root / "firmware/config.json", private / "config.json"):
        if config.exists():
            data = json.loads(config.read_text())
            values.update([data.get("wifi", {}).get("password"),
                           data.get("gateway", {}).get("token"), data.get("api_token")])
    needles = set()
    for value in values:
        if isinstance(value, str) and value and not value.startswith("REPLACE"):
            raw = value.encode()
            needles.update((raw, json.dumps(value)[1:-1].encode(), base64.b64encode(raw)))
    return needles


def check():
    root = Path(git("rev-parse", "--show-toplevel").decode().strip())
    staged = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
    paths = [p for p in staged.split(b"\0") if p]
    ignored = subprocess.run(["git", "check-ignore", "--no-index", "--stdin", "-z"],
                             input=staged, stdout=subprocess.PIPE, check=False)
    if ignored.returncode not in (0, 1):
        raise RuntimeError("Could not check ignore rules")
    blocked = {p for p in ignored.stdout.split(b"\0") if p}
    needles = known_secrets(root)
    for path in paths:
        # Read staged bytes, not the possibly different working copy.
        content = git("show", ":" + path.decode())
        if any(secret in content for secret in needles):
            blocked.add(path)
    if blocked:
        print("Commit blocked: ignored private file or known credential found in staged files:", file=sys.stderr)
        for path in sorted(blocked):
            print("  " + path.decode(errors="replace"), file=sys.stderr)
        return 1
    print("Staged private-file and known-credential check passed.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(check())
    except Exception:
        # Do not print exceptions that might include malformed credential values.
        print("Commit blocked: credential check failed; inspect private config locally.", file=sys.stderr)
        sys.exit(1)
