##############################################################################################

# GST_nodeDefinitions.py — Custom Python node registrations
# This script runs on Gaffer GUI startup and registers custom Python-defined nodes.

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

# Register custom Python nodes
registered_nodes = []

# 1. GST_IDExtractor — ID matte extraction
try:
    from GST_ID_Extractor import GST_IDExtractor

    registered_nodes.append("GST_IDExtractor")
    print("[GST] Registered GST_IDExtractor node")
except ImportError as e:
    print(f"[GST] Could not load GST_ID_Extractor: {e}")

# 2. GST_VectorTracker — Vector-based tracking
try:
    from GST_VectorTracker import GST_VectorTracker

    registered_nodes.append("GST_VectorTracker")
    print("[GST] Registered GST_VectorTracker node")
except ImportError as e:
    print(f"[GST] Could not load GST_VectorTracker: {e}")

# 3. GST_CardToTrack — Card-to-track conversion (v7)
try:
    from GST_cardToTrack import GST_CardToTrack

    registered_nodes.append("GST_CardToTrack")
    print("[GST] Registered GST_CardToTrack node")
except ImportError as e:
    print(f"[GST] Could not load GST_cardToTrack: {e}")

# 4. GST_CardToTrack_v9 — Enhanced card-to-track (v9)
try:
    from GST_cardToTrack_v9 import GST_CardToTrack_v9

    registered_nodes.append("GST_CardToTrack_v9")
    print("[GST] Registered GST_CardToTrack_v9 node")
except ImportError as e:
    print(f"[GST] Could not load GST_cardToTrack_v9: {e}")

# 5. GST_StickIt — Surface projection / motion transfer
try:
    from GST_stickit import GST_StickIt

    registered_nodes.append("GST_StickIt")
    print("[GST] Registered GST_StickIt node")
except ImportError as e:
    print(f"[GST] Could not load GST_stickit: {e}")

# 6. GST_GradientEditor — Interactive gradient editor (UI widget)
try:
    from GST_GradientEditor import GST_GradientEditor

    registered_nodes.append("GST_GradientEditor")
    print("[GST] Registered GST_GradientEditor widget")
except ImportError as e:
    print(f"[GST] Could not load GST_GradientEditor: {e}")

# Summary
if registered_nodes:
    print(
        f"[GST] Successfully registered {len(registered_nodes)} custom nodes: {', '.join(registered_nodes)}"
    )
else:
    print("[GST] Warning: No custom nodes were registered")
