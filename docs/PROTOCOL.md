# Mini Keyboard HID Protocol

This document describes the USB HID protocol used by CH552/CH57x-based mini programmable keyboards.

## Device Identification

| Field | Value |
|-------|-------|
| Vendor ID | 0x1189 (4489) |
| Product ID | 0x8890 or 0x8840 |
| Interface | MI_00 (interface 0) for configuration |
| Usage Page | 0xFF00 (vendor-specific) |

## HID Report Structure

Reports are 8 bytes (plus report ID prefix).

### Report IDs

The keyboard firmware version determines which report ID to use:

| Report ID | Firmware Version |
|-----------|-----------------|
| 0 | v0 (oldest) |
| 2 | v2 |
| 3 | v3 (most common) |

Detection: Try writing `[report_id, 0, 0, 0, 0, 0, 0, 0, 0]` with each ID. The one that succeeds is correct.

## Commands

### Layer Switch (0xA1)

Switch to a configuration layer before setting keys.

```
Byte 0: 0xA1 (command)
Byte 1: Layer number (1-3)
Bytes 2-7: 0x00
```

### Basic Key Configuration

Configure a physical key to send a keyboard key.

**Packet 1 (header):**
```
Byte 0: Physical key number (1-18)
Byte 1: (Layer << 4) | KeyType (1 for basic)
Byte 2: Number of keys in sequence (1 for single key)
Byte 3: Sequence index (0)
Byte 4: Modifier flags
Byte 5: 0x00
Bytes 6-7: 0x00
```

**Packet 2 (keycode):**
```
Byte 0: Physical key number (1-18)
Byte 1: (Layer << 4) | KeyType
Byte 2: Number of keys in sequence (1)
Byte 3: Sequence index (1)
Byte 4: Modifier flags
Byte 5: USB HID keycode
Bytes 6-7: 0x00
```

### Media Key Configuration

```
Byte 0: Physical key number (1-18)
Byte 1: (Layer << 4) | KeyType (2 for media)
Byte 2: Media keycode
Byte 3: Media keycode high byte (usually 0)
Bytes 4-7: 0x00
```

### Mouse Key Configuration

```
Byte 0: Physical key number (1-18)
Byte 1: (Layer << 4) | KeyType (3 for mouse)
Bytes 2-6: Mouse action data
Byte 7: 0x00
```

### LED Mode Configuration

```
Byte 0: 0xB0 (176 - LED indicator)
Byte 1: KeyType (8 for LED)
Byte 2: LED mode (0=off, 1=on, 2=breathing, etc.)
Bytes 3-7: 0x00
```

### Flash/Save Command (0xAA)

Write configuration to persistent storage.

```
Byte 0: 0xAA
Byte 1: 0xAA (for keys) or 0xA1 (for LED)
Bytes 2-7: 0x00
```

## Physical Key Numbers

| Key | Number | Description |
|-----|--------|-------------|
| 1-12 | 1-12 | Regular keys |
| 13 | 13 | Knob 1 counter-clockwise |
| 14 | 14 | Knob 1 press |
| 15 | 15 | Knob 1 clockwise |
| 16 | 16 | Knob 2 counter-clockwise |
| 17 | 17 | Knob 2 press |
| 18 | 18 | Knob 2 clockwise |

## Key Types

| Type | Value | Description |
|------|-------|-------------|
| Basic | 1 | Standard keyboard keys |
| Media | 2 | Media/consumer control keys |
| Mouse | 3 | Mouse buttons/movement |
| LED | 8 | LED control |

## Modifier Flags

| Modifier | Bit | Value |
|----------|-----|-------|
| Ctrl | 0 | 0x01 |
| Shift | 1 | 0x02 |
| Alt | 2 | 0x04 |
| Win/GUI | 3 | 0x08 |
| Right Ctrl | 4 | 0x10 |
| Right Shift | 5 | 0x20 |
| Right Alt | 6 | 0x40 |
| Right Win | 7 | 0x80 |

## USB HID Keycodes

Standard USB HID keyboard scan codes:

| Key | Code | Key | Code |
|-----|------|-----|------|
| A-Z | 4-29 | 1-0 | 30-39 |
| Enter | 40 | Escape | 41 |
| Backspace | 42 | Tab | 43 |
| Space | 44 | F1-F12 | 58-69 |
| Insert | 73 | Home | 74 |
| Page Up | 75 | Delete | 76 |
| End | 77 | Page Down | 78 |
| Right | 79 | Left | 80 |
| Down | 81 | Up | 82 |

## Media Keycodes (Report ID 3)

| Function | Code |
|----------|------|
| Play/Pause | 205 |
| Stop | 183 |
| Previous | 182 |
| Next | 181 |
| Mute | 226 |
| Volume Up | 233 |
| Volume Down | 234 |

## Example: Set Key 1 to Ctrl+C

```python
report_id = 3
physical_key = 1
layer = 1
key_type = 1  # basic
modifiers = 0x01  # Ctrl
keycode = 6  # 'C'

type_byte = (layer << 4) | key_type

# Layer switch
write([report_id, 0xA1, layer, 0, 0, 0, 0, 0, 0])

# Config packet 1 (header)
write([report_id, physical_key, type_byte, 1, 0, modifiers, 0, 0, 0])

# Config packet 2 (keycode)
write([report_id, physical_key, type_byte, 1, 1, modifiers, keycode, 0, 0])

# Flash
write([report_id, 0xAA, 0xAA, 0, 0, 0, 0, 0, 0])
```

## Known Variants

### PID 0x8890
- Well documented
- Protocol confirmed working via decompiled source analysis
- Uses MI_00 (usage page 0xFF00) for configuration

### PID 0x8840
- Less common variant
- Device detected correctly, HID writes accepted (65 bytes)
- **Configuration not applied** - firmware ignores standard protocol
- Possible different packet structure or initialization sequence required
- USB traffic capture from working software needed to reverse engineer

## Protocol Source

The protocol was reverse-engineered from decompiled .NET source code of the vendor software. Key findings from `FormMain.Designer.cs`:

### Download_Click Method (Line 353)

For basic keys, the software sends packets in a loop:

```csharp
for (byte index = 0; index <= KeyGroup_CharNum; ++index)
{
    arrayBuff[3] = index;
    switch (index)
    {
        case 0:  // Header packet
            arrayBuff[4] = modifiers;
            arrayBuff[5] = 0;
            break;
        case 1:  // Keycode packet
            arrayBuff[4] = modifiers;
            arrayBuff[5] = keycode;
            break;
        // cases 2-5 for multi-key sequences...
    }
    WriteDataToDevice(ReportID, arrayBuff);
}
Send_WriteFlash_Cmd();
```

### Version Detection (KeyBoardVersion_Check)

The software tries report IDs in order: 3, 0, 2

```csharp
ReportID = 3;
if (!WriteToDevice(ReportID, arrayBuff))
{
    ReportID = 0;
    if (!WriteToDevice(ReportID, arrayBuff))
        ReportID = 2;
}
```

### Layer Switch (Send_SwLayer)

```csharp
arrayBuff[0] = 0xA1;  // 161
arrayBuff[1] = layer; // 1, 2, or 3
```

### Flash Command (Send_WriteFlash_Cmd)

```csharp
arrayBuff[0] = 0xAA;  // 170
arrayBuff[1] = isLed ? 0xA1 : 0xAA;  // 161 for LED, 170 for keys
```
