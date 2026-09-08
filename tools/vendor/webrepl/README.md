# WebREPL protocol helper

Derived from MicroPython's `webrepl_cli.py`, commit
`1e09d9a1d90fe52aba11d1e659afbc95a50cf088`:
https://github.com/micropython/webrepl/blob/1e09d9a1d90fe52aba11d1e659afbc95a50cf088/webrepl_cli.py

MIT license included. Local changes: removed the upstream command-line entry
point (which prints passwords), use `sendall`, and raise on closed sockets rather
than looping. Our wrapper supplies the handshake, timeouts and deployment flow.
This minimal WebSocket implementation is specifically for MicroPython WebREPL.
