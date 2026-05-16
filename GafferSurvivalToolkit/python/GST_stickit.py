##############################################################################################

# GST_stickit — Surface projection / motion transfer assistant
# Ported from Nuke Survival Toolkit NST_stickit by Mads Hagbarth Damsbo
#
# StickIt helps you stick elements to surfaces by using tracking data
# from a CameraTracker node to solve 2D transforms, cornerpins, rotos,
# and splinewarps.
#
# The core algorithm:
#   1. Export 2D tracking features from a CameraTracker
#   2. For each target point, find the 3 nearest tracking features
#   3. Triangulate motion using distance-weighted interpolation
#   4. Apply solved motion to selected nodes (Transform, CornerPin, Roto, etc.)
#
# In Gaffer, this is implemented as a TaskNode that:
#   - Takes tracking data as input (JSON or plug-based)
#   - Computes motion transfer using triangulation
#   - Outputs solved positions for downstream use

import Gaffer
import GafferImage
import GafferDispatch
import GafferScene
import IECore
import imath
import math


class GST_StickIt(GafferDispatch.TaskNode):
    """Surface projection / motion transfer using tracking data triangulation."""

    def __init__(self, name="GST_StickIt"):
        GafferDispatch.TaskNode.__init__(self, name)

        # --- Tracking data input ---
        self["trackingDataFile"] = Gaffer.StringPlug(defaultValue="")
        self["trackingDataJSON"] = Gaffer.StringPlug(defaultValue="{}")

        # --- Frame range ---
        self["refFrame"] = Gaffer.IntPlug(defaultValue=1)
        self["firstFrame"] = Gaffer.IntPlug(defaultValue=1)
        self["lastFrame"] = Gaffer.IntPlug(defaultValue=100)

        # --- Solve method ---
        self["solveMethod"] = Gaffer.StringPlug(defaultValue="local")

        # --- Target points (positions to solve for) ---
        # Stored as JSON: [{"name": "point1", "x": 100, "y": 200}, ...]
        self["targetPoints"] = Gaffer.StringPlug(defaultValue="[]")

        # --- Output ---
        self["outputFile"] = Gaffer.StringPlug(defaultValue="")
        self["solvedData"] = Gaffer.StringPlug(
            direction=Gaffer.Plug.Direction.Out, defaultValue="{}"
        )

        # --- Assist options ---
        self["appendAnimation"] = Gaffer.BoolPlug(defaultValue=False)
        self["assistStep"] = Gaffer.BoolPlug(defaultValue=False)
        self["assistStepSize"] = Gaffer.IntPlug(defaultValue=10)

    def requiresSequenceExecution(self):
        return True

    def execute(self):
        """Execute motion transfer across the frame range."""
        import json

        first = self["firstFrame"].getValue()
        last = self["lastFrame"].getValue()
        ref = self["refFrame"].getValue()
        solve_method = self["solveMethod"].getValue()

        # Load tracking data
        tracking_data = self._loadTrackingData()
        if not tracking_data:
            IECore.msg(
                IECore.Msg.Level.Error,
                "GST_StickIt",
                "No tracking data provided. Connect tracking data or specify a file.",
            )
            return

        # Load target points
        target_points = json.loads(self["targetPoints"].getValue() or "[]")
        if not target_points:
            IECore.msg(
                IECore.Msg.Level.Warning,
                "GST_StickIt",
                "No target points defined. Add points to solve for.",
            )
            return

        # Build frame-indexed tracking data for fast lookup
        indexed_data = self._buildIndex(tracking_data)

        # Solve each target point
        results = {}
        for point in target_points:
            point_name = point.get("name", f"point_{len(results)}")
            init_x = point.get("x", 0)
            init_y = point.get("y", 0)

            solved_positions = self._solvePoint(
                init_x,
                init_y,
                ref,
                first,
                last,
                solve_method,
                tracking_data,
                indexed_data,
            )

            results[point_name] = solved_positions

        # Store results
        self["solvedData"].setValue(json.dumps(results))

        # Write to file if specified
        output_file = self["outputFile"].getValue()
        if output_file:
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
            IECore.msg(
                IECore.Msg.Level.Info,
                "GST_StickIt",
                f"Solved data written to {output_file}",
            )

        IECore.msg(
            IECore.Msg.Level.Info,
            "GST_StickIt",
            f"Solved {len(results)} points over {abs(last - first)} frames",
        )

    def _loadTrackingData(self):
        """Load tracking data from file or JSON plug."""
        import json

        # Try JSON plug first
        json_str = self["trackingDataJSON"].getValue()
        if json_str and json_str != "{}":
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Try file
        file_path = self["trackingDataFile"].getValue()
        if file_path:
            try:
                with open(file_path, "r") as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                IECore.msg(
                    IECore.Msg.Level.Error,
                    "GST_StickIt",
                    f"Failed to load tracking data from {file_path}: {e}",
                )

        return None

    def _buildIndex(self, tracking_data):
        """
        Build a frame-indexed lookup for tracking data.

        Input format: [[frame, x, y], [frame, x, y], ...] per track
        Output: {frame: [[x, y, track_index, first_frame, last_frame], ...]}
        """
        item_dict = {}
        for track_index, track in enumerate(tracking_data):
            if not track:
                continue
            first_frame = track[0][0]
            last_frame = track[-1][0]

            for entry in track:
                frame = entry[0]
                if frame not in item_dict:
                    item_dict[frame] = []
                item_dict[frame].append(
                    [
                        entry[1],
                        entry[2],  # x, y
                        track_index,
                        first_frame,
                        last_frame,
                    ]
                )

        return item_dict

    def _solvePoint(
        self,
        init_x,
        init_y,
        ref_frame,
        first,
        last,
        solve_method,
        tracking_data,
        indexed_data,
    ):
        """
        Solve motion for a single target point.

        Uses triangulation-based interpolation from nearby tracking features.
        """
        positions = [{"frame": ref_frame, "x": init_x, "y": init_y}]

        # Solve backwards
        temp_x, temp_y = init_x, init_y
        for frame in range(ref_frame - 1, first - 1, -1):
            ref_points = self._getAnimationList(
                tracking_data, indexed_data, frame, reverse=True
            )
            dx, dy = self._calculatePositionDelta(
                solve_method, ref_points, temp_x, temp_y
            )
            temp_x += dx
            temp_y += dy
            positions.append({"frame": frame, "x": temp_x, "y": temp_y})

        # Solve forwards
        temp_x, temp_y = init_x, init_y
        for frame in range(ref_frame, last):
            ref_points = self._getAnimationList(tracking_data, indexed_data, frame)
            dx, dy = self._calculatePositionDelta(
                solve_method, ref_points, temp_x, temp_y
            )
            temp_x += dx
            temp_y += dy
            positions.append({"frame": frame + 1, "x": temp_x, "y": temp_y})

        # Sort by frame
        positions.sort(key=lambda p: p["frame"])
        return positions

    def _getAnimationList(self, tracking_data, indexed_data, frame, reverse=False):
        """
        Get tracking features that have data at this frame and the next.

        Returns list of [this_frame_position, next_frame_position] pairs.
        """
        output = []
        if frame not in indexed_data:
            return output

        for item in indexed_data[frame]:
            x, y, track_idx, track_first, track_last = item
            if track_last > frame:
                # Find next frame position
                track = tracking_data[track_idx]
                for entry in track:
                    if entry[0] == frame + 1:
                        if reverse:
                            output.append(
                                [
                                    [frame + 1, entry[1], entry[2]],
                                    [frame, x, y],
                                ]
                            )
                        else:
                            output.append(
                                [
                                    [frame, x, y],
                                    [frame + 1, entry[1], entry[2]],
                                ]
                            )
                        break

        return output

    def _calculatePositionDelta(self, solve_method, ref_points, temp_x, temp_y):
        """
        Calculate motion delta using the specified solve method.

        Methods:
          - local: Distance-weighted interpolation from 3 nearest points
          - median: Median of all tracking feature deltas
          - average: Average of all tracking feature deltas
        """
        if len(ref_points) < 3:
            if len(ref_points) == 0:
                return (0.0, 0.0)
            # Use available points
            total_dx = sum(p[1][1] - p[0][1] for p in ref_points)
            total_dy = sum(p[1][2] - p[0][2] for p in ref_points)
            return (total_dx / len(ref_points), total_dy / len(ref_points))

        if solve_method == "local":
            return self._localInterpolation(ref_points, temp_x, temp_y)
        elif solve_method == "median":
            return self._medianInterpolation(ref_points)
        else:  # average
            return self._averageInterpolation(ref_points)

    def _localInterpolation(self, ref_points, temp_x, temp_y):
        """Distance-weighted interpolation from 3 nearest points."""
        # Calculate distances
        distances = []
        for point in ref_points:
            dx = point[0][1] - temp_x
            dy = point[0][2] - temp_y
            dist = math.sqrt(dx * dx + dy * dy) + 1  # +1 to avoid division by zero
            distances.append(dist)

        # Sort by distance
        sorted_indices = sorted(range(len(distances)), key=lambda i: distances[i])

        # Take 3 nearest
        indices = sorted_indices[:3]

        # Calculate weights (inverse distance)
        weights = [1.0 / distances[i] for i in indices]
        total_weight = sum(weights)

        # Interpolate
        dx_total = 0.0
        dy_total = 0.0
        for i, idx in enumerate(indices):
            w = weights[i] / total_weight
            dx_total += (ref_points[idx][1][1] - ref_points[idx][0][1]) * w
            dy_total += (ref_points[idx][1][2] - ref_points[idx][0][2]) * w

        return (dx_total, dy_total)

    def _medianInterpolation(self, ref_points):
        """Median of all tracking feature deltas."""
        dx_list = [p[1][1] - p[0][1] for p in ref_points]
        dy_list = [p[1][2] - p[0][2] for p in ref_points]

        dx_list.sort()
        dy_list.sort()

        n = len(dx_list)
        if n % 2 == 1:
            return (dx_list[n // 2], dy_list[n // 2])
        else:
            return (
                (dx_list[n // 2 - 1] + dx_list[n // 2]) / 2,
                (dy_list[n // 2 - 1] + dy_list[n // 2]) / 2,
            )

    def _averageInterpolation(self, ref_points):
        """Average of all tracking feature deltas."""
        dx_total = sum(p[1][1] - p[0][1] for p in ref_points)
        dy_total = sum(p[1][2] - p[0][2] for p in ref_points)
        count = max(len(ref_points), 1)
        return (dx_total / count, dy_total / count)


# Register the node type
IECore.registerRunTimeTyped(GST_StickIt, GafferDispatch.TaskNode.staticTypeId())

# Register metadata for UI
Gaffer.Metadata.registerNode(
    GST_StickIt,
    "description",
    """
Surface projection / motion transfer assistant.

Uses tracking data from a CameraTracker to solve 2D motion for
target points using triangulation-based interpolation.

Three solve methods available:
  - Local: Distance-weighted interpolation from 3 nearest tracks
  - Median: Median of all tracking feature deltas
  - Average: Average of all tracking feature deltas

Ported from Nuke Survival Toolkit.
    """,
    "trackingDataFile",
    """
    Path to JSON file containing tracking data.
    Format: [[[frame, x, y], ...], [[frame, x, y], ...], ...]
    """,
    "trackingDataJSON",
    """
    Inline JSON tracking data (overrides file if provided).
    """,
    "refFrame",
    """
    Reference frame where target points are defined.
    """,
    "firstFrame",
    """
    First frame to solve.
    """,
    "lastFrame",
    """
    Last frame to solve.
    """,
    "solveMethod",
    """
    Method for interpolating motion: local, median, or average.
    """,
    "solveMethod.presets",
    {"Local": "local", "Median": "median", "Average": "average"},
    "targetPoints",
    """
    JSON array of target points to solve for.
    Format: [{"name": "point1", "x": 100, "y": 200}, ...]
    """,
    "outputFile",
    """
    Optional file path to write solved data (JSON).
    """,
    "appendAnimation",
    """
    Append to existing animation instead of replacing.
    """,
    "assistStep",
    """
    Only solve within a step range around current frame.
    """,
    "assistStepSize",
    """
    Number of frames to solve around current frame when assistStep is enabled.
    """,
    # Plug categories
    "layout:section:Input.label",
    "Tracking Data",
    "layout:section:Range.label",
    "Frame Range",
    "layout:section:Solve.label",
    "Solve Settings",
    "layout:section:Output.label",
    "Output",
    "trackingDataFile.layout:section",
    "Tracking Data",
    "trackingDataJSON.layout:section",
    "Tracking Data",
    "refFrame.layout:section",
    "Frame Range",
    "firstFrame.layout:section",
    "Frame Range",
    "lastFrame.layout:section",
    "Frame Range",
    "solveMethod.layout:section",
    "Solve Settings",
    "targetPoints.layout:section",
    "Solve Settings",
    "outputFile.layout:section",
    "Output",
    "appendAnimation.layout:section",
    "Solve Settings",
    "assistStep.layout:section",
    "Solve Settings",
    "assistStepSize.layout:section",
    "Solve Settings",
)
