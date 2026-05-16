##############################################################################################

# GST_menu.py — Main menu registration for Gaffer Survival Toolkit
# This script runs on Gaffer GUI startup and registers all GST tools into the node menus.
# AUTO-GENERATED — covers 250+ tools across all categories.

import sys
from pathlib import Path

# Add GST python modules to path
GST_root = Path(__file__).parent.parent.parent
GST_pythonPath = (GST_root / "python").as_posix()
if GST_pythonPath not in sys.path:
    sys.path.insert(0, GST_pythonPath)

import Gaffer
import GafferImage
import GafferScene
import GafferDispatch
import GafferUI
import IECore

import GST_helper

# Import Python-backed nodes (may fail if dependencies missing)
GST_PythonNodes = {}
try:
    from GST_ID_Extractor import GST_IDExtractor

    GST_PythonNodes["ID_Extractor"] = GST_IDExtractor
except ImportError as e:
    IECore.msg(
        IECore.Msg.Level.Warning, "GST_menu", f"Could not load GST_IDExtractor: {e}"
    )

try:
    from GST_VectorTracker import GST_VectorTracker

    GST_PythonNodes["VectorTracker"] = GST_VectorTracker
except ImportError as e:
    IECore.msg(
        IECore.Msg.Level.Warning, "GST_menu", f"Could not load GST_VectorTracker: {e}"
    )

try:
    from GST_cardToTrack import GST_CardToTrack

    GST_PythonNodes["CardToTrack"] = GST_CardToTrack
except ImportError as e:
    IECore.msg(
        IECore.Msg.Level.Warning, "GST_menu", f"Could not load GST_CardToTrack: {e}"
    )

try:
    from GST_cardToTrack_v9 import GST_CardToTrack_v9

    GST_PythonNodes["CardToTrack_v9"] = GST_CardToTrack_v9
except ImportError as e:
    IECore.msg(
        IECore.Msg.Level.Warning, "GST_menu", f"Could not load GST_cardToTrack_v9: {e}"
    )

try:
    from GST_stickit import GST_StickIt

    GST_PythonNodes["StickIt"] = GST_StickIt
except ImportError as e:
    IECore.msg(IECore.Msg.Level.Warning, "GST_menu", f"Could not load GST_StickIt: {e}")

##############################################################################################
### Documentation configuration
##############################################################################################

GST_helper.GST_DOCS_ONLINE_URL = (
    "https://github.com/ddesmond/NukeSurvivalToolkit_publicRelease/wiki"
)
GST_helper.GST_DOCS_ONLINE_TIMEOUT_SECONDS = 1.5
GST_helper.GST_DOCS_PDF_NAME = "GafferSurvivalToolkit_Documentation_Release_v1.0.0.pdf"
GST_helper.GST_DOCS_OFFLINE_INDEX = Path("GST_Documentation/index.html")

##############################################################################################
### Helper functions
##############################################################################################


def __createNode(menu, nodeClass, icon=""):
    """Create a node and add it to the current script."""
    script = menu.ancestor(GafferUI.ScriptWindow).scriptNode()
    node = nodeClass()
    script.addChild(node)
    GafferUI.NodeEditor.acquire(node)


def __createNodeWithPath(menu, nodeClass, gfrPath):
    """Load a .gfr file and fix file paths."""
    script = menu.ancestor(GafferUI.ScriptWindow).scriptNode()
    GST_helper.filepathLoadReference(script, gfrPath)


def __runFunction(menu, func):
    """Execute a callable (for documentation helpers, etc.)."""
    func()


def __registerNode(menuDefinition, path, nodeClass, icon="", shortcut=""):
    """Register a node class in the menu."""
    menuDefinition.append(
        f"/{path}",
        {
            "command": lambda menu: __createNode(menu, nodeClass),
            "icon": icon,
            "shortCut": shortcut,
        },
    )


def __registerGFR(menuDefinition, path, gfrPath, icon="", shortcut=""):
    """Register a .gfr file in the menu."""
    fullPath = (GST_root / gfrPath).as_posix()
    menuDefinition.append(
        f"/{path}",
        {
            "command": lambda menu: __createNodeWithPath(menu, None, fullPath),
            "icon": icon,
            "shortCut": shortcut,
        },
    )


def __registerAction(menuDefinition, path, func, icon="", shortcut=""):
    """Register a callable action in the menu."""
    menuDefinition.append(
        f"/{path}",
        {
            "command": lambda menu: __runFunction(menu, func),
            "icon": icon,
            "shortCut": shortcut,
        },
    )


def __registerSubmenu(menuDefinition, path, subMenuFunc):
    """Register a submenu with its own items."""
    menuDefinition.append(
        f"/{path}",
        {
            "subMenu": subMenuFunc,
        },
    )


##############################################################################################
### Documentation menu
##############################################################################################


def __documentationMenu():
    menuDefinition = IECore.MenuDefinition()
    __registerAction(
        menuDefinition, "Wiki/Docs (Auto)", GST_helper.openGSTDocumentationDefault
    )
    __registerAction(
        menuDefinition, "Wiki (Online)", GST_helper.openGSTDocumentationOnline
    )
    __registerAction(
        menuDefinition, "Wiki (Offline)", GST_helper.openGSTDocumentationOffline
    )
    __registerAction(menuDefinition, "Docs (PDF)", GST_helper.openGSTDocumentationPDF)
    return menuDefinition


##############################################################################################
### Image menu
##############################################################################################


def __imageMenu():
    menuDefinition = IECore.MenuDefinition()
    __registerNode(menuDefinition, "ImageReader", GafferImage.ImageReader)
    __registerNode(menuDefinition, "ImageWriter", GafferImage.ImageWriter)
    __registerNode(menuDefinition, "Constant", GafferImage.Constant)
    __registerNode(menuDefinition, "Ramp", GafferImage.Ramp)
    __registerNode(menuDefinition, "Noise", GafferImage.Noise)
    __registerNode(menuDefinition, "Grade", GafferImage.Grade)
    __registerNode(menuDefinition, "Shuffle", GafferImage.Shuffle)
    __registerNode(menuDefinition, "CopyChannels", GafferImage.CopyChannels)
    __registerNode(menuDefinition, "DeleteChannels", GafferImage.DeleteChannels)
    __registerNode(menuDefinition, "Merge", GafferImage.Merge)
    __registerNode(menuDefinition, "Mix", GafferImage.Mix)
    __registerNode(menuDefinition, "Blur", GafferImage.Blur)
    __registerNode(menuDefinition, "Dilate", GafferImage.Dilate)
    __registerNode(menuDefinition, "Erode", GafferImage.Erode)
    __registerNode(menuDefinition, "Median", GafferImage.Median)
    __registerNode(menuDefinition, "VectorWarp", GafferImage.VectorWarp)
    __registerNode(menuDefinition, "Crop", GafferImage.Crop)
    __registerNode(menuDefinition, "Resize", GafferImage.Resize)
    __registerNode(menuDefinition, "Resample", GafferImage.Resample)
    __registerNode(menuDefinition, "Offset", GafferImage.Offset)
    __registerNode(menuDefinition, "Mirror", GafferImage.Mirror)
    __registerNode(menuDefinition, "ImageTransform", GafferImage.ImageTransform)
    __registerNode(menuDefinition, "Clamp", GafferImage.Clamp)
    __registerNode(menuDefinition, "ColorSpace", GafferImage.ColorSpace)
    __registerNode(menuDefinition, "DisplayTransform", GafferImage.DisplayTransform)
    __registerNode(menuDefinition, "ContactSheet", GafferImage.ContactSheet)
    __registerNode(menuDefinition, "DeepMerge", GafferImage.DeepMerge)
    __registerNode(menuDefinition, "DeepHoldout", GafferImage.DeepHoldout)
    __registerNode(menuDefinition, "DeepRecolor", GafferImage.DeepRecolor)
    __registerNode(menuDefinition, "DeepSampler", GafferImage.DeepSampler)
    __registerNode(menuDefinition, "DeepToFlat", GafferImage.DeepToFlat)
    __registerNode(menuDefinition, "DeepState", GafferImage.DeepState)
    __registerNode(menuDefinition, "DeepSlice", GafferImage.DeepSlice)
    __registerNode(menuDefinition, "DeepTidy", GafferImage.DeepTidy)
    __registerNode(menuDefinition, "FlatToDeep", GafferImage.FlatToDeep)
    __registerNode(menuDefinition, "ImageStats", GafferImage.ImageStats)
    __registerNode(menuDefinition, "ImageSampler", GafferImage.ImageSampler)
    __registerNode(menuDefinition, "Expression", Gaffer.Expression)
    __registerNode(menuDefinition, "TimeWarp", Gaffer.TimeWarp)
    __registerGFR(menuDefinition, "LabelFromRead", "gfr/Image/LabelFromRead.gfr")
    return menuDefinition


def __cgMenu():
    menuDefinition = IECore.MenuDefinition()

    __registerGFR(menuDefinition, "C44Kernel", "gfr/CG/C44Kernel.gfr")
    __registerGFR(menuDefinition, "CameraNormals", "gfr/CG/CameraNormals.gfr")
    __registerGFR(menuDefinition, "ConvertPNZ", "gfr/CG/ConvertPNZ.gfr")
    __registerGFR(menuDefinition, "Emission", "gfr/CG/Emission.gfr")
    __registerGFR(menuDefinition, "EnvReflect_bb", "gfr/CG/EnvReflect_bb.gfr")
    __registerGFR(menuDefinition, "GlueP", "gfr/CG/GlueP.gfr")
    __registerGFR(menuDefinition, "LightSwitch", "gfr/CG/LightSwitch.gfr")
    __registerGFR(menuDefinition, "LightSwitchPuppet", "gfr/CG/LightSwitchPuppet.gfr")
    __registerGFR(menuDefinition, "NReflection", "gfr/CG/NReflection.gfr")
    __registerGFR(menuDefinition, "Noise3D", "gfr/CG/Noise3D.gfr")
    __registerGFR(menuDefinition, "Noise4D", "gfr/CG/Noise4D.gfr")
    __registerGFR(menuDefinition, "NormalsRotate", "gfr/CG/NormalsRotate.gfr")
    __registerGFR(menuDefinition, "P2N", "gfr/CG/P2N.gfr")
    __registerGFR(menuDefinition, "P2Z", "gfr/CG/P2Z.gfr")
    __registerGFR(menuDefinition, "PNoiseAdvanced", "gfr/CG/PNoiseAdvanced.gfr")
    __registerGFR(menuDefinition, "PProject", "gfr/CG/PProject.gfr")
    __registerGFR(menuDefinition, "PRamp", "gfr/CG/PRamp.gfr")
    __registerGFR(menuDefinition, "PosMatte", "gfr/CG/PosMatte.gfr")
    __registerGFR(menuDefinition, "PosPattern", "gfr/CG/PosPattern.gfr")
    __registerGFR(menuDefinition, "PosProjection", "gfr/CG/PosProjection.gfr")
    __registerGFR(menuDefinition, "ReProject3D", "gfr/CG/ReProject3D.gfr")
    __registerGFR(menuDefinition, "RelightSimple", "gfr/CG/RelightSimple.gfr")
    __registerGFR(menuDefinition, "Relight_bb", "gfr/CG/Relight_bb.gfr")
    __registerGFR(menuDefinition, "SimpleSSS", "gfr/CG/SimpleSSS.gfr")
    __registerGFR(menuDefinition, "UVMapper", "gfr/CG/UVMapper.gfr")
    __registerGFR(menuDefinition, "Z2N", "gfr/CG/Z2N.gfr")
    __registerGFR(menuDefinition, "Z2P", "gfr/CG/Z2P.gfr")
    __registerGFR(menuDefinition, "aPmatte", "gfr/CG/aPmatte.gfr")
    __registerGFR(menuDefinition, "aeRefracTHOR", "gfr/CG/aeRefracTHOR.gfr")
    __registerGFR(menuDefinition, "apDirLight", "gfr/CG/apDirLight.gfr")
    __registerGFR(menuDefinition, "apFresnel", "gfr/CG/apFresnel.gfr")

    return menuDefinition


def __channelMenu():
    menuDefinition = IECore.MenuDefinition()

    # Python-backed nodes
    if "ID_Extractor" in GST_PythonNodes:
        __registerNode(menuDefinition, "ID_Extractor", GST_PythonNodes["ID_Extractor"])

    __registerGFR(menuDefinition, "BinaryAlpha", "gfr/Channel/BinaryAlpha.gfr")
    __registerGFR(menuDefinition, "ChannelCombiner", "gfr/Channel/ChannelCombiner.gfr")
    __registerGFR(menuDefinition, "ChannelControl", "gfr/Channel/ChannelControl.gfr")
    __registerGFR(menuDefinition, "ChannelCreator", "gfr/Channel/ChannelCreator.gfr")
    __registerGFR(menuDefinition, "IDExtractor_gfr", "gfr/Channel/IDExtractor.gfr")
    __registerGFR(
        menuDefinition, "InjectMatteChannel", "gfr/Channel/InjectMatteChannel.gfr"
    )
    __registerGFR(menuDefinition, "renameChannels", "gfr/Channel/renameChannels.gfr")
    __registerGFR(menuDefinition, "streamCart", "gfr/Channel/streamCart.gfr")

    return menuDefinition


def __colorMenu():
    menuDefinition = IECore.MenuDefinition()

    __registerGFR(menuDefinition, "BiasedSaturation", "gfr/Color/BiasedSaturation.gfr")
    __registerGFR(menuDefinition, "BlacksMatch", "gfr/Color/BlacksMatch.gfr")
    __registerGFR(menuDefinition, "ColorCopy", "gfr/Color/ColorCopy.gfr")
    __registerGFR(menuDefinition, "Contrast", "gfr/Color/Contrast.gfr")
    __registerGFR(menuDefinition, "GammaPlus", "gfr/Color/GammaPlus.gfr")
    __registerGFR(menuDefinition, "GradeLayerPass", "gfr/Color/GradeLayerPass.gfr")
    __registerGFR(menuDefinition, "HSLTool", "gfr/Color/HSLTool.gfr")
    __registerGFR(
        menuDefinition, "HighlightSuppress", "gfr/Color/HighlightSuppress.gfr"
    )
    __registerGFR(menuDefinition, "MonochromePlus", "gfr/Color/MonochromePlus.gfr")
    __registerGFR(menuDefinition, "ShadowMult", "gfr/Color/ShadowMult.gfr")
    __registerGFR(menuDefinition, "SuppressRGBCMY", "gfr/Color/SuppressRGBCMY.gfr")
    __registerGFR(menuDefinition, "WhiteBalance", "gfr/Color/WhiteBalance.gfr")
    __registerGFR(menuDefinition, "WhiteSoftClip", "gfr/Color/WhiteSoftClip.gfr")
    __registerGFR(menuDefinition, "aeRelight2D", "gfr/Color/aeRelight2D.gfr")
    __registerGFR(menuDefinition, "apColorSampler", "gfr/Color/apColorSampler.gfr")
    __registerGFR(menuDefinition, "apVignette", "gfr/Color/apVignette.gfr")

    return menuDefinition


def __deepMenu():
    menuDefinition = IECore.MenuDefinition()

    __registerGFR(menuDefinition, "DVPColorCorrect", "gfr/Deep/DVPColorCorrect.gfr")
    __registerGFR(menuDefinition, "DVPShader", "gfr/Deep/DVPShader.gfr")
    __registerGFR(menuDefinition, "DVPToImage", "gfr/Deep/DVPToImage.gfr")
    __registerGFR(menuDefinition, "DVPToonShader", "gfr/Deep/DVPToonShader.gfr")
    __registerGFR(menuDefinition, "DVPattern", "gfr/Deep/DVPattern.gfr")
    __registerGFR(menuDefinition, "DVPfresnel", "gfr/Deep/DVPfresnel.gfr")
    __registerGFR(menuDefinition, "DVPmatte", "gfr/Deep/DVPmatte.gfr")
    __registerGFR(menuDefinition, "DVPortal", "gfr/Deep/DVPortal.gfr")
    __registerGFR(menuDefinition, "DVPrelight", "gfr/Deep/DVPrelight.gfr")
    __registerGFR(menuDefinition, "DVPrelightPT", "gfr/Deep/DVPrelightPT.gfr")
    __registerGFR(menuDefinition, "DVProjection", "gfr/Deep/DVProjection.gfr")
    __registerGFR(menuDefinition, "DVPscene", "gfr/Deep/DVPscene.gfr")
    __registerGFR(menuDefinition, "DVPsetLight", "gfr/Deep/DVPsetLight.gfr")
    __registerGFR(menuDefinition, "Deep2VP", "gfr/Deep/Deep2VP.gfr")
    __registerGFR(menuDefinition, "Deep2VPosition", "gfr/Deep/Deep2VPosition.gfr")
    __registerGFR(menuDefinition, "DeepBoolean", "gfr/Deep/DeepBoolean.gfr")
    __registerGFR(menuDefinition, "DeepCopyBBox", "gfr/Deep/DeepCopyBBox.gfr")
    __registerGFR(menuDefinition, "DeepCropSoft", "gfr/Deep/DeepCropSoft.gfr")
    __registerGFR(menuDefinition, "DeepFromDepth", "gfr/Deep/DeepFromDepth.gfr")
    __registerGFR(menuDefinition, "DeepFromPosition", "gfr/Deep/DeepFromPosition.gfr")
    __registerGFR(
        menuDefinition, "DeepHoldoutSmoother", "gfr/Deep/DeepHoldoutSmoother.gfr"
    )
    __registerGFR(menuDefinition, "DeepKeyMix", "gfr/Deep/DeepKeyMix.gfr")
    __registerGFR(menuDefinition, "DeepMergeAdvanced", "gfr/Deep/DeepMergeAdvanced.gfr")
    __registerGFR(menuDefinition, "DeepRecolorMatte", "gfr/Deep/DeepRecolorMatte.gfr")
    __registerGFR(menuDefinition, "DeepSampleCount", "gfr/Deep/DeepSampleCount.gfr")
    __registerGFR(menuDefinition, "DeepSer", "gfr/Deep/DeepSer.gfr")
    __registerGFR(menuDefinition, "DeepThickness", "gfr/Deep/DeepThickness.gfr")

    return menuDefinition


def __drawMenu():
    menuDefinition = IECore.MenuDefinition()

    __registerGFR(menuDefinition, "AutoFlare", "gfr/Draw/AutoFlare.gfr")
    __registerGFR(menuDefinition, "BokehBuilder", "gfr/Draw/BokehBuilder.gfr")
    __registerGFR(menuDefinition, "CellNoise", "gfr/Draw/CellNoise.gfr")
    __registerGFR(menuDefinition, "ConstantPro", "gfr/Draw/ConstantPro.gfr")
    __registerGFR(menuDefinition, "DasGrain", "gfr/Draw/DasGrain.gfr")
    __registerGFR(menuDefinition, "FlareSuperStar", "gfr/Draw/FlareSuperStar.gfr")
    __registerGFR(menuDefinition, "GradientEditor", "gfr/Draw/GradientEditor.gfr")
    __registerGFR(menuDefinition, "GrainAdvanced", "gfr/Draw/GrainAdvanced.gfr")
    __registerGFR(menuDefinition, "HexColor", "gfr/Draw/HexColor.gfr")
    __registerGFR(menuDefinition, "LensEngine", "gfr/Draw/LensEngine.gfr")
    __registerGFR(menuDefinition, "LineTool", "gfr/Draw/LineTool.gfr")
    __registerGFR(menuDefinition, "LumaGrain", "gfr/Draw/LumaGrain.gfr")
    __registerGFR(menuDefinition, "PerspectiveGuide", "gfr/Draw/PerspectiveGuide.gfr")
    __registerGFR(menuDefinition, "PlotScanline", "gfr/Draw/PlotScanline.gfr")
    __registerGFR(menuDefinition, "RadialAdvanced", "gfr/Draw/RadialAdvanced.gfr")
    __registerGFR(menuDefinition, "RingsOfPower", "gfr/Draw/RingsOfPower.gfr")
    __registerGFR(menuDefinition, "Silk", "gfr/Draw/Silk.gfr")
    __registerGFR(menuDefinition, "SliceTool", "gfr/Draw/SliceTool.gfr")
    __registerGFR(menuDefinition, "SpotFlare", "gfr/Draw/SpotFlare.gfr")
    __registerGFR(menuDefinition, "SpotLight", "gfr/Draw/SpotLight.gfr")
    __registerGFR(menuDefinition, "UVMap", "gfr/Draw/UVMap.gfr")
    __registerGFR(menuDefinition, "VoronoiGradient", "gfr/Draw/VoronoiGradient.gfr")
    __registerGFR(menuDefinition, "WaterLens", "gfr/Draw/WaterLens.gfr")
    __registerGFR(menuDefinition, "XTesla", "gfr/Draw/XTesla.gfr")

    return menuDefinition


def __filterMenu():
    menuDefinition = IECore.MenuDefinition()

    # Python-backed nodes
    if "VectorTracker" in GST_PythonNodes:
        __registerNode(
            menuDefinition, "VectorTracker", GST_PythonNodes["VectorTracker"]
        )

    __registerGFR(
        menuDefinition, "AntiAliasingFilter", "gfr/Filter/AntiAliasingFilter.gfr"
    )
    __registerGFR(menuDefinition, "BeautifulSkin", "gfr/Filter/BeautifulSkin.gfr")
    __registerGFR(menuDefinition, "BlacksExpon", "gfr/Filter/BlacksExpon.gfr")
    __registerGFR(menuDefinition, "CatsEyeDefocus", "gfr/Filter/CatsEyeDefocus.gfr")
    __registerGFR(menuDefinition, "ChromaSmear", "gfr/Filter/ChromaSmear.gfr")
    __registerGFR(
        menuDefinition, "ChromaticAberration", "gfr/Filter/ChromaticAberration.gfr"
    )
    __registerGFR(menuDefinition, "Chromatik", "gfr/Filter/Chromatik.gfr")
    __registerGFR(menuDefinition, "ColorSmear", "gfr/Filter/ColorSmear.gfr")
    __registerGFR(
        menuDefinition, "ConvolutionMatrix", "gfr/Filter/ConvolutionMatrix.gfr"
    )
    __registerGFR(
        menuDefinition, "DeflickerVelocity", "gfr/Filter/DeflickerVelocity.gfr"
    )
    __registerGFR(
        menuDefinition, "DefocusSwirlyBokeh", "gfr/Filter/DefocusSwirlyBokeh.gfr"
    )
    __registerGFR(menuDefinition, "Diffusion", "gfr/Filter/Diffusion.gfr")
    __registerGFR(menuDefinition, "DirectionalBlur", "gfr/Filter/DirectionalBlur.gfr")
    __registerGFR(menuDefinition, "Edge", "gfr/Filter/Edge.gfr")
    __registerGFR(menuDefinition, "EdgeDetectAlias", "gfr/Filter/EdgeDetectAlias.gfr")
    __registerGFR(menuDefinition, "EdgeDetectPRO", "gfr/Filter/EdgeDetectPRO.gfr")
    __registerGFR(menuDefinition, "EdgeExpand", "gfr/Filter/EdgeExpand.gfr")
    __registerGFR(menuDefinition, "EdgeFromAlpha", "gfr/Filter/EdgeFromAlpha.gfr")
    __registerGFR(menuDefinition, "EdgeRimLight", "gfr/Filter/EdgeRimLight.gfr")
    __registerGFR(menuDefinition, "ErodeFine", "gfr/Filter/ErodeFine.gfr")
    __registerGFR(menuDefinition, "ErodeSmooth", "gfr/Filter/ErodeSmooth.gfr")
    __registerGFR(menuDefinition, "ExponBlurSimple", "gfr/Filter/ExponBlurSimple.gfr")
    __registerGFR(menuDefinition, "ExponGlow", "gfr/Filter/ExponGlow.gfr")
    __registerGFR(
        menuDefinition, "FastComplexityDistort", "gfr/Filter/FastComplexityDistort.gfr"
    )
    __registerGFR(menuDefinition, "FillSampler", "gfr/Filter/FillSampler.gfr")
    __registerGFR(menuDefinition, "FractalBlur", "gfr/Filter/FractalBlur.gfr")
    __registerGFR(menuDefinition, "Glass", "gfr/Filter/Glass.gfr")
    __registerGFR(menuDefinition, "GlowExponential", "gfr/Filter/GlowExponential.gfr")
    __registerGFR(menuDefinition, "GuidedBlur", "gfr/Filter/GuidedBlur.gfr")
    __registerGFR(menuDefinition, "Halation", "gfr/Filter/Halation.gfr")
    __registerGFR(menuDefinition, "HeatWave", "gfr/Filter/HeatWave.gfr")
    __registerGFR(menuDefinition, "HighPass", "gfr/Filter/HighPass.gfr")
    __registerGFR(menuDefinition, "KillOutline", "gfr/Filter/KillOutline.gfr")
    __registerGFR(menuDefinition, "LightWrapPro", "gfr/Filter/LightWrapPro.gfr")
    __registerGFR(menuDefinition, "MECfiller", "gfr/Filter/MECfiller.gfr")
    __registerGFR(menuDefinition, "MotionBlurPaint", "gfr/Filter/MotionBlurPaint.gfr")
    __registerGFR(menuDefinition, "RadialDilate", "gfr/Filter/RadialDilate.gfr")
    __registerGFR(menuDefinition, "RankFilter", "gfr/Filter/RankFilter.gfr")
    __registerGFR(menuDefinition, "VectorExtendEdge", "gfr/Filter/VectorExtendEdge.gfr")
    __registerGFR(menuDefinition, "WaveletBlur", "gfr/Filter/WaveletBlur.gfr")
    __registerGFR(menuDefinition, "XAtonVolumetrics", "gfr/Filter/XAtonVolumetrics.gfr")
    __registerGFR(menuDefinition, "XDenoise", "gfr/Filter/XDenoise.gfr")
    __registerGFR(menuDefinition, "XDistort", "gfr/Filter/XDistort.gfr")
    __registerGFR(menuDefinition, "XSharpen", "gfr/Filter/XSharpen.gfr")
    __registerGFR(menuDefinition, "XSoften", "gfr/Filter/XSoften.gfr")
    __registerGFR(menuDefinition, "aeShadows", "gfr/Filter/aeShadows.gfr")
    __registerGFR(menuDefinition, "apChroma", "gfr/Filter/apChroma.gfr")
    __registerGFR(menuDefinition, "apChromaBlur", "gfr/Filter/apChromaBlur.gfr")
    __registerGFR(menuDefinition, "apChromaMerge", "gfr/Filter/apChromaMerge.gfr")
    __registerGFR(menuDefinition, "apChromaPremult", "gfr/Filter/apChromaPremult.gfr")
    __registerGFR(
        menuDefinition, "apChromaTransform", "gfr/Filter/apChromaTransform.gfr"
    )
    __registerGFR(
        menuDefinition, "apChromaUnpremult", "gfr/Filter/apChromaUnpremult.gfr"
    )
    __registerGFR(menuDefinition, "apEdgeCrush", "gfr/Filter/apEdgeCrush.gfr")
    __registerGFR(menuDefinition, "apEdgePush", "gfr/Filter/apEdgePush.gfr")
    __registerGFR(menuDefinition, "apGlow", "gfr/Filter/apGlow.gfr")
    __registerGFR(menuDefinition, "bmOpticalGlow", "gfr/Filter/bmOpticalGlow.gfr")
    __registerGFR(
        menuDefinition, "bmOpticalLightwrap", "gfr/Filter/bmOpticalLightwrap.gfr"
    )
    __registerGFR(menuDefinition, "deHaze", "gfr/Filter/deHaze.gfr")
    __registerGFR(menuDefinition, "iBlur", "gfr/Filter/iBlur.gfr")
    __registerGFR(menuDefinition, "iConvolve", "gfr/Filter/iConvolve.gfr")
    __registerGFR(menuDefinition, "iErode", "gfr/Filter/iErode.gfr")

    return menuDefinition


def __keyerMenu():
    menuDefinition = IECore.MenuDefinition()

    __registerGFR(menuDefinition, "AdditiveKeyerPro", "gfr/Keyer/AdditiveKeyerPro.gfr")
    __registerGFR(menuDefinition, "DespillToColor", "gfr/Keyer/DespillToColor.gfr")
    __registerGFR(menuDefinition, "KeyChew", "gfr/Keyer/KeyChew.gfr")
    __registerGFR(menuDefinition, "LumaKeyer", "gfr/Keyer/LumaKeyer.gfr")
    __registerGFR(menuDefinition, "PointCloudKeyer", "gfr/Keyer/PointCloudKeyer.gfr")
    __registerGFR(menuDefinition, "SkyMatte", "gfr/Keyer/SkyMatte.gfr")
    __registerGFR(menuDefinition, "SpillCorrect", "gfr/Keyer/SpillCorrect.gfr")
    __registerGFR(menuDefinition, "apDespill", "gfr/Keyer/apDespill.gfr")
    __registerGFR(menuDefinition, "apScreenClean", "gfr/Keyer/apScreenClean.gfr")
    __registerGFR(menuDefinition, "apScreenGrow", "gfr/Keyer/apScreenGrow.gfr")

    return menuDefinition


def __mergeMenu():
    menuDefinition = IECore.MenuDefinition()

    __registerGFR(menuDefinition, "ContactSheetAuto", "gfr/Merge/ContactSheetAuto.gfr")
    __registerGFR(menuDefinition, "KeymixBBox", "gfr/Merge/KeymixBBox.gfr")
    __registerGFR(menuDefinition, "MergeAll", "gfr/Merge/MergeAll.gfr")
    __registerGFR(menuDefinition, "MergeAtmos", "gfr/Merge/MergeAtmos.gfr")
    __registerGFR(menuDefinition, "MergeBlend", "gfr/Merge/MergeBlend.gfr")

    return menuDefinition


def __sceneMenu():
    menuDefinition = IECore.MenuDefinition()

    __registerGFR(menuDefinition, "Distance3D", "gfr/Scene/Distance3D.gfr")
    __registerGFR(
        menuDefinition, "DistanceBetweenCS", "gfr/Scene/DistanceBetweenCS.gfr"
    )
    __registerGFR(menuDefinition, "DummyCam", "gfr/Scene/DummyCam.gfr")
    __registerGFR(menuDefinition, "GeoToPoints", "gfr/Scene/GeoToPoints.gfr")
    __registerGFR(menuDefinition, "GodRaysProjector", "gfr/Scene/GodRaysProjector.gfr")
    __registerGFR(menuDefinition, "Lightning3D", "gfr/Scene/Lightning3D.gfr")
    __registerGFR(menuDefinition, "MirrorDimension", "gfr/Scene/MirrorDimension.gfr")
    __registerGFR(menuDefinition, "Noise3DTexture", "gfr/Scene/Noise3DTexture.gfr")
    __registerGFR(menuDefinition, "ParticleKiller", "gfr/Scene/ParticleKiller.gfr")
    __registerGFR(menuDefinition, "ParticleLights", "gfr/Scene/ParticleLights.gfr")
    __registerGFR(menuDefinition, "RainMaker", "gfr/Scene/RainMaker.gfr")
    __registerGFR(menuDefinition, "RayDeepAO", "gfr/Scene/RayDeepAO.gfr")
    __registerGFR(menuDefinition, "SSMesh", "gfr/Scene/SSMesh.gfr")
    __registerGFR(
        menuDefinition, "SceneDepthCalculator", "gfr/Scene/SceneDepthCalculator.gfr"
    )
    __registerGFR(menuDefinition, "Sparky", "gfr/Scene/Sparky.gfr")
    __registerGFR(menuDefinition, "UVEditor", "gfr/Scene/UVEditor.gfr")
    __registerGFR(
        menuDefinition, "Unify3DCoordinate", "gfr/Scene/Unify3DCoordinate.gfr"
    )
    __registerGFR(menuDefinition, "aPCard", "gfr/Scene/aPCard.gfr")
    __registerGFR(menuDefinition, "mScatterGeo", "gfr/Scene/mScatterGeo.gfr")
    __registerGFR(menuDefinition, "origami", "gfr/Scene/origami.gfr")
    __registerGFR(menuDefinition, "waterSchmutz", "gfr/Scene/waterSchmutz.gfr")

    return menuDefinition


def __timeMenu():
    menuDefinition = IECore.MenuDefinition()

    __registerGFR(menuDefinition, "FrameFiller", "gfr/Time/FrameFiller.gfr")
    __registerGFR(menuDefinition, "FrameHoldSpecial", "gfr/Time/FrameHoldSpecial.gfr")
    __registerGFR(menuDefinition, "FrameMedian", "gfr/Time/FrameMedian.gfr")
    __registerGFR(menuDefinition, "Looper", "gfr/Time/Looper.gfr")
    __registerGFR(menuDefinition, "TimeMachine", "gfr/Time/TimeMachine.gfr")
    __registerGFR(menuDefinition, "apLoop", "gfr/Time/apLoop.gfr")

    return menuDefinition


def __transformMenu():
    menuDefinition = IECore.MenuDefinition()

    # Python-backed nodes
    if "CardToTrack" in GST_PythonNodes:
        __registerNode(menuDefinition, "CardToTrack", GST_PythonNodes["CardToTrack"])
    if "CardToTrack_v9" in GST_PythonNodes:
        __registerNode(
            menuDefinition, "CardToTrack_v9", GST_PythonNodes["CardToTrack_v9"]
        )
    if "StickIt" in GST_PythonNodes:
        __registerNode(menuDefinition, "StickIt", GST_PythonNodes["StickIt"])

    __registerGFR(menuDefinition, "AutoCropTool", "gfr/Transform/AutoCropTool.gfr")
    __registerGFR(menuDefinition, "BBoxToFormat", "gfr/Transform/BBoxToFormat.gfr")
    __registerGFR(menuDefinition, "CProject", "gfr/Transform/CProject.gfr")
    __registerGFR(menuDefinition, "CProject2", "gfr/Transform/CProject2.gfr")
    __registerGFR(
        menuDefinition, "CardToTrack_v7_gfr", "gfr/Transform/CardToTrack_v7.gfr"
    )
    __registerGFR(
        menuDefinition, "CardToTrack_v9_gfr", "gfr/Transform/CardToTrack_v9.gfr"
    )
    __registerGFR(
        menuDefinition, "CornerPin2DMatrix", "gfr/Transform/CornerPin2DMatrix.gfr"
    )
    __registerGFR(menuDefinition, "IIDistort", "gfr/Transform/IIDistort.gfr")
    __registerGFR(menuDefinition, "ITransform", "gfr/Transform/ITransform.gfr")
    __registerGFR(menuDefinition, "ImagePlane3D", "gfr/Transform/ImagePlane3D.gfr")
    __registerGFR(
        menuDefinition, "InverseMatrix3x3", "gfr/Transform/InverseMatrix3x3.gfr"
    )
    __registerGFR(
        menuDefinition, "InverseMatrix4x4", "gfr/Transform/InverseMatrix4x4.gfr"
    )
    __registerGFR(menuDefinition, "Matrix4x4Math", "gfr/Transform/Matrix4x4Math.gfr")
    __registerGFR(menuDefinition, "MatrixInverse", "gfr/Transform/MatrixInverse.gfr")
    __registerGFR(menuDefinition, "MirrorBorder", "gfr/Transform/MirrorBorder.gfr")
    __registerGFR(menuDefinition, "MorphDissolve", "gfr/Transform/MorphDissolve.gfr")
    __registerGFR(
        menuDefinition, "PlanarProjection", "gfr/Transform/PlanarProjection.gfr"
    )
    __registerGFR(menuDefinition, "RPReformat", "gfr/Transform/RPReformat.gfr")
    __registerGFR(
        menuDefinition, "Reconcile3DFast", "gfr/Transform/Reconcile3DFast.gfr"
    )
    __registerGFR(menuDefinition, "RotoCentroid", "gfr/Transform/RotoCentroid.gfr")
    __registerGFR(
        menuDefinition, "RotoPaintTransform", "gfr/Transform/RotoPaintTransform.gfr"
    )
    __registerGFR(menuDefinition, "STmapInverse", "gfr/Transform/STmapInverse.gfr")
    __registerGFR(menuDefinition, "StickIt_gfr", "gfr/Transform/StickIt.gfr")
    __registerGFR(menuDefinition, "Symmetry", "gfr/Transform/Symmetry.gfr")
    __registerGFR(menuDefinition, "TProject", "gfr/Transform/TProject.gfr")
    __registerGFR(menuDefinition, "TProject2", "gfr/Transform/TProject2.gfr")
    __registerGFR(
        menuDefinition, "TransformCutOut", "gfr/Transform/TransformCutOut.gfr"
    )
    __registerGFR(
        menuDefinition, "TransformMatrix", "gfr/Transform/TransformMatrix.gfr"
    )
    __registerGFR(menuDefinition, "TransformMix", "gfr/Transform/TransformMix.gfr")
    __registerGFR(menuDefinition, "bmCameraShake", "gfr/Transform/bmCameraShake.gfr")
    __registerGFR(menuDefinition, "iMorph", "gfr/Transform/iMorph.gfr")

    return menuDefinition


def __utilitiesMenu():
    menuDefinition = IECore.MenuDefinition()

    __registerGFR(menuDefinition, "GUISwitch", "gfr/Utilities/GUISwitch.gfr")
    __registerGFR(menuDefinition, "NANINF_Killer", "gfr/Utilities/NANINF_Killer.gfr")
    __registerGFR(menuDefinition, "NukeZ", "gfr/Utilities/NukeZ.gfr")
    __registerGFR(menuDefinition, "Pyclopedia", "gfr/Utilities/Pyclopedia.gfr")
    __registerGFR(menuDefinition, "PythonAndTCL", "gfr/Utilities/PythonAndTCL.gfr")
    __registerGFR(menuDefinition, "RotoQC", "gfr/Utilities/RotoQC.gfr")
    __registerGFR(
        menuDefinition, "apViewerBlocker", "gfr/Utilities/apViewerBlocker.gfr"
    )
    __registerGFR(menuDefinition, "bmMatteCheck", "gfr/Utilities/bmMatteCheck.gfr")
    __registerGFR(menuDefinition, "viewer_render", "gfr/Utilities/viewer_render.gfr")

    return menuDefinition


def __nodeMenuDefinition():
    menuDefinition = IECore.MenuDefinition()

    menuDefinition.append("/Documentation", {"subMenu": __documentationMenu})
    menuDefinition.append("/Image", {"subMenu": __imageMenu})
    menuDefinition.append("/CG", {"subMenu": __cgMenu})
    menuDefinition.append("/Channel", {"subMenu": __channelMenu})
    menuDefinition.append("/Color", {"subMenu": __colorMenu})
    menuDefinition.append("/Deep", {"subMenu": __deepMenu})
    menuDefinition.append("/Draw", {"subMenu": __drawMenu})
    menuDefinition.append("/Filter", {"subMenu": __filterMenu})
    menuDefinition.append("/Keyer", {"subMenu": __keyerMenu})
    menuDefinition.append("/Merge", {"subMenu": __mergeMenu})
    menuDefinition.append("/Scene", {"subMenu": __sceneMenu})
    menuDefinition.append("/Time", {"subMenu": __timeMenu})
    menuDefinition.append("/Transform", {"subMenu": __transformMenu})
    menuDefinition.append("/Utilities", {"subMenu": __utilitiesMenu})

    return menuDefinition


# Register GST menu under the Image category
# NodeMenu.acquire() requires an Application object; we get it from the current context
def __registerGSTMenu():
    try:
        app = Gaffer.ApplicationRoot.currentApplication()
        if app is not None:
            nodeMenu = GafferUI.NodeMenu.acquire(app)
            nodeMenu.definition().append(
                "/Image/GST", {"subMenu": __nodeMenuDefinition}
            )
    except Exception as e:
        IECore.msg(
            IECore.Msg.Level.Warning, "GST_menu", f"Could not register GST menu: {e}"
        )


__registerGSTMenu()
