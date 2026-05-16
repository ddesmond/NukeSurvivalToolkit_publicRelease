# AGENTS.md - Nuke Survival Toolkit

## Project Overview

A Foundry Nuke plugin providing 290+ compositing gizmos organized into a custom toolbar. No build system, linter, or test framework — this is a Nuke plugin that runs inside the Nuke application.

## Directory Structure

```
NukeSurvivalToolkit/
├── menu.py            # Main entry point — creates toolbar, registers all tools
├── init.py            # Minimal stub (work done in menu.py)
├── gizmos/            # 290+ .gizmo files (all prefixed NST_)
├── python/            # Supporting Python modules
├── nk_files/          # .nk script templates and presets
├── icons/             # Menu and tool icons (.png)
└── images/            # Demo images referenced by gizmos
```

## Commands

### Testing
There is no automated test suite. Manual testing requires Nuke:

1. Add toolkit path to `~/.nuke/init.py`:
   ```python
   nuke.pluginAddPath("/path/to/NukeSurvivalToolkit_publicRelease/NukeSurvivalToolkit")
   ```
2. Restart Nuke and look for the red multi-tool icon in the toolbar
3. Test individual tools by creating them from the menu

### Linting / Formatting
No linter or formatter is configured. Follow existing code conventions (see below).

## Python Code Style

### Imports
- Standard library imports first, then `nuke`/`nukescripts`, then third-party
- Group imports logically with blank line separators
- Use `from pathlib import Path` for all path operations
- PySide6 for UI (Nuke 16+); was PySide2 in older versions

```python
import nuke
import nukescripts
import webbrowser
from pathlib import Path
from PySide6 import QtGui, QtCore, QtWidgets
```

### Path Handling
- **Always use `Path.as_posix()`** to force forward slashes on all platforms
- Never use `os.path.dirname()` for toolkit paths — it produces backslashes on Windows

```python
# CORRECT
NST_FolderPath = Path(__file__).parent.as_posix()

# WRONG — breaks on Windows
NST_FolderPath = os.path.dirname(__file__)
```

### Naming Conventions
- **Gizmo files**: `NST_ToolName.gizmo` — all toolkit gizmos use `NST_` prefix
- **Python modules**: `NST_moduleName.py` for toolkit-specific, descriptive names for others
- **Functions**: `camelCase` (matching Nuke API style) or `snake_case`
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `NST_FolderPath`, `LOAD_EXPRESSION_MENU`)
- **Global prefix**: `prefixNST = "NST_"` stored as global in `menu.py`

### Formatting
- Indentation: **4 spaces** (no tabs)
- Line length: flexible, but aim for readability
- f-strings preferred for string formatting
- Docstrings for public functions

### Error Handling
- Use **specific exception types** (`ImportError`, `RuntimeError`), not bare `except:`
- Print informative messages on failure, then `pass`
- Optional dependencies should fail silently (e.g., `stamps` integration)

```python
# CORRECT
try:
    import ColorGradientUi
    drawMenu.addCommand("GradientEditor MHD", ...)
except ImportError as e:
    print(f"Could not load ColorGradientUi: {e}")
    pass

# CORRECT — for nuke.load()
try:
    nuke.load(f'{prefixNST}VectorTracker.py')
except RuntimeError as e:
    print(f"Could not load VectorTracker.py: {e}")
    pass
```

### Menu Registration Patterns
Three ways tools are added:

```python
# 1. Direct gizmo creation (most common)
menu.addCommand('ToolName', f"nuke.createNode('{prefixNST}ToolName')", icon="icon.png")

# 2. Node paste from .nk template
menu.addCommand('Template', f'nuke.nodePaste("{nk_path("Template.nk")}")')

# 3. Helper function (for dynamic file path replacement)
menu.addCommand('AutoFlare', f"NST_helper.filepathCreateNode('{prefixNST}AutoFlare2')")
```

### Dynamic File Path Replacement
Gizmos with Read/Camera nodes use `<<<replace>>>` placeholder:

```python
# In gizmo: file path contains "<<<replace>>>"
# NST_helper.filepathCreateNode() swaps it with actual toolkit path at runtime
# Supported node classes: Read, DeepRead, ReadGeo, ReadGeo2, Camera2, Axis2
```

### Gizmo File Conventions
- Save as **Group**, not Gizmo (so scripts work without NST installed)
- `Group {` must be the first line — strip `set cut_paste_input`, `version`, `push` boilerplate
- Remove `xpos` and `ypos` lines before the first `addUserKnob`
- Camera compatibility: check for `Camera`, `Camera2`, and `Camera3` (Nuke 13+)

### TCL Expressions
Used within gizmos for node traversal and dynamic expressions:

```tcl
# Find upstream camera through any group depth
if {[class $x]=="Camera3"||[class $x]=="Camera2"||[class $x]=="Camera"} { ... }
```

### Configuration
User-configurable variables in `menu.py`:
```python
LOAD_EXPRESSION_MENU = False  # Submenu under Draw, disabled by default
```

Documentation URLs configured in `menu.py`, assigned to `NST_helper` module:
```python
NST_helper.NST_DOCS_ONLINE_URL = "https://..."
NST_helper.NST_DOCS_ONLINE_TIMEOUT_SECONDS = 1.5
NST_helper.NST_DOCS_PDF_NAME = "NukeSurvivalToolkit_Documentation_Release_v2.2.0.pdf"
NST_helper.NST_DOCS_OFFLINE_INDEX = Path("NST_Documentation/index.html")
```

## Contributing Workflow

1. Name gizmo file `NST_ToolName.gizmo`
2. Add menu entry in appropriate section of `menu.py`
3. Add icon to `icons/` if needed
4. For image assets: place in `images/`, use `<<<replace>>>` placeholder in Read nodes
5. Update `CHANGELOG.md` with the addition

## Module Dependencies

| Module | Dependencies |
|--------|-------------|
| `ColorGradientUi.py` | PySide6, configparser |
| `NST_helper.py` | nuke, nukescripts, pathlib, stdlib (http, threading, ssl, webbrowser) |
| `NST_ID_Extractor.py` | nuke, nukescripts, optional: stamps |
| `NST_VectorTracker.py` | nuke |
| `NST_cardToTrack.py` | nuke, math, threading |
| `NST_cardToTrack_v9.py` | nuke, math, re, time |
| `NST_stickit.py` | nuke, nuke.splinewarp, math |
