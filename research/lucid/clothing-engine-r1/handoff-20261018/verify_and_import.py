#!/usr/bin/env python3
"""Verify the exact LUCID Clothing Engine clean handoff; extract only on request."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import sys
import zipfile

NAME = "LUCID_CLOTHING_ENGINE_CLEAN_HANDOFF_20261018"
ARCHIVE_SHA256 = "738ffaa2db9c727c3b4ce331269e989c166c3b3b1ccff73c73407d457f24a047"
MAX_UNCOMPRESSED_BYTES = 150_000_000


def hash_stream(stream):
    digest = hashlib.sha256()
    for piece in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(piece)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip", type=Path, help="Exact separately supplied clean archive")
    parser.add_argument("--extract", type=Path, help="Extract only after all checks pass")
    args = parser.parse_args()
    with args.zip.open("rb") as stream:
        digest = hash_stream(stream)
    if digest != ARCHIVE_SHA256:
        raise ValueError(f"Wrong ZIP SHA-256: {digest} (expected {ARCHIVE_SHA256})")
    prefix = NAME + "/"
    with zipfile.ZipFile(args.zip, "r") as z:
        members = z.infolist()
        if sum(m.file_size for m in members) > MAX_UNCOMPRESSED_BYTES:
            raise ValueError("Expanded file size exceeds defensive limit")
        names = set()
        for m in members:
            path = PurePosixPath(m.filename)
            if (not m.filename.startswith(prefix) or "\\" in m.filename
                    or "//" in m.filename or any(x in (".", "..") for x in path.parts)
                    or (m.external_attr >> 16) & stat.S_IFMT(0o777777) == stat.S_IFLNK):
                raise ValueError(f"Unsafe ZIP path/type: {m.filename!r}")
            if m.filename in names:
                raise ValueError(f"Duplicate ZIP member: {m.filename}")
            names.add(m.filename)
        if z.testzip() is not None:
            raise ValueError("ZIP CRC validation failed")
        manifest = json.loads(z.read(prefix + "MANIFEST_SHA256.json"))
        entries = manifest["files"]
        expected = {prefix + e["path"]: e for e in entries}
        actual = {m.filename for m in members if not m.is_dir()} - {prefix + "MANIFEST_SHA256.json"}
        if actual != set(expected) or manifest["file_count"] != len(expected):
            raise ValueError(f"Manifest file-set mismatch: {len(actual)} actual vs {len(expected)} expected")
        for filename, spec in expected.items():
            if z.getinfo(filename).file_size != spec["size_bytes"]:
                raise ValueError(f"Size mismatch: {filename}")
            with z.open(filename) as f:
                if hash_stream(f) != spec["sha256"]:
                    raise ValueError(f"SHA-256 mismatch: {filename}")
        if args.extract is not None:
            dest = args.extract.resolve()
            if dest.exists() and any(dest.iterdir()):
                raise ValueError(f"Extraction destination is not empty: {dest}")
            dest.mkdir(parents=True, exist_ok=True)
            z.extractall(dest)
    print(json.dumps({"verified": True, "archive_sha256": digest,
                      "verified_files": len(expected), "extracted_to": str(args.extract.resolve()) if args.extract else None}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
