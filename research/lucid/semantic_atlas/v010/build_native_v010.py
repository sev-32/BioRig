#!/usr/bin/env python3
"""Reproduce true native MuJoCo 84-actuator x 102 generalized-velocity Jacobians.
All simulation objects are cloned from pinned R574 assets, model-local SCM correction
is applied identically to R590, and R590 saved *poses* are never modified on disk.
"""
from __future__ import annotations
import os,sys,io,csv,json,zipfile,hashlib
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data');OUT=ROOT/'BioRig_SEMANTIC_ATLAS_010';OUT.mkdir(exist_ok=True)
RUNTIME=OUT/'runtime'/'LUCID_R552_WORKSPACE'
sys.path[:0]=[str(OUT/'.pydeps'),str(RUNTIME/'BIOMECH_CAUSAL_RIG'),str(RUNTIME/'R543_MULTICONTACT_LEARNING'),str(RUNTIME/'R541_DEVELOPMENTAL_CURRICULUM'),str(RUNTIME/'R542_MOTOR_LEARNING')]
import mujoco as mj
from run_r543 import make_body,reset,SEAT_XML
from lucid_bcr.contact_flight_r46 import muscle_moment_matrix
from lucid_bcr.assets import verify_sources
np.set_printoptions(precision=9)
arch=ROOT/'BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13.zip'
refs={};saved={}
with zipfile.ZipFile(arch) as z:
 for k,n in [('continuous','R590_SETTLED_CONTINUOUS_NATIVE_QPOS.npz'),('restart_no_push','R590_RESTART_PUSH_+0N_QPOS.npz'),('restart_plus120N','R590_RESTART_PUSH_+120N_QPOS.npz')]:
  b=z.read(n);refs[k]={'sourceArchive':arch.name,'sourceMember':n,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
  f=np.load(io.BytesIO(b));saved[k]={key:f[key].copy() for key in f.files}
  assert saved[k]['qpos'].shape==(31,103)
  assert saved[k]['timeS'].shape==(31,)
  assert np.all(np.diff(saved[k]['timeS'])>0.)
# Exactly the original constructor invoked through the R543 factory used by R590.
locks=verify_sources();assert all(x['match'] for x in locks.values()) and len(locks)==13
pb=make_body('seated');m=pb.model;d=pb.data
for side in ('left','right'):
 sid=mj.mj_name2id(m,mj.mjtObj.mjOBJ_SITE,f's_{side}_sternocleidomastoid_1')
 assert sid>=0
 m.site_pos[sid,2]=-.025
m.opt.noslip_iterations=6;m.opt.noslip_tolerance=1e-6
reset(pb)
assert (m.nu,m.na,m.nq,m.nv,m.ngeom)==(84,84,103,102,117)
assert np.allclose(m.opt.gravity,[0,-9.81,0])
seat_id=mj.mj_name2id(m,mj.mjtObj.mjOBJ_GEOM,'research_seat');assert seat_id>=0
assert np.allclose(m.geom_size[seat_id],[.28,.08,.23])
assert np.allclose(m.geom_friction[seat_id],[.9,.005,.0001])
assert set(map(int,m.actuator_actadr))==set(range(84))

with (ROOT/'BioRig_SEMANTIC_ATLAS_009'/'ALL_84_MUSCLE_CHANNELS_AND_WINNING_COMMAND_WRITERS.csv').open() as file:
 register=list(csv.DictReader(file))
nameids=[]
for idx,row in enumerate(register):
 name=row['actuatorName']
 got=mj.mj_id2name(m,mj.mjtObj.mjOBJ_ACTUATOR,idx)
 assert got==name,(idx,name,got)
 nameids.append({'muJoCoIndex':idx,'name':name,'activationIndex':int(m.actuator_actadr[idx]),'catalogSourceLine':int(row['catalogLine']),
 'R589Writer':row['R589_candidate_lastCommandWriter'],'R590Writer':row['R590_restart_lastCommandWriter'],
 'controlMin':float(m.actuator_ctrlrange[idx,0]),'controlMax':float(m.actuator_ctrlrange[idx,1])})
assert len(nameids)==84
assert all(x['controlMin']==0 and x['controlMax']==1 for x in nameids)
(OUT/'NATIVE_84_ACTUATOR_NUMERIC_IDENTITY.json').write_text(json.dumps(nameids,indent=2)+'\n')

# Exact generalized velocity (nv) coordinate names and units, including free root.
dofs=[None]*m.nv
for jid in range(m.njnt):
 addr=int(m.jnt_dofadr[jid]); typ=m.jnt_type[jid]
 nn=6 if typ==mj.mjtJoint.mjJNT_FREE else 3 if typ==mj.mjtJoint.mjJNT_BALL else 1
 name=mj.mj_id2name(m,mj.mjtObj.mjOBJ_JOINT,jid) or f'joint_{jid}'
 kind={int(mj.mjtJoint.mjJNT_FREE):'free',int(mj.mjtJoint.mjJNT_BALL):'ball',int(mj.mjtJoint.mjJNT_HINGE):'hinge',int(mj.mjtJoint.mjJNT_SLIDE):'slide'}[int(typ)]
 for k in range(nn):
  unit='metres per metre' if (kind=='free' and k<3) or kind=='slide' else 'metres per radian'
  dofs[addr+k]={'index':addr+k,'jointName':name,'jointID':jid,'kind':kind,'component':k,'coordinateKind':'translation' if unit=='metres per metre' else 'rotation','nativeMomentJacobianUnit':unit}
assert all(dofs)
with (OUT/'NATIVE_102_DOF_SEMANTIC_INDEX.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(dofs[0]));w.writeheader();w.writerows(dofs)

# Record actual posture-dependent moment Jacobians, never edited qpos and no pose interpolation.
# The continuous segment contains qpos/qvel/act. Restart files only contain qpos, so
# the reconstructed Jacobian is strictly configuration-dependent, NOT a replay of its forces.
case_names=['cold_seated_reset','continuous_12to24','restart_no_push','restart_plus120N']
allmat=[];alltimes=[];labels=[];force_residual=[];force_observed=[]

# 'cold' root initial pose is baseline cold start before any time steps, already has mj_forward from reset.
def take(case,t):
 mj.mj_forward(m,d)
 matrix=muscle_moment_matrix(d,m.nu,m.nv)
 assert matrix.shape==(84,102) and np.isfinite(matrix).all()
 allmat.append(matrix);alltimes.append(float(t));labels.append(case)
 if case=='continuous_12to24':
  # Recorded qpos/qvel/act are all available here. This is a native force
  # reconstruction at observed states, not a reintegration of original history.
  predicted=matrix.T@d.actuator_force
  residual=float(np.max(np.abs(predicted-d.qfrc_actuator)))
  assert residual<1e-9, residual
  force_residual.append(residual)
  force_observed.append(float(np.max(np.abs(d.actuator_force))))
 return matrix
initial_matrix=take('cold_seated_reset',0.)
for key in case_names[1:]:
 state=saved['continuous' if key=='continuous_12to24' else key];q=state['qpos'];tv=state['timeS']
 for j in range(len(tv)):
  d.qpos[:]=q[j]
  if 'qvel' in state:d.qvel[:]=state['qvel'][j]
  else:d.qvel[:]=0.
  if 'act' in state:d.act[:]=state['act'][j]
  else:d.act[:]=0.
  d.time=float(tv[j]) + (12. if key.startswith('restart_') else 0.)
  take(key,tv[j])
M=np.stack(allmat).astype('float64');assert M.shape==(94,84,102)
assert max(np.max(abs(M[:,:,:6])),0.)<1e-10
assert all(np.isfinite(M.flat))

# At exact cold seated pose all channels have an exact name and a row of moment arms.
threshold=1e-6
edges={}
for i,name in enumerate(nameids):
 for j,dof in enumerate(dofs):
  vals=M[:,i,j]
  nz=abs(vals)>threshold
  if nz.any():
   v=vals[nz]
   sg=np.sign(v)
   flips=int(np.count_nonzero(sg[1:]!=sg[:-1]))
  else:flips=0
  edges[(i,j)]={'muscleIndex':i,'muscleName':name['name'],'dofIndex':j,'jointName':dof['jointName'],
      'unit':dof['nativeMomentJacobianUnit'],'firstStateValue':float(vals[0]),
      'minAcrossSavedStates':float(vals.min()),'maxAcrossSavedStates':float(vals.max()),
      'meanAbsoluteAcrossSavedStates':float(np.mean(abs(vals))),
      'above1eMinus6StateCount':int(nz.sum()),'signFlipsAcrossNonzeroStates':flips,
      'unknownOutsideSamples':True}

# Full 84*102 typed channel-to-DOF causal geometry table. Do not silently omit zeros.
import gzip
cols=list(next(iter(edges.values())))
with gzip.open(OUT/'ALL_8568_MUSCLE_TO_DOF_MECHANICAL_EDGES.csv.gz','wt',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');w.writeheader()
 for r in edges.values():w.writerow(r)
np.savez_compressed(OUT/'NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz',
                   momentJacobian=M,cases=np.array(labels),sourceTimesS=np.array(alltimes),
                   actuatorNames=np.array([n['name'] for n in nameids]),
                   dofNames=np.array([d['jointName'] for d in dofs]))

stats={}
for case in case_names:
 ix=[i for i,l in enumerate(labels) if l==case];tmp=M[ix]
 stats[case]={
  'frames':len(ix),'nonzeroFirstFrameAt1eMinus6':int(np.count_nonzero(abs(tmp[0])>threshold)),
  'everNonzeroAt1eMinus6':int(np.count_nonzero(np.any(abs(tmp)>threshold,axis=0))),
  'maxAbs':float(np.abs(tmp).max()),'timeFirstS':float(alltimes[ix[0]]),'timeLastS':float(alltimes[ix[-1]])}

receipts={
 'schema':'biorig.semantic-atlas.v010.native-forward-sparse-moment-geometry',
 'model':'R543 seated 84-muscle PhysicsBody; R590 model-local SCM attachment correction and noslip solver option',
 'muJoCoVersion':mj.__version__,
 'canonicalSourceArchiveSha256':hashlib.sha256((ROOT/'LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip').read_bytes()).hexdigest(),
 'r590NumericalSourceArchiveSha256':hashlib.sha256(arch.read_bytes()).hexdigest(),
 'nativeModelDimensions':{'nu':m.nu,'na':m.na,'nq':m.nq,'nv':m.nv,'ngeom':m.ngeom,'nbody':m.nbody},
 'gravityXYZ':m.opt.gravity.tolist(),
 'seat':{'geomID':seat_id,'sizeHalfExtentsM':m.geom_size[seat_id].tolist(), 'friction':m.geom_friction[seat_id].tolist()},
 'assetSourceLocksCount':len(locks),'assetSourceLocksMatch':all(x['match'] for x in locks.values()),
 'sourcePoseSnapshots':refs,'matrixShape':list(M.shape),'matrixSnapshotLabels':dict(zip(case_names,[labels.count(x) for x in case_names])),
 'momentEntries':int(M.size),'trajectoryStats':stats,'everNonzeroAcrossAllStates':int(np.count_nonzero(np.any(abs(M)>threshold,axis=0))),
 'allMomentJacobianRoot6NumericallyZero':bool(np.max(abs(M[:,:,:6]))<1e-10),
 'nonzeroThreshold':threshold,
 'nativeGeneralizedForceProjection':{'continuousStateCount':len(force_residual),'maxAbsReconstructionResidual':max(force_residual),'peakAbsoluteNativeActuatorForceN':max(force_observed),'assumption':'Recorded qpos/qvel/act evaluated in source native model with mj_forward. Not original recorded qfrc_actuator or re-integrated dynamics.'},
 'observationBoundary':'Native MuJoCo reconstruction of geometric moment Jacobians only. Source qpos are physically sampled; restart qvel/act unavailable so zeros only for static forward geom evaluation; no regenerated muscle/contact dynamics.',
 'originalSimulationSourceModified':False,'GitHubActionsUsed':False}
(OUT/'NATIVE_84x102_AND_94_STATE_RECEIPT.json').write_text(json.dumps(receipts,indent=2)+'\n')

paper=f'''# V010 — measured MuJoCo muscle-to-joint mechanical relationship matrix

**Reproduction state:** the **original pinned Skin78 physical assets** pass all 13 SHA-256 identity checks. The native R543 `make_body('seated')` factory constructs the same 84-muscle model family inherited by R590. We apply the exact R585/R590 model-local SCM insertion at site z = -0.025 m and R590 `noslip_iterations = 6` to the local test instance. No archived source or numerical snapshot has been edited.

## Verified native model

- Physics solver: native **MuJoCo {mj.__version__}** from the original offline wheel.
- Physical state: **nq={m.nq}**, **nv={m.nv}**, **na={m.na}**; **nu={m.nu}** independently named muscle actuators, **{m.ngeom}** collision geoms including the seat.
- The research seat is a **rigid box** with half extents {m.geom_size[seat_id].tolist()} metres and friction coefficients {m.geom_friction[seat_id].tolist()}. This is not a deformable cushion; visual arm bouncing cannot be attributed to an explicitly simulated squishy seat. Contact compliance and controller oscillation remain possible causes.
- World gravity is {m.opt.gravity.tolist()} m/s²: **Y is vertical**, and X/Z horizontal.
- Native `mj_id2name` confirms every catalog channel in the original exact **84-index order**. `actuator_actadr` maps all 84 actuators one-to-one to 84 activation states.
- At all **{len(force_residual)}** fully recorded continuous states, the native identity `momentJacobian.T @ actuator_force == qfrc_actuator` holds with maximum absolute residual **{max(force_residual):.3e}** in native generalized-force units. The largest reconstructed native actuator force magnitude is **{max(force_observed):.2f} N**. This validates the implemented instantaneous generalized-force projection, not the historical time integration nor biological calibration.

## New source-to-physics relationship data

For each observed generalized coordinate, MuJoCo stores sparse tendon Jacobians (`moment_rowadr`, `moment_rownnz`, `moment_colind`, `actuator_moment`). The original `lucid_bcr.contact_flight_r46.muscle_moment_matrix` expands them into an **84×102 numeric matrix** at an actual physical configuration. It describes how instantaneous actuator tendon length changes under generalized motion; magnitude has dimension metres/radian for rotating DOFs and metres/metre for translational DOFs. **It is geometry, not an observed muscle torque, strength, or excitation.**

We derived **{M.shape[0]} native geometric Jacobians × 84 muscles × 102 velocity DOFs = {M.size:,} numeric cells** from saved authentic MuJoCo poses, with exact channel IDs and exact native joint IDs:

| Source pose sequence | Captures | Above 10⁻⁶ in first pose | Ever above 10⁻⁶ in sequence | Maximum magnitude |
| --- | ---: | ---: | ---: | ---: |
'''
for key in case_names:
 dstat=stats[key]
 paper+=f"| `{key}` | {dstat['frames']} | {dstat['nonzeroFirstFrameAt1eMinus6']} | {dstat['everNonzeroAt1eMinus6']} | {dstat['maxAbs']:.6f} |\n"
paper+=f'''
Across all {M.shape[0]} samples, **{receipts['everNonzeroAcrossAllStates']} of 8,568 possible muscle–DOF ordered pairs** exceed 10⁻⁶ in at least one state. Every pair, including zeros, is included in `ALL_8568_MUSCLE_TO_DOF_MECHANICAL_EDGES.csv.gz` with its exact unit, minimum/maximum measured value, mean absolute value, observed nonzero count, and sign flips. The full dense values and source time labels are in `NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz`.

**All six unactuated root DOFs are near machine-zero** for all 84 muscles across all 94 poses. This validates the intended root unactuation within the tested geometry. Muscle-induced whole-body movement occurs through relative internal joint forces and external contacts, not by adding an artificial root actuator.

## Important epistemic limits

1. The `continuous_12to24` input records real `qpos`, `qvel` and muscle `act`. `restart_no_push` and `restart_plus120N` record **qpos only**: their velocity and activation arrays were not serialized in those files. We use zero velocities/activation **only** when recomputing geometric moment Jacobians from the recorded poses. We do **not** call these reconstructed state tuples a faithful replay of their muscle forces or controller history.
2. This is a full relationship matrix **for muscle-to-generalized-coordinate geometry over these 94 states**. It does not establish all possible muscle interactions under all postures, contact mechanics, neural motor competence, or complete semantic understanding of the 70,823 archived code lines.
3. A signed actuator moment coefficient multiplied by actual actuator force yields a generalized-force contribution. `data.ctrl` alone is not delivered muscle force; the archived activation delay and force–length–velocity dynamics intervene.
4. The `>10⁻⁶` edge threshold is a reporting convention; the full raw numerical matrices retain floating point values without thresholding.
5. The 31 poses for each R590 variant were genuine MuJoCo-generated snapshots, **not newly integrated physical trajectories in V010**. This test loads the source physical model and applies native forward calculations to those poses.

## Preservation / next step

V009 and all older documented versions remain unchanged. We should next compare the signed force direction, actual antagonist recruitment, and observed delayed activation under true MuJoCo replays. Then trace general goal/planner output to the correct 84-channel command owner without making the existing historical versions disappear. No GitHub Actions.
'''
(OUT/'NATIVE_MUSCLE_TO_DOF_PHYSICS_SEMANTICS.md').write_text(paper)
print(json.dumps({'result':'PASS','muJoCoVersion':mj.__version__,'model':receipts['nativeModelDimensions'],'snapshots':len(labels),'matrixCells':int(M.size),'everNonzeroPairs':receipts['everNonzeroAcrossAllStates'],'maxForceResidual':max(force_residual),'rootZero':receipts['allMomentJacobianRoot6NumericallyZero']},indent=2))
