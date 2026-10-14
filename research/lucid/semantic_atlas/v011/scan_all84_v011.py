#!/usr/bin/env python3
"""Matched-input native 84x102 conditional dynamic perturbation response matrix.
Run isolated +0.12 muscle excitation pulse on each of all 84 channels, starting
from the same recorded (qpos,qvel,act) R590 12-second physical state.
No controller, no external applied force, no body lock; results conditional on
an open-loop unbalanced seated model and must not be called task competence.
"""
from __future__ import annotations
import csv,json,hashlib,time
from pathlib import Path
import numpy as np
import mujoco as mj
from build_v011 import initialize,DT,ROOT,PULSE_ON,PULSE_OFF,measure_contacts,write_json

PULSE_DELTA=.12;ON=.020;OFF=.100;END=.200
READ_STEPS=[30,60,100]

def run():
 begin=time.monotonic()
 pb,original,sha=initialize();m,d=pb.model,pb.data
 names=[mj.mj_id2name(m,mj.mjtObj.mjOBJ_ACTUATOR,i) for i in range(m.nu)]
 q0=d.qpos.copy();v0=d.qvel.copy();a0=d.act.copy();t0=float(d.time)
 base_ctrl=np.clip(a0,0,1)
 assert len(names)==84 and np.all(base_ctrl>=0) and np.all(base_ctrl<=1)
 ids=[None]+list(range(84))
 # Arrays: [85 cases, 3 timestamps, N] full snapshots to independently recompute pairwise changes.
 out={}
 for field,n in [('qpos',m.nq),('qvel',m.nv),('act',m.na),('actuator_force',m.nu),('qfrc_actuator',m.nv),('ctrl',m.nu)]:
  out[field]=np.zeros((len(ids),len(READ_STEPS),n))
 for field in ['timeS','seatNormalN','seatContactCount','penetrationM']:
  out[field]=np.zeros((len(ids),len(READ_STEPS)))
 for ci,channel in enumerate(ids):
  x=mj.MjData(m);x.qpos[:]=q0;x.qvel[:]=v0;x.act[:]=a0;x.time=t0
  x.qfrc_applied[:]=0;x.xfrc_applied[:]=0
  for step in range(1,max(READ_STEPS)+1):
   current=(step-1)*DT
   x.ctrl[:]=base_ctrl
   if channel is not None and ON<=current<OFF: x.ctrl[channel]=min(1.,base_ctrl[channel]+PULSE_DELTA)
   mj.mj_step(m,x)
   if step in READ_STEPS:
    idx=READ_STEPS.index(step)
    x.ctrl[:]=base_ctrl
    if channel is not None and ON<=step*DT<OFF:x.ctrl[channel]=min(1.,base_ctrl[channel]+PULSE_DELTA)
    mj.mj_forward(m,x)
    for field in ['qpos','qvel','act','ctrl','actuator_force','qfrc_actuator']:
     out[field][ci,idx,:]=getattr(x,field)
    for field,val in [('timeS',step*DT),('seatNormalN',measure_contacts(m,x)[0]),('seatContactCount',measure_contacts(m,x)[1]),('penetrationM',measure_contacts(m,x)[2])]:out[field][ci,idx]=val
  if ci%14==0:print('assayed',ci,'of 84; elapsed seconds',round(time.monotonic()-begin,1),flush=True)
 assert np.allclose(out['timeS'][:],np.array(READ_STEPS)[None,:]*DT)
 assert np.all(np.isfinite(out['qpos']))
 DELTA_V=out['qvel'][1:]-out['qvel'][0]
 DELTA_Q=np.zeros((84,3,m.nv))
 for j in range(84):
  for k in range(3):mj.mj_differentiatePos(m,DELTA_Q[j,k],1.,out['qpos'][0,k],out['qpos'][j+1,k])
 DELTA_F=out['actuator_force'][1:]-out['actuator_force'][0]
 DELTA_ACT=out['act'][1:]-out['act'][0]
 DELTA_QFRC=out['qfrc_actuator'][1:]-out['qfrc_actuator'][0]
 for field,val in [('delta_velocity_84x3x102',DELTA_V),('delta_position_tangent_84x3x102',DELTA_Q),('delta_muscle_force_84x3x84',DELTA_F),('delta_muscle_activation_84x3x84',DELTA_ACT),('delta_generalized_actuator_force_84x3x102',DELTA_QFRC)]:out[field]=val
 out['inputActuatorIDs']=np.arange(84,dtype=np.int32)
 out['samplesAfterStartS']=np.array(READ_STEPS)*DT
 out['inputActuatorNames']=np.array(names,dtype='U100')
 out['nativeBaselineAct']=base_ctrl
 out['sourceInitialQpos']=q0;out['sourceInitialQvel']=v0;out['sourceInitialAct']=a0
 outfile=ROOT/'ALL_84x102_NATIVE_CONTROL_TO_DOF_TIME_RESPONSE.npz'
 np.savez_compressed(outfile,**out)
 # Two independent physical response matrices, each 84x102: velocity response and position response.
 summary=[]
 for i in range(84):
  dv=DELTA_V[i,-1];dq=DELTA_Q[i,-1]
  row={'actuatorID':i,'name':names[i], 'baseCtrl':float(base_ctrl[i]),'actualPulseIncrease':float(min(PULSE_DELTA,1.-base_ctrl[i])),
       'activationDeltaAtT12S':float(DELTA_ACT[i,1,i]),'maxAbsVelocityResponseT20':float(np.max(abs(dv))),
       'rmsVelocityResponseT20':float(np.sqrt(np.mean(dv**2))),
       'maxAbsPositionTangentResponseT20':float(np.max(abs(dq))),
       'rmsPositionTangentResponseT20':float(np.sqrt(np.mean(dq**2))),
       'maxAbsActuatorForceDifferenceT20':float(np.max(abs(DELTA_F[i,-1]))),
       'maxAbsGeneralizedForceDifferenceT20':float(np.max(abs(DELTA_QFRC[i,-1]))),
       'deltaSeatLoadT20N':float(out['seatNormalN'][i+1,-1]-out['seatNormalN'][0,-1]),
       'nonzeroVelocityEffectsAbove1eMinus5':int(np.sum(abs(dv)>1e-5))}
  summary.append(row)
 with (ROOT/'ALL_84_CHANNEL_NATIVE_DYNAMIC_EFFECTS.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(summary[0]),lineterminator='\n');w.writeheader();w.writerows(summary)
 metrics={'schema':'biorig.atlas.v011.full-native-open-loop-84x102-conditional-actuation-response',
  'mujoco':mj.__version__,'inputStateR590EmbeddedNPZSha256':sha,
  'modelSize':{'nu':84,'na':84,'nq':m.nq,'nv':102},'initialPhysicalTimeSeconds':t0,
  'inputPulse':{'pulseAdditive':PULSE_DELTA,'onS':ON,'offS':OFF,'dt':DT,'baselineCommands':'clipped R590 physically recorded activation (proxy, not saved controller state)'},
  'assay':{'cases':len(ids),'baselineCases':1,'singleMusclePulseCases':84,'allOthersCommands':'held to initial recorded activation','physicalSimulation':True,'postureController':False,'lockRoot':False,'externalRootForce':False,'recordTimesS':list(np.array(READ_STEPS)*DT)},
  'responseShapes':{name:list(np.shape(val)) for name,val in out.items() if name.startswith('delta_')},
  'fullSourceStateAtStart':{'qposSha256':hashlib.sha256(q0.tobytes()).hexdigest(),'qvelSha256':hashlib.sha256(v0.tobytes()).hexdigest(),'actSha256':hashlib.sha256(a0.tobytes()).hexdigest()},
  'baselineSeatLoadT20N':float(out['seatNormalN'][0,-1]),
  'baselineSeatLoadPeakSnapshotsN':float(out['seatNormalN'][0].max()),
  'nonzeroVelocityResponsesT20Count':int(np.sum(abs(DELTA_V[:,-1])>1e-5)),
  'nonzeroPositionResponsesT20Count':int(np.sum(abs(DELTA_Q[:,-1])>1e-5)),
  'largestPeakVelocityResponseT20':max(summary,key=lambda s:s['maxAbsVelocityResponseT20']),
  'largestSeatResponseMagnitudeT20':max(summary,key=lambda s:abs(s['deltaSeatLoadT20N'])),
  'NPZSHA256':hashlib.sha256(outfile.read_bytes()).hexdigest(),
  'NPZBytes':outfile.stat().st_size,
  'executionWallSeconds':round(time.monotonic()-begin,1),
  'limits':[
   'These are conditional end-to-end MuJoCo perturbation responses in an open-loop scene, not a globally linear transfer function.',
   'Controller disabled intentionally: baseline seat load and body motion may be unstable; do not misreport these as accepted BioRig runtime metrics.',
   'Unlike V010 moment matrix, these effects propagate through delayed activation, force-length-velocity, inertial and contact evolution; they are state and duration dependent.',
   'Position tangent responses for generalized quaternion coordinates use native mj_differentiatePos to return 102 values.',
   'No proof of actual goal-directed intent execution, anatomical calibration, general balance, or steady-state equilibrium.'
  ],'originalCodeModified':False,'GithubActionsUsed':False}
 write_json(ROOT/'V011_FULL84_RESPONSE_RECEIPT.json',metrics)
 print('FINISHED',json.dumps({k:metrics[k] for k in ['nonzeroVelocityResponsesT20Count','nonzeroPositionResponsesT20Count','largestPeakVelocityResponseT20','largestSeatResponseMagnitudeT20','executionWallSeconds','NPZBytes']},indent=2))
if __name__=='__main__':run()
