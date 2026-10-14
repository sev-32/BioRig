#!/usr/bin/env python3
"""Relate V010 *geometric direct* moment arms at R590 t12 to V011 full dynamical responses."""
from pathlib import Path
import csv,gzip,io,zipfile,json,hashlib
import numpy as np
from build_v011 import ROOT,write_json
p010=Path('/mnt/data/BioRig_LUCID_SEMANTIC_ATLAS_V010_NATIVE_84x102_MECHANICAL_RELATIONSHIPS_2026-10-13.zip')
p011=ROOT/'ALL_84x102_NATIVE_CONTROL_TO_DOF_TIME_RESPONSE.npz'
with zipfile.ZipFile(p010) as z:
 b=z.read('V010/NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz')
 with np.load(io.BytesIO(b)) as d:
  print('matrix keys:',d.files)
  for k in d.files:print(k,d[k].shape,d[k].dtype)
with np.load(io.BytesIO(b)) as d:
 moment=d['momentJacobian'][1].copy()
 ac=d['actuatorNames'].copy();dofs=d['dofNames'].copy()
 assert d['cases'][1]=='continuous_12to24' and abs(float(d['sourceTimesS'][1])-12.0)<1e-9
with np.load(p011) as x:
 assert np.array_equal(ac,x['inputActuatorNames'])
 vel=x['delta_velocity_84x3x102'].copy()
 delta=x['delta_position_tangent_84x3x102'].copy()
 times=x['samplesAfterStartS'].copy()
 assert np.allclose(times,[.06,.12,.20])
fields=['actuatorID','actuatorName','dofID','dofName','geometricDirectMomentAtT12','directAbove1eMinus6','deltaDofVelocityT006','deltaDofVelocityT012','deltaDofVelocityT020','deltaDofPositionT020','dynamicAbove1eMinus2AtT020','directOnlyAtStart','dynamicOnlyAtT020']
counts={'allEdges':84*102,'geometricDirectInitial':0,'dynamicAtT020Above1eMinus2':0,'dynamicWithNoGeometricMomentAtInitialT020':0,'directGeometricWithoutLargeVelocityAtT020':0}
file=ROOT/'V010_V011_8568_DIRECT_VS_DYNAMICAL_COUPLING.csv.gz'
with gzip.open(file,'wt',newline='',compresslevel=9) as f:
 w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
 for i in range(84):
  for j in range(102):
   direct=abs(moment[i,j])>1e-6
   observed=abs(vel[i,2,j])>1e-2
   counts['geometricDirectInitial']+=int(direct)
   counts['dynamicAtT020Above1eMinus2']+=int(observed)
   counts['dynamicWithNoGeometricMomentAtInitialT020']+=int(observed and not direct)
   counts['directGeometricWithoutLargeVelocityAtT020']+=int(direct and not observed)
   w.writerow(dict(actuatorID=i,actuatorName=str(ac[i]),dofID=j,dofName=str(dofs[j]),
    geometricDirectMomentAtT12=float(moment[i,j]),directAbove1eMinus6=int(direct),
    deltaDofVelocityT006=float(vel[i,0,j]),deltaDofVelocityT012=float(vel[i,1,j]),deltaDofVelocityT020=float(vel[i,2,j]),
    deltaDofPositionT020=float(delta[i,2,j]),dynamicAbove1eMinus2AtT020=int(observed),
    directOnlyAtStart=int(direct and not observed),dynamicOnlyAtT020=int(observed and not direct)))
counts.update({
 'sourceV010NPZSHA256':hashlib.sha256(b).hexdigest(),
 'sourceV011NPZSHA256':hashlib.sha256(p011.read_bytes()).hexdigest(),
 'sourceGeometricPose':'R590 uninterrupted physical state t12.000s, matched to V011 start',
 'outputFileSHA256':hashlib.sha256(file.read_bytes()).hexdigest(),
 'outputFileBytes':file.stat().st_size,
 'interpretation':'Comparison is geometric-direct at t12 vs full-body dynamical+contact effect after 0.20s, not proof of a constant linear transfer relation',
 'thresholdCaution':'Mixed translation/rotation velocity coordinate units; 0.01 is numeric reporting threshold, not calibrated significance or biological threshold',
})
write_json(ROOT/'V010_V011_MECHANICAL_DYNAMIC_BRIDGE_RECEIPT.json',counts)
print(json.dumps(counts,indent=2))
