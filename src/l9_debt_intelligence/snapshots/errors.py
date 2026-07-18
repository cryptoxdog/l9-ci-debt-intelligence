from __future__ import annotations


class SnapshotError(RuntimeError):
    """Base error for immutable corpus snapshots."""


class SnapshotSourceError(SnapshotError):
    """The ingestion source is missing or invalid."""


class SnapshotCollisionError(SnapshotError):
    """An immutable snapshot path already contains different content."""


class SnapshotVerificationError(SnapshotError):
    """A snapshot failed integrity or semantic verification."""
