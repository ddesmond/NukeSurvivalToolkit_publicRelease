#!/usr/bin/env python
"""
Gaffer Survival Toolkit — Installation Helper

This script helps configure Gaffer to use the Gaffer Survival Toolkit.
It can be run standalone or sourced from your Gaffer startup configuration.

Usage:
    Option 1: Add to ~/.gaffer/startup/gui/user.py:
        import sys
        sys.path.append("/path/to/GafferSurvivalToolkit/python")

    Option 2: Set environment variables:
        export PYTHONPATH="/path/to/GafferSurvivalToolkit/python:$PYTHONPATH"
        export GAFFER_STARTUP_PATHS="/path/to/GafferSurvivalToolkit/startup:$GAFFER_STARTUP_PATHS"

    Option 3: Run this script interactively in Gaffer's Python Editor:
        exec(open("/path/to/GafferSurvivalToolkit/install.py").read())
"""

import os
import sys
from pathlib import Path


def get_toolkit_root():
    """Return the GafferSurvivalToolkit root directory."""
    return Path(__file__).parent.resolve()


def install():
    """Add GafferSurvivalToolkit to Gaffer's paths."""
    toolkit_root = get_toolkit_root()
    python_path = (toolkit_root / "python").as_posix()
    startup_path = (toolkit_root / "startup").as_posix()

    # Add Python modules to sys.path
    if python_path not in sys.path:
        sys.path.insert(0, python_path)
        print(f"[GST] Added {python_path} to sys.path")

    # Add startup path to GAFFER_STARTUP_PATHS environment variable
    current_startup_paths = os.environ.get("GAFFER_STARTUP_PATHS", "")
    if startup_path not in current_startup_paths:
        if current_startup_paths:
            os.environ["GAFFER_STARTUP_PATHS"] = (
                f"{startup_path}:{current_startup_paths}"
            )
        else:
            os.environ["GAFFER_STARTUP_PATHS"] = startup_path
        print(f"[GST] Added {startup_path} to GAFFER_STARTUP_PATHS")

    print(f"[GST] Gaffer Survival Toolkit installed from: {toolkit_root}")
    print(f"[GST] Python path: {python_path}")
    print(f"[GST] Startup path: {startup_path}")
    print(f"[GST] Restart Gaffer or run 'import GST_menu' to load the menu.")


def verify():
    """Verify that the toolkit is properly installed."""
    toolkit_root = get_toolkit_root()
    issues = []

    # Check python directory
    python_path = toolkit_root / "python"
    if not python_path.is_dir():
        issues.append(f"Python directory not found: {python_path}")
    else:
        # Check for required modules
        required_modules = ["GST_helper.py"]
        for module in required_modules:
            if not (python_path / module).is_file():
                issues.append(f"Required module not found: {module}")

    # Check startup directory
    startup_path = toolkit_root / "startup"
    if not startup_path.is_dir():
        issues.append(f"Startup directory not found: {startup_path}")
    else:
        gui_startup = startup_path / "gui" / "GST_menu.py"
        if not gui_startup.is_file():
            issues.append(f"Menu startup not found: {gui_startup}")

    # Check gfr directory
    gfr_path = toolkit_root / "gfr"
    if not gfr_path.is_dir():
        issues.append(f"GFR directory not found: {gfr_path}")

    if issues:
        print("[GST] Verification FAILED:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("[GST] Verification PASSED — all required files found.")
        return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gaffer Survival Toolkit Installer")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify toolkit installation",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install toolkit paths",
    )

    args = parser.parse_args()

    if args.verify:
        verify()
    elif args.install:
        install()
    else:
        # Default: install and verify
        install()
        print()
        verify()
