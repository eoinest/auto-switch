# Raspberry Pi Pico W source CAD

`PicoW-step.zip` is the unmodified official Raspberry Pi download obtained on 2026-09-05 from <https://pip.raspberrypi.com/documents/RP-008318-DS>. It contains `PicoW.stp`, whose internal file name is `PicoW-4.stp` and timestamp is 2023-08-11T10:10:01. The assembly root is `rpi-picow-r3-2.brd`.

`PicoW.obj`, `PicoW.mtl`, and `PicoW-mesh-metadata.json` are a tessellation of that source, produced by `../convert_step.py` using cadquery-ocp 8.0.1.0.0. Geometry is supplied by Raspberry Pi; the conversion does not make it original auto-switch geometry. Coordinates are millimetres and preserve the original origin. Label colors are retained where supplied; objects without a label color use gray. Face-level color variations are not retained. The original CAD itself simplifies or omits some physical components and does not include soldered headers.

These files retain their original permission terms, reproduced below. They are not relicensed under the repository's MIT license. Raspberry Pi's source documentation also distinguishes the licensed Abracon/Proant antenna technology; this enclosure reference does not grant a license to reproduce that RF design.

Source of permission: Raspberry Pi Pico W Datasheet, release 7, build 03 July 2026, section 1.1, and [Raspberry Pi's official hardware design-resource documentation](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#resources-for-wireless-raspberry-pi-pico-boards).

> Permission to use, copy, modify, and/or distribute this design for any purpose with or without fee is hereby granted.
>
> THE DESIGN IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS DESIGN INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS DESIGN.

Attribution: Raspberry Pi Ltd. Manufacturer references and SHA-256 checksums are recorded in `../board-servo.json`. Verify production fit against the actual board and its current datasheet. The Pico W geometry must not be labeled as an exact Pico 2 W assembly.
