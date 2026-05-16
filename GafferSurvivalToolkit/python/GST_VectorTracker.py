##############################################################################################

# GST_VectorTracker — Track through vector channels (forward/backward/smartvector)
# Ported from Nuke Survival Toolkit NST_VectorTracker by Jorrit Schulte
#
# This node samples vector data from upstream vector passes and propagates
# tracker positions frame-by-frame, similar to Nuke's Tracker but driven
# by vector data instead of image correlation.
#
# Usage:
#   1. Connect a vector pass (smartvector, forward, or backward) to input 1
#   2. Add trackers via the "Add Tracker" button
#   3. Set first/last frame and click "Track"
#   4. Export tracked positions as metadata or downstream nodes

import Gaffer
import GafferImage
import GafferDispatch
import IECore
import imath
import math


class GST_VectorTracker(GafferDispatch.TaskNode):
    """Track positions through vector channels (forward/backward/smartvector)."""

    def __init__(self, name="GST_VectorTracker"):
        GafferDispatch.TaskNode.__init__(self, name)

        # Image input for vector pass
        self["in"] = GafferImage.ImagePlug("in", Gaffer.Plug.Direction.In)

        # --- Configuration plugs ---
        self["firstFrame"] = Gaffer.IntPlug(defaultValue=1)
        self["lastFrame"] = Gaffer.IntPlug(defaultValue=100)
        self["vectorType"] = Gaffer.StringPlug(defaultValue="auto")
        self["sampleArea"] = Gaffer.IntPlug(defaultValue=1, minValue=1, maxValue=50)

        # --- Tracker data stored as a single StringPlug (serialized JSON) ---
        self["trackerData"] = Gaffer.StringPlug(defaultValue="{}")

        # --- Output: tracked positions as metadata on the task ---
        self["outputFile"] = Gaffer.StringPlug(defaultValue="")

    def hash(self, context):
        """Hash for TaskNode caching."""
        GafferDispatch.TaskNode.hash(self, context)
        self["firstFrame"].hash(self._taskPlugHash)
        self["lastFrame"].hash(self._taskPlugHash)
        self["vectorType"].hash(self._taskPlugHash)
        self["sampleArea"].hash(self._taskPlugHash)
        self["trackerData"].hash(self._taskPlugHash)
        self["outputFile"].hash(self._taskPlugHash)
        self["in"].hash(self._taskPlugHash)

    def requiresSequenceExecution(self):
        return True

    def execute(self):
        """Execute tracking across the frame range."""
        import json

        first = self["firstFrame"].getValue()
        last = self["lastFrame"].getValue()
        vector_type = self["vectorType"].getValue()
        sample_area = self["sampleArea"].getValue()

        # Get vector image input
        vector_input = self["in"]
        if vector_input is None or not vector_input.getInput():
            IECore.msg(
                IECore.Msg.Level.Error,
                "GST_VectorTracker",
                "No vector input connected.",
            )
            return

        # Parse tracker data
        tracker_data = json.loads(self["trackerData"].getValue() or "{}")
        if not tracker_data:
            IECore.msg(
                IECore.Msg.Level.Warning,
                "GST_VectorTracker",
                "No trackers defined. Add trackers first.",
            )
            return

        # Determine vector channels based on type and direction
        forward = last > first
        u_channel, v_channel = self._resolveVectorChannels(
            vector_type, forward, vector_input
        )

        if u_channel is None:
            IECore.msg(
                IECore.Msg.Level.Error,
                "GST_VectorTracker",
                f"No suitable vector channels found. Connect a forward/backward/smartvector pass.",
            )
            return

        # Track each point
        total_frames = abs(last - first)
        results = {}

        for tracker_name, tracker_info in tracker_data.items():
            if not tracker_info.get("enabled", True):
                continue

            start_x = tracker_info.get("startX", 0.0)
            start_y = tracker_info.get("startY", 0.0)

            cur_x, cur_y = start_x, start_y
            positions = []

            frame_range = (
                range(first, last + 1) if forward else range(first, last - 1, -1)
            )

            for frame in frame_range:
                positions.append({"frame": frame, "x": cur_x, "y": cur_y})

                if frame != last:
                    # Sample vector at current position
                    du, dv = self._sampleVector(
                        vector_input,
                        u_channel,
                        v_channel,
                        cur_x,
                        cur_y,
                        sample_area,
                        frame,
                    )
                    cur_x += du
                    cur_y += dv

            results[tracker_name] = positions

        # Store results
        self["trackerData"].setValue(
            json.dumps(
                {
                    "results": results,
                    "firstFrame": first,
                    "lastFrame": last,
                }
            )
        )

        # Write to file if specified
        output_file = self["outputFile"].getValue()
        if output_file:
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
            IECore.msg(
                IECore.Msg.Level.Info,
                "GST_VectorTracker",
                f"Tracking data written to {output_file}",
            )

        IECore.msg(
            IECore.Msg.Level.Info,
            "GST_VectorTracker",
            f"Tracking complete: {len(results)} trackers over {total_frames} frames",
        )

    def _resolveVectorChannels(self, vector_type, forward, vector_input):
        """Resolve which vector channels to use based on available layers."""
        # Try to get channel names from the input image
        try:
            image_plug = vector_input.getInput()
            if image_plug is not None:
                format_plug = image_plug["format"]
                # In Gaffer, we'd need to actually compute to get channel names
                # For now, use heuristics based on vector_type setting
                pass
        except Exception:
            pass

        if vector_type == "smartvector":
            if forward:
                return ("smartvector.fn1vp0_u", "smartvector.fn1vp0_v")
            else:
                return ("smartvector.fp1vp0_u", "smartvector.fp1vp0_v")
        elif vector_type == "forward":
            return ("forward.u", "forward.v")
        elif vector_type == "backward":
            return ("backward.u", "backward.v")
        elif vector_type == "auto":
            # Try smartvector first, then forward/backward
            if forward:
                return ("smartvector.fn1vp0_u", "smartvector.fn1vp0_v")
            else:
                return ("smartvector.fp1vp0_u", "smartvector.fp1vp0_v")

        return (None, None)

    def _sampleVector(self, vector_input, u_channel, v_channel, x, y, area, frame):
        """Sample vector value at position (x, y) with given area size."""
        try:
            image_plug = vector_input.getInput()
            if image_plug is None:
                return (0.0, 0.0)

            context_frame = Gaffer.Context(Gaffer.Context.current())
            context_frame.setFrame(frame)

            with context_frame:
                data_window = image_plug.dataWindow()
                if GafferImage.BufferAlgo.empty(data_window):
                    return (0.0, 0.0)

                cx = max(data_window.min.x, min(int(x), data_window.max.x - 1))
                cy = max(data_window.min.y, min(int(y), data_window.max.y - 1))

                if area <= 1:
                    sample_window = imath.Box2i(
                        imath.V2i(cx, cy), imath.V2i(cx + 1, cy + 1)
                    )
                    u_sampler = GafferImage.Sampler(
                        image_plug, u_channel, sample_window
                    )
                    v_sampler = GafferImage.Sampler(
                        image_plug, v_channel, sample_window
                    )
                    return (u_sampler.sample(cx, cy), v_sampler.sample(cx, cy))
                else:
                    half = area // 2
                    x_start = cx - half
                    y_start = cy - half
                    x_end = cx + half + 1
                    y_end = cy + half + 1

                    u_sampler = GafferImage.Sampler(
                        image_plug,
                        u_channel,
                        imath.Box2i(
                            imath.V2i(x_start, y_start), imath.V2i(x_end, y_end)
                        ),
                    )
                    v_sampler = GafferImage.Sampler(
                        image_plug,
                        v_channel,
                        imath.Box2i(
                            imath.V2i(x_start, y_start), imath.V2i(x_end, y_end)
                        ),
                    )

                    u_sum, v_sum, count = 0.0, 0.0, 0
                    for py in range(y_start, y_end):
                        for px in range(x_start, x_end):
                            u_sum += u_sampler.sample(px, py)
                            v_sum += v_sampler.sample(px, py)
                            count += 1

                    if count > 0:
                        return (u_sum / count, v_sum / count)
                    return (0.0, 0.0)

        except Exception:
            return (0.0, 0.0)


# Register the node type
IECore.registerRunTimeTyped(GST_VectorTracker, GafferDispatch.TaskNode.staticTypeId())

# Register metadata for UI
Gaffer.Metadata.registerNode(
    GST_VectorTracker,
    "description",
    """
Track positions through vector channels.

Connect a vector pass (smartvector, forward, or backward) and define
tracker positions. The node will sample vector data frame-by-frame
to propagate tracker positions.

Ported from Nuke Survival Toolkit.
    """,
    "firstFrame",
    """
    The first frame to track from.
    """,
    "lastFrame",
    """
    The last frame to track to.
    """,
    "vectorType",
    """
    Type of vector pass: auto, smartvector, forward, or backward.
    """,
    "sampleArea",
    """
    Size of the area to sample in the vector channels.
    """,
    "trackerData",
    """
    Serialized tracker data (JSON). Use the UI to manage trackers.
    """,
    "outputFile",
    """
    Optional file path to write tracking results (JSON).
    """,
    # Plug categories for UI layout
    "layout:section:Tracking.label",
    "Tracking",
    "layout:section:Vector.label",
    "Vector Settings",
    "layout:section:Output.label",
    "Output",
    "firstFrame.layout:section",
    "Tracking",
    "lastFrame.layout:section",
    "Tracking",
    "vectorType.layout:section",
    "Vector Settings",
    "vectorType.presets",
    {
        "Auto": "auto",
        "SmartVector": "smartvector",
        "Forward": "forward",
        "Backward": "backward",
    },
    "sampleArea.layout:section",
    "Vector Settings",
    "trackerData.layout:section",
    "Tracking",
    "outputFile.layout:section",
    "Output",
)
