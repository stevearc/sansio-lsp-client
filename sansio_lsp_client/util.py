from urllib.parse import urlparse
from collections import UserDict
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


class PathDict(UserDict):
    def __getitem__(self, key):
        if key == "" and key not in self.data:
            return self.data
        pieces = key.split(".")
        cur = self.data
        for piece in pieces:
            cur = cur[piece]
        return cur

    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, TypeError):
            return default
