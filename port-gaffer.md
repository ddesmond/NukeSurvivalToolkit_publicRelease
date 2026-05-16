# Porting Nuke Survival Toolkit → Gaffer 1.6.18.0

## Architectural Overview

### Nuke → Gaffer Mapping

| Nuke Concept | Gaffer Equivalent |
|---|---|
| `.gizmo` files | `.gfr` Group nodes (serialized Python) or Python-defined nodes |
| `.nk` templates | `.gfr` scripts or `.grf` references |
| `menu.py` | Startup scripts (`GAFFER_STARTUP_PATHS`) |
| TCL expressions | Gaffer expressions (Python-based in Expression nodes) |
| `nuke.createNode()` | `root.addChild(GafferImage.NodeName())` |
| Image processing | `GafferImage` module (ImageProcessor, ImageNode base classes) |
| 3D/Scene | `GafferScene` module (SceneProcessor, SceneNode base classes) |
| PySide6 UI | GafferUI (built on Qt, but different API) |
| `init.py` | `startup/` scripts |

### Key API Differences

| Nuke API | Gaffer API |
|---|---|
| `nuke.thisNode()` | `plug.node()` |
| `nuke.thisGroup()` | `node.ancestor(Gaffer.ScriptNode)` |
| `node.knob("name").getValue()` | `node["name"].getValue()` |
| `node.knob("name").setValue(v)` | `node["name"].setValue(v)` |
| `node.setInput(0, other)` | `node["in"].setInput(other["out"])` |
| `node.dependent()` | `plug.outputs()` |
| `nuke.nodes.NodeName()` | `GafferImage.NodeName()` + `root.addChild(node)` |
| `nukescripts.clear_selection_recursive()` | `root.selection().clear()` |
| `nuke.frame()` | `root.context().getFrame()` |
| `addCallback(fn)` | `plug.valueChangedSignal().connect(fn)` |
| `nuke.message("text")` | `GafferUI.InfoMessage("text")` |

## Proposed Project Structure

```
GafferSurvivalToolkit/
├── python/                          # Python modules (on PYTHONPATH)
│   ├── GST_helper.py                # Ported from NST_helper.py
│   ├── GST_VectorTracker.py         # Ported from NST_VectorTracker.py
│   ├── GST_ID_Extractor.py          # Ported from NST_ID_Extractor.py
│   ├── GST_cardToTrack.py           # Ported from NST_cardToTrack.py
│   ├── GST_cardToTrack_v9.py        # Ported from NST_cardToTrack_v9.py
│   ├── GST_stickit.py               # Ported from NST_stickit.py
│   ├── GST_GradientEditor.py        # Ported from ColorGradientUi.py (GafferUI)
│   └── GST_GradientEditorUI.py      # UI metadata for GradientEditor
│
├── gfr/                             # Pre-built .gfr node graphs (replaces gizmos)
│   ├── Image/
│   │   ├── LabelFromRead.gfr
│   │   └── ...
│   ├── Draw/
│   │   ├── ConstantPro.gfr
│   │   ├── GradMagic.gfr
│   │   └── ...
│   ├── Color/
│   ├── Filter/
│   ├── Keyer/
│   ├── Merge/
│   ├── Transform/
│   ├── Deep/
│   └── CG/
│
├── startup/                         # Startup scripts (on GAFFER_STARTUP_PATHS)
│   ├── gui/
│   │   ├── GST_menu.py              # Main menu registration
│   │   └── GST_nodeDefinitions.py   # Custom Python node registrations
│   └── dispatch/
│       └── GST_tasks.py             # Dispatch/task node registrations
│
├── icons/                           # Ported icon assets
├── images/                          # Demo images (<<<replace>>> → GST_FolderPath)
├── nk_files/                        # Ported .nk templates → .gfr conversions
│   └── ...
├── __init__.py                      # Package init
└── install.py                       # Installation helper script
```

## Porting Strategy by Tool Type

### Type A: Pure Gizmo Node Graphs (~230 tools) → `.gfr` Files

These are the bulk of the toolkit — node graphs wrapped as gizmos.

**Approach:**
1. Recreate each gizmo as a Gaffer node graph using `GafferImage`/`GafferScene` equivalents
2. Save as `.gfr` files organized by category
3. Register in menu via startup scripts

**Example — Porting `NST_ConstantPro` → `ConstantPro.gfr`:**
```python
# Nuke version (gizmo): Group with Constant + user knobs
# Gaffer version (.gfr):
import GafferImage
import Gaffer

node = GafferImage.Constant( "ConstantPro" )
# Add custom plugs for user controls
node.addChild( Gaffer.FloatPlug( "brightness", defaultValue=1.0 ) )
# ... recreate internal node graph
```

### Type B: Python-Backed Tools (6 tools) → Python Node Definitions

These need custom Python classes: `VectorTracker`, `ID_Extractor`, `CardToTrack v7/v9`, `StickIt`, `GradientEditor`.

**Approach:**
1. Subclass appropriate Gaffer base class (`Gaffer.DependencyNode`, `GafferImage.ImageProcessor`)
2. Implement `affects()`, `hash()`, `compute()` methods (or use internal node graphs for performance)
3. Register with `Gaffer.Metadata.registerNode()` for UI
4. Add to menu via startup script

**Important:** The Gaffer team strongly recommends using internal node graphs instead of overriding `compute()` in Python, because Python ComputeNodes have horrendous performance due to the GIL. Build an internal network that outputs to the `out` plug.

**Example — Python Node Pattern:**
```python
import Gaffer
import GafferImage

class GST_IDExtractor( GafferImage.ImageProcessor ) :

    def __init__( self, name = "GST_IDExtractor" ) :
        GafferImage.ImageProcessor.__init__( self, name )
        self["redChannel"] = Gaffer.StringPlug()
        self["greenChannel"] = Gaffer.StringPlug()
        self["blueChannel"] = Gaffer.StringPlug()
        # Build internal node graph instead of compute() for performance
        self.__setupInternalGraph()

    def __setupInternalGraph( self ) :
        # Create internal Shuffle, Expression nodes wired to self["out"]
        # This approach gives performance equivalent to an Expression node
        pass
```

### Type C: .nk Templates (~30+ tools) → `.gfr` Scripts

Multi-node setups saved as `.nk` files.

**Approach:**
1. Convert each `.nk` template to equivalent Gaffer node graph
2. Save as `.gfr` files
3. Load via `root.load()` or register as Reference nodes (`.grf`)

### Type D: Expression Nodes (~48 tools) → Gaffer Expression Nodes

Nuke expression-based tools (Random colors, Alpha analysis, Pixel ops, etc.)

**Approach:**
1. Convert Nuke expressions to Gaffer Expression node Python code
2. Wrap in `.gfr` files or create as reusable node graphs
3. Many map directly to existing `GafferImage` nodes (e.g., `Grade`, `Shuffle`, `Expression`)

## Menu Registration (Gaffer Startup System)

Gaffer uses a startup script system. Scripts in `GAFFER_STARTUP_PATHS` run automatically:
- `startup/gui/` — runs when GUI launches
- `startup/` — runs always (CLI + GUI)

**`startup/gui/GST_menu.py`:**
```python
import Gaffer
import GafferImage
import GafferScene
import GafferDispatch
import GafferUI
import IECore

from pathlib import Path

GST_FolderPath = Path( __file__ ).parent.parent.parent.as_posix()

def __registerNode( menuDefinition, path, nodeClass, icon="" ) :
    menuDefinition.append( f"/{path}", {
        "command": lambda menu: __createNode( menu, nodeClass ),
        "icon": icon,
    } )

def __createNode( menu, nodeClass ) :
    script = menu.scriptNode()
    node = nodeClass()
    script.addChild( node )
    GafferUI.NodeEditor.acquire( node )

def __nodeMenuDefinition() :
    import GafferImageUI
    import GafferSceneUI

    menuDefinition = IECore.MenuDefinition()

    # Image category
    __registerNode( menuDefinition, "GST/Image/LabelFromRead", GafferImage.SomeNode )

    # Draw category
    __registerNode( menuDefinition, "GST/Draw/ConstantPro", GafferImage.Constant )
    __registerNode( menuDefinition, "GST/Draw/GradMagic", GafferImage.Ramp )
    # ... all 290+ tools

    return menuDefinition

GafferUI.NodeMenu.acquire( "Image" ).append( "GST", __nodeMenuDefinition )
```

## Tool Categorization & Gaffer Module Mapping

### By Gaffer Module

| Gaffer Module | Est. Count | Source Categories |
|---|---|---|
| `GafferImage` | ~230 | Image, Draw, Color, Channel, Merge, Filter, Keyer, Deep, CG (most) |
| `GafferScene` | ~30 | 3D, Particles, Transform (projections), CG (scene ops) |
| `GafferDispatch` | ~12 | Curves (animation), Utilities, render management |
| `Gaffer` (core) | ~25 | Vector math, matrix ops, expressions |
| `GafferOSL` | ~5 | Relight, shader-based CG tools |
| Custom Python | 6 | VectorTracker, ID_Extractor, CardToTrack x2, StickIt, GradientEditor |

### By Tool Type

| Type | Count | Description |
|------|-------|-------------|
| Pure gizmo → `.gfr` | ~230 | Node graphs — recreate as Gaffer graphs |
| Python-backed | 6 | Need custom Python node definitions |
| Templates → `.gfr` | ~30+ | Multi-node setups — convert to Gaffer scripts |
| Expression nodes | ~48 | Nuke expressions → Gaffer Expression Python |

### Detailed Tool Inventory

#### Documentation (4 tools)
| Tool | Gaffer Mapping | Type |
|------|---------------|------|
| Wiki/Docs (Auto) | Utility | Python helper |
| Wiki (Online) | Utility | Python helper |
| Wiki (Offline) | Utility | Python helper |
| Docs (PDF) | Utility | Python helper |

#### Image (1 tool)
| Tool | Gaffer Mapping | Type |
|------|---------------|------|
| LabelFromRead TL | GafferImage | Gizmo |

#### Draw (~38 tools + Expression submenu ~48)
| Tool | Gaffer Mapping | Type |
|------|---------------|------|
| ConstantPro TL | GafferImage | Gizmo |
| HexColor NW | GafferImage | Gizmo |
| GradMagic TL | GafferImage | Gizmo |
| NoiseAdvanced TL | GafferImage | Gizmo |
| RadialAdvanced TL | GafferImage | Gizmo |
| UV Map AG | GafferImage | Gizmo |
| SpotLight TL | GafferImage | Gizmo |
| Rings of Power TL | GafferImage | Gizmo |
| WaterLens MJT | GafferImage | Gizmo |
| Silk MHD | GafferImage | Gizmo |
| GradientEditor MHD | GafferImage | Python+Gizmo |
| VoronoiGradient NW | GafferImage | Gizmo |
| CellNoise NKPD | GafferImage | Gizmo |
| LineTool NKPD | GafferImage | Gizmo |
| PlotScanline NKPD | GafferImage | Gizmo |
| SliceTool FR | GafferImage | Gizmo |
| PerspectiveGuide NKPD | GafferImage | Gizmo |
| DasGrain FH | GafferImage | Gizmo |
| LumaGrain LUMA | GafferImage | Gizmo |
| Grain_Advanced SPIN | GafferImage | Gizmo |
| X_Tesla XM | GafferImage | Gizmo |
| SpotFlare MHD | GafferImage | Gizmo |
| FlareSuperStar NKPD | GafferImage | Gizmo |
| AutoFlare NKPD | GafferImage | Gizmo |
| BokehBuilder KB | GafferImage | Gizmo |
| LensEngine KB | GafferImage | Gizmo |

**Expression Nodes AG Submenu** (disabled by default in Nuke, ~48 .nk templates):
- Creations: Random Colors/Frame/Pixel, lines, circles, points, bricks, gradients, radial, Trunc
- Alpha: binary, comparison, exists?, sum
- Pixel: abs, check negative, nan/inf, create/kill nan/inf
- Transform: Coordinates, UV↔Vector, transform, twist, STMap_invert
- 3D and Deep: Normal Relight, C4x4, Deep↔Depth, Depth normalize
- Keying and Despill: despill green/blue, keying, differenceKey, IBKGizmo

#### Time (5 tools)
| Tool | Gaffer Mapping | Type |
|------|---------------|------|
| apLoop AP | GafferImage | Gizmo |
| FrameHold Special AG | GafferImage | Gizmo |
| Looper DB | GafferImage | Gizmo |
| FrameMedian MHD | GafferImage | Gizmo |
| TimeMachine NKPD | GafferImage | Gizmo |
| FrameFiller MJT | GafferImage | Gizmo |

#### Channel (7 tools)
| Tool | Gaffer Mapping | Type |
|------|---------------|------|
| BinaryAlpha TL | GafferImage | Gizmo |
| ChannelCombiner TL | GafferImage | Gizmo |
| ChannelControl TL | GafferImage | Gizmo |
| ChannelCreator TL | GafferImage | Gizmo |
| InjectMatteChannel TL | GafferImage | Gizmo |
| ID_Extractor TL | GafferImage | Python+Gizmo |
| streamCart MJT | GafferImage | Gizmo |
| renameChannels AG | GafferImage | Gizmo |

#### Color (13 tools)
| Tool | Gaffer Mapping | Type |
|------|---------------|------|
| BlacksMatch TL | GafferImage | Gizmo |
| ColorCopy TL | GafferImage | Gizmo |
| Contrast TL | GafferImage | Gizmo |
| GradeLayerPass TL | GafferImage | Gizmo |
| HighlightSuppress TL | GafferImage | Gizmo |
| ShadowMult TL | GafferImage | Gizmo |
| WhiteSoftClip TL | GafferImage | Gizmo |
| WhiteBalance TL | GafferImage | Gizmo |
| apColorSampler AP | GafferImage | Gizmo |
| apVignette AP | GafferImage | Gizmo |
| GammaPlus MJT | GafferImage | Gizmo |
| MonochromePlus CF | GafferImage | Gizmo |
| aeRelight2D AE | GafferImage | Gizmo |
| Suppress_RGBCMY SPIN | GafferImage | Gizmo |
| BiasedSaturation NKPD | GafferImage | Gizmo |
| HSL_Tool NKPD | GafferImage | Gizmo |

#### Filter (~56 tools)

**Glows:** apGlow, ExponGlow, Glow_Exponential, bm_OpticalGlow
**Blurs:** ExponBlurSimple, DirectionalBlur, MotionBlurPaint, iBlur, WaveletBlur
**Edges:** apEdgePush, apEdgeCrush, EdgeDetectAlias, AntiAliasingFilter, ErodeSmooth, iErode, Edge_RimLight, EdgeDetectPRO, Erode_Fine, Edge_Expand, Edge, KillOutline, ColorSmear, EdgeFromAlpha, VectorExtendEdge, GuidedBlur, FractalBlur
**Distortions:** Glass, HeatWave, X_Distort, FastComplexityDistort
**X_Tools:** X_Aton_Volumetrics, X_Denoise, X_Sharpen, X_Soften
**apChroma:** apChroma, apChromaMerge, apChromaBlur, apChromaTransform, apChromaUnpremult, apChromaPremult
**Top-level:** BeautifulSkin, BlacksExpon, aeShadows, Halation, HighPass, Diffusion, LightWrapPro, bm_OpticalLightwrap, iConvolve, ConvolutionMatrix, Chromatik, ChromaticAberration, ChromaSmear, CatsEyeDefocus, DefocusSwirlyBokeh, deHaze, RankFilter, RadialDilate, DeflickerVelocity, FillSampler, MECfiller

#### Keyer (9 tools)
| Tool | Gaffer Mapping | Type |
|------|---------------|------|
| apDespill AP | GafferImage | Gizmo |
| SpillCorrect SPIN | GafferImage | Gizmo |
| DespillToColor NKPD | GafferImage | Gizmo |
| AdditiveKeyerPro TL | GafferImage | Gizmo |
| apScreenClean AP | GafferImage | Gizmo |
| apScreenGrow AP | GafferImage | Gizmo |
| KeyChew NKPD | GafferImage | Gizmo |
| LumaKeyer DR | GafferImage | Gizmo |
| PointCloudKeyer IS | GafferScene | Gizmo |
| SkyMatte CF | GafferImage | Gizmo |

#### Merge (5 tools)
| Tool | Gaffer Mapping | Type |
|------|---------------|------|
| ContactSheetAuto TL | GafferImage | Gizmo |
| KeymixBBox TL | GafferImage | Gizmo |
| MergeAtmos TL | GafferImage | Gizmo |
| MergeBlend TL | GafferImage | Gizmo |
| MergeAll AP | GafferImage | Gizmo |

#### Transform (~52 tools)

**Vector Math Tools VM:** Invert/Zero Axis, Matrix4 ops (Invert/Product/Rotate/Scale/Transform/Translate/Transpose), Vector2/Vector3 ops (Cross/Dot/Magnitude/Normalize/Rotate/Transform), Generate Matrix4/STMap, Convert (Luma→Vector3, STMap↔Vector2, Vector3→Matrix4)

**Main Transform:**
| Tool | Gaffer Mapping | Type |
|------|---------------|------|
| vector3DMathExpression EL | Gaffer core | Gizmo |
| Vectors_Direction EL | Gaffer core | Gizmo |
| Vectors_to_Degrees EL | Gaffer core | Gizmo |
| VectorTracker NKPD | GafferImage | Python+Gizmo |
| AutoCropTool TL | GafferImage | Gizmo |
| BBoxToFormat TL | Gaffer core | Gizmo |
| ImagePlane3D TL | GafferScene | Gizmo |
| Matrix_Inverse TL | Gaffer core | Gizmo |
| Matrix4x4Math TL | Gaffer core | Gizmo |
| MirrorBorder TL | GafferImage | Gizmo |
| TransformCutOut TL | GafferImage | Gizmo |
| iMorph AP | GafferImage | Gizmo |
| Symmetry TL | GafferImage | Gizmo |
| RP_Reformat MJT | GafferImage | Gizmo |
| InverseMatrix3x3 MJT | Gaffer core | Gizmo |
| InverseMatrix4x4 MJT | Gaffer core | Gizmo |
| CardToTrack_v7 AK | GafferScene | Python+Gizmo |
| CardToTrack_v9 AK | GafferScene | Python+Gizmo |
| CProject AK | GafferImage | Gizmo |
| CProject2 AK | GafferImage | Gizmo |
| TProject AK | GafferImage | Gizmo |
| TProject2 AK | GafferImage | Gizmo |
| StickIt MHD | GafferScene | Python+Gizmo |
| TransformMatrix AG | GafferImage | Gizmo |
| CornerPin2D_Matrix AG | GafferImage | Gizmo |
| RotoPaintTransform AG | GafferImage | Gizmo |
| IIDistort EL | GafferImage | Gizmo |
| bm_CameraShake BM | GafferImage | Gizmo |
| ITransform AE | GafferImage | Gizmo |
| MorphDissolve SPIN | GafferImage | Gizmo |
| RotoCentroid NKPD | Gaffer core | Gizmo |
| STmapInverse NKPD | GafferImage | Gizmo |
| TransformMix NKPD | GafferImage | Gizmo |
| PlanarProjection NKPD | GafferScene | Gizmo |
| Reconcile3DFast DR | GafferScene | Gizmo |

#### 3D (13 tools)
| Tool | Gaffer Mapping | Type |
|------|---------------|------|
| aPCard AP | GafferScene | Gizmo |
| DummyCam | GafferScene | Gizmo |
| mScatterGeo MJT | GafferScene | Gizmo |
| GeoToPoints MHD | GafferScene | Gizmo |
| origami MJT | GafferScene | Gizmo |
| RayDeepAO MJT | GafferScene | Gizmo |
| SceneDepthCalculator MJT | GafferScene | Gizmo |
| SSMesh MJT | GafferScene | Gizmo |
| Unify3DCoordinate MJT | GafferScene | Gizmo |
| UVEditor MJT | GafferScene | Gizmo |
| Distance3D NKPD | GafferScene | Gizmo |
| DistanceBetween_CS NKPD | GafferScene | Gizmo |
| Lightning3D EL | GafferScene | Gizmo |
| Noise3DTexture NKPD | GafferScene | Gizmo |
| GodRaysProjector CF | GafferScene | Gizmo |
| MirrorDimension TL | GafferScene | Gizmo |

#### Particles (5 tools)
| Tool | Gaffer Mapping | Type |
|------|---------------|------|
| waterSchmutz DR | GafferScene | Gizmo |
| RainMaker MR | GafferScene | Gizmo |
| Sparky DB | GafferScene | Gizmo |
| ParticleLights MHD | GafferScene | Gizmo |
| ParticleKiller NKPD | GafferScene | Gizmo |

#### Deep (24 tools)

**Deep2VP Suite:** Deep2VP, Deep2VPosition, DVPColorCorrect, DVPortal, DVPToImage, DVPfresnel, DVPrelight, DVPrelightPT, DVPscene, DVPsetLight, DVPattern, DVPmatte, DVProjection, DVP_ToonShader, DVP_Shader

**Main Deep:** DeepBoolean, DeepFromPosition, DeepSampleCount, DeepSer, DeepFromDepth, DeepRecolorMatte, Deep Thickness (.nk template), DeepMerge_Advanced, DeepCropSoft, DeepKeyMix, DeepHoldoutSmoother, DeepCopyBBox

#### CG (29 tools)

**PNZsuite:** ConvertPNZ, P2N, P2Z, Z2N, Z2P
**PosToolkit:** PosMatte, PosPattern, PosProjection
**Main:** UV Mapper, Noise_3D, Noise4D (.nk template), Relight_Simple, ReProject_3D, C44Kernel, apDirLight, apFresnel, CameraNormals, NormalsRotate, Relight_bb, EnvReflect_bb, N_Reflection, aeRefracTHOR, Emission, SimpleSSS, aPmatte, P_Ramp, P_Project, Glue_P, P_Noise_Advanced, LightSwitch (GafferScene), LightSwitchPuppet (.nk template)

#### Curves (9 tools)

**Wave Machine:** WaveMaker, WaveCustom, WaveGrade, WaveRetime, WaveMerge
**Main:** Randomizer, AnimationCurve, bm_CurveRemapper, bm_NoiseGen

#### Utilities (8 tools)
| Tool | Gaffer Mapping | Type |
|------|---------------|------|
| GUI Switch TL | GafferDispatch | Gizmo |
| NAN INF Killer TL | GafferImage | Gizmo |
| apViewerBlocker AP | GafferDispatch | Gizmo |
| Python_and_TCL AG | GafferDispatch | Gizmo |
| RotoQC NKPD | GafferDispatch | Gizmo |
| bm_MatteCheck BM | GafferImage | Gizmo |
| viewer_render MJT | GafferDispatch | Gizmo |
| NukeZ MJT | GafferDispatch | Gizmo |
| Pyclopedia MJT | GafferDispatch | Gizmo |

#### Templates (3 + 6 demo scripts)
- Advanced Keying Template Stamps TL, Advanced Keying Template TL, STMap Keyer Setup EL
- Demo scenes: WaterLens, SSMesh, UVEditor, Sparky, ParticleLights, X_Aton Volumetric

## Phased Implementation Plan

### Phase 1: Foundation (Week 1-2)
- Create project structure
- Port `GST_helper.py` (path replacement, documentation)
- Create startup script framework with menu system
- Port 5-10 representative tools as proof-of-concept:
  - `ConstantPro` (simple gizmo → .gfr)
  - `LabelFromRead` (metadata reading)
  - `ID_Extractor` (Python-backed node)
  - `Grade`-based color tool
  - One template conversion

### Phase 2: Core Image Tools (Week 3-6)
- Draw menu (~38 tools) — gradients, noise, grain, flares
- Color menu (~13 tools) — grade, contrast, white balance
- Channel menu (~7 tools) — shuffle, channel ops
- Merge menu (~5 tools) — merge, contact sheet
- Filter menu glows/blurs (~9 tools)

### Phase 3: Filter & Keyer (Week 7-10)
- Filter edges/distortions (~25 tools)
- Filter chroma/X_tools (~15 tools)
- Keyer menu (~9 tools)
- Python-backed: `VectorTracker`, `StickIt`

### Phase 4: Transform & 3D (Week 11-14)
- Transform menu (~52 tools) — matrix ops, STMap, projections
- 3D menu (~13 tools) — cards, scatter, depth
- Particles menu (~5 tools)
- Python-backed: `CardToTrack v7/v9`

### Phase 5: Deep, CG, Curves, Utilities (Week 15-18)
- Deep menu (~24 tools)
- CG menu (~29 tools)
- Curves menu (~9 tools)
- Utilities menu (~8 tools)
- Expression nodes submenu (~48 tools)

### Phase 6: Polish & Testing (Week 19-20)
- Icon assets
- Documentation
- Cross-platform testing
- Performance optimization

## Key Technical Challenges & Solutions

| Challenge | Solution |
|---|---|
| Nuke TCL expressions | Rewrite as Gaffer Expression node Python code |
| `nuke.thisNode()` / `nuke.thisGroup()` | Use `node = plug.node()` or `node.ancestor(Gaffer.ScriptNode)` |
| Dynamic path replacement (`<<<replace>>>`) | Port `GST_helper.filepathCreateNode()` to use Gaffer's `ImageReader` with context variables |
| PySide6 UI (GradientEditor) | Rewrite using GafferUI (`GafferUI.Window`, `GafferUI.Widget`) |
| Nuke knob callbacks (`addCallback`) | Use Gaffer plug signals (`plug.valueChangedSignal()`) |
| Nuke node traversal (`node.input(0)`) | Use `plug.getInput()` and `plug.outputs()` |
| Performance (Python ComputeNode) | Use internal node graphs instead of `compute()` — Gaffer team recommends this |
| Stamps integration | Optional dependency — fail silently like Nuke version |

## Naming Convention

- All custom nodes prefixed with `GST_` (Gaffer Survival Toolkit)
- Python modules: `GST_moduleName.py`
- `.gfr` files: `ToolName.gfr` (matching original tool name)
- Menu path: `GST/Category/ToolName`

## Gaffer 1.6.18.0 API Reference

### Core Operations
```python
# Create a node
import GafferScene
node = GafferScene.Sphere()
root.addChild( node )

# Rename a node
node.setName( "newName" )

# Get/set plug values
value = node["plugName"].getValue()
node["plugName"].setValue( value )

# Make a connection
destinationNode["destinationPlugName"].setInput( sourceNode["sourcePlugName"] )

# Break a connection
node["plugName"].setInput( None )

# Get a node by name
node = root["nodeName"]

# Loop over all nodes
for node in root.children( Gaffer.Node ) :
    ...

# Get selected nodes
root.selection()

# Select a node
root.selection().clear()
root.selection().add( root["nodeName"] )

# Set the current frame
root.context().setFrame( frame )

# Get the frame range
start = root["frameRange"]["start"].getValue()
end = root["frameRange"]["end"].getValue()
```

### Metadata Registration
```python
# Register a value for a plug/node
Gaffer.Metadata.registerValue( plug, "name", value )
Gaffer.Metadata.registerValue( node, "name", value )

# Query a value
Gaffer.Metadata.value( plug, "name" )
```

### Scene Operations
```python
# Get an object at a location
o = node["out"].object( "/path/to/location" )

# Get the local transform
matrix = node["out"].transform( "/path/to/location" )

# Get the world space bounding box
bound = node["out"].bound( "/path/to/location" ) * node["out"].fullTransform( "/path/to/location" )

# Get full attributes
attributes = node["out"].fullAttributes( "/path/to/location" )
```

### Custom Python Node Base Classes
- `Gaffer.DependencyNode` — basic dependency tracking
- `Gaffer.ComputeNode` — custom computation (avoid for performance)
- `GafferImage.ImageNode` — image source
- `GafferImage.ImageProcessor` — image filter (single input, single output)
- `GafferScene.SceneNode` — scene source
- `GafferScene.SceneProcessor` — scene filter
- `GafferScene.FilteredSceneProcessor` — scene filter with filter input

### GafferImage Node Reference (key nodes for porting)
- `Blur`, `Dilate`, `Erode`, `Median` — filters
- `Grade`, `Mix`, `Shuffle`, `CopyChannels`, `DeleteChannels` — color/channel
- `Constant`, `Ramp`, `Checkerboard`, `Text` — generators
- `Crop`, `Resize`, `Resample`, `Offset`, `Mirror`, `ImageTransform` — transforms
- `Merge`, `ContactSheet`, `CollectImages` — compositing
- `DeepMerge`, `DeepHoldout`, `DeepRecolor`, `DeepSampler`, `DeepToFlat` — deep
- `VectorWarp` — vector-based warping
- `ImageStats`, `ImageSampler`, `DataWindowQuery` — analysis
- `ColorSpace`, `DisplayTransform`, `LookTransform`, `LUT` — color management
- `Clamp`, `Premultiply`, `Unpremultiply` — utility

### GafferScene Node Reference (key nodes for porting)
- `Camera`, `Cube`, `Sphere`, `Plane`, `Grid` — primitives
- `Group`, `MergeScenes`, `SubTree` — scene assembly
- `Transform`, `Duplicate`, `Instancer`, `Scatter` — transforms/instances
- `ShaderAssignment`, `Attributes`, `CustomAttributes` — shading
- `PathFilter`, `SetFilter`, `FilterResults` — filtering
- `ImageToPoints`, `MeshToPoints`, `ImageScatter` — point generation
- `CopyAttributes`, `CopyPrimitiveVariables`, `ShufflePrimitiveVariables` — data transfer
- `DeleteAttributes`, `DeleteObject`, `DeletePrimitiveVariables` — deletion
- `Render`, `InteractiveRender`, `Display` — rendering

### GafferDispatch Node Reference (key nodes for porting)
- `TaskNode` — base task
- `LocalDispatcher`, `Wedge` — dispatch
- `TaskSwitch`, `TaskList` — task flow
- `PythonCommand`, `SystemCommand` — execution

## Gaffer Expression Node Syntax

Gaffer expressions use Python (not TCL like Nuke). Example:

```python
# In a Gaffer Expression node:
parent["Grade"]["black"]["r"] = parent["ImageStats"]["stats"]["min"]["r"]
parent["Grade"]["white"]["r"] = parent["ImageStats"]["stats"]["max"]["r"]
```

Context variables available in expressions:
- `context.getFrame()` — current frame
- `context["variableName"]` — custom context variables

## Installation (End User)

```python
# Add to ~/.gaffer/startup/gui/user.py:
import sys
sys.path.append( "/path/to/GafferSurvivalToolkit/python" )

# Add to GAFFER_STARTUP_PATHS:
# /path/to/GafferSurvivalToolkit/startup
```

Or run the included `install.py` which handles path setup automatically.
