##############################################################################################

# GST helper utilities:
# - Fixes file paths on created nodes that contain the <<<replace>>> token.
# - Handles Documentation menu behavior (Auto, Online, Offline, PDF).
# - Applies docs fallback order: Online -> Offline -> PDF with clear user messages.

import functools
import http.server
import socketserver
import ssl
import threading
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

import IECore

##############################################################################################


# Use Path.as_posix() to ensure forward slashes on all platforms (fixes Windows path issues)
GST_FolderPath = Path(__file__).parent.parent.as_posix()


def filepathCreateNode(script, nodeClass):
    """
    Create a Gaffer node and replace <<<replace>>> placeholders in file paths.

    In Gaffer, file-reading nodes use GafferImage.ImageReader, GafferScene.SceneReader,
    etc. This function creates the node and fixes any paths containing <<<replace>>>
    with the actual toolkit folder path.

    Args:
        script: The Gaffer ScriptNode (root of the graph)
        nodeClass: The Gaffer node class to instantiate

    Returns:
        The created node instance
    """
    import Gaffer

    node = nodeClass()
    script.addChild(node)

    # Walk all plugs on the node looking for file path plugs
    for plug in node.children(Gaffer.Plug):
        if isinstance(plug, Gaffer.StringPlug):
            value = plug.getValue()
            if value and "<<<replace>>>" in value:
                new_value = value.replace("<<<replace>>>", GST_FolderPath)
                plug.setValue(new_value)

    return node


def filepathLoadReference(script, gfrPath):
    """
    Load a .gfr file and replace <<<replace>>> placeholders in all file paths.

    Args:
        script: The Gaffer ScriptNode
        gfrPath: Path to the .gfr file to load

    Returns:
        List of nodes loaded from the file
    """
    import Gaffer

    # Get the set of existing nodes before loading
    existing = set(n for n in script.children(Gaffer.Node))

    # Load the .gfr file
    script.importFile(gfrPath)

    # Find newly added nodes
    new_nodes = [n for n in script.children(Gaffer.Node) if n not in existing]

    # Fix file paths in all new nodes
    for node in new_nodes:
        _fixNodeFilePaths(node)

    return new_nodes


def _fixNodeFilePaths(node):
    """Recursively fix <<<replace>>> placeholders in a node's string plugs."""
    import Gaffer

    for plug in node.children(Gaffer.Plug):
        if isinstance(plug, Gaffer.StringPlug):
            value = plug.getValue()
            if value and "<<<replace>>>" in value:
                new_value = value.replace("<<<replace>>>", GST_FolderPath)
                plug.setValue(new_value)


##############################################################################################
##############################################################################################
### Documentation configuration
# Values are configured in GST_menu.py and assigned onto this module:
# - GST_DOCS_ONLINE_URL
# - GST_DOCS_ONLINE_TIMEOUT_SECONDS
# - GST_DOCS_PDF_NAME
# - GST_DOCS_OFFLINE_INDEX

##############################################################################################
##############################################################################################

# Section to Handle Documentation Logic: Online -> Offline -> PDF


def _toolkit_root():
    return Path(GST_FolderPath)


def find_offline_index():
    # Offline wiki is installed in one canonical location.
    # Checking if it's available.
    doc_path = _toolkit_root() / GST_DOCS_OFFLINE_INDEX
    if doc_path.is_file():
        return doc_path
    return None


def find_pdf_doc():
    # PDF path is explicit; when docs release changes, update GST_DOCS_PDF_NAME.
    # Checking if it's available.
    pdf_path = _toolkit_root() / GST_DOCS_PDF_NAME
    if pdf_path.is_file():
        return pdf_path

    return None


# Local HTTP server for offline MkDocs (Material search / workers do not work reliably on file://).
_httpd = None
_httpd_thread = None
_served_root = None


class _ReusableThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


class _QuietStaticHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Same as SimpleHTTPRequestHandler but does not print one line per request to stderr."""

    def log_message(self, format, *args):
        pass


def _shutdown_offline_http_server():
    """Stop the background http.server if it was started."""
    global _httpd, _httpd_thread, _served_root
    if _httpd is None:
        return
    httpd = _httpd
    thread = _httpd_thread
    _httpd = None
    _httpd_thread = None
    _served_root = None
    try:
        httpd.shutdown()
    except Exception:
        pass
    if thread is not None and thread.is_alive():
        thread.join(timeout=2.0)


def _ensure_local_http_server(root):
    """Serve root on 127.0.0.1 with an ephemeral port; reuse if already serving same path."""
    global _httpd, _httpd_thread, _served_root
    root = Path(root).resolve()
    if (
        _httpd is not None
        and _httpd_thread is not None
        and _httpd_thread.is_alive()
        and _served_root == root
    ):
        return _httpd.server_address[1]
    _shutdown_offline_http_server()
    handler = functools.partial(_QuietStaticHTTPRequestHandler, directory=str(root))
    _httpd_local = _ReusableThreadingTCPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=_httpd_local.serve_forever, daemon=True)
    thread.start()
    _httpd = _httpd_local
    _httpd_thread = thread
    _served_root = root
    return _httpd.server_address[1]


def _open_url_in_browser_async(url):
    """
    Open the system browser without blocking Gaffer's main thread.
    webbrowser.open can stall the UI while the OS launches or hands off to the browser.
    """

    def _run():
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=_run, daemon=True).start()


def _open_offline_index_in_browser(offline_index):
    """
    Open offline wiki in the default browser. Prefer http://127.0.0.1 so MkDocs search works;
    fall back to file:// if the local server cannot start.
    """
    try:
        port = _ensure_local_http_server(offline_index.parent)
        _open_url_in_browser_async(f"http://127.0.0.1:{port}/")
    except Exception:
        _open_url_in_browser_async(offline_index.as_uri())


def is_online_wiki_reachable(timeout=None):
    if timeout is None:
        timeout = globals().get("GST_DOCS_ONLINE_TIMEOUT_SECONDS", 1.5)
    # Short preflight check prevents dead-clicks when the site is blocked/unreachable.
    # Some environments/proxies reject HEAD while allowing GET, so always fall back to GET
    # before returning False.
    # If Python's SSL trust store cannot validate certs, treat as reachable and let the
    # user's browser handle HTTPS trust (avoids false PDF fallback).
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(
            GST_DOCS_ONLINE_URL,
            headers={"User-Agent": "GafferSurvivalToolkit"},
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout):
                return True
        except urllib.error.HTTPError:
            if method == "HEAD":
                continue
            return False
        except urllib.error.URLError as error:
            if isinstance(getattr(error, "reason", None), ssl.SSLCertVerificationError):
                return True
            if method == "HEAD":
                continue
            return False
        except ValueError:
            if method == "HEAD":
                continue
            return False
    return False


def openGSTDocumentationDefault():
    # Auto fallback order: Online -> Offline -> PDF
    # Note: this runs HTTPS reachability checks first (can block up to ~timeout per attempt).
    # Use "Wiki (Offline)" when you have no network to skip that step.
    if is_online_wiki_reachable():
        webbrowser.open(GST_DOCS_ONLINE_URL)
        return

    offline_index = find_offline_index()
    if offline_index:
        _open_offline_index_in_browser(offline_index)
        return

    pdf_doc = find_pdf_doc()
    if pdf_doc:
        webbrowser.open(pdf_doc.as_uri())
        return

    _showMessage(
        "No documentation source was found.\n"
        "Use 'Wiki (Online)', or unzip GST_Documentation_Release_x.y.z.zip into "
        "GafferSurvivalToolkit/GST_Documentation, or place a documentation PDF in the toolkit root."
    )


def openGSTDocumentationOnline():
    # Online command stays direct: no fallback, just clear guidance if unreachable.
    if is_online_wiki_reachable():
        webbrowser.open(GST_DOCS_ONLINE_URL)
        return

    _showMessage(
        "Online wiki is not reachable right now.\nTry 'Wiki (Offline)' or 'Docs (PDF)'."
    )


def openGSTDocumentationOffline():
    # Offline command opens canonical local index only.
    offline_index = find_offline_index()
    if offline_index:
        _open_offline_index_in_browser(offline_index)
        return

    _showMessage(
        "Offline wiki not found.\n"
        "Unzip GST_Documentation_Release_x.y.z.zip into GafferSurvivalToolkit so "
        "GST_Documentation/index.html exists."
    )


def openGSTDocumentationPDF():
    # PDF command opens one explicit release PDF path.
    pdf_doc = find_pdf_doc()
    if pdf_doc:
        webbrowser.open(pdf_doc.as_uri())
        return

    _showMessage(
        "Documentation PDF not found in toolkit root.\n"
        "Try 'Wiki (Online)' or install the optional offline docs release ZIP."
    )


def _showMessage(text):
    """Show a message to the user. Uses IECore.msg for console output."""
    IECore.msg(IECore.Msg.Level.Info, "GST_helper", text)


##############################################################################################
