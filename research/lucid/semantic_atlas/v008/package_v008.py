#!/usr/bin/env python3
"""Create an append-only verified code/docs semantic checkpoint (V007 embedded unchanged)."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path('/mnt/data');HERE=ROOT/'BioRig_SEMANTIC_ATLAS_008'
prev=ROOT/'BioRig_LUCID_SEMANTIC_ATLAS_V007_GOAL_MUSCLE_ONTOLOGY_CONTRACTS_2026-10-13.zip'
out=ROOT/'BioRig_LUCID_SEMANTIC_ATLAS_V008_CONTROLLER_AUTHORITY_AND_STATE_LIFECYCLE_2026-10-13.zip'
assert prev.is_file()
files=sorted([p for p in HERE.iterdir() if p.is_file() and p.name not in ('DELIVERY_RECEIPT.json','package_v008.py')]);files.append(HERE/'package_v008.py')
file_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
manifest={'schema':'lucid.semantic-atlas.v008-package','predecessor':prev.name,'predecessorSHA256':hashlib.sha256(prev.read_bytes()).hexdigest(),'sourceRoot':'BioRig_SEMANTIC_ATLAS_008/','filesSHA256':file_hashes,'boundaries':['Source-exact AST documentation only','No MuJoCo runtime result from V008','No rendered image claimed','No original model/controller modified']}
(HERE/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
files=sorted([p for p in HERE.iterdir() if p.is_file() and p.name!='DELIVERY_RECEIPT.json'])
with zipfile.ZipFile(out,'w') as z:
 z.write(prev,'PREVIOUS/'+prev.name,compress_type=zipfile.ZIP_STORED)
 for p in files:z.write(p,'V008/'+p.name,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert z.read('PREVIOUS/'+prev.name)==prev.read_bytes()
 for p in files:assert z.read('V008/'+p.name)==p.read_bytes()
 assert out.stat().st_size < 30_000_000
 receipt={'file':out.name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'entries':len(z.namelist()),'crcVerified':True,'v007PreservedByteExact':True,'localVerifier':'PASS','noGitHubActions':True}
(HERE/'DELIVERY_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
