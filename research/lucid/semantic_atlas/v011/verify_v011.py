#!/usr/bin/env python3
"""Independent regeneration of each stored V011 native MuJoCo physical state.
No invocation of V011 build scripts (except constants from released receipts)."""
from pathlib import Path
import hashlib,io,json,zipfile
import numpy as np
import mujoco as mj
import sys
ROOT=Path(__file__).resolve().parent
RUNTIME=ROOT/'runtime'/'LUCID_R552_WORKSPACE'
sys.path[:0]=[str(ROOT/'.pydeps'),str(RUNTIME/'BIOMECH_CAUSAL_RIG'),str(RUNTIME/'R543_MULTICONTACT_LEARNING'),str(RUNTIME/'R541_DEVELOPMENTAL_CURRICULUM'),str(RUNTIME/'R542_MOTOR_LEARNING')]
from run_r543 import make_body,reset
from lucid_bcr.assets import verify_sources
from lucid_bcr.contact_flight_r46 import muscle_moment_matrix

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 receipt=json.loads((ROOT/'V011_FULL84_RESPONSE_RECEIPT.json').read_text())
 t_receipt=json.loads((ROOT/'V011_NATIVE_DYNAMIC_VERIFICATION.json').read_text())
 bridge=json.loads((ROOT/'V010_V011_MECHANICAL_DYNAMIC_BRIDGE_RECEIPT.json').read_text())
 src=Path('/mnt/data/LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip');hist=Path('/mnt/data/BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13.zip');v010=Path('/mnt/data/BioRig_LUCID_SEMANTIC_ATLAS_V010_NATIVE_84x102_MECHANICAL_RELATIONSHIPS_2026-10-13.zip')
 assert sha(src.read_bytes())==t_receipt['sourceInputR574SHA256']
 assert sha(hist.read_bytes())==t_receipt['sourceInputR590SHA256']
 with zipfile.ZipFile(hist) as z:b=z.read('R590_SETTLED_CONTINUOUS_NATIVE_QPOS.npz')
 assert sha(b)==receipt['inputStateR590EmbeddedNPZSha256']
 with np.load(io.BytesIO(b)) as recorded:
  q0=recorded['qpos'][0].copy();v0=recorded['qvel'][0].copy();a0=recorded['act'][0].copy();t0=float(recorded['timeS'][0])
 with np.load(ROOT/'ALL_84x102_NATIVE_CONTROL_TO_DOF_TIME_RESPONSE.npz') as trace:
  A={k:trace[k] for k in trace.files}
 assert len(verify_sources())==13 and all(s['match'] for s in verify_sources().values())
 model=make_body('seated').model
 for side in ('left','right'):
  k=mj.mj_name2id(model,mj.mjtObj.mjOBJ_SITE,f's_{side}_sternocleidomastoid_1')
  assert k>=0;model.site_pos[k,2]=-.025
 model.opt.noslip_iterations=6;model.opt.noslip_tolerance=1e-6
 assert (model.nu,model.na,model.nq,model.nv,model.ngeom)==(84,84,103,102,117)
 names=[mj.mj_id2name(model,mj.mjtObj.mjOBJ_ACTUATOR,i) for i in range(84)]
 assert np.array_equal(names,A['inputActuatorNames'])
 assert np.array_equal(A['inputActuatorIDs'],np.arange(84))
 base=np.clip(a0,0,1)
 assert np.array_equal(base,A['nativeBaselineAct'])
 assert np.array_equal(q0,A['sourceInitialQpos'])
 assert np.array_equal(v0,A['sourceInitialQvel'])
 assert np.array_equal(a0,A['sourceInitialAct'])
 diffs=[];proj=[];power=[]
 for i in range(85):
  d=mj.MjData(model)
  d.qpos[:]=q0;d.qvel[:]=v0;d.act[:]=a0;d.time=t0
  d.xfrc_applied[:]=0;d.qfrc_applied[:]=0
  for step in range(1,101):
   t=(step-1)*.002
   d.ctrl[:]=base
   if i>0 and .020<=t<.100:d.ctrl[i-1]=min(1.,base[i-1]+.12)
   mj.mj_step(model,d)
   if step in (30,60,100):
    k=(30,60,100).index(step)
    d.ctrl[:]=base
    if i>0 and .020<=step*.002<.100:d.ctrl[i-1]=min(1.,base[i-1]+.12)
    mj.mj_forward(model,d)
    for key in ['qpos','qvel','act','ctrl','actuator_force','qfrc_actuator']:
     observed=np.array(getattr(d,key));expected=A[key][i,k]
     err=float(np.max(abs(observed-expected)))
     assert err<1e-10,(i,k,key,err)
     diffs.append(err)
    moment=muscle_moment_matrix(d,model.nu,model.nv)
    perr=float(np.max(abs(moment.T@d.actuator_force-d.qfrc_actuator)))
    powerr=float(abs(float(d.actuator_force@d.actuator_velocity)-float(d.qfrc_actuator@d.qvel)))
    assert perr<1e-8 and powerr<1e-8
    proj.append(perr);power.append(powerr)
 assert max(diffs)<1e-10
 assert A['delta_velocity_84x3x102'].shape==(84,3,102)
 assert A['delta_position_tangent_84x3x102'].shape==(84,3,102)
 assert np.array_equal(A['delta_velocity_84x3x102'],A['qvel'][1:]-A['qvel'][0])
 assert np.array_equal(A['delta_muscle_force_84x3x84'],A['actuator_force'][1:]-A['actuator_force'][0])
 assert np.array_equal(A['delta_muscle_activation_84x3x84'],A['act'][1:]-A['act'][0])
 # Native quaternion-safe general coordinate displacement contract.
 tmp=np.zeros(102)
 for i in range(84):
  for k in range(3):
   mj.mj_differentiatePos(model,tmp,1.,A['qpos'][0,k],A['qpos'][i+1,k])
   assert np.allclose(tmp,A['delta_position_tangent_84x3x102'][i,k],rtol=0,atol=1e-12)
 with zipfile.ZipFile(v010) as z: earlier=z.read('V010/NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz')
 assert sha(earlier)==bridge['sourceV010NPZSHA256']
 with np.load(io.BytesIO(earlier)) as mprev:
  G=mprev['momentJacobian'][1]
  assert mprev['cases'][1]=='continuous_12to24' and float(mprev['sourceTimesS'][1])==12.
  assert np.array_equal(mprev['actuatorNames'],A['inputActuatorNames'])
 v=A['delta_velocity_84x3x102'][:,-1]
 direct=(abs(G)>1e-6);dynamic=(abs(v)>1e-2)
 assert int(direct.sum())==bridge['geometricDirectInitial']==334
 assert int(dynamic.sum())==bridge['dynamicAtT020Above1eMinus2']==3172
 assert int((dynamic&~direct).sum())==bridge['dynamicWithNoGeometricMomentAtInitialT020']==2932
 assert int((direct&~dynamic).sum())==bridge['directGeometricWithoutLargeVelocityAtT020']==94
 summary={
  'schema':'biorig.semantic-atlas.v011.native-independent-statewise-verification',
  'passed':True,'tracesReintegrated':85,'stepsPerTrace':100,'nativeSamplesCompared':255,'nativeFieldComparisons':1530,
  'maxAbsNativeStateComparison':max(diffs),'maxAbsNativeGeneralizedForceProjection':max(proj),
  'maxAbsPowerBalanceResidual':max(power),
  'every84x102ResponseRebuilt':True,'every84x102GeometricComparisonRebuilt':True,
  'originalPhysicalInputsVerifiedSHA256':True,
  'historicalSourcesEdited':False,'githubActionsUsed':False,
 }
 (ROOT/'V011_INDEPENDENT_VERIFICATION.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
