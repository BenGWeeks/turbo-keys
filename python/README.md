# Mini Keyboard Configurator (Python)

Cross-platform Python tool for configuring cheap programmable macro keyboards
(CH552/CH57x based) commonly sold on AliExpress, Amazon, Temu, etc.

## Supported Devices

- Vendor ID: 0x1189 (4489)
- Product ID: 0x8890 (34960)
- Keyboards with 3-16 keys and 1-3 rotary encoders

## Installation

### Windows

```bash
pip install hidapi
```

### Linux

```bash
# Install system dependencies
sudo apt install libhidapi-hidraw0 libhidapi-libusb0

# Install Python package
pip install hidapi

# Add udev rule for non-root access
sudo tee /etc/udev/rules.d/99-minikeyboard.rules << 'EOF'
SUBSYSTEM=="usb", ATTR{idVendor}=="1189", ATTR{idProduct}=="8890", MODE="0666"
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="1189", ATTRS{idProduct}=="8890", MODE="0666"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger
```

### macOS

```bash
pip install hidapi
```

## Usage

```bash
# List connected devices
python minikeyboard.py list

# Set key 1 to press 'A'
python minikeyboard.py set key1 a

# Set key 2 to Ctrl+C (copy)
python minikeyboard.py set key2 ctrl+c

# Set key 3 to Ctrl+Shift+Escape (task manager)
python minikeyboard.py set key3 ctrl+shift+escape

# Set knob clockwise rotation to volume up
python minikeyboard.py set knob1_cw volup

# Set knob counter-clockwise to volume down
python minikeyboard.py set knob1_ccw voldown

# Set knob press to mute
python minikeyboard.py set knob1_press mute

# Set a key on layer 2
python minikeyboard.py set key5 f5 --layer 2

# Set LED mode (0=off, 1=on, 2=breathing)
python minikeyboard.py led 1
```

## Physical Keys

| Name | Description |
|------|-------------|
| key1-key12 | Regular keys |
| knob1_left, k1_left | Knob 1 counter-clockwise |
| knob1_press, k1_press | Knob 1 click/press |
| knob1_right, k1_right | Knob 1 clockwise |
| knob2_left, k2_left | Knob 2 counter-clockwise |
| knob2_press, k2_press | Knob 2 click/press |
| knob2_right, k2_right | Knob 2 clockwise |

## Supported Keys

### Basic Keys
- Letters: a-z
- Numbers: 0-9
- Function keys: f1-f12
- Navigation: up, down, left, right, home, end, pageup, pagedown, insert, delete
- Special: enter, escape, backspace, tab, space, capslock
- Punctuation: comma, period, slash, backslash, semicolon, quote, etc.

### Modifiers
- ctrl, shift, alt, win

Combine with `+`: `ctrl+c`, `ctrl+shift+escape`, `alt+f4`

### Media Keys
- play, pause, playpause
- next, prev/previous
- volup/volumeup, voldown/volumedown
- mute

## Layers

The keyboard supports 3 layers. Use `--layer` to configure keys on different layers:

```bash
python minikeyboard.py set key1 a --layer 1
python minikeyboard.py set key1 b --layer 2
python minikeyboard.py set key1 c --layer 3
```

## Troubleshooting

### "Could not connect to keyboard"

1. Make sure the keyboard is plugged in
2. On Linux, add the udev rule (see Installation)
3. Try running as root/administrator to test permissions
4. Check `python minikeyboard.py list` to see if device is detected

### "Permission denied"

On Linux, either:
- Add the udev rule and replug the keyboard
- Run with `sudo`

## Protocol Documentation

The keyboard uses 8-byte HID reports:

**Basic key mapping:**
- Byte 0: Physical key number (1-18)
- Byte 1: (Layer << 4) | KeyType (1=basic, 2=media, 3=mouse, 8=LED)
- Byte 2: Number of keys in sequence
- Byte 3: Sequence index
- Byte 4: Modifiers (Ctrl=1, Shift=2, Alt=4, Win=8)
- Byte 5: USB HID keycode

**Flash command:** `[0xAA, 0xAA, 0, 0, 0, 0, 0, 0]`

**Layer switch:** `[0xA1, layer, 0, 0, 0, 0, 0, 0]`
