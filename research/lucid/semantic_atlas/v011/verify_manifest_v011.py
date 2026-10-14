#!/usr/bin/env python3
"""Check V011 sealed evidence hashes, with a portable nested-V010 fallback."""
import json,hashlib,zipfile
from pathlib import Path
folder=Path(__file__).resolve().parent
manifest=json.loads((folder/'V011_PACKAGE_MANIFEST.json').read_text())
for item in manifest['v011files']:
 p=folder/item['path'];assert p.is_file(),p
 assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],item['path']
fn=manifest['preservedV010']['filename']
archives=[folder.parent/'PRESERVED_PREVIOUS'/fn,Path('/mnt/data')/fn]
archive=next((x for x in archives if x.is_file()),None)
assert archive is not None, f'missing verbatim previous V010 ZIP, tried {archives}'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['preservedV010']['sha256']
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('PASS',len(manifest['v011files']),'V011 files; preserved V010',manifest['preservedV010']['sha256'])
