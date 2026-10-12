#!/usr/bin/env python3
"""R575 research-only physical latency audit; R574 source and training frozen.

At t=60ms apply a goal-conditioned decision computed using measurements from
60/40/20ms. At each 40ms extra-muscle controller feedback update apply the
same sensor delay. The MuJoCo plant and inherited native-muscle stabilizer
remain unchanged and still observe privileged current simulator mechanics.

This is therefore a true 8/12s native physical rollout with delayed high-level
sensing and pulse safety feedback, NOT full system-wide neuro-sensory latency.
No policy refit; no use of future outcomes when selecting an action.
"""
from __future__ import annotations
import sys,json,argparse,hashlib
from functools import lru_cache
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'R574_INTENTION_AND_AVERSION'))
import r574_evaluate as baseline
import r574_intention as goal
phys=goal.phy
DT=phys.DT
STEP_20MS=round(.020/DT)
STEP_40MS=round(.040/DT)
STEP_60MS=round(.060/DT)
assert (STEP_20MS,STEP_40MS,STEP_60MS)==(10,20,30)

@lru_cache(maxsize=8)
def frozen_scene(width,friction):
    return phys.paired_scene(width,friction)

def simulate(scene,agent,delay_ms=0,seconds=8.,goal_name='restore_supported_equilibrium',keep_trace=True):
    """One independently cloned saved initial physical state per condition."""
    assert delay_ms in (0,20,40)
    assert seconds in (8.,12.)
    pb,ref,neutral,saved=frozen_scene(scene['seatHalfWidthM'],scene['friction'])
    original_hash=phys.plant.sha_state(pb.data)
    d=mj.MjData(pb.model)
    mj.mj_copyData(d,pb.model,saved)
    kdelay=round(delay_ms/1000/DT)
    ctl=phys.TimedPulse(pb.model,'none')
    samples={};trace=[];action=None;decision=None
    arm=floor=tilt=0.;loss=0;settled_run=0.;longest=0.;last=None
    total_steps=round(seconds/DT)
    for k in range(total_steps+1):
        t=k*DT
        if k%STEP_20MS==0 or k==total_steps:
            obs=phys.sense(pb,d)
            samples[k]=obs
            last=obs
            arm=max(arm,obs['armsSeatN'])
            floor=max(floor,obs['otherFloorN'])
            tilt=max(tilt,obs['rootTiltDeg'])
            if obs['pelvisSeatN']<5 and obs['feetFloorN']<5:loss+=1
            # Match inherited r569 terminal definition, but only after release.
            release=(max(st+hold+.12 for st,g,hold,amp in ctl.profile)
                     if ctl.profile else 0.)
            settled=bool(t>=release+.16 and phys.settle.is_settled(obs))
            settled_run=settled_run+.02 if settled else 0.
            longest=max(longest,settled_run)
            if keep_trace:trace.append({'timeS':round(t,3),'settledNow':settled,**obs})
        if k==STEP_60MS:
            used=samples[k-kdelay]
            decision=agent.decide(used,goal_name)
            action=decision['choice']
            ctl=phys.TimedPulse(pb.model,action)
        if k==total_steps:break
        if k%STEP_40MS==0:
            # Delayed feedback only for extra-pulse controller; inherited
            # underlying muscle stabilizer in step_perturbed is instantaneous.
            sensing_step=max(0,k-kdelay)
            ctl.update(t,samples[sensing_step])
        applied=scene['forceN']*scene['direction']
        force=np.array([applied if t<phys.plant.PUSH_S else 0.,0.,0.])
        phys.plant.step_perturbed(pb,d,ref,neutral,ctl.output(),force)
    assert action is not None
    assert original_hash==phys.plant.sha_state(pb.data)
    hazard=bool(arm>=50 or floor>=50 or tilt>=45 or loss>=3)
    return {'schema':'lucid.r575.latency-physical-branch.v1',
        'researchOnly':True,'productionModified':False,'delayMs':delay_ms,
        'seconds':seconds,'scene':scene,'initialSHA256':original_hash,
        'chosenAction':action,'choiceReason':decision['reason'],
        'observedAtMs':60-delay_ms,'hazard':hazard,
        'settledAtEnd':bool(settled_run>=1.),'peakRootTiltDeg':tilt,
        'peakArmSeatN':arm,'peakOtherFloorN':floor,'bothSupportLossSamples':loss,
        'longestSettledS':longest,'finalX':last['xPosition'],'finalV':last['xSpeed'],
        'finalTiltDeg':last['rootTiltDeg'],'commandMax':ctl.peak,
        'trace':trace if keep_trace else None}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--indices',type=int,nargs='+',default=list(range(14)))
    ap.add_argument('--delays',type=int,nargs='+',default=[0,20,40])
    ap.add_argument('--seconds',type=float,default=8.)
    args=ap.parse_args()
    out=HERE/'measured'
    out.mkdir(exist_ok=True)
    agent,old,lock=baseline.frozen()
    scs=baseline.scenarios(lock)
    for i in args.indices:
      for delay in args.delays:
        s=scs[i]
        record=simulate(s,agent,delay,args.seconds)
        record['index']=i
        record['r574LockSHA256']=goal.sha(ROOT/'R574_INTENTION_AND_AVERSION/R574_EVALUATION_LOCK.json')
        record['r574ControllerSHA256']=goal.sha(ROOT/'R574_INTENTION_AND_AVERSION/r574_intention.py')
        record['r575SourceSHA256']=goal.sha(Path(__file__))
        dest=out/f'scene_{i:02d}_lag_{delay:02d}ms_{int(args.seconds)}s.json'
        dest.write_text(json.dumps(record,indent=2,allow_nan=False))
        print(f"R575 i={i:02d} lag={delay:02d}ms act={record['chosenAction']:<4} hazard={record['hazard']} settled={record['settledAtEnd']} peakTilt={record['peakRootTiltDeg']:.3f} arm={record['peakArmSeatN']:.3f}",flush=True)
if __name__=='__main__':main()
