# Security Analysis of Vendor Software

This document provides a security analysis of the original vendor software (`MINI KeyBoard.exe`) that ships with CH552-based mini programmable keyboards.

## Executive Summary

**Risk Level: LOW**

The decompiled source code shows the software is a legitimate keyboard configuration tool with no malicious behavior detected.

## Analysis Method

1. Static analysis using `strings` command on executable
2. Decompilation of .NET assembly (source available in `MiniKeyboard48/` folder)
3. Runtime monitoring during brief execution

## Findings

### Network Activity

| Check | Result |
|-------|--------|
| HTTP/HTTPS URLs | None found |
| Socket connections | None |
| DNS lookups | None |
| Download/upload code | None |

**Conclusion:** No network activity whatsoever.

### File System Operations

| Check | Result |
|-------|--------|
| File read operations | None (except .NET runtime) |
| File write operations | None |
| Temp file creation | None |
| Config file storage | None |

**Conclusion:** The software doesn't persist any data to disk.

### System Modifications

| Check | Result |
|-------|--------|
| Registry access | None |
| Startup entries | None |
| Scheduled tasks | None |
| Service installation | None |
| Driver installation | None |

**Conclusion:** No persistence mechanisms.

### Process Operations

| Check | Result |
|-------|--------|
| Shell execution | None |
| Process spawning | None |
| DLL injection | None |
| Memory manipulation | None |

**Conclusion:** No suspicious process activity.

### External Communication

| Type | Details |
|------|---------|
| USB HID | Yes - communicates with keyboard device only |
| Vendor ID filter | 0x1189 only |
| Product ID filter | 0x8890, 0x8840 |

**Conclusion:** Only communicates with the specific keyboard hardware via HID protocol.

## Code Structure

The software consists of:

```
MINI KeyBoard.exe      - Main .NET Windows Forms application
HidLibrary.dll         - Standard HID communication library
Theraot.Core.dll       - .NET compatibility shim
```

### Key Classes

| Class | Purpose |
|-------|---------|
| `FormMain` | Main UI and configuration logic |
| `HidOperations` | USB HID device enumeration and I/O |
| `BasicKeys` | Basic keyboard key mapping UI |
| `MediaKeys` | Media key mapping UI |
| `MouseKeys` | Mouse button mapping UI |
| `LedFunctions` | LED control UI |
| `LayerFunctions` | Layer switching UI |

### Data Flow

1. User selects physical key (KEY1-KEY12, K1_Left, etc.)
2. User selects target key/function from UI
3. Configuration stored in `KeyParam.Data_Send_Buff[]`
4. "Download" button sends HID packets to device
5. Flash command persists configuration

## Runtime Behavior

During brief execution:

- ✅ No new processes spawned
- ✅ No network connections established
- ✅ No files created or modified
- ✅ No registry changes
- ✅ No startup entries added
- ✅ Only localhost connections (normal inter-process communication)

## Recommendations

1. **Safe to use** for keyboard configuration if desired
2. **Consider VM** if extra caution needed
3. **Use Python tool** (`python/minikeyboard.py`) as open-source alternative for PID 0x8890
4. **USB capture** still needed to support PID 0x8840 variant

## DLL Dependencies

### HidLibrary.dll
- Standard open-source HID library
- No suspicious strings found
- Source: https://github.com/mikeobrien/HidLibrary

### Theraot.Core.dll
- .NET Standard compatibility backport
- No suspicious strings found
- Source: https://github.com/theraot/Theraot

## Conclusion

The vendor software appears to be a straightforward keyboard configuration utility with no malicious code. The primary concerns are:

1. **Unsigned binary** - No code signing certificate
2. **Unknown origin** - Distributed via generic Chinese e-commerce channels
3. **No source code** - Closed source (though decompilable)

These are common characteristics of cheap peripheral software from Chinese manufacturers, but do not indicate malicious intent in this case.

---

*Analysis performed: January 2026*
*Analyst: Claude (AI assistant)*
*Method: Static analysis + decompilation + runtime monitoring*
