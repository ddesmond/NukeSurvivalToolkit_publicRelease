##############################################################################################

# GST_CardToTrack — Convert 3D card corners to 2D track points via camera
# Ported from Nuke Survival Toolkit NST_cardToTrack
#
# Projects the 4 corners of a 3D card through a camera to produce 2D
# cornerpin track points for each frame.
#
# Implementation: Gaffer.ComputeNode with V2f output plugs for each corner.
# Uses ScenePlug.transform() to get camera and card transforms, then
# projects 3D corners through the camera matrix to 2D screen space.

import Gaffer
import GafferScene
import IECore
import imath
import math


class GST_CardToTrack(Gaffer.ComputeNode):
    """Project 3D card corners through camera to 2D track points."""

    def __init__(self, name="GST_CardToTrack"):
        Gaffer.ComputeNode.__init__(self, name)

        # Input scene
        self["in"] = GafferScene.ScenePlug()

        # Configuration
        self["cameraPath"] = Gaffer.StringPlug(defaultValue="")
        self["cardPath"] = Gaffer.StringPlug(defaultValue="")
        self["firstFrame"] = Gaffer.IntPlug(defaultValue=1)
        self["lastFrame"] = Gaffer.IntPlug(defaultValue=100)
        self["formatWidth"] = Gaffer.IntPlug(defaultValue=1920)
        self["formatHeight"] = Gaffer.IntPlug(defaultValue=1080)

        # Output corner positions (2D screen space)
        self["to1"] = Gaffer.V2fPlug(direction=Gaffer.Plug.Direction.Out)
        self["to2"] = Gaffer.V2fPlug(direction=Gaffer.Plug.Direction.Out)
        self["to3"] = Gaffer.V2fPlug(direction=Gaffer.Plug.Direction.Out)
        self["to4"] = Gaffer.V2fPlug(direction=Gaffer.Plug.Direction.Out)

        # From positions (reference frame corners)
        self["from1"] = Gaffer.V2fPlug(defaultValue=imath.V2f(0, 0))
        self["from2"] = Gaffer.V2fPlug(defaultValue=imath.V2f(1920, 0))
        self["from3"] = Gaffer.V2fPlug(defaultValue=imath.V2f(1920, 1080))
        self["from4"] = Gaffer.V2fPlug(defaultValue=imath.V2f(0, 1080))

        # Card corner offsets in card local space (unit card)
        self["cardWidth"] = Gaffer.FloatPlug(defaultValue=1.0)
        self["cardHeight"] = Gaffer.FloatPlug(defaultValue=1.0)

    def affects(self, input):
        outputs = Gaffer.ComputeNode.affects(self, input)

        if input in (
            self["in"],
            self["cameraPath"],
            self["cardPath"],
            self["firstFrame"],
            self["lastFrame"],
            self["formatWidth"],
            self["formatHeight"],
            self["cardWidth"],
            self["cardHeight"],
        ):
            outputs.append(self["to1"])
            outputs.append(self["to2"])
            outputs.append(self["to3"])
            outputs.append(self["to4"])

        return outputs

    def hash(self, output, context, h):
        if output in (self["to1"], self["to2"], self["to3"], self["to4"]):
            self["in"].hash(h)
            self["cameraPath"].hash(h)
            self["cardPath"].hash(h)
            self["formatWidth"].hash(h)
            self["formatHeight"].hash(h)
            self["cardWidth"].hash(h)
            self["cardHeight"].hash(h)
            h.append(context.getFrame())

    def _projectPointToScreen(self, camera_matrix, point, width, height):
        """Project a 3D point through camera matrix to 2D screen coordinates."""
        # Transform point into camera space
        cam_point = camera_matrix * imath.V4f(point.x, point.y, point.z, 1.0)

        if cam_point.w == 0:
            return imath.V2f(0, 0)

        # Perspective divide
        x = cam_point.x / cam_point.w
        y = cam_point.y / cam_point.w

        # Convert to screen coordinates (Nuke-style: origin at top-left)
        screen_x = (x * 0.5 + 0.5) * width
        screen_y = (1.0 - (y * 0.5 + 0.5)) * height

        return imath.V2f(screen_x, screen_y)

    def _computeCardCorners(self, card_matrix, width, height):
        """Compute the 4 corners of the card in world space, then project."""
        hw, hh = width * 0.5, height * 0.5
        card_w = self["cardWidth"].getValue()
        card_h = self["cardHeight"].getValue()

        # Card corners in local space
        corners_local = [
            imath.V3f(-card_w * 0.5, -card_h * 0.5, 0),  # bottom-left
            imath.V3f(card_w * 0.5, -card_h * 0.5, 0),  # bottom-right
            imath.V3f(card_w * 0.5, card_h * 0.5, 0),  # top-right
            imath.V3f(-card_w * 0.5, card_h * 0.5, 0),  # top-left
        ]

        # Transform to world space
        return [card_matrix * imath.V4f(c.x, c.y, c.z, 1.0) for c in corners_local]

    def compute(self, plug, context):
        if plug not in (self["to1"], self["to2"], self["to3"], self["to4"]):
            return

        frame = context.getFrame()
        width = self["formatWidth"].getValue()
        height = self["formatHeight"].getValue()

        # Get camera world transform at this frame
        camera_path_str = self["cameraPath"].getValue()
        if not camera_path_str:
            plug.setValue(imath.V2f(0, 0))
            return

        camera_path = GafferScene.ScenePlug.stringToPath(camera_path_str)
        camera_matrix = self["in"].transform(camera_path)

        # Invert camera matrix to get world-to-camera transform
        try:
            world_to_cam = camera_matrix.inverse()
        except Exception:
            plug.setValue(imath.V2f(0, 0))
            return

        # Get card world transform
        card_path_str = self["cardPath"].getValue()
        if not card_path_str:
            plug.setValue(imath.V2f(0, 0))
            return

        card_path = GafferScene.ScenePlug.stringToPath(card_path_str)
        card_matrix = self["in"].transform(card_path)

        # Compute card corners in world space
        card_w = self["cardWidth"].getValue()
        card_h = self["cardHeight"].getValue()
        corners_local = [
            imath.V3f(-card_w * 0.5, -card_h * 0.5, 0),
            imath.V3f(card_w * 0.5, -card_h * 0.5, 0),
            imath.V3f(card_w * 0.5, card_h * 0.5, 0),
            imath.V3f(-card_w * 0.5, card_h * 0.5, 0),
        ]
        corners_world = [
            card_matrix * imath.V4f(c.x, c.y, c.z, 1.0) for c in corners_local
        ]

        # Project each corner through camera
        screen_corners = []
        for cw in corners_world:
            cam_point = world_to_cam * cw
            if cam_point.w == 0 or cam_point.z <= 0:
                screen_corners.append(imath.V2f(0, 0))
                continue

            x = cam_point.x / cam_point.z
            y = cam_point.y / cam_point.z

            # Simple perspective projection (assuming standard camera)
            screen_x = (x * 0.5 + 0.5) * width
            screen_y = (1.0 - (y * 0.5 + 0.5)) * height
            screen_corners.append(imath.V2f(screen_x, screen_y))

        # Set the appropriate output plug
        corner_index = {
            self["to1"]: 0,
            self["to2"]: 1,
            self["to3"]: 2,
            self["to4"]: 3,
        }[plug]

        plug.setValue(screen_corners[corner_index])


IECore.registerRunTimeTyped(GST_CardToTrack, Gaffer.ComputeNode.staticTypeId())

Gaffer.Metadata.registerNode(
    GST_CardToTrack,
    "description",
    """
Project 3D card corners through a camera to produce 2D track points.

Useful for converting 3D tracking data into 2D cornerpin data.

Ported from Nuke Survival Toolkit.
    """,
    "in",
    "The input scene containing the camera and card.",
    "cameraPath",
    "Path to the camera in the scene.",
    "cardPath",
    "Path to the card in the scene.",
    "firstFrame",
    "First frame to process.",
    "lastFrame",
    "Last frame to process.",
    "formatWidth",
    "Output format width in pixels.",
    "formatHeight",
    "Output format height in pixels.",
    "to1",
    "Screen position of corner 1 (bottom-left).",
    "to2",
    "Screen position of corner 2 (bottom-right).",
    "to3",
    "Screen position of corner 3 (top-right).",
    "to4",
    "Screen position of corner 4 (top-left).",
    "layout:section:Scene.label",
    "Scene",
    "layout:section:Output.label",
    "Output",
    "layout:section:Card.label",
    "Card Dimensions",
    "cameraPath.layout:section",
    "Scene",
    "cardPath.layout:section",
    "Scene",
    "firstFrame.layout:section",
    "Output",
    "lastFrame.layout:section",
    "Output",
    "formatWidth.layout:section",
    "Output",
    "formatHeight.layout:section",
    "Output",
    "to1.layout:section",
    "Output",
    "to2.layout:section",
    "Output",
    "to3.layout:section",
    "Output",
    "to4.layout:section",
    "Output",
    "cardWidth.layout:section",
    "Card Dimensions",
    "cardHeight.layout:section",
    "Card Dimensions",
)
