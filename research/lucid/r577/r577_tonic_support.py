#!/usr/bin/env python3
"""R577: native sensed-state bounded tonic recruitment research.

The frozen R574 predictor, R569/562 base stabilizer, MuJoCo model and initial
states are never modified. The optional low-level overlay senses only current
posture/contacts. R577 candidate parameters are tuned on R574 scene00 and have
NOT been certified on held-out scenes. No root locking or external pose forces.
"""
from __future__ import annotations
import argparse,json,sys,hashlib
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'r576')]
import r576_longhorizon as baseline

DT=baseline.DT
phys=baseline.phy
CONFIG={'onsetS':1.4,'positionGateM':0.008,
        'tonicDose':0.025,'slewPer40ms':0.003,
        'contactAbortArmN':15.0,'tiltAbortDeg':35.0,
        'decisionIntervalS':0.04,'sampleIntervalS':0.02}

class TonicSupport:
    def __init__(self,model,config=None):
        self.config=dict(CONFIG if config is None else config)
        c=self.config
        assert c['tonicDose']<=phys.plant.MAX_EXTRA and c['tonicDose']>=0
        assert c['slewPer40ms']>0 and c['positionGateM']>=0
        self.masks={side:phys.plant.pulse_for(model,side+'_lateral')/phys.plant.MAX_EXTRA
            for side in ('left','right')}
        self.amplitude=0.0
        self.command=np.zeros(model.nu)
        self.lastGroup=None
        self.enabledUpdates=0
        self.abortUpdates=0
        self.maxAmplitude=0.
        self.commandL1Seconds=0.
        self.history=[]

    def update(self,t,obs):
        c=self.config
        x=float(obs['xPosition'])
        group='left' if x>0 else 'right'
        hardstop=bool(obs['armsSeatN']>=c['contactAbortArmN'] or
                      obs['rootTiltDeg']>=c['tiltAbortDeg'])
        target=(c['tonicDose'] if t>=c['onsetS'] and
                abs(x)>c['positionGateM'] and not hardstop else 0.)
        self.amplitude=float(np.clip(target,self.amplitude-c['slewPer40ms'],
                                    self.amplitude+c['slewPer40ms']))
        self.command[:]=self.masks[group]*self.amplitude
        self.lastGroup=group if self.amplitude>0 else None
        self.maxAmplitude=max(self.maxAmplitude,self.amplitude)
        self.commandL1Seconds+=self.amplitude*c['decisionIntervalS']
        self.enabledUpdates+=int(self.amplitude>0)
        self.abortUpdates+=int(hardstop)
        self.history.append({'timeS':round(t,3),'measuredPositionM':x,
            'measuredSpeedMps':float(obs['xSpeed']),
            'measuredTiltDeg':float(obs['rootTiltDeg']),
            'measuredArmN':float(obs['armsSeatN']),
            'muscleGroup':self.lastGroup,
            'dose':self.amplitude,'safetyAbort':hardstop})
    def output(self):return self.command


def rollout(scene,choice='none',seconds=40.,tonic=True,trace_interval=.1,
            stop_on_hazard=False):
    """Reinstantiate and clone the same warmup for every condition.

    stop_on_hazard is only a resource bound, used for *failed* runs. Hazards are
    sampled at 20 ms independently of whether the caller requests a trace.
    """
    if choice not in ('none','R28'):raise ValueError(choice)
    if seconds<=0 or trace_interval<DT:raise ValueError('invalid horizon/trace interval')
    pb,ref,neutral,saved=phys.paired_scene(scene['seatHalfWidthM'],scene['friction'])
    initial=phys.plant.sha_state(pb.data)
    d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
    early=phys.TimedPulse(pb.model,choice)
    guard=TonicSupport(pb.model) if tonic else None
    max_arm=max_other=max_tilt=0.
    loss=0;settled=0.;max_settled=0.;trace=[];observed_s=0.;first_hazard=None
    release=max((start+hold+.12 for start,group,hold,amp in early.profile),default=0.)
    sample_interval=round(.020/DT);update_interval=round(.040/DT)
    skip=max(1,round(trace_interval/.020));sample_i=0
    for k in range(round(seconds/DT)+1):
        t=k*DT
        if k%sample_interval==0 or k==round(seconds/DT):
            o=phys.sense(pb,d);observed_s=t
            max_arm=max(max_arm,o['armsSeatN']);max_other=max(max_other,o['otherFloorN'])
            max_tilt=max(max_tilt,o['rootTiltDeg'])
            loss+=int(o['pelvisSeatN']<5 and o['feetFloorN']<5)
            # Tonic muscle maintenance is not a pulse-release event; posture
            # and contact requirements are nevertheless measured without relaxation.
            settled_now=(t>=release+.16 and baseline.settling.is_settled(o))
            settled=settled+.020 if settled_now else 0.
            max_settled=max(max_settled,settled)
            haz=max_arm>=50 or max_other>=50 or max_tilt>=45 or loss>=3
            if haz and first_hazard is None:first_hazard=t
            if sample_i%skip==0 or k==round(seconds/DT):
                trace.append({'timeS':round(t,3),'settledNow':bool(settled_now),
                              'tonicDose':guard.amplitude if guard else 0.,**o})
            sample_i+=1
            if stop_on_hazard and haz:break
        if k==round(seconds/DT):break
        if k%update_interval==0:
            o=phys.sense(pb,d)
            early.update(t,o)
            if guard:guard.update(t,o)
        delta=early.output() if not guard else np.clip(early.output()+guard.output(),0.,.04)
        push=np.array([scene['forceN']*scene['direction'] if t<phys.plant.PUSH_S else 0.,0.,0.])
        phys.plant.step_perturbed(pb,d,ref,neutral,delta,push)
    assert phys.plant.sha_state(pb.data)==initial
    return {'schema':'lucid.r577.tonic-recruitment.native.v1',
       'requestedHorizonS':seconds,'observedHorizonS':round(observed_s,3),
       'complete':abs(observed_s-seconds)<1e-6,'frozenR574Choice':choice,
       'initialSHA256':initial,'tonicEnabled':tonic,
       'hazard':first_hazard is not None,'firstHazardS':first_hazard,
       'peakRootTiltDeg':max_tilt,'peakArmSeatN':max_arm,
       'peakOtherFloorN':max_other,'bothSupportLossSamples':loss,
       'settledAtEnd':bool(settled>=1.),'longestSettledS':max_settled,
       'finalX':float(o['xPosition']),'finalV':float(o['xSpeed']),
       'finalTiltDeg':float(o['rootTiltDeg']),
       'finalAngularSpeed':float(o['rootAngularSpeed']),
       'finalSeatN':float(o['pelvisSeatN']),
       'finalFeetN':float(o['feetFloorN']),
       'muscleDoseIntegralSeconds':(guard.commandL1Seconds if guard else 0.),
       'tonicUpdates':guard.enabledUpdates if guard else 0,
       'tonicAbortUpdates':guard.abortUpdates if guard else 0,
       'maxAdditionalDose':guard.maxAmplitude if guard else 0.,
       'trace':trace}


def main():
    a=argparse.ArgumentParser()
    a.add_argument('--indices',type=int,nargs='+',default=[0])
    a.add_argument('--seconds',type=float,default=40.)
    a.add_argument('--control',choices=('none','tonic'),default='tonic')
    a.add_argument('--trace-interval',type=float,default=.1)
    a.add_argument('--stop-on-hazard',action='store_true')
    a.add_argument('--out',type=Path,required=True)
    args=a.parse_args()
    agent,_,lock=baseline.frozen.frozen();scenes=baseline.frozen.scenarios(lock)
    rows=[]
    for i in args.indices:
        scene=scenes[i]
        pb,ref,neut,saved=phys.paired_scene(scene['seatHalfWidthM'],scene['friction'])
        obs=phys.initial_observation(pb,saved,ref,neut,scene['forceN']*scene['direction'])
        choice=agent.decide(obs,'restore_supported_equilibrium')['choice']
        outcome=rollout(scene,choice,args.seconds,args.control=='tonic',args.trace_interval,args.stop_on_hazard)
        rows.append({'index':i,'harness':scene,'chosenFromSensed60ms':choice,
                     'outcome':outcome})
        print(f'R577 scene={i} choice={choice} control={args.control} ' +
             f'completed={outcome["complete"]} hazard={outcome["hazard"]} ' +
             f'lastTilt={outcome["finalTiltDeg"]:.2f} settled={outcome["settledAtEnd"]}',flush=True)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps({'schema':'lucid.r577.frozen-postlock-experiments.v1',
           'experimentalNotPromotionEvidence':True,'configuration':CONFIG,
           'frozenR574LockSHA256':baseline.frozen.ctl.sha(baseline.ROOT/'R574_INTENTION_AND_AVERSION/R574_EVALUATION_LOCK.json'),
           'rows':rows},indent=2,allow_nan=False))
if __name__=='__main__':main()
