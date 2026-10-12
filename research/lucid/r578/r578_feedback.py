#!/usr/bin/env python3
"""R578 controlled research: support-aware gradual muscle feedback vs frozen R577.

No edits to R574/R575/R576/R577. All online variables are sensed; counterfactual
scene/force metadata is only applied to the test harness. No position locking.
Experimental tuning on known-failing scene00 is *not heldout generalization*.
"""
from __future__ import annotations
import argparse,sys,json
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'r577'),str(HERE.parent/'r576')]
import r577_tonic_support as inherited
from r578_support import measure
phys=inherited.phys
DT=inherited.DT

CONFIG={
 'initialTonicDose':.025,'feedbackStartS':4.,'onsetS':1.4,
 'rootTargetM':.026,'kpRootPerM':.40,'kdRootPerMps':.40,
 'kpComPerM':.0,'comDeadbandM':.007,'doseFloor':.015,'doseCeiling':.038,
 'positionGateM':.008,'slewPer40ms':.003,'armAbortN':15.,
 'tiltAbortDeg':35.,'minSupportLoadN':50.,'updateIntervalS':.04}

class SupportFeedback:
    def __init__(self,model,config=None):
        self.c={**CONFIG,**(config or {})}
        c=self.c
        assert 0 <= c['doseFloor'] <= c['initialTonicDose'] <= c['doseCeiling'] <= phys.plant.MAX_EXTRA
        self.masks={side:phys.plant.pulse_for(model,side+'_lateral')/phys.plant.MAX_EXTRA for side in ('left','right')}
        self.command=np.zeros(model.nu)
        self.amplitude=0.
        self.energy_proxy=0.;self.updates=0;self.aborts=0
        self.last_support=None
        self.events=[]
    def update(self,t,obs,pb,d):
        c=self.c
        sup=measure(pb.model,d)
        self.last_support=sup
        x=float(obs['xPosition']);v=float(obs['xSpeed'])
        sign=1 if x>=0 else -1
        side='left' if sign==1 else 'right'
        forbidden=(not sup.valid or sup.measuredNormalLoad_N<c['minSupportLoadN'] or
                   obs['armsSeatN']>=c['armAbortN'] or obs['rootTiltDeg']>=c['tiltAbortDeg'])
        requested=0.
        if t>=c['onsetS'] and abs(x)>c['positionGateM'] and not forbidden:
            requested=c['initialTonicDose']
            if t>=c['feedbackStartS']:
                # Root position and velocity use pelvis x as a support-relative
                # approximation on fixed bench. COM-CoP adds independent feedback.
                comterm=(sign*sup.comRelativeToPressure_m-c['comDeadbandM'])
                requested+= (c['kpRootPerM']*(abs(x)-c['rootTargetM'])
                             +c['kdRootPerMps']*(sign*v)
                             +c['kpComPerM']*comterm)
                requested=float(np.clip(requested,c['doseFloor'],c['doseCeiling']))
        self.amplitude=float(np.clip(requested,self.amplitude-c['slewPer40ms'],
                          self.amplitude+c['slewPer40ms']))
        self.command[:]=self.masks[side]*self.amplitude
        self.energy_proxy+=self.amplitude*c['updateIntervalS']
        self.updates+=int(self.amplitude>0)
        self.aborts+=int(forbidden)
        if round(t*25)%25==0:
            self.events.append({'t':round(t,2),'dose':self.amplitude,
                    'x':x,'speed':v,'comX':sup.comX_m,
                    'pressureX':sup.centerOfPressureX_m,
                    'comOverSupport':sup.comRelativeToPressure_m,
                    'supportLoadN':sup.measuredNormalLoad_N,
                    'contacts':sup.contactCount,'forbidden':forbidden})
    def output(self):return self.command


def run(scene,choice='none',seconds=40,mode='pd',config=None,stop_on_hazard=False,trace_interval=.2):
    if mode not in ('pd','tonic','neutral'):raise ValueError(mode)
    if choice not in ('none','R28'):raise ValueError(choice)
    pb,ref,neutral,saved=phys.paired_scene(scene['seatHalfWidthM'],scene['friction'])
    initial=phys.plant.sha_state(pb.data)
    d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
    early=phys.TimedPulse(pb.model,choice)
    controller=(SupportFeedback(pb.model,config) if mode=='pd' else
                inherited.TonicSupport(pb.model) if mode=='tonic' else None)
    maxarm=maxother=maxtilt=0.;loss=0;settled=0.;longest=0.;trace=[]
    firsthazard=None;lastobs=None;observed=0.
    steps=round(seconds/DT);sample_step=round(.02/DT);update_step=round(.04/DT)
    trace_step=max(1,round(trace_interval/.02));sample_no=0
    release=max((st+hold+.12 for st,group,hold,amp in early.profile),default=0)
    for k in range(steps+1):
        t=k*DT
        if k%sample_step==0 or k==steps:
            obs=phys.sense(pb,d);lastobs=obs;observed=t
            maxarm=max(maxarm,float(obs['armsSeatN']))
            maxother=max(maxother,float(obs['otherFloorN']))
            maxtilt=max(maxtilt,float(obs['rootTiltDeg']))
            loss+=int(obs['pelvisSeatN']<5 and obs['feetFloorN']<5)
            quiet=bool(t>=release+.16 and inherited.baseline.settling.is_settled(obs))
            settled=settled+.02 if quiet else 0.
            longest=max(longest,settled)
            hazard=maxarm>=50 or maxother>=50 or maxtilt>=45 or loss>=3
            if firsthazard is None and hazard:firsthazard=t
            if sample_no%trace_step==0 or k==steps:
                sup=measure(pb.model,d)
                trace.append({'t':round(t,3),'x':obs['xPosition'],
                   'v':obs['xSpeed'],'tilt':obs['rootTiltDeg'],
                   'armN':obs['armsSeatN'],'seatN':obs['pelvisSeatN'],
                   'feetN':obs['feetFloorN'],'settled':quiet,
                   'dose':controller.amplitude if controller is not None else 0.,
                   'comRelativeToSupport_m':sup.comRelativeToPressure_m,
                   'supportLoadN':sup.measuredNormalLoad_N,'supportValid':sup.valid})
            sample_no+=1
            if stop_on_hazard and hazard:break
        if k==steps:break
        if k%update_step==0:
            obs=phys.sense(pb,d);early.update(t,obs)
            if mode=='pd':controller.update(t,obs,pb,d)
            elif mode=='tonic':controller.update(t,obs)
        delta=early.output() if controller is None else np.clip(early.output()+controller.output(),0.,.04)
        ext=np.array([scene['forceN']*scene['direction'] if t<phys.plant.PUSH_S else 0.,0.,0.])
        phys.plant.step_perturbed(pb,d,ref,neutral,delta,ext)
    assert phys.plant.sha_state(pb.data)==initial
    result={'schema':'lucid.r578.feedback-physical-v1','mode':mode,'choice':choice,
      'initialSHA256':initial,'requestedHorizonS':seconds,'observedHorizonS':round(observed,3),
      'complete':abs(observed-seconds)<1e-6,'hazard':firsthazard is not None,
      'firstHazardS':firsthazard,'peakTiltDeg':maxtilt,'peakArmN':maxarm,
      'peakOtherFloorN':maxother,'supportLossSamples':loss,
      'settledAtEnd':settled>=1.,'longestSettledS':longest,
      'finalX':lastobs['xPosition'],'finalV':lastobs['xSpeed'],
      'finalTilt':lastobs['rootTiltDeg'],'finalSeatN':lastobs['pelvisSeatN'],
      'finalFeetN':lastobs['feetFloorN'],
      'doseIntegralSeconds':controller.energy_proxy if mode=='pd' else
                           (controller.commandL1Seconds if mode=='tonic' else 0.),
      'controlEvents':controller.events if mode=='pd' else [],'trace':trace}
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--indices',nargs='+',type=int,default=[0]);ap.add_argument('--seconds',type=float,default=40.)
    ap.add_argument('--mode',choices=['pd','tonic','neutral'],default='pd')
    ap.add_argument('--root-target',type=float,default=CONFIG['rootTargetM'])
    ap.add_argument('--kp-root',type=float,default=CONFIG['kpRootPerM'])
    ap.add_argument('--kd-root',type=float,default=CONFIG['kdRootPerMps'])
    ap.add_argument('--kp-com',type=float,default=CONFIG['kpComPerM'])
    ap.add_argument('--stop-on-hazard',action='store_true')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    agent,_,lock=inherited.baseline.frozen.frozen();scenes=inherited.baseline.frozen.scenarios(lock)
    conf={**CONFIG,'rootTargetM':a.root_target,'kpRootPerM':a.kp_root,'kdRootPerMps':a.kd_root,'kpComPerM':a.kp_com}
    out={'schema':'lucid.r578.experimental-paired.v1','notHeldoutEvidence':True,
         'controlConfig':conf,'results':[]}
    for i in a.indices:
        sc=scenes[i]
        pb,ref,neutral,saved=phys.paired_scene(sc['seatHalfWidthM'],sc['friction'])
        measured=phys.initial_observation(pb,saved,ref,neutral,sc['forceN']*sc['direction'])
        choice=agent.decide(measured,'restore_supported_equilibrium')['choice']
        result=run(sc,choice,a.seconds,mode=a.mode,config=conf,stop_on_hazard=a.stop_on_hazard)
        out['results'].append({'sceneIndex':i,'scene':sc,'choice':choice,'outcome':result})
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(out,indent=2,allow_nan=False))
        print(f'R578 {a.mode} scene={i} {a.seconds}s complete={result["complete"]} hazard={result["hazard"]} settled={result["settledAtEnd"]} x={result["finalX"]:.6f} tilt={result["finalTilt"]:.2f} dose_s={result["doseIntegralSeconds"]:.4f}',flush=True)
if __name__=='__main__':main()
