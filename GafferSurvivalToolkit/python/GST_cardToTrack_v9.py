##############################################################################################

# GST_CardToTrack_v9 — Enhanced 3D card to 2D track with matrix output
# Ported from Nuke Survival Toolkit NST_cardToTrack_v9
#
# Extended version that also computes transform matrix components
# (translate, rotate, scale) for roto workflows, plus Euler flip detection.
#
# Implementation: Gaffer.ComputeNode with V2f/V3f/M44f output plugs.

import Gaffer
import GafferScene
import IECore
import imath
import math


class GST_CardToTrack_v9(Gaffer.ComputeNode):
    """Project 3D card corners through camera with matrix output."""

    def __init__(self, name="GST_CardToTrack_v9"):
        Gaffer.ComputeNode.__init__(self, name)

        # Input scene
        self["in"] = GafferScene.ScenePlug()

        # Configuration
        self["cameraPath"] = Gaffer.StringPlug(defaultValue="")
        self["cardPath"] = Gaffer.StringPlug(defaultValue="")
        self["formatWidth"] = Gaffer.IntPlug(defaultValue=1920)
        self["formatHeight"] = Gaffer.IntPlug(defaultValue=1080)
        self["cardWidth"] = Gaffer.FloatPlug(defaultValue=1.0)
        self["cardHeight"] = Gaffer.FloatPlug(defaultValue=1.0)

        # Output corner positions (2D screen space)
        self["to1"] = Gaffer.V2fPlug(direction=Gaffer.Plug.Direction.Out)
        self["to2"] = Gaffer.V2fPlug(direction=Gaffer.Plug.Direction.Out)
        self["to3"] = Gaffer.V2fPlug(direction=Gaffer.Plug.Direction.Out)
        self["to4"] = Gaffer.V2fPlug(direction=Gaffer.Plug.Direction.Out)

        # From positions (reference frame)
        self["from1"] = Gaffer.V2fPlug(defaultValue=imath.V2f(0, 0))
        self["from2"] = Gaffer.V2fPlug(defaultValue=imath.V2f(1920, 0))
        self["from3"] = Gaffer.V2fPlug(defaultValue=imath.V2f(1920, 1080))
        self["from4"] = Gaffer.V2fPlug(defaultValue=imath.V2f(0, 1080))

        # Transform matrix outputs (for roto workflows)
        self["outTranslate"] = Gaffer.V2fPlug(direction=Gaffer.Plug.Direction.Out)
        self["outRotate"] = Gaffer.V3fPlug(direction=Gaffer.Plug.Direction.Out)
        self["outScale"] = Gaffer.V2fPlug(direction=Gaffer.Plug.Direction.Out)
        self["outMatrix"] = Gaffer.M44fPlug(direction=Gaffer.Plug.Direction.Out)

        # Euler flip detection
        self["eulerFlipWarning"] = Gaffer.BoolPlug(direction=Gaffer.Plug.Direction.Out)

    def affects(self, input):
        outputs = Gaffer.ComputeNode.affects(self, input)

        if input in (
            self["in"],
            self["cameraPath"],
            self["cardPath"],
            self["formatWidth"],
            self["formatHeight"],
            self["cardWidth"],
            self["cardHeight"],
        ):
            outputs.append(self["to1"])
            outputs.append(self["to2"])
            outputs.append(self["to3"])
            outputs.append(self["to4"])
            outputs.append(self["outTranslate"])
            outputs.append(self["outRotate"])
            outputs.append(self["outScale"])
            outputs.append(self["outMatrix"])
            outputs.append(self["eulerFlipWarning"])

        return outputs

    def hash(self, output, context, h):
        if output in (
            self["to1"],
            self["to2"],
            self["to3"],
            self["to4"],
            self["outTranslate"],
            self["outRotate"],
            self["outScale"],
            self["outMatrix"],
            self["eulerFlipWarning"],
        ):
            self["in"].hash(h)
            self["cameraPath"].hash(h)
            self["cardPath"].hash(h)
            self["formatWidth"].hash(h)
            self["formatHeight"].hash(h)
            self["cardWidth"].hash(h)
            self["cardHeight"].hash(h)
            h.append(context.getFrame())

    def _computeCardCorners(self, card_matrix, card_w, card_h):
        """Compute 4 card corners in world space."""
        corners_local = [
            imath.V3f(-card_w * 0.5, -card_h * 0.5, 0),
            imath.V3f(card_w * 0.5, -card_h * 0.5, 0),
            imath.V3f(card_w * 0.5, card_h * 0.5, 0),
            imath.V3f(-card_w * 0.5, card_h * 0.5, 0),
        ]
        return [card_matrix * imath.V4f(c.x, c.y, c.z, 1.0) for c in corners_local]

    def _projectToScreen(self, world_to_cam, world_point, width, height):
        """Project world point to screen coordinates."""
        cam_point = world_to_cam * world_point
        if cam_point.w == 0 or cam_point.z <= 0:
            return imath.V2f(0, 0)

        x = cam_point.x / cam_point.z
        y = cam_point.y / cam_point.z

        screen_x = (x * 0.5 + 0.5) * width
        screen_y = (1.0 - (y * 0.5 + 0.5)) * height
        return imath.V2f(screen_x, screen_y)

    def _extractEulerAngles(self, matrix):
        """Extract Euler angles (XYZ order) from rotation matrix."""
        # Remove translation
        rot = imath.M44f()
        for i in range(3):
            for j in range(3):
                rot[i][j] = matrix[i][j]

        # Normalize rows
        for i in range(3):
            length = math.sqrt(sum(rot[i][j] ** 2 for j in range(3)))
            if length > 0:
                for j in range(3):
                    rot[i][j] /= length

        # Extract Euler angles (XYZ order)
        sy = math.sqrt(rot[0][0] ** 2 + rot[1][0] ** 2)
        singular = sy < 1e-6

        if not singular:
            rx = math.atan2(rot[2][1], rot[2][2])
            ry = math.atan2(-rot[2][0], sy)
            rz = math.atan2(rot[1][0], rot[0][0])
        else:
            rx = math.atan2(-rot[1][2], rot[1][1])
            ry = math.atan2(-rot[2][0], sy)
            rz = 0

        return imath.V3f(math.degrees(rx), math.degrees(ry), math.degrees(rz))

    def _checkEulerFlip(self, matrix):
        """Detect if Euler angles have flipped (gimbal lock proximity)."""
        sy = math.sqrt(matrix[0][0] ** 2 + matrix[1][0] ** 2)
        return sy < 1e-6  # Near gimbal lock

    def _buildTransformMatrix(self, from_corners, to_corners):
        """Build a 4x4 transform from corner correspondences."""
        # Compute center points
        from_center = sum(from_corners, imath.V2f(0)) / 4.0
        to_center = sum(to_corners, imath.V2f(0)) / 4.0

        # Compute scale from average edge length ratio
        def edge_length(corners):
            d1 = (corners[1] - corners[0]).length()
            d2 = (corners[2] - corners[1]).length()
            d3 = (corners[3] - corners[2]).length()
            d4 = (corners[0] - corners[3]).length()
            return (d1 + d2 + d3 + d4) / 4.0

        from_len = edge_length(from_corners)
        to_len = edge_length(to_corners)
        scale = to_len / from_len if from_len > 0 else 1.0

        # Build matrix
        matrix = imath.M44f()
        matrix[0][0] = scale
        matrix[1][1] = scale
        matrix[3][0] = to_center.x - from_center.x * scale
        matrix[3][1] = to_center.y - from_center.y * scale

        return matrix

    def compute(self, plug, context):
        outputs = (
            self["to1"],
            self["to2"],
            self["to3"],
            self["to4"],
            self["outTranslate"],
            self["outRotate"],
            self["outScale"],
            self["outMatrix"],
            self["eulerFlipWarning"],
        )
        if plug not in outputs:
            return

        width = self["formatWidth"].getValue()
        height = self["formatHeight"].getValue()
        card_w = self["cardWidth"].getValue()
        card_h = self["cardHeight"].getValue()

        # Get camera world-to-camera transform
        camera_path_str = self["cameraPath"].getValue()
        if not camera_path_str:
            plug.setValue(
                imath.V2f(0, 0)
                if plug
                in (
                    self["to1"],
                    self["to2"],
                    self["to3"],
                    self["to4"],
                    self["outTranslate"],
                    self["outScale"],
                )
                else imath.M44f()
                if plug == self["outMatrix"]
                else imath.V3f(0)
                if plug == self["outRotate"]
                else False
            )
            return

        camera_path = GafferScene.ScenePlug.stringToPath(camera_path_str)
        camera_matrix = self["in"].transform(camera_path)
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

        # Compute corners
        corners_world = self._computeCardCorners(card_matrix, card_w, card_h)
        screen_corners = [
            self._projectToScreen(world_to_cam, cw, width, height)
            for cw in corners_world
        ]

        # Set corner outputs
        corner_map = {self["to1"]: 0, self["to2"]: 1, self["to3"]: 2, self["to4"]: 3}
        if plug in corner_map:
            plug.setValue(screen_corners[corner_map[plug]])
            return

        # Compute transform matrix
        from_corners = [
            self["from1"].getValue(),
            self["from2"].getValue(),
            self["from3"].getValue(),
            self["from4"].getValue(),
        ]
        matrix = self._buildTransformMatrix(from_corners, screen_corners)

        if plug == self["outMatrix"]:
            plug.setValue(matrix)
            return

        if plug == self["outTranslate"]:
            plug.setValue(imath.V2f(matrix[3][0], matrix[3][1]))
            return

        if plug == self["outScale"]:
            plug.setValue(imath.V2f(matrix[0][0], matrix[1][1]))
            return

        if plug == self["outRotate"]:
            euler = self._extractEulerAngles(matrix)
            plug.setValue(euler)
            return

        if plug == self["eulerFlipWarning"]:
            plug.setValue(self._checkEulerFlip(matrix))
            return


IECore.registerRunTimeTyped(GST_CardToTrack_v9, Gaffer.ComputeNode.staticTypeId())

Gaffer.Metadata.registerNode(
    GST_CardToTrack_v9,
    "description",
    """
Project 3D card corners through camera with matrix output.

Extended version that also computes transform matrix components
(translate, rotate, scale) for roto workflows.

Ported from Nuke Survival Toolkit.
    """,
    "in",
    "The input scene.",
    "cameraPath",
    "Path to the camera.",
    "cardPath",
    "Path to the card.",
    "formatWidth",
    "Output format width.",
    "formatHeight",
    "Output format height.",
    "cardWidth",
    "Card width in world units.",
    "cardHeight",
    "Card height in world units.",
    "to1",
    "Corner 1 screen position.",
    "to2",
    "Corner 2 screen position.",
    "to3",
    "Corner 3 screen position.",
    "to4",
    "Corner 4 screen position.",
    "outTranslate",
    "Computed translation.",
    "outRotate",
    "Computed rotation (Euler XYZ in degrees).",
    "outScale",
    "Computed scale.",
    "outMatrix",
    "Full 4x4 transform matrix.",
    "eulerFlipWarning",
    "True when near gimbal lock.",
    "layout:section:Scene.label",
    "Scene",
    "layout:section:Output.label",
    "Output",
    "layout:section:Matrix.label",
    "Matrix Output",
    "cameraPath.layout:section",
    "Scene",
    "cardPath.layout:section",
    "Scene",
    "formatWidth.layout:section",
    "Output",
    "formatHeight.layout:section",
    "Output",
    "cardWidth.layout:section",
    "Output",
    "cardHeight.layout:section",
    "Output",
    "to1.layout:section",
    "Output",
    "to2.layout:section",
    "Output",
    "to3.layout:section",
    "Output",
    "to4.layout:section",
    "Output",
    "outTranslate.layout:section",
    "Matrix Output",
    "outRotate.layout:section",
    "Matrix Output",
    "outScale.layout:section",
    "Matrix Output",
    "outMatrix.layout:section",
    "Matrix Output",
    "eulerFlipWarning.layout:section",
    "Matrix Output",
)
