from urllib.parse import urlparse
import os

__all__ = ["uri_from_fname", "fname_from_uri"]


def uri_from_fname(fname: str) -> str:
    fullpath = os.path.abspath(fname)
    # Convert paths on windows
    if os.name == "nt":
        # FIXME
        pass
    return "file://{}".format(fullpath)


def fname_from_uri(uri: str, root: str = None) -> str:
    parsed = urlparse(uri)
    if parsed.scheme != "file":
        return uri
    if os.name == "nt":
        # FIXME
        pass
    path = parsed.path
    if root is not None:
        path = os.path.relpath(path, root)
    return path
