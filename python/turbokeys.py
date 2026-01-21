#!/usr/bin/env python3
"""
Mini Keyboard Configurator - Cross-platform Python implementation

Configures cheap programmable macro keyboards (CH552/CH57x based) sold on
AliExpress, Amazon, Temu etc.

Vendor ID: 0x1189 (4489)
Product ID: 0x8890 (34960)
"""

import hid
from enum import IntEnum
from typing import Optional, List, Tuple
from dataclasses import dataclass


# Device identifiers
VENDOR_ID = 0x1189   # 4489
PRODUCT_IDS = [0x8890, 0x8840]  # Different firmware versions use different PIDs


class KeyType(IntEnum):
    """Type of key mapping"""
    BASIC = 1
    MEDIA = 2
    MOUSE = 3
    LED = 8


class Modifier(IntEnum):
    """Keyboard modifier flags"""
    NONE = 0
    CTRL = 1
    SHIFT = 2
    ALT = 4
    WIN = 8
    # Right-side modifiers
    RCTRL = 16
    RSHIFT = 32
    RALT = 64
    RWIN = 128


# USB HID keyboard scan codes
KEYCODES = {
    # Letters
    'a': 4, 'b': 5, 'c': 6, 'd': 7, 'e': 8, 'f': 9, 'g': 10, 'h': 11,
    'i': 12, 'j': 13, 'k': 14, 'l': 15, 'm': 16, 'n': 17, 'o': 18, 'p': 19,
    'q': 20, 'r': 21, 's': 22, 't': 23, 'u': 24, 'v': 25, 'w': 26, 'x': 27,
    'y': 28, 'z': 29,

    # Numbers
    '1': 30, '2': 31, '3': 32, '4': 33, '5': 34,
    '6': 35, '7': 36, '8': 37, '9': 38, '0': 39,

    # Special keys
    'enter': 40, 'return': 40,
    'escape': 41, 'esc': 41,
    'backspace': 42,
    'tab': 43,
    'space': 44,
    'minus': 45, '-': 45,
    'equal': 46, '=': 46,
    'leftbracket': 47, '[': 47,
    'rightbracket': 48, ']': 48,
    'backslash': 49, '\\': 49,
    'semicolon': 51, ';': 51,
    'quote': 52, "'": 52,
    'grave': 53, '`': 53,
    'comma': 54, ',': 54,
    'period': 55, '.': 55,
    'slash': 56, '/': 56,
    'capslock': 57,

    # Function keys
    'f1': 58, 'f2': 59, 'f3': 60, 'f4': 61, 'f5': 62, 'f6': 63,
    'f7': 64, 'f8': 65, 'f9': 66, 'f10': 67, 'f11': 68, 'f12': 69,

    # Navigation
    'printscreen': 70, 'prtsc': 70,
    'scrolllock': 71,
    'pause': 72, 'break': 72,
    'insert': 73,
    'home': 74,
    'pageup': 75, 'pgup': 75,
    'delete': 76, 'del': 76,
    'end': 77,
    'pagedown': 78, 'pgdn': 78,
    'right': 79, 'left': 80, 'down': 81, 'up': 82,

    # Numpad
    'numlock': 83,
    'kp_divide': 84, 'kp_multiply': 85, 'kp_minus': 86, 'kp_plus': 87,
    'kp_enter': 88,
    'kp_1': 89, 'kp_2': 90, 'kp_3': 91, 'kp_4': 92, 'kp_5': 93,
    'kp_6': 94, 'kp_7': 95, 'kp_8': 96, 'kp_9': 97, 'kp_0': 98,
    'kp_period': 99, 'kp_dot': 99,

    # Menu
    'menu': 101, 'app': 101,
}


# Media key codes (for report_id=3, which is most common)
MEDIA_KEYCODES = {
    'play': 205, 'pause': 205, 'playpause': 205,
    'stop': 183,
    'prev': 182, 'previous': 182,
    'next': 181,
    'mute': 226,
    'volup': 233, 'volumeup': 233,
    'voldown': 234, 'volumedown': 234,
}


# Physical key names for the 12-key + 1-knob layout
PHYSICAL_KEYS = {
    'key1': 1, 'key2': 2, 'key3': 3, 'key4': 4,
    'key5': 5, 'key6': 6, 'key7': 7, 'key8': 8,
    'key9': 9, 'key10': 10, 'key11': 11, 'key12': 12,
    # Knob 1
    'k1_left': 13, 'knob1_left': 13, 'knob1_ccw': 13,
    'k1_press': 14, 'knob1_press': 14, 'knob1_click': 14,
    'k1_right': 15, 'knob1_right': 15, 'knob1_cw': 15,
    # Knob 2 (if present)
    'k2_left': 16, 'knob2_left': 16, 'knob2_ccw': 16,
    'k2_press': 17, 'knob2_press': 17, 'knob2_click': 17,
    'k2_right': 18, 'knob2_right': 18, 'knob2_cw': 18,
}


@dataclass
class KeyMapping:
    """Represents a key mapping configuration"""
    physical_key: int
    key_type: KeyType
    modifiers: int = 0
    keycode: int = 0
    layer: int = 1


class MiniKeyboard:
    """Interface to the mini keyboard device"""

    def __init__(self):
        self.device: Optional[hid.device] = None
        self.report_id: int = 3  # Default, will be detected

    def find_device(self) -> Optional[dict]:
        """Find the mini keyboard device - uses MI_01 like vendor software"""
        for pid in PRODUCT_IDS:
            devices = list(hid.enumerate(VENDOR_ID, pid))

            # Vendor software uses MI_01 (interface 1), not MI_00!
            # See HidOperations.cs line 60: hidDevice.DevicePath.IndexOf("mi_01")
            for dev in devices:
                path = dev.get('path', b'')
                if isinstance(path, bytes):
                    path = path.decode('utf-8', errors='ignore')

                # Match vendor software behavior: use mi_01
                if 'mi_01' in path.lower():
                    return dev

            # Fallback: try MI_00 (vendor-specific interface)
            for dev in devices:
                usage_page = dev.get('usage_page', 0)
                iface = dev.get('interface_number', -1)
                if usage_page == 0xff00 or iface == 0:
                    return dev

            # Last resort: return first device
            if devices:
                return devices[0]
        return None

    def connect(self) -> bool:
        """Connect to the keyboard"""
        dev_info = self.find_device()
        if not dev_info:
            return False

        self.device = hid.device()
        try:
            self.device.open_path(dev_info['path'])
            self.device.set_nonblocking(True)
            self._detect_version()
            return True
        except Exception as e:
            print(f"Failed to open device: {e}")
            self.device = None
            return False

    def disconnect(self):
        """Disconnect from the keyboard"""
        if self.device:
            self.device.close()
            self.device = None

    def _detect_version(self):
        """Detect keyboard firmware version by trying different report IDs"""
        test_data = [0] * 8

        # Try report ID 3 first (most common)
        for rid in [3, 0, 2]:
            try:
                self.device.write([rid] + test_data)
                self.report_id = rid
                return
            except Exception:
                continue

        # Default to 3 if all fail
        self.report_id = 3

    def _write_report(self, data: List[int]) -> bool:
        """Write an 8-byte report to the device"""
        if not self.device:
            return False

        # Ensure data is exactly 8 bytes
        report = (data + [0] * 8)[:8]

        try:
            self.device.write([self.report_id] + report)
            return True
        except Exception as e:
            print(f"Write failed: {e}")
            return False

    def _send_layer_switch(self, layer: int) -> bool:
        """Send layer switch command"""
        if layer < 1:
            layer = 1
        return self._write_report([0xA1, layer, 0, 0, 0, 0, 0, 0])

    def _send_flash_command(self, is_led: bool = False) -> bool:
        """Send command to write configuration to flash"""
        second_byte = 0xA1 if is_led else 0xAA
        return self._write_report([0xAA, second_byte, 0, 0, 0, 0, 0, 0])

    def set_basic_key(self, physical_key: int, keycode: int,
                      modifiers: int = 0, layer: int = 1) -> bool:
        """
        Configure a physical key to send a basic keyboard key

        Args:
            physical_key: Physical key number (1-18)
            keycode: USB HID keycode
            modifiers: Modifier flags (Ctrl=1, Shift=2, Alt=4, Win=8)
            layer: Layer number (1-3)
        """
        if not self.device:
            return False

        # Send layer switch for v2/v3 devices
        if self.report_id != 0:
            self._send_layer_switch(layer)

        # Build the key configuration packet
        # Byte 0: Physical key number (1-18)
        # Byte 1: Layer (upper nibble) | Key type (lower nibble)
        # Byte 2: Number of keys in sequence (1 for single key)
        # Byte 3: Sequence index (0 for first/only key)
        # Byte 4: Modifiers
        # Byte 5: Keycode

        key_type = KeyType.BASIC

        if self.report_id == 0:
            type_byte = key_type & 0x0F
        else:
            type_byte = (layer << 4) | (key_type & 0x0F)

        # Send the key mapping
        data = [physical_key, type_byte, 1, 0, modifiers, keycode, 0, 0]
        if not self._write_report(data):
            return False

        # Write to flash
        return self._send_flash_command()

    def set_media_key(self, physical_key: int, media_keycode: int,
                      layer: int = 1) -> bool:
        """
        Configure a physical key to send a media key

        Args:
            physical_key: Physical key number (1-18)
            media_keycode: Media key code
            layer: Layer number (1-3)
        """
        if not self.device:
            return False

        if self.report_id != 0:
            self._send_layer_switch(layer)

        key_type = KeyType.MEDIA

        if self.report_id == 0:
            type_byte = key_type & 0x0F
        else:
            type_byte = (layer << 4) | (key_type & 0x0F)

        data = [physical_key, type_byte, media_keycode, 0, 0, 0, 0, 0]
        if not self._write_report(data):
            return False

        return self._send_flash_command()

    def set_led_mode(self, mode: int) -> bool:
        """
        Set LED mode

        Args:
            mode: LED mode (0=off, 1=on, 2=breathing, etc.)
        """
        if not self.device:
            return False

        # LED uses special key number 176 (0xB0)
        key_type = KeyType.LED
        type_byte = key_type & 0x0F

        data = [0xB0, type_byte, mode, 0, 0, 0, 0, 0]
        if not self._write_report(data):
            return False

        return self._send_flash_command(is_led=True)

    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self.device is not None


def parse_key_combo(combo_str: str) -> Tuple[int, int]:
    """
    Parse a key combination string like 'ctrl+shift+a' into modifiers and keycode

    Returns:
        Tuple of (modifiers, keycode)
    """
    parts = combo_str.lower().replace(' ', '').split('+')
    modifiers = 0
    keycode = 0

    for part in parts:
        if part in ('ctrl', 'control'):
            modifiers |= Modifier.CTRL
        elif part == 'shift':
            modifiers |= Modifier.SHIFT
        elif part == 'alt':
            modifiers |= Modifier.ALT
        elif part in ('win', 'super', 'meta', 'gui'):
            modifiers |= Modifier.WIN
        elif part in KEYCODES:
            keycode = KEYCODES[part]
        elif len(part) == 1 and part.isalpha():
            keycode = KEYCODES.get(part, 0)

    return modifiers, keycode


def list_devices():
    """List all connected mini keyboards"""
    devices = []
    for pid in PRODUCT_IDS:
        devices.extend(hid.enumerate(VENDOR_ID, pid))

    if not devices:
        print("No mini keyboard devices found")
        print(f"Looking for VID=0x{VENDOR_ID:04x} with PIDs: {', '.join(f'0x{p:04x}' for p in PRODUCT_IDS)}")
        return

    print(f"Found {len(devices)} device interface(s):")
    for dev in devices:
        print(f"  Path: {dev['path']}")
        print(f"  VID:PID = 0x{dev['vendor_id']:04x}:0x{dev['product_id']:04x}")
        print(f"  Manufacturer: {dev.get('manufacturer_string', 'N/A')}")
        print(f"  Product: {dev.get('product_string', 'N/A')}")
        print(f"  Interface: {dev.get('interface_number', 'N/A')}")
        print(f"  Usage Page: 0x{dev.get('usage_page', 0):04x}")
        print(f"  Usage: 0x{dev.get('usage', 0):04x}")
        print()


def monitor_device(duration: int = 10):
    """Monitor HID traffic from the keyboard"""
    import time

    devices = []
    for pid in PRODUCT_IDS:
        devices.extend(hid.enumerate(VENDOR_ID, pid))

    if not devices:
        print("No devices found")
        return

    print(f"Monitoring keyboard for {duration} seconds. Press keys on the keyboard...")
    print("(Watching all interfaces that can be read)\n")

    # Open all readable interfaces
    open_devices = []
    for i, dev_info in enumerate(devices):
        try:
            device = hid.device()
            device.open_path(dev_info['path'])
            device.set_nonblocking(True)
            iface = dev_info.get('interface_number', '?')
            usage = dev_info.get('usage_page', 0)
            open_devices.append((device, f"iface{iface}_0x{usage:04x}"))
            print(f"  Opened interface {iface} (usage 0x{usage:04x})")
        except Exception as e:
            pass

    if not open_devices:
        print("Could not open any interfaces for reading")
        return

    print(f"\nListening... (press keys now)\n")

    start = time.time()
    while time.time() - start < duration:
        for device, name in open_devices:
            try:
                data = device.read(64, timeout_ms=10)
                if data:
                    hex_str = ' '.join(f'{b:02x}' for b in data)
                    print(f"[{name}] {hex_str}")
            except Exception:
                pass

    # Close all
    for device, _ in open_devices:
        try:
            device.close()
        except:
            pass

    print("\nDone monitoring.")



    """Debug: probe all interfaces and try different protocols"""
    import time

    devices = []
    for pid in PRODUCT_IDS:
        devices.extend(hid.enumerate(VENDOR_ID, pid))

    if not devices:
        print("No devices found")
        return

    print(f"Found {len(devices)} interface(s). Testing each...\n")

    for i, dev_info in enumerate(devices):
        path = dev_info['path']
        if isinstance(path, bytes):
            path_str = path.decode('utf-8', errors='ignore')
        else:
            path_str = path

        print(f"=== Interface {i} ===")
        print(f"Path: {path_str}")
        print(f"Interface number: {dev_info.get('interface_number', 'N/A')}")
        print(f"Usage page: 0x{dev_info.get('usage_page', 0):04x}")
        print(f"Usage: 0x{dev_info.get('usage', 0):04x}")

        try:
            device = hid.device()
            device.open_path(dev_info['path'])
            device.set_nonblocking(True)
            print("  Opened successfully")

            # Try reading first to see if there's any data
            print("  Attempting read...")
            data = device.read(64, timeout_ms=500)
            if data:
                print(f"  Read data: {[hex(b) for b in data]}")
            else:
                print("  No data to read")

            # Try different report IDs
            for rid in [0, 2, 3]:
                # Test write - just zeros
                test_data = [rid] + [0] * 8
                try:
                    result = device.write(test_data)
                    print(f"  Report ID {rid}: write OK ({result} bytes)")
                except Exception as e:
                    print(f"  Report ID {rid}: write FAIL - {e}")

            # Try feature report
            for rid in [0, 2, 3]:
                try:
                    feat = device.get_feature_report(rid, 9)
                    if feat:
                        print(f"  Feature report {rid}: {[hex(b) for b in feat]}")
                except Exception as e:
                    pass  # Feature reports often fail

            device.close()
        except Exception as e:
            print(f"  Failed to open: {e}")

        print()


def debug_init_sequences():
    """Try various initialization sequences that might unlock configuration"""
    import time

    devices = list(hid.enumerate(VENDOR_ID, 0x8840))
    if not devices:
        print("No 0x8840 device found")
        return

    # Find the vendor interface
    dev_info = None
    for d in devices:
        if d.get('usage_page') == 0xff00:
            dev_info = d
            break

    if not dev_info:
        dev_info = devices[0]

    print(f"Testing initialization sequences on 0x8840 device")
    print(f"Interface: {dev_info.get('interface_number')}, Usage: 0x{dev_info.get('usage_page', 0):04x}\n")

    device = hid.device()
    device.open_path(dev_info['path'])
    device.set_nonblocking(True)

    rid = 3
    key = 1
    keycode = 4  # 'A'
    layer = 1
    type_byte = (layer << 4) | KeyType.BASIC

    # Common initialization sequences to try
    init_sequences = [
        ("Enter config mode 0xA0", [[rid, 0xA0, 0, 0, 0, 0, 0, 0, 0]]),
        ("Enter config mode 0xA2", [[rid, 0xA2, 0, 0, 0, 0, 0, 0, 0]]),
        ("Enter config mode 0xAA", [[rid, 0xAA, 0, 0, 0, 0, 0, 0, 0]]),
        ("Read config 0xB0", [[rid, 0xB0, 0, 0, 0, 0, 0, 0, 0]]),
        ("Init 0xFF", [[rid, 0xFF, 0, 0, 0, 0, 0, 0, 0]]),
        ("Reset 0x00", [[rid, 0, 0, 0, 0, 0, 0, 0, 0]]),
        ("Wake sequence", [
            [rid, 0xA1, 1, 0, 0, 0, 0, 0, 0],  # Layer 1
            [rid, 0xA0, 0, 0, 0, 0, 0, 0, 0],  # Config mode?
        ]),
        ("Double layer switch", [
            [rid, 0xA1, 0, 0, 0, 0, 0, 0, 0],  # Layer 0
            [rid, 0xA1, 1, 0, 0, 0, 0, 0, 0],  # Layer 1
        ]),
    ]

    for name, init_pkts in init_sequences:
        print(f"\n=== {name} ===")
        try:
            # Send init
            for pkt in init_pkts:
                result = device.write(pkt)
                print(f"  Init: {[hex(b) for b in pkt[1:]]} -> {result}b")
                time.sleep(0.05)

            # Check for response
            resp = device.read(64, timeout_ms=100)
            if resp:
                print(f"  Response: {[hex(b) for b in resp]}")

            # Try setting key
            config = [rid, key, type_byte, 1, 0, 0, keycode, 0, 0]
            result = device.write(config)
            print(f"  Config: {result}b")

            # Flash
            flash = [rid, 0xAA, 0xAA, 0, 0, 0, 0, 0, 0]
            result = device.write(flash)
            print(f"  Flash: {result}b")

            # Check response
            resp = device.read(64, timeout_ms=100)
            if resp:
                print(f"  Response: {[hex(b) for b in resp]}")

            time.sleep(0.3)
        except Exception as e:
            print(f"  Error: {e}")

    # Try querying device info
    print("\n=== Query device info ===")
    query_cmds = [0x00, 0x01, 0x10, 0x20, 0x80, 0x90, 0xF0, 0xFF]
    for cmd in query_cmds:
        try:
            device.write([rid, cmd, 0, 0, 0, 0, 0, 0, 0])
            time.sleep(0.05)
            resp = device.read(64, timeout_ms=100)
            if resp:
                print(f"  0x{cmd:02x}: {[hex(b) for b in resp]}")
        except:
            pass

    device.close()
    print("\nDone. Press key 1 to test if any sequence worked.")


def debug_set_key(physical_key: int = 1, keycode: int = 4):
    """Debug: try setting a key on all interfaces with various protocols"""
    import time

    devices = []
    for pid in PRODUCT_IDS:
        devices.extend(hid.enumerate(VENDOR_ID, pid))

    if not devices:
        print("No devices found")
        return

    print(f"Attempting to set key {physical_key} to keycode {keycode} (A)")
    print(f"Found {len(devices)} interface(s)\n")

    # Only test interface 0 (vendor-specific) with various protocols
    dev_info = devices[0]
    print(f"Testing interface 0 (MI_00, usage=0x{dev_info.get('usage_page', 0):04x})")

    try:
        device = hid.device()
        device.open_path(dev_info['path'])
        device.set_nonblocking(True)

        rid = 3  # Only report ID that works
        layer = 1
        type_byte = (layer << 4) | KeyType.BASIC

        # Protocol A: Try feature report instead of output report
        print("\n=== Testing Feature Reports ===")
        try:
            feat_data = [rid, physical_key, type_byte, 1, 0, 0, keycode, 0, 0]
            device.send_feature_report(feat_data)
            print(f"  Feature report sent: {feat_data}")
            device.send_feature_report([rid, 0xAA, 0xAA, 0, 0, 0, 0, 0, 0])
            print("  Flash feature sent")
        except Exception as e:
            print(f"  Feature report failed: {e}")

        time.sleep(0.5)

        # Protocol B: Different byte order - what if key number is byte 1 not byte 0?
        print("\n=== Testing Alternate Byte Orders ===")
        # Order 1: [cmd, key, type, ...]
        packets = [
            ("Cmd prefix", [rid, 0xA1, physical_key, type_byte, 1, 0, keycode, 0, 0]),
            ("Key at byte 2", [rid, type_byte, physical_key, 1, 0, 0, keycode, 0, 0]),
            ("Flat format", [rid, physical_key, keycode, 0, 0, 0, 0, 0, 0]),
        ]
        for name, pkt in packets:
            try:
                result = device.write(pkt)
                print(f"  {name}: {pkt[1:]} -> {result} bytes")
                device.write([rid, 0xAA, 0xAA, 0, 0, 0, 0, 0, 0])
            except Exception as e:
                print(f"  {name} failed: {e}")
            time.sleep(0.2)

        # Protocol C: Larger packet sizes
        print("\n=== Testing Larger Packets (64 bytes) ===")
        big_packet = [rid] + [physical_key, type_byte, 1, 0, 0, keycode] + [0] * 57
        try:
            result = device.write(big_packet)
            print(f"  64-byte packet: {result} bytes")
            device.write([rid] + [0xAA, 0xAA] + [0] * 61)
        except Exception as e:
            print(f"  64-byte failed: {e}")

        time.sleep(0.5)

        # Protocol D: Try without report ID in data (raw write)
        print("\n=== Testing Raw Writes ===")
        raw_packets = [
            [physical_key, type_byte, 1, 0, 0, keycode, 0, 0],
            [0, physical_key, type_byte, 1, 0, 0, keycode, 0],
        ]
        for i, pkt in enumerate(raw_packets):
            try:
                result = device.write(pkt)
                print(f"  Raw {i}: {pkt} -> {result} bytes")
            except Exception as e:
                print(f"  Raw {i} failed: {e}")

        # Protocol E: Try reading response after write
        print("\n=== Testing Write then Read ===")
        device.write([rid, physical_key, type_byte, 1, 0, 0, keycode, 0, 0])
        time.sleep(0.1)
        response = device.read(64, timeout_ms=500)
        if response:
            print(f"  Response: {[hex(b) for b in response]}")
        else:
            print("  No response")

        device.write([rid, 0xAA, 0xAA, 0, 0, 0, 0, 0, 0])
        time.sleep(0.1)
        response = device.read(64, timeout_ms=500)
        if response:
            print(f"  Flash response: {[hex(b) for b in response]}")
        else:
            print("  No flash response")

        device.close()
    except Exception as e:
        print(f"Failed: {e}")

    print("\n\nDone. Press key 1 to test.")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Mini Keyboard Configurator - Configure cheap macro keyboards',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                          # List connected devices
  %(prog)s set key1 a                    # Set key 1 to 'A'
  %(prog)s set key1 ctrl+c               # Set key 1 to Ctrl+C
  %(prog)s set knob1_cw volup            # Set knob clockwise to volume up
  %(prog)s set key5 f5 --layer 2         # Set key 5 to F5 on layer 2
  %(prog)s led 1                         # Set LED mode 1

Physical keys: key1-key12, knob1_left/press/right (k1_left/k1_press/k1_right)
Modifiers: ctrl, shift, alt, win
Media keys: play, pause, next, prev, volup, voldown, mute
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List command
    subparsers.add_parser('list', help='List connected devices')

    # Debug command
    subparsers.add_parser('debug', help='Debug: probe all interfaces')

    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor HID traffic from keyboard')
    monitor_parser.add_argument('--time', '-t', type=int, default=10, help='Duration in seconds (default: 10)')

    # Debug init command
    subparsers.add_parser('debug-init', help='Debug: try init sequences for 0x8840')

    # Debug set command
    debug_set_parser = subparsers.add_parser('debug-set', help='Debug: try setting key1 to A on all interfaces')
    debug_set_parser.add_argument('--key', '-k', type=int, default=1, help='Physical key number (default: 1)')
    debug_set_parser.add_argument('--code', '-c', type=int, default=4, help='Keycode (default: 4 = A)')

    # Set command
    set_parser = subparsers.add_parser('set', help='Set a key mapping')
    set_parser.add_argument('key', help='Physical key (key1-key12, knob1_left, etc.)')
    set_parser.add_argument('mapping', help='Key to map (a-z, f1-f12, ctrl+c, volup, etc.)')
    set_parser.add_argument('--layer', '-l', type=int, default=1,
                           help='Layer (1-3, default: 1)')

    # LED command
    led_parser = subparsers.add_parser('led', help='Set LED mode')
    led_parser.add_argument('mode', type=int, help='LED mode (0=off, 1=on, 2=breathing)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'list':
        list_devices()
        return

    if args.command == 'debug':
        debug_interfaces()
        return

    if args.command == 'monitor':
        monitor_device(args.time)
        return

    if args.command == 'debug-init':
        debug_init_sequences()
        return

    if args.command == 'debug-set':
        debug_set_key(args.key, args.code)
        return

    # Commands that need device connection
    kb = MiniKeyboard()

    if not kb.connect():
        print("Error: Could not connect to keyboard")
        print("Make sure the keyboard is plugged in and you have permissions.")
        print("On Linux, you may need to add a udev rule or run as root.")
        return

    try:
        if args.command == 'set':
            # Parse physical key
            key_name = args.key.lower()
            if key_name not in PHYSICAL_KEYS:
                print(f"Error: Unknown physical key '{args.key}'")
                print(f"Valid keys: {', '.join(sorted(PHYSICAL_KEYS.keys()))}")
                return

            physical_key = PHYSICAL_KEYS[key_name]
            mapping = args.mapping.lower()

            # Check if it's a media key
            if mapping in MEDIA_KEYCODES:
                media_code = MEDIA_KEYCODES[mapping]
                if kb.set_media_key(physical_key, media_code, args.layer):
                    print(f"Set {args.key} to media key '{mapping}' on layer {args.layer}")
                else:
                    print("Failed to set key mapping")
            else:
                # Parse as basic key combo
                modifiers, keycode = parse_key_combo(mapping)
                if keycode == 0:
                    print(f"Error: Unknown key '{mapping}'")
                    print(f"Valid keys: {', '.join(sorted(KEYCODES.keys()))}")
                    return

                if kb.set_basic_key(physical_key, keycode, modifiers, args.layer):
                    print(f"Set {args.key} to '{mapping}' on layer {args.layer}")
                else:
                    print("Failed to set key mapping")

        elif args.command == 'led':
            if kb.set_led_mode(args.mode):
                print(f"Set LED mode to {args.mode}")
            else:
                print("Failed to set LED mode")

    finally:
        kb.disconnect()


if __name__ == '__main__':
    main()
