#!/usr/bin/env python3
"""Seal small code/documentation + original computed numeric evidence; preserve exact V010.
No historical simulation executable/source or model binaries bundled again."""
from pathlib import Path
import hashlib,zipfile,json,os
here=Path(__file__).resolve().parent
prev=Path('/mnt/data/BioRig_LUCID_SEMANTIC_ATLAS_V010_NATIVE_84x102_MECHANICAL_RELATIONSHIPS_2026-10-13.zip')
target=Path('/mnt/data/BioRig_LUCID_SEMANTIC_ATLAS_V011_NATIVE_TIME_DEPENDENT_CAUSAL_MATRIX_2026-10-13.zip')
names=['README.md','ACTIVATION_TO_CONTACT_CAUSAL_PAPER.md','build_v011.py','scan_all84_v011.py','build_mechanical_dynamic_bridge.py','verify_v011.py','verify_manifest_v011.py','package_v011.py','NATIVE_84_MUSCLE_CAUSAL_TIME_TRACES.npz','ALL_84x102_NATIVE_CONTROL_TO_DOF_TIME_RESPONSE.npz','PULSED_ACTUATOR_NATIVE_DIFFERENTIAL_EFFECTS.csv','ALL_84_CHANNEL_NATIVE_DYNAMIC_EFFECTS.csv','V010_V011_8568_DIRECT_VS_DYNAMICAL_COUPLING.csv.gz','V011_NATIVE_DYNAMIC_VERIFICATION.json','V011_FULL84_RESPONSE_RECEIPT.json','V010_V011_MECHANICAL_DYNAMIC_BRIDGE_RECEIPT.json','V011_INDEPENDENT_VERIFICATION.json']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
manifest={
 'schema':'biorig.semantic-atlas.v011.integrity-manifest',
 'V011':'Native pulse-to-muscle-activation-to-force-to-dynamics and seat contact audit; no intentional motor policy',
 'inputPreservation':'V010 nested verbatim. Source SHA256 references pinned original R574 and R590 archives. No model assets duplicated.',
 'preservedV010':{'filename':prev.name,'sha256':sha(prev),'bytes':prev.stat().st_size},
 'v011files':[{'path':name,'sha256':sha(here/name),'bytes':(here/name).stat().st_size} for name in names],
 'verifiedNativeCases':85,'nativeStepsPerCase':100,'independentlyReintegratedStates':255,'sourceCasesWithHighRateTracing':4,
 'causalEdgesPerMatrix':8568,'timeSamplesPerEdge':3,'allUnprovenRelationshipsExplicitlyUnknown':True,
 'originalBioRigCodeEdited':False,'GitHubActionsUsed':False
}
(here/'V011_PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7,allowZip64=True) as z:
 z.write(prev,f'PRESERVED_PREVIOUS/{prev.name}',compress_type=zipfile.ZIP_STORED)
 for n in names+['V011_PACKAGE_MANIFEST.json']:z.write(here/n,'V011/'+n)
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(names)+2
 nested=z.read(f'PRESERVED_PREVIOUS/{prev.name}');assert hashlib.sha256(nested).hexdigest()==manifest['preservedV010']['sha256']
 for item in manifest['v011files']:assert hashlib.sha256(z.read('V011/'+item['path'])).hexdigest()==item['sha256']
assert target.stat().st_size<=30000000
receipt={'archive':target.name,'sha256':sha(target),'bytes':target.stat().st_size,'totalEntries':len(names)+2,'nestedPreviousSHA256':sha(prev),'zipCRC':'PASS','v011SHA256':'PASS','sizeLimit30MB':'PASS'}
(here/'V011_DELIVERY_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,indent=2))
