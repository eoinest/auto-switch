"""Frozen app entry point; the same bundled runtime handles USB child commands."""
import os
import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--device-command':
        # Windowed builds may replace sys.std* with None. USB child invocations
        # get explicit subprocess pipes; restore those streams without logging.
        if sys.stdout is None:
            sys.stdout = os.fdopen(os.dup(1), 'w', buffering=1)
        if sys.stderr is None:
            sys.stderr = os.fdopen(os.dup(2), 'w', buffering=1)
        if sys.stdin is None:
            sys.stdin = open(os.devnull)
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        from mpremote.main import main as device_main
        return device_main()
    # Finder launch has no terminal. Suppress diagnostic stdout rather than
    # letting a print fail; never log credentials or device command output.
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')
    from server import main as serve
    # An ephemeral loopback port permits multiple installs without collisions.
    return serve(['--port', '0', '--open-browser'] + sys.argv[1:])


if __name__ == '__main__':
    raise SystemExit(main())
