#!/usr/bin/env python3
"""Independent native MuJoCo reconstruction against V010 indexed numerical evidence.
Never mutates the pinned source/archive/previous checkpoint.
"""
from __future__ import annotations
import os,sys,json,hashlib,zipfile,io,csv,gzip
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data');OUT=ROOT/'BioRig_SEMANTIC_ATLAS_010';BASE=OUT/'runtime'/'LUCID_R552_WORKSPACE'
sys.path[:0]=[str(OUT/'.pydeps'),str(BASE/'BIOMECH_CAUSAL_RIG'),str(BASE/'R543_MULTICONTACT_LEARNING'),str(BASE/'R541_DEVELOPMENTAL_CURRICULUM'),str(BASE/'R542_MOTOR_LEARNING')]
import mujoco as mj
from run_r543 import make_body,reset
from lucid_bcr.contact_flight_r46 import muscle_moment_matrix
from lucid_bcr.assets import verify_sources

rec=json.loads((OUT/'NATIVE_84x102_AND_94_STATE_RECEIPT.json').read_text())
assert rec['muJoCoVersion']==mj.__version__=='3.15.0'
assert rec['assetSourceLocksMatch'] and len(verify_sources())==13
archive=ROOT/'BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==rec['r590NumericalSourceArchiveSha256']
with zipfile.ZipFile(archive) as z:
 inputs={}
 for k,info in rec['sourcePoseSnapshots'].items():
  b=z.read(info['sourceMember']);assert hashlib.sha256(b).hexdigest()==info['sha256']
  f=np.load(io.BytesIO(b));inputs[k]={s:f[s].copy() for s in f.files}

with np.load(OUT/'NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz') as raw:
 matrix=raw['momentJacobian'].copy(); labels=raw['cases'].tolist(); times=raw['sourceTimesS'].tolist()
 actnames=raw['actuatorNames'].tolist();jnames=raw['dofNames'].tolist()
assert matrix.shape==(94,84,102)
with (OUT/'NATIVE_84_ACTUATOR_NUMERIC_IDENTITY.json').open() as f: actuator_json=json.load(f)
assert len(actuator_json)==84
assert [r['name'] for r in actuator_json]==actnames
with (OUT/'NATIVE_102_DOF_SEMANTIC_INDEX.csv').open() as f: dof_rows=list(csv.DictReader(f))
assert len(dof_rows)==102 and [r['jointName'] for r in dof_rows]==jnames
assert max(np.abs(matrix[:,:,:6]).flat)<1e-10
cases=['cold_seated_reset','continuous_12to24','restart_no_push','restart_plus120N']
assert [labels.count(x) for x in cases]==[1,31,31,31]
assert rec['matrixShape']==[94,84,102] and rec['momentEntries']==matrix.size
with gzip.open(OUT/'ALL_8568_MUSCLE_TO_DOF_MECHANICAL_EDGES.csv.gz','rt') as f: edge_rows=list(csv.DictReader(f))
assert len(edge_rows)==84*102
for row in edge_rows:
 i=int(row['muscleIndex']);j=int(row['dofIndex']);v=matrix[:,i,j]
 assert abs(float(row['minAcrossSavedStates'])-float(v.min()))<1e-14
 assert abs(float(row['maxAcrossSavedStates'])-float(v.max()))<1e-14
 assert int(row['above1eMinus6StateCount'])==int(np.sum(np.abs(v)>1e-6))
 assert row['muscleName']==actnames[i] and row['jointName']==jnames[j]
assert sum(int(r['above1eMinus6StateCount'])>0 for r in edge_rows)==rec['everNonzeroAcrossAllStates']==334

# Recreate a fresh native body. Do not import the V010 computation function.
pb=make_body('seated');m=pb.model;d=pb.data
for side in ['left','right']:
 site=mj.mj_name2id(m,mj.mjtObj.mjOBJ_SITE,f's_{side}_sternocleidomastoid_1')
 assert site>=0;m.site_pos[site,2]=-.025
m.opt.noslip_iterations=6;m.opt.noslip_tolerance=1e-6
reset(pb)
assert (m.nu,m.na,m.nq,m.nv,m.ngeom)==(84,84,103,102,117)
for a in actuator_json:
 i=a['muJoCoIndex'];name=mj.mj_id2name(m,mj.mjtObj.mjOBJ_ACTUATOR,i)
 assert name==a['name'] and int(m.actuator_actadr[i])==a['activationIndex']
actual=[];force_resids=[]
def visit(case,t):
 mj.mj_forward(m,d)
 A=muscle_moment_matrix(d,m.nu,m.nv)
 if case=='continuous_12to24':
  err=float(np.max(np.abs(A.T@d.actuator_force-d.qfrc_actuator)))
  assert err<1e-9
  force_resids.append(err)
 actual.append(A)
visit('cold_seated_reset',0)
for label,key in [('continuous_12to24','continuous'),('restart_no_push','restart_no_push'),('restart_plus120N','restart_plus120N')]:
 state=inputs[key]
 for index in range(31):
  d.qpos[:]=state['qpos'][index]
  if 'qvel' in state:d.qvel[:]=state['qvel'][index]
  else:d.qvel[:]=0.
  if 'act' in state:d.act[:]=state['act'][index]
  else:d.act[:]=0.
  d.time=float(state['timeS'][index])+(12 if key.startswith('restart_') else 0)
  visit(label,state['timeS'][index])
actual=np.stack(actual)
maxerror=float(np.max(np.abs(matrix-actual)))
assert maxerror<1e-12,maxerror
assert len(force_resids)==31
assert abs(max(force_resids)-rec['nativeGeneralizedForceProjection']['maxAbsReconstructionResidual'])<1e-12
result={'schema':'biorig.semantic-atlas.v010.independent-verification','result':'PASS','sourceArchivesSHA256Match':True,
 'originalAssetLocksVerified':13,'freshModelDimensionsVerified':True,'nativeRowsVerified':84,'nativeDofsVerified':102,
 'frameMatricesRecomputed':94,'floatingPointCellsIndependentlyCompared':805392,
 'maximumAbsoluteJacobianDifference':maxerror,'muscleToDofEdgesVerified':8568,
 'forceMappingStatesChecked':31,'maximumAbsoluteGeneralizedForceReconstructionResidual':max(force_resids),
 'noNativeTrajectoriesIntegrated':True,'simulationSourceEdited':False,'GitHubActionsRun':False}
(OUT/'INDEPENDENT_V010_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
