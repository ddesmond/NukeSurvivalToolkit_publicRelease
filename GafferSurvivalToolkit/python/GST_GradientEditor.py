##############################################################################################

# GST_GradientEditor — Interactive gradient editor for Gaffer
# Ported from Nuke Survival Toolkit ColorGradientUi by Mads Hagbarth Damsbo
#
# This provides an interactive gradient editing UI with:
#   - Visual gradient bar with draggable color handles
#   - Color picker for selected handles
#   - HSV sliders for fine-tuning
#   - Preset system with save/load
#   - Interpolation mode selection
#
# In Gaffer, this is implemented as:
#   - A custom GafferUI.Widget subclass for the gradient editor
#   - Integration with GafferImage.ColorLookup or Grade nodes
#   - Preset storage in a configuration file

import Gaffer
import GafferImage
import GafferUI
import IECore
import imath
import os
import json
from pathlib import Path


class GST_GradientEditor(GafferUI.Widget):
    """Interactive gradient editor widget for Gaffer."""

    def __init__(self, grade_node=None, **kw):
        self._gradeNode = grade_node
        self._colorList = []
        self._selectedHandle = None
        self._widgetOffset = 10
        self._widgetHeight = 40
        self._widgetTop = 15
        self._handleWidth = 7

        # Build UI using standard GafferUI widgets
        with GafferUI.ListContainer(
            GafferUI.ListContainer.Orientation.Vertical, spacing=8
        ) as widget:
            # Top bar: preset menu + interpolation selector
            with GafferUI.ListContainer(
                GafferUI.ListContainer.Orientation.Horizontal, spacing=8
            ) as top_bar:
                self._presetButton = GafferUI.MenuButton("Gradient Presets")
                self._presetButton.setMenu(GafferUI.Menu(self._buildPresetMenu()))

                self._interpolationLabel = GafferUI.Label("Interpolation")
                self._interpolationCombo = GafferUI.ComboBox()
                self._interpolationCombo.setItems(
                    [
                        "Constant",
                        "Linear",
                        "Smooth",
                        "Catmull-Rom",
                        "Cubic",
                        "Horizontal",
                    ]
                )
                self._interpolationCombo.setCurrentIndex(2)

                self._addPresetButton = GafferUI.Button("+")

            # Gradient visualization using a label with stylesheet
            self._gradientLabel = GafferUI.Label("")
            self._gradientLabel._qtWidget().setFixedHeight(60)
            self._gradientLabel._qtWidget().setMinimumWidth(200)
            self._gradientLabel._qtWidget().setMouseTracking(True)

            # HSV sliders
            with GafferUI.ListContainer(
                GafferUI.ListContainer.Orientation.Horizontal, spacing=8
            ) as hsv_bar:
                GafferUI.Label("H")
                self._hueSlider = GafferUI.Slider(min=0, max=255)

                GafferUI.Label("S")
                self._satSlider = GafferUI.Slider(min=0, max=255)

                GafferUI.Label("V")
                self._lumSlider = GafferUI.Slider(min=0, max=255)

        # Connect signals
        self._hueSlider.valueChangedSignal().connect(
            Gaffer.WeakMethod(self._onHSVChanged)
        )
        self._satSlider.valueChangedSignal().connect(
            Gaffer.WeakMethod(self._onHSVChanged)
        )
        self._lumSlider.valueChangedSignal().connect(
            Gaffer.WeakMethod(self._onHSVChanged)
        )
        self._interpolationCombo.currentIndexChangedSignal().connect(
            Gaffer.WeakMethod(self._onInterpolationChanged)
        )
        self._addPresetButton.clickedSignal().connect(
            Gaffer.WeakMethod(self._onAddPreset)
        )

        # Mouse events on the gradient label using GafferUI signals
        self._gradientLabel.buttonPressSignal().connect(
            Gaffer.WeakMethod(self._onGafferButtonPress)
        )
        self._gradientLabel.mouseMoveSignal().connect(
            Gaffer.WeakMethod(self._onGafferMouseMove)
        )
        self._gradientLabel.buttonReleaseSignal().connect(
            Gaffer.WeakMethod(self._onGafferButtonRelease)
        )
        self._gradientLabel.buttonDoubleClickSignal().connect(
            Gaffer.WeakMethod(self._onGafferButtonDoubleClick)
        )

        self._dragging = False

        # Initialize with default colors
        self._initDefaultColors()

    def _onGafferButtonPress(self, widget, event):
        """Handle button press on gradient label."""
        self._dragging = True
        self._handleGafferMouseEvent(event)

    def _onGafferMouseMove(self, widget, event):
        """Handle mouse move on gradient label."""
        if self._dragging:
            self._handleGafferMouseEvent(event)

    def _onGafferButtonRelease(self, widget, event):
        """Handle button release on gradient label."""
        self._dragging = False
        self._updateGradeNode()

    def _onGafferButtonDoubleClick(self, widget, event):
        """Handle double-click to add new color handle."""
        pos_x = self._normalizeXFromEvent(event)
        handle = self._getNearestHandle(pos_x, 0)
        if handle is None:
            color = self._getColorAtPosition(pos_x)
            new_handle = {"position": pos_x, "color": color, "selected": True}
            self._colorList.append(new_handle)
            self._selectHandle(new_handle)
            self._updateGradientVisual()
            self._updateGradeNode()

    def _handleGafferMouseEvent(self, event):
        """Process GafferUI mouse event on gradient bar."""
        pos_x = self._normalizeXFromEvent(event)
        handle = self._getNearestHandle(pos_x, 0)
        if handle:
            self._selectHandle(handle)
        elif self._dragging and self._selectedHandle:
            self._selectedHandle["position"] = max(0.0, min(1.0, pos_x))
            self._updateGradientVisual()
            self._updateGradeNode()

    def _normalizeXFromEvent(self, event):
        """Normalize x coordinate from GafferUI event to 0-1 range."""
        x = event.line.p0.x
        width = self._gradientLabel._qtWidget().width() - 2 * self._widgetOffset
        if width <= 0:
            return 0.5
        return max(0.0, min(1.0, (x - self._widgetOffset) / width))

    def _getNearestHandle(self, pos_x, pos_y):
        """Find the nearest handle to the given position."""
        min_dist = float("inf")
        nearest = None

        for handle in self._colorList:
            dist = abs(pos_x - handle["position"])
            if dist < min_dist and dist < self._handleWidth / 100.0:
                min_dist = dist
                nearest = handle

        return nearest

    def _selectHandle(self, handle):
        """Select a color handle and update UI."""
        for h in self._colorList:
            h["selected"] = False
        handle["selected"] = True
        self._selectedHandle = handle
        self._updateSliders()

    def _getColorAtPosition(self, pos_x):
        """Get interpolated color at a given position."""
        sorted_colors = sorted(self._colorList, key=lambda c: c["position"])

        prev_color = sorted_colors[0]
        next_color = sorted_colors[-1]

        for i, color in enumerate(sorted_colors):
            if color["position"] >= pos_x:
                if i > 0:
                    prev_color = sorted_colors[i - 1]
                next_color = color
                break

        if prev_color["position"] == next_color["position"]:
            return prev_color["color"]

        t = (pos_x - prev_color["position"]) / (
            next_color["position"] - prev_color["position"]
        )
        t = max(0.0, min(1.0, t))

        r = prev_color["color"][0] * (1 - t) + next_color["color"][0] * t
        g = prev_color["color"][1] * (1 - t) + next_color["color"][1] * t
        b = prev_color["color"][2] * (1 - t) + next_color["color"][2] * t
        a = prev_color["color"][3] * (1 - t) + next_color["color"][3] * t

        return (r, g, b, a)

    def _updateGradientVisual(self):
        """Update the gradient bar visualization using CSS."""
        sorted_colors = sorted(self._colorList, key=lambda c: c["position"])

        stops = []
        for color in sorted_colors:
            r, g, b, a = color["color"]
            pos = color["position"] * 100
            stops.append(
                f"rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, {a:.2f}) {pos:.1f}%"
            )

        gradient_css = f"linear-gradient(to right, {', '.join(stops)})"

        qt_widget = self._gradientLabel._qtWidget()
        qt_widget.setStyleSheet(
            f"QLabel {{ background: q{gradient_css}; border: 1px solid #555; border-radius: 4px; }}"
        )

    def _updateSliders(self):
        """Update HSV sliders to match selected handle color."""
        if self._selectedHandle is None:
            return

        r, g, b, a = self._selectedHandle["color"]

        max_c = max(r, g, b)
        min_c = min(r, g, b)
        diff = max_c - min_c

        if max_c == 0:
            s = 0
        else:
            s = diff / max_c

        h = 0
        if diff != 0:
            if max_c == r:
                h = (60 * ((g - b) / diff) + 360) % 360
            elif max_c == g:
                h = (60 * ((b - r) / diff) + 120) % 360
            else:
                h = (60 * ((r - g) / diff) + 240) % 360

        self._hueSlider.setValue(h / 360.0 * 255)
        self._satSlider.setValue(s * 255)
        self._lumSlider.setValue(max_c * 255)

    def _onHSVChanged(self, widget):
        """Update selected handle color from HSV sliders."""
        if self._selectedHandle is None:
            return

        h = self._hueSlider.getValue() / 255.0 * 360
        s = self._satSlider.getValue() / 255.0
        v = self._lumSlider.getValue() / 255.0

        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c

        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        self._selectedHandle["color"] = (
            r + m,
            g + m,
            b + m,
            self._selectedHandle["color"][3],
        )
        self._updateGradientVisual()
        self._updateGradeNode()

    def _onInterpolationChanged(self, widget):
        """Update grade node when interpolation mode changes."""
        self._updateGradeNode()

    def _onAddPreset(self, widget):
        """Add current gradient as a preset."""
        if self._gradeNode is None:
            return

        preset_data = self._serializeGradient()
        self._savePreset(preset_data)

    def _serializeGradient(self):
        """Serialize gradient to JSON format."""
        sorted_colors = sorted(self._colorList, key=lambda c: c["position"])
        return {
            "colors": [
                {
                    "position": c["position"],
                    "color": list(c["color"]),
                }
                for c in sorted_colors
            ],
            "interpolation": self._interpolationCombo.getCurrentItem(),
        }

    def _savePreset(self, preset_data):
        """Save gradient preset to configuration file."""
        presets_path = self._getPresetsPath()
        config = {}

        if presets_path.exists():
            try:
                with open(presets_path, "r") as f:
                    config = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        if "Default" not in config:
            config["Default"] = {}

        preset_name = f"preset_{len(config['Default']) + 1}"
        config["Default"][preset_name] = preset_data

        try:
            with open(presets_path, "w") as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            IECore.msg(
                IECore.Msg.Level.Error,
                "GST_GradientEditor",
                f"Failed to save preset: {e}",
            )

    def _getPresetsPath(self):
        """Get path to presets configuration file."""
        gst_root = Path(__file__).parent.parent
        return gst_root / "python" / "GradientPresets.json"

    def _buildPresetMenu(self):
        """Build the preset menu from saved presets."""
        menu = IECore.MenuDefinition()
        presets_path = self._getPresetsPath()

        if presets_path.exists():
            try:
                with open(presets_path, "r") as f:
                    config = json.load(f)

                for category, presets in config.items():
                    if isinstance(presets, dict):
                        for name, data in presets.items():
                            menu.append(
                                f"/{category}/{name}",
                                {
                                    "command": lambda m, d=data: self._loadPreset(d),
                                },
                            )
            except (json.JSONDecodeError, IOError):
                pass

        if not menu.items():
            menu.append("/No Presets Saved", {"command": None})

        return menu

    def _loadPreset(self, preset_data):
        """Load a gradient preset."""
        self._colorList = []
        try:
            if isinstance(preset_data, dict):
                colors = preset_data.get("colors", [])
                for c in colors:
                    self._colorList.append(
                        {
                            "position": c.get("position", 0.0),
                            "color": tuple(c.get("color", (1.0, 1.0, 1.0, 1.0))),
                            "selected": False,
                        }
                    )
            elif isinstance(preset_data, str):
                lines = preset_data.strip().split("\n")
                channel_colors = {"red": [], "green": [], "blue": [], "alpha": []}
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) < 3:
                        continue
                    i = 1
                    while i < len(parts) - 1:
                        if parts[i].startswith("x"):
                            pos = float(parts[i][1:])
                            val = float(parts[i + 1])
                            for ch in channel_colors:
                                channel_colors[ch].append((pos, val))
                            i += 2
                        else:
                            i += 1

                positions = [p for p, v in channel_colors["red"]]
                for idx, pos in enumerate(positions):
                    r = channel_colors["red"][idx][1]
                    g = channel_colors["green"][idx][1]
                    b = channel_colors["blue"][idx][1]
                    a = (
                        channel_colors["alpha"][idx][1]
                        if idx < len(channel_colors["alpha"])
                        else 1.0
                    )
                    self._colorList.append(
                        {
                            "position": pos,
                            "color": (r, g, b, a),
                            "selected": False,
                        }
                    )

            if self._colorList:
                self._colorList[0]["selected"] = True
                self._selectedHandle = self._colorList[0]
                self._updateSliders()
                self._updateGradientVisual()
                self._updateGradeNode()
        except Exception as e:
            IECore.msg(
                IECore.Msg.Level.Warning,
                "GST_GradientEditor",
                f"Failed to load preset: {e}",
            )
            self._initDefaultColors()

    def _updateGradeNode(self):
        """Update the connected Grade/ColorLookup node with current gradient."""
        if self._gradeNode is None:
            return

        try:
            sorted_colors = sorted(self._colorList, key=lambda c: c["position"])

            if hasattr(self._gradeNode, "colorLookup"):
                # For ColorLookup nodes, set the curve
                color_lookup = self._gradeNode["colorLookup"]
                for channel_idx, channel in enumerate(
                    ["red", "green", "blue", "alpha"]
                ):
                    points = []
                    for color in sorted_colors:
                        points.append((color["position"], color["color"][channel_idx]))

                    # Build curve string for ColorLookup
                    curve_parts = []
                    for pos, val in points:
                        curve_parts.append(f"{pos} {val}")
                    curve_str = " ".join(curve_parts)

                    if channel_idx == 0:
                        color_lookup["red"].setValue(curve_str)
                    elif channel_idx == 1:
                        color_lookup["green"].setValue(curve_str)
                    elif channel_idx == 2:
                        color_lookup["blue"].setValue(curve_str)
                    elif channel_idx == 3:
                        color_lookup["alpha"].setValue(curve_str)

            elif hasattr(self._gradeNode, "multiply"):
                # For Grade nodes, compute average color as multiply
                avg_r = sum(c["color"][0] for c in sorted_colors) / len(sorted_colors)
                avg_g = sum(c["color"][1] for c in sorted_colors) / len(sorted_colors)
                avg_b = sum(c["color"][2] for c in sorted_colors) / len(sorted_colors)
                self._gradeNode["multiply"].setValue(
                    imath.Color4f(avg_r, avg_g, avg_b, 1.0)
                )
        except Exception as e:
            IECore.msg(
                IECore.Msg.Level.Warning,
                "GST_GradientEditor",
                f"Failed to update grade node: {e}",
            )


# Register metadata for the widget
Gaffer.Metadata.registerValue(
    GST_GradientEditor,
    "description",
    """
Interactive gradient editor for Gaffer.

Provides a visual interface for creating and editing color gradients
with draggable handles, HSV sliders, and preset management.

Connect to a Grade or ColorLookup node to apply the gradient.

Ported from Nuke Survival Toolkit.
    """,
)
