<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/logo.svg">
    <img alt="Turbo Keys" src="assets/logo.svg" width="100%">
  </picture>
</p>

Turbo Keys is a **free, open source** configuration tool for cheap programmable macro keyboards (CH552/CH57x based) sold on Amazon, AliExpress, Wish, Temu, etc. A safe alternative to the dodgy vendor software with a beautiful GUI.

**Macro keyboard** | **Programmable keys** | **Cross-platform** | **Open source** | **No bloatware**

![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)

## Features

- **Visual key mapper** - click keys to configure them with an intuitive GUI
- **Modifier combos** - easily set Ctrl+C, Alt+Tab, Win+L, etc.
- **Media keys** - volume, play/pause, next/prev track
- **Multi-layer** - up to 3 layers per key
- **LED control** - configure backlight modes
- **Cross-platform** - Linux, macOS, and Windows support
- **No installer** - portable, no admin rights needed

## Supported Devices

| Vendor ID | Product ID | Status |
|-----------|------------|--------|
| 0x1189 | 0x8890 | Supported |
| 0x1189 | 0x8840 | In Progress |

Sold as:
- One Handed Mechanical Gaming Keyboard
- One Handed Programmable Mechanical Keyboard
- Mini Keypad Programmable Macro Keyboard with Knob
- Mini 3 Key Keypad with Knob
- Bewinner Mini 12 Key Keypad

## Installation

### Python CLI (All Platforms)

```bash
pip install hidapi
cd python
python turbokeys.py list                    # List devices
python turbokeys.py set key1 ctrl+c         # Set key 1 to Ctrl+C
python turbokeys.py set knob1_cw volup      # Knob clockwise = volume up
python turbokeys.py led 1                   # Set LED mode
```

### Python GUI (Coming Soon)

```bash
pip install hidapi PyQt6
python turbokeys-gui.py
```

## Documentation

- [Python CLI Documentation](python/README.md)
- [Protocol Documentation](docs/PROTOCOL.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.adoc)
- [Solution Design](docs/SOLUTION_DESIGN.adoc)
- [Security Analysis of Vendor Software](docs/SECURITY_ANALYSIS.md)

## Credits

- [HidLibrary](https://github.com/mikeobrien/HidLibrary) - .NET HID communication
- [emonkey/MiniKeyboard](https://github.com/emonkey/MiniKeyboard) - Original decompiled C# version

## Reviews

|||
|---|---|
| [![Aliexpress Programmable Macro Keypads / Keyboards](https://i.ytimg.com/vi/Kl6IwDdUPi4/hqdefault.jpg?sqp=-oaymwEbCKgBEF5IVfKriqkDDggBFQAAiEIYAXABwAEG&rs=AOn4CLCNIeZ7GHtl0m3HscGXdy9QowyYVA)](https://www.youtube.com/watch?v=Kl6IwDdUPi4) | Aliexpress Programmable Macro Keypads / Keyboards - Five Things You Should Know! |
| [![Macro Keyboard Tutorial](https://i.ytimg.com/vi/HIMiSwXkSXI/hqdefault.jpg?sqp=-oaymwE1CKgBEF5IVfKriqkDKAgBFQAAiEIYAXABwAEG8AEB-AH-CYAC0AWKAgwIABABGGEgYShhMA8=&rs=AOn4CLDz0rpaRjqgN1MbLyCxOqFPZlPolg)](https://www.youtube.com/watch?v=HIMiSwXkSXI) | Macro Keyboard Tutorial - Download software and program tutorial |
| [![Finding "GOOD" Tech on Temu](https://i.ytimg.com/vi/OOCxMQCDTQI/hqdefault.jpg?sqp=-oaymwEbCKgBEF5IVfKriqkDDggBFQAAiEIYAXABwAEG&rs=AOn4CLDdvwjPkQAfRNw0DkR7PmeFR0DKfQ)](https://youtu.be/OOCxMQCDTQI?si=O8_OHDWQIJwR3OG5&t=578) | Finding "GOOD" Tech on Temu |
| [![I Bought 10 Weird Keyboards from AliExpress](https://i.ytimg.com/vi/YBTARvcFZ1A/hqdefault.jpg?sqp=-oaymwEbCKgBEF5IVfKriqkDDggBFQAAiEIYAXABwAEG&rs=AOn4CLCFMdvQP48ye28heNjBfT32wG0bTA)](https://www.youtube.com/watch?v=YBTARvcFZ1A&t=787s) | I Bought 10 Weird Keyboards from AliExpress |

## Changelog

- JAN 26: Rebranded to Turbo Keys, added ASCII logo
- JAN 26: Added security analysis of vendor software, debug commands for PID 0x8840 investigation
- JAN 25: Added Python CLI tool with cross-platform support
- DEC 23: Updated and tested using VS 2019, VS 2022
