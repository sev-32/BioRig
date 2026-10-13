#!/usr/bin/env python3
"""Compact archive: preserve V009 and all ancestors byte-for-byte; no assets or wheel."""
from pathlib import Path
import hashlib,json,zipfile
root=Path('/mnt/data');work=root/'BioRig_SEMANTIC_ATLAS_010'
prev=root/'BioRig_LUCID_SEMANTIC_ATLAS_V009_MUSCLE_COMMAND_AUTHORITY_2026-10-13.zip'
out=root/'BioRig_LUCID_SEMANTIC_ATLAS_V010_NATIVE_84x102_MECHANICAL_RELATIONSHIPS_2026-10-13.zip'
with zipfile.ZipFile(prev) as z:assert z.testzip() is None
files=sorted(x for x in work.iterdir() if x.is_file() and not x.name.startswith('.'))
receipt={'schema':'biorig.semantic-atlas.v010-delivery','preserves':{'name':prev.name,'sha256':hashlib.sha256(prev.read_bytes()).hexdigest(),'bytes':prev.stat().st_size},
 'files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
 'runtimeDistributionEmbedded':False,'noSimulationSourceChanged':True,'noGitHubActions':True}
(work/'DELIVERY_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=sorted(x for x in work.iterdir() if x.is_file() and not x.name.startswith('.'))
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
 z.write(prev,'PRESERVED_PREVIOUS/'+prev.name,compress_type=zipfile.ZIP_STORED)
 for p in files:z.write(p,'V010/'+p.name)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert z.read('PRESERVED_PREVIOUS/'+prev.name)==prev.read_bytes()
 for p in files:assert z.read('V010/'+p.name)==p.read_bytes()
 assert len(z.namelist())==len(files)+1
assert out.stat().st_size<30_000_000
print(json.dumps({'result':'PASS','file':out.name,'bytes':out.stat().st_size,'entries':len(files)+1,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
