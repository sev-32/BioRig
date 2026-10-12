#!/usr/bin/env python3
"""R579: hip-dominant muscle synergy experiment on the unchanged R574 plant.

The plant and frozen R574 policy are immutable. Profiles redistribute the *same*
R577 command amplitude over independently identified actuator channels; only
current proprioceptive observations determine side, onset and dose. No probe
result is read during online control; probes establish offline hypotheses.
"""
from __future__ import annotations
import argparse,json,sys,math
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/'r577'),str(HERE.parent/'r576')]
import r577_tonic_support as r577
import run_r551 as r551
phys=r577.phys
DT=r577.DT
# Normalized per-muscle excitation weights, not fractions of a force budget.
PROFILES={
 'r577_full':(1.,1.,1.,1.),
 'hip_only':(0.,0.,1.,0.),
 'hip_trunk_20pct':(.2,.2,1.,.2),
 'hip_trunk_50pct':(.5,.5,1.,.5),
}

class MuscleSynergy(r577.TonicSupport):
 def __init__(self,model,profile='hip_only'):
  super().__init__(model)
  if profile not in PROFILES:raise ValueError(profile)
  self.profile=profile
  self.weights=PROFILES[profile]
  self.effort_channel_seconds=0.
  self.effort_sq_seconds=0.
  self.muscle_channels={}
  self.group_counts={}
  for side in ('left','right'):
   names=r551.GROUPS[side+'_lateral']
   ids=[]
   for name in names:
    i=mj.mj_name2id(model,mj.mjtObj.mjOBJ_ACTUATOR,name)
    if i<0:raise KeyError(name)
    ids.append(i)
   self.muscle_channels[side]=tuple(ids)
  self.last_mask=np.zeros(model.nu)
 def update(self,t,o):
  super().update(t,o)
  self.command[:]=0.
  if self.amplitude>0:
   side='left' if o['xPosition']>=0 else 'right'
   for aid,w in zip(self.muscle_channels[side],self.weights):
    self.command[aid]=self.amplitude*w
  self.effort_channel_seconds+=float(self.command.sum())*.04
  self.effort_sq_seconds+=float(np.dot(self.command,self.command))*.04
  self.last_mask[:]=self.command


def rollout(scene,choice,profile,seconds=12.,trace_step_s=.2,stop_on_hazard=False):
 if seconds<=0 or choice not in ('none','R28') or profile not in PROFILES:raise ValueError('invalid inputs')
 pb,ref,neu,saved=phys.paired_scene(scene['seatHalfWidthM'],scene['friction'])
 initial=phys.plant.sha_state(pb.data)
 d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
 early=phys.TimedPulse(pb.model,choice)
 support=MuscleSynergy(pb.model,profile)
 max_arm=max_other=max_tilt=0.
 sample_step=round(.02/DT); update_step=round(.04/DT)
 trace_jump=max(1,round(trace_step_s/.02))
 both_lost=0; settled_run=0.;longest=0.;first_hazard=None;obs_last=None;sample_idx=0
 trace=[];total_steps=round(seconds/DT)
 release=max((start+hold+.12 for start,group,hold,amp in early.profile),default=0.)
 for k in range(total_steps+1):
  t=k*DT
  if k%sample_step==0 or k==total_steps:
   obs=phys.sense(pb,d);obs_last=obs
   max_arm=max(max_arm,obs['armsSeatN']);max_other=max(max_other,obs['otherFloorN']);max_tilt=max(max_tilt,obs['rootTiltDeg'])
   both_lost+=int(obs['pelvisSeatN']<5 and obs['feetFloorN']<5)
   settled=bool(t>=release+.16 and r577.baseline.settling.is_settled(obs))
   settled_run=settled_run+.02 if settled else 0.
   longest=max(longest,settled_run)
   hazard=max_arm>=50 or max_other>=50 or max_tilt>=45 or both_lost>=3
   if first_hazard is None and hazard:first_hazard=t
   if sample_idx%trace_jump==0 or k==total_steps:
    trace.append({'timeS':round(t,3),'xM':obs['xPosition'],'speedMps':obs['xSpeed'],'tiltDeg':obs['rootTiltDeg'],
      'seatN':obs['pelvisSeatN'],'feetN':obs['feetFloorN'],'armN':obs['armsSeatN'],
      'tonicPerMuscleDose':support.amplitude,'settledNow':settled})
   sample_idx+=1
   if stop_on_hazard and hazard:break
  if k==total_steps:break
  if k%update_step==0:
   obs=phys.sense(pb,d)
   early.update(t,obs)
   support.update(t,obs)
  delta=np.clip(early.output()+support.output(),0.,.04)
  ext=np.array([scene['forceN']*scene['direction'] if t<phys.plant.PUSH_S else 0.,0.,0.])
  phys.plant.step_perturbed(pb,d,ref,neu,delta,ext)
 assert initial==phys.plant.sha_state(pb.data)
 return {'schema':'lucid.r579.muscle-synergy.v1','profile':profile,'choice':choice,
  'initialSHA256':initial,'requestedHorizonS':seconds,'observedHorizonS':round(t,3),
  'complete':abs(t-seconds)<1e-7,'hazard':first_hazard is not None,'firstHazardS':first_hazard,
  'peakTiltDeg':max_tilt,'peakArmSeatN':max_arm,'peakOtherFloorN':max_other,'bothSupportLossSamples':both_lost,
  'settledAtEnd':settled_run>=1.,'maxContinuousSettledS':longest,
  'finalX_m':obs_last['xPosition'],'finalV_mps':obs_last['xSpeed'],'finalTilt_deg':obs_last['rootTiltDeg'],
  'finalSeatN':obs_last['pelvisSeatN'],'finalFeetN':obs_last['feetFloorN'],
  'sumChannelExcitationSeconds':support.effort_channel_seconds,
  'sumSquaredChannelExcitationSeconds':support.effort_sq_seconds,
  'tonicControllerAmplitudeSeconds':support.commandL1Seconds,'tonicUpdates':support.enabledUpdates,
  'muscleChannelWeights':PROFILES[profile],'trace':trace}

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--scenes',type=int,nargs='+',default=[0]);parser.add_argument('--profiles',nargs='+',default=['r577_full','hip_only','hip_trunk_20pct'])
 parser.add_argument('--seconds',type=float,default=12.)
 parser.add_argument('--stop-on-hazard',action='store_true')
 parser.add_argument('--out',type=Path,required=True)
 a=parser.parse_args()
 agent,old,lock=r577.baseline.frozen.frozen();scenes=r577.baseline.frozen.scenarios(lock)
 report={'schema':'lucid.r579.matched-profile-sweep.v1','frozenR574LockSHA256':r577.baseline.frozen.ctl.sha(r577.baseline.ROOT/'R574_INTENTION_AND_AVERSION/R574_EVALUATION_LOCK.json'),
    'selectedAfterObservingScene00Failure':True,'researchOnly':True,'results':[]}
 for i in a.scenes:
  scene=scenes[i]
  pb,ref,neutral,saved=phys.paired_scene(scene['seatHalfWidthM'],scene['friction'])
  sensed=phys.initial_observation(pb,saved,ref,neutral,scene['forceN']*scene['direction'])
  choice=agent.decide(sensed,'restore_supported_equilibrium')['choice']
  for p in a.profiles:
   result=rollout(scene,choice,p,a.seconds,stop_on_hazard=a.stop_on_hazard)
   report['results'].append({'sceneIndex':i,'scene':scene,'choiceAt60ms':choice,'result':result})
   a.out.parent.mkdir(parents=True,exist_ok=True)
   a.out.write_text(json.dumps(report,indent=2,allow_nan=False))
   print(f'R579 scene={i} profile={p} {a.seconds:g}s done={result["complete"]} hazard={result["hazard"]} settle={result["settledAtEnd"]} x={result["finalX_m"]:.6f} tilt={result["finalTilt_deg"]:.2f} effort={result["sumChannelExcitationSeconds"]:.5f}',flush=True)
if __name__=='__main__':main()
