#!/usr/bin/env python3
"""Restore original LUCID research archives offline without changing input bytes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

R574_SHA256 = "21e0c354023badd40485840296e09034809ae4eb055fd926eff39ac0b8700701"

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def extract_checked(archive: Path, destination: Path, prefix: str | None = None) -> int:
    count = 0
    destination = destination.resolve()
    with ZipFile(archive) as z:
        corrupt = z.testzip()
        if corrupt is not None:
            raise ValueError(f"corrupt archive entry: {corrupt}")
        for item in z.infolist():
            name = PurePosixPath(item.filename)
            if (name.is_absolute() or '..' in name.parts or not name.parts
                    or '\\' in item.filename):
                raise ValueError(f"unsafe archive entry: {item.filename}")
            if item.is_dir() or (prefix and not item.filename.startswith(prefix)):
                continue
            target = destination.joinpath(*name.parts)
            if not target.resolve().is_relative_to(destination):
                raise ValueError(f"ZIP traversal: {item.filename}")
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                if hashlib.sha256(target.read_bytes()).digest() != hashlib.sha256(z.read(item)).digest():
                    raise FileExistsError(f"refuse to overwrite changed file: {target}")
            else:
                with z.open(item) as src, target.open('wb') as dst:
                    while chunk := src.read(1024 * 1024):
                        dst.write(chunk)
            count += 1
    return count

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--r574', type=Path, required=True)
    parser.add_argument('--r575', type=Path, required=True)
    parser.add_argument('--destination', type=Path, default=Path('runtime'))
    parser.add_argument('--r574-only-research', action='store_true',
                        help='Exclude inherited base; NOT enough for native replay')
    args = parser.parse_args()
    if digest(args.r574) != R574_SHA256:
        raise ValueError('R574 original SHA-256 mismatch: aborting')
    prefix = 'R574_INTENTION_AND_AVERSION/' if args.r574_only_research else None
    n574 = extract_checked(args.r574, args.destination, prefix)
    n575 = extract_checked(args.r575, args.destination)
    record = {
        'schema': 'biorig.lucid.archive-intake.v1',
        'R574_SHA256': digest(args.r574), 'R575_SHA256': digest(args.r575),
        'R574_extracted_count': n574, 'R575_extracted_count': n575,
        'r574_only_research': args.r574_only_research,
        'ready_for_native_physics': not args.r574_only_research,
    }
    receipt = args.destination / 'BIORIG_IMPORT_RECEIPT.json'
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(json.dumps(record, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
