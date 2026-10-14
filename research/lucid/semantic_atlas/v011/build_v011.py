#!/usr/bin/env python3
"""Native full-body, open-loop muscle command pulse assays from genuine R590 t=12s.
Research data only; not an accepted goal controller or naturalistic reach animation.
Reproduction requires the R574 pinned native runtime extracted alongside this script.
"""
from __future__ import annotations
import os,sys,math,json,csv,hashlib,io,zipfile,datetime
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
RUNTIME=ROOT/'runtime'/'LUCID_R552_WORKSPACE'
sys.path[:0]=[str(ROOT/'.pydeps'),str(RUNTIME/'BIOMECH_CAUSAL_RIG'),str(RUNTIME/'R543_MULTICONTACT_LEARNING'),str(RUNTIME/'R541_DEVELOPMENTAL_CURRICULUM'),str(RUNTIME/'R542_MOTOR_LEARNING')]
import mujoco as mj
from run_r543 import make_body,reset
from lucid_bcr.assets import verify_sources
from lucid_bcr.contact_flight_r46 import muscle_moment_matrix

PINNED_R574='21e0c354023badd40485840296e09034809ae4eb055fd926eff39ac0b8700701'
PINNED_R590='42c080f6a0c78042882bd27c5309d8158709a825a3fc6399ed07a5416f4679a7'
R574=Path('/mnt/data/LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip')
R590=Path('/mnt/data/BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13.zip')
NPZ_MEMBER='R590_SETTLED_CONTINUOUS_NATIVE_QPOS.npz'
# Three shoulder motor channels, with antagonist tested separately, no combined controller.
PULSE_MUSCLES=['m_left_deltoid_middle','m_left_pectoralis_major','m_right_deltoid_middle','m_right_pectoralis_major']
DT=.002;SEC=.28;PULSE_ON=.030;PULSE_OFF=.160;INCREMENT=.14

def digest(b):return hashlib.sha256(b).hexdigest()
def write_json(path,value):Path(path).write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
def fail(msg): raise AssertionError(msg)

def initialize():
 if digest(R574.read_bytes())!=PINNED_R574:fail('original R574 ZIP SHA mismatch')
 if digest(R590.read_bytes())!=PINNED_R590:fail('original R590 ZIP SHA mismatch')
 with zipfile.ZipFile(R590) as z:
  b=z.read(NPZ_MEMBER)
 with np.load(io.BytesIO(b)) as d:
  arrays={k:d[k].copy() for k in d.files}
 assert arrays['qpos'].shape==(31,103) and arrays['qvel'].shape==(31,102) and arrays['act'].shape==(31,84)
 source_sha=digest(b)
 src=verify_sources();assert len(src)==13 and all(x['match'] for x in src.values())
 pb=make_body('seated')
 m,d=pb.model,pb.data
 for side in ('left','right'):
  sid=mj.mj_name2id(m,mj.mjtObj.mjOBJ_SITE,f's_{side}_sternocleidomastoid_1');assert sid>=0
  m.site_pos[sid,2]=-.025
 m.opt.noslip_iterations=6;m.opt.noslip_tolerance=1e-6
 reset(pb)
 assert (m.nu,m.na,m.nq,m.nv,m.ngeom)==(84,84,103,102,117)
 assert abs(m.opt.timestep-DT)<1e-12
 # Fully recorded R590 continuous physical state at t=12s; control state is not recorded.
 d.qpos[:]=arrays['qpos'][0];d.qvel[:]=arrays['qvel'][0];d.act[:]=arrays['act'][0]
 d.time=float(arrays['timeS'][0]);d.ctrl[:]=np.clip(d.act,0.,1.)
 d.qfrc_applied[:]=0;d.xfrc_applied[:]=0
 mj.mj_forward(m,d)
 assert np.isfinite(d.qpos).all() and np.isfinite(d.qvel).all()
 return pb,arrays,source_sha

def measure_contacts(model,data):
 seat=mj.mj_name2id(model,mj.mjtObj.mjOBJ_GEOM,'research_seat')
 force=np.zeros(6);seat_n=0.;seat_count=0;floor_count=0;maxpenetration=0.
 for i in range(data.ncon):
  c=data.contact[i];pair=(int(c.geom1),int(c.geom2))
  if seat in pair:
   mj.mj_contactForce(model,data,i,force)
   seat_n+=abs(float(force[0]));seat_count+=1
  if 1 in pair: floor_count+=1 # floor geom id NOT guaranteed; exploratory only
  maxpenetration=max(maxpenetration,max(0.,-float(c.dist)))
 return seat_n,seat_count,maxpenetration

def main():
 pb,arrays,state_sha=initialize();m,d=pb.model,pb.data
 names=[mj.mj_id2name(m,mj.mjtObj.mjOBJ_ACTUATOR,i) for i in range(m.nu)]
 assert len(names)==84 and len(set(names))==84
 indexes={x:names.index(x) for x in PULSE_MUSCLES}
 initial_qpos=d.qpos.copy();initial_qvel=d.qvel.copy();initial_act=d.act.copy()
 state0=d.time
 baseline_ctrl=np.clip(initial_act,0,1)
 conditions=['baseline']+PULSE_MUSCLES
 timeline={};results=[];power_error_max=0;proj_error_max=0
 steps=round(SEC/DT)
 for condition in conditions:
  temp=mj.MjData(m)
  temp.qpos[:]=initial_qpos;temp.qvel[:]=initial_qvel;temp.act[:]=initial_act
  temp.time=state0;temp.ctrl[:]=baseline_ctrl
  temp.qfrc_applied[:]=0;temp.xfrc_applied[:]=0
  rows={k:[] for k in ('t','act','ctrl','forces','qfrc','qpos','qvel','actuator_velocity','seat_normal_N','seat_contact_count','penetration_m','act_dot','sum_kinetic')}
  for step in range(steps+1):
   t=step*DT
   temp.ctrl[:]=baseline_ctrl
   if condition!='baseline' and PULSE_ON<=t<PULSE_OFF:
    i=indexes[condition];temp.ctrl[i]=min(1.,float(baseline_ctrl[i]+INCREMENT))
   mj.mj_forward(m,temp)
   moment=muscle_moment_matrix(temp,m.nu,m.nv)
   calc=moment.T@temp.actuator_force
   projection_error=float(np.max(np.abs(calc-temp.qfrc_actuator)))
   proj_error_max=max(proj_error_max,projection_error)
   assert projection_error<1e-8
   # Work rate is computed from physical generalized force and actual generalized velocity.
   pg=float(temp.qfrc_actuator@temp.qvel)
   pm=float(temp.actuator_force@temp.actuator_velocity)
   power_error_max=max(power_error_max,abs(pg-pm))
   assert abs(pg-pm)<1e-7
   ns,nc,pen=measure_contacts(m,temp)
   for key,val in (
    ('t',t),('act',temp.act.copy()),('ctrl',temp.ctrl.copy()),('forces',temp.actuator_force.copy()),
    ('qfrc',temp.qfrc_actuator.copy()),('qpos',temp.qpos.copy()),('qvel',temp.qvel.copy()),
    ('actuator_velocity',temp.actuator_velocity.copy()),('seat_normal_N',ns),('seat_contact_count',nc),
    ('penetration_m',pen),('act_dot',temp.act_dot.copy()),('sum_kinetic',float(temp.qvel@m.dof_M0*temp.qvel) if False else float(np.linalg.norm(temp.qvel)))):
    rows[key].append(val)
   if step<steps:mj.mj_step(m,temp)
  timeline[condition]={k:np.stack(v) for k,v in rows.items()}
  assert np.isfinite(timeline[condition]['qpos']).all()
  assert np.allclose(timeline[condition]['qpos'][0],initial_qpos)
  assert np.allclose(timeline[condition]['qvel'][0],initial_qvel)
  assert np.allclose(timeline[condition]['act'][0],initial_act)
 assert power_error_max<1e-7
 base=timeline['baseline']
 for cond in conditions[1:]:
  result=timeline[cond];i=indexes[cond]
  dx=result['act'][:,i]-base['act'][:,i]
  ff=result['forces'][:,i]-base['forces'][:,i]
  qvel_delta=result['qvel']-base['qvel']
  qpos_delta=result['qpos']-base['qpos']
  pulse= (result['t']>=PULSE_ON)&(result['t']<PULSE_OFF)
  after=(result['t']>=PULSE_OFF)
  row={
   'muscle':cond,'nativeActuatorID':i,'commandBaseline':float(baseline_ctrl[i]),
   'commandPeak':float(np.max(result['ctrl'][:,i])),
   'atPulseEndDeltaActivation':float(dx[np.where(after)[0][0]]),
   'maxDeltaActivation':float(np.max(dx)),
   'maxAbsoluteDeltaForceN':float(np.max(np.abs(ff))),
   'maxAbsoluteDeltaQvel':float(np.max(np.abs(qvel_delta))),
   'finalRMSDeltaQvel':float(np.sqrt(np.mean(qvel_delta[-1]**2))),
   'finalMaxAbsDeltaQpos':float(np.max(abs(qpos_delta[-1]))),
   'maxDeltaSeatNormalN':float(np.max(abs(result['seat_normal_N']-base['seat_normal_N']))),
   'finalDeltaSeatNormalN':float(result['seat_normal_N'][-1]-base['seat_normal_N'][-1]),
   'minDerivedForceN':float(result['forces'][:,i].min()),
   'maxDerivedForceN':float(result['forces'][:,i].max()),
   'baselinePeakSeatForceN':float(base['seat_normal_N'].max()),
   'perturbedPeakSeatForceN':float(result['seat_normal_N'].max()),
   'responseFirstTimeDeltaActivationAbove1e4S':(float(result['t'][np.flatnonzero(dx>1e-4)[0]]) if np.any(dx>1e-4) else None),
  }
  # Effector outputs measured in each run, no inverse-to-controller equivalence claim.
  assert row['maxDeltaActivation']>1e-4,cond
  results.append(row)
 out=ROOT/'NATIVE_84_MUSCLE_CAUSAL_TIME_TRACES.npz'
 np.savez_compressed(out,**{f'{case}__{k}':v for case,dat in timeline.items() for k,v in dat.items()})
 fields=list(results[0]);withcsv=ROOT/'PULSED_ACTUATOR_NATIVE_DIFFERENTIAL_EFFECTS.csv'
 with withcsv.open('w',newline='') as f:
  w=csv.DictWriter(f,fields);w.writeheader();w.writerows(results)
 summary={
  'schema':'biorig.atlas.v011.native-openloop-differential-muscle-causality',
  'sourceInputR574SHA256':PINNED_R574,'sourceInputR590SHA256':PINNED_R590,
  'sourceFullStateNPZSha256':state_sha,'sourcePhysicalTimeS':state0,
  'nativeMuJoCoVersion':mj.__version__,'modelDims':dict(nu=m.nu,na=m.na,nq=m.nq,nv=m.nv,ngeom=m.ngeom),
  'initialQposSHA256':digest(initial_qpos.tobytes()),'initialQvelSHA256':digest(initial_qvel.tobytes()),'initialActSHA256':digest(initial_act.tobytes()),
  'simTimeS':SEC,'timeStepS':DT,'samplesPerCase':steps+1,'cases':conditions,
  'command':'Initial recorded activation used as constant baseline excitation proxy; +0.14 clipped muscle-specific pulse from 0.030 to 0.160s',
  'normalControlSource':'None. Deliberate open-loop causal assay; no postural controller, goal agent, R589 arm landing, external root stabilizer or visual acceptance',
  'seatedSeatCollisionAndFloorEnabled':True,
  'muJoCoExternalAppliedForce':False,
  'nativeProjectionMaxAbsResidual':proj_error_max,
  'nativeMechanicalPowerResidualMaxAbs':power_error_max,
  'maxBaselineSeatN':float(base['seat_normal_N'].max()),
  'initialMeanActivation':float(initial_act.mean()),
  'initialHighActivation':float(initial_act.max()),
  'conditionsSummary':results,
  'traceFileSHA256':digest(out.read_bytes()),
  'traceFileBytes':out.stat().st_size,
  'knownLimits':[
   'Original controller commands at t=12s were not captured in R590, so baseline ctrl=initial act is NOT a faithful continuation of R590 control.',
   'This is an actual MuJoCo simulation from the saved physical state, but entirely open-loop over 0.28s.',
   'Differential effects use matched initial states; anatomical force model itself is uncalibrated for real physiology.',
   'No goal command or whole-body intent planner was exercised; no claim of reach, balance or recovery.',
   'Generalized coordinate response depends on changing contact and all other actuator activations; it is not the isolated tendon Jacobian.',
  ],
  'simulationSourceModified':False,'GitHubActionsUsed':False,
 }
 write_json(ROOT/'V011_NATIVE_DYNAMIC_VERIFICATION.json',summary)
 print(json.dumps({'maxForceResidual':proj_error_max,'maxPowerResidual':power_error_max,'baselinePeakSeatN':summary['maxBaselineSeatN'],'traceBytes':out.stat().st_size,'conditionResults':results},indent=2))
if __name__=='__main__':main()
