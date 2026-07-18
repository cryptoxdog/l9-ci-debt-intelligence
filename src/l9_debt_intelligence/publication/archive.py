from __future__ import annotations

import gzip
import io
import tarfile
from collections.abc import Iterable
from pathlib import Path


def build_deterministic_archive(
    *,
    source_root: Path,
    members: Iterable[Path],
    destination: Path,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    with tarfile.open(
        fileobj=buffer,
        mode="w",
        format=tarfile.PAX_FORMAT,
    ) as archive:
        for relative in sorted(
            members,
            key=lambda path: path.as_posix(),
        ):
            source = source_root / relative
            if not source.is_file():
                raise FileNotFoundError(source)
            content = source.read_bytes()
            info = tarfile.TarInfo(relative.as_posix())
            info.size = len(content)
            info.mode = 0o644
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mtime = 0
            info.pax_headers = {}
            archive.addfile(info, io.BytesIO(content))
    buffer.seek(0)
    with destination.open("wb") as stream:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=stream,
            mtime=0,
            compresslevel=9,
        ) as compressed:
            compressed.write(buffer.getvalue())
