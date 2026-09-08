"""Local filesystem storage abstraction.

Every caller addresses files by a logical ``key`` (e.g.
``"projects/<id>/final_mesh.ply"``), never a filesystem path. Swapping in
an S3-compatible backend later means implementing this same
:class:`StorageBackend` interface -- no caller code changes.
"""

from __future__ import annotations

import hashlib
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO

from app.core.config import settings


class StorageError(Exception):
    pass


class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, fileobj: BinaryIO) -> tuple[int, str]:
        """Write ``fileobj`` to ``key``. Returns (size_bytes, sha256_hex)."""

    @abstractmethod
    def open(self, key: str) -> BinaryIO:
        ...

    @abstractmethod
    def path_for(self, key: str) -> Path:
        """A real filesystem path for ``key`` -- for internal use only
        (e.g. handing a path to the processing engine). Never return this
        to a client."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        ...

    @abstractmethod
    def delete_prefix(self, prefix: str) -> None:
        ...


def _safe_join(root: Path, key: str) -> Path:
    """Resolve ``key`` under ``root``, rejecting any path-traversal attempt."""
    candidate = (root / key).resolve()
    root_resolved = root.resolve()
    if root_resolved not in candidate.parents and candidate != root_resolved:
        raise StorageError(f"Rejected unsafe storage key: {key!r}")
    return candidate


class LocalStorage(StorageBackend):
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or settings.storage_root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, fileobj: BinaryIO) -> tuple[int, str]:
        path = _safe_join(self.root, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        hasher = hashlib.sha256()
        size = 0
        with path.open("wb") as out:
            while chunk := fileobj.read(1024 * 1024):
                out.write(chunk)
                hasher.update(chunk)
                size += len(chunk)
        return size, hasher.hexdigest()

    def open(self, key: str) -> BinaryIO:
        path = _safe_join(self.root, key)
        if not path.exists():
            raise StorageError(f"No such storage object: {key!r}")
        return path.open("rb")

    def path_for(self, key: str) -> Path:
        return _safe_join(self.root, key)

    def exists(self, key: str) -> bool:
        try:
            return _safe_join(self.root, key).exists()
        except StorageError:
            return False

    def delete_prefix(self, prefix: str) -> None:
        target = _safe_join(self.root, prefix)
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
        elif target.exists():
            target.unlink()


storage: StorageBackend = LocalStorage()
