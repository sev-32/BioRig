#!/usr/bin/env python3
"""R580: causal, bounded proprioceptive hip/trunk adaptive recruitment.

The original 84-muscle R574 MuJoCo plant, baseline stabilizer and early intention
selector are never modified. Research controller only reads current sensors.
Development calibration: R579 scene00 drift between 23 and 28 simulated seconds.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/'r579'),str(HERE.parent/'r577'),str(HERE.parent/'r576')]
import r579_synergy as r579
import r577_tonic_support as r577
phys=r579.phys
DT=r579.DT

CONFIG={
    'triggerPositionM':0.0268,
    'fullRecruitAtM':0.0292,
    'lookaheadS':2.0,
    'hipNominal':0.025,
    'hipMax':0.037,
    'minimumTrunkFraction':0.20,
    'trunkSlewPer40ms':0.08,
    'hipSlewPer40ms':0.003,
    'startS':1.4,
    'positionGateM':0.008,
    'armAbortN':15.,
    'tiltAbortDeg':35.,
    'updateSeconds':0.04,
}

def clamp(v,a,b):return min(max(v,a),b)

def smoothstep(z):
    v=clamp(float(z),0.,1.)
    return v*v*(3.-2.*v)

class AdaptiveSynergy:
    """Maps sensed body state to named muscles, bounded in excitation units."""
    def __init__(self,model,config=None):
        self.config={**CONFIG,**(config or {})}
        c=self.config
        assert 0<=c['hipNominal']<=c['hipMax']<=phys.plant.MAX_EXTRA
        assert c['fullRecruitAtM']>c['triggerPositionM']>=0
        assert 0<=c['minimumTrunkFraction']<=1
        assert 0<c['trunkSlewPer40ms']<=1 and c['hipSlewPer40ms']>0
        self.model=model
        self.command=np.zeros(model.nu)
        self.groups={}
        for side in ('left','right'):
            names=r579.r551.GROUPS[side+'_lateral']
            self.groups[side]=tuple(mj.mj_name2id(model,mj.mjtObj.mjOBJ_ACTUATOR,n) for n in names)
            if any(i<0 for i in self.groups[side]):raise ValueError('missing anatomical actuator')
        self.hipDose=0.
        self.trunkFraction=c['minimumTrunkFraction']
        self.channelExcitationSeconds=0.
        self.squaredChannelExcitationSeconds=0.
        self.peakChannelDose=0.
        self.activeUpdates=0
        self.abortUpdates=0
        self.history=[]

    def update(self,t,obs):
        c=self.config
        x=float(obs['xPosition']);v=float(obs['xSpeed'])
        if not (np.isfinite(x) and np.isfinite(v)):
            self.command[:]=0.;self.hipDose=0.;self.abortUpdates+=1
            return
        away_speed=max(0.,np.sign(x)*v)
        predicted_abs_x=abs(x)+c['lookaheadS']*away_speed
        urgency=smoothstep((predicted_abs_x-c['triggerPositionM']) /
                           (c['fullRecruitAtM']-c['triggerPositionM']))
        target_trunk=c['minimumTrunkFraction']+(1-c['minimumTrunkFraction'])*urgency
        self.trunkFraction=clamp(target_trunk,
                                self.trunkFraction-c['trunkSlewPer40ms'],
                                self.trunkFraction+c['trunkSlewPer40ms'])
        abort=bool(float(obs['armsSeatN'])>=c['armAbortN'] or
                   float(obs['rootTiltDeg'])>=c['tiltAbortDeg'])
        engaged=bool(t>=c['startS'] and abs(x)>c['positionGateM'] and not abort)
        target=(c['hipNominal']+(c['hipMax']-c['hipNominal'])*urgency) if engaged else 0.
        self.hipDose=clamp(target,self.hipDose-c['hipSlewPer40ms'],
                          self.hipDose+c['hipSlewPer40ms'])
        self.command[:]=0.
        side='left' if x>=0 else 'right'
        trunk=self.hipDose*self.trunkFraction
        # R551 fixed anatomical order: QL-iliolumbar, QL-iliocostal,
        # gluteus medius, external oblique.
        for j,aid in enumerate(self.groups[side]):
            self.command[aid]=self.hipDose if j==2 else trunk
        self.channelExcitationSeconds+=float(self.command.sum())*c['updateSeconds']
        self.squaredChannelExcitationSeconds+=float(np.dot(self.command,self.command))*c['updateSeconds']
        self.peakChannelDose=max(self.peakChannelDose,float(np.max(self.command)))
        self.activeUpdates+=int(self.hipDose>0)
        self.abortUpdates+=int(abort)
        # compact 1Hz diagnostics; never read future data
        if round(t*25)%25==0:
            self.history.append({'t':round(t,2),'xM':x,'vxMps':v,
              'predictedAbsX_m':predicted_abs_x,'urgency':urgency,
              'hipDose':self.hipDose,'trunkFraction':self.trunkFraction,
              'safetyAbort':abort})
    def output(self):return self.command


def rollout(scene,choice,seconds=40.,config=None,stop_on_hazard=False,trace_period=.2):
    if choice not in ('none','R28'):raise ValueError('invalid R574 early action')
    if seconds<=0:raise ValueError('positive time required')
    pb,ref,neutral,saved=phys.paired_scene(scene['seatHalfWidthM'],scene['friction'])
    initial=phys.plant.sha_state(pb.data)
    d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
    early=phys.TimedPulse(pb.model,choice)
    support=AdaptiveSynergy(pb.model,config)
    max_arm=max_other=max_tilt=0.;lost=0;quietS=longestQuietS=0.;firstHazard=None
    trace=[];lastobs=None
    updates=round(.04/DT);sample=round(.02/DT);traceJump=max(1,round(trace_period/.02))
    release=max((st+hold+.12 for st,grp,hold,amp in early.profile),default=0.)
    total=round(seconds/DT);sidx=0
    for k in range(total+1):
        t=k*DT
        if k%sample==0 or k==total:
            obs=phys.sense(pb,d);lastobs=obs
            max_arm=max(max_arm,float(obs['armsSeatN']))
            max_other=max(max_other,float(obs['otherFloorN']))
            max_tilt=max(max_tilt,float(obs['rootTiltDeg']))
            lost+=int(obs['pelvisSeatN']<5 and obs['feetFloorN']<5)
            settled=bool(t>=release+.16 and r577.baseline.settling.is_settled(obs))
            quietS=quietS+.02 if settled else 0.
            longestQuietS=max(longestQuietS,quietS)
            hazard=max_arm>=50 or max_other>=50 or max_tilt>=45 or lost>=3
            if hazard and firstHazard is None:firstHazard=t
            if sidx%traceJump==0 or k==total:
                trace.append({'t':round(t,3),'xM':obs['xPosition'],'vxMps':obs['xSpeed'],
                    'tiltDeg':obs['rootTiltDeg'],'seatN':obs['pelvisSeatN'],
                    'feetN':obs['feetFloorN'],'armN':obs['armsSeatN'],
                    'hipDose':support.hipDose,'trunkFraction':support.trunkFraction,
                    'settledNow':settled})
            sidx+=1
            if stop_on_hazard and hazard:break
        if k==total:break
        if k%updates==0:
            obs=phys.sense(pb,d)
            early.update(t,obs)
            support.update(t,obs)
        cmd=np.clip(early.output()+support.output(),0.,phys.plant.MAX_EXTRA)
        applied=np.array([scene['forceN']*scene['direction'] if t<phys.plant.PUSH_S else 0.,0.,0.])
        phys.plant.step_perturbed(pb,d,ref,neutral,cmd,applied)
    assert initial==phys.plant.sha_state(pb.data)
    return {'schema':'lucid.r580.adaptive-synergy.native.v1','researchOnly':True,
        'controllerConfig':support.config,'initialSHA256':initial,
        'R574Choice':choice,'horizonS':seconds,'observedS':round(t,3),
        'complete':abs(t-seconds)<1e-7,'hazard':firstHazard is not None,
        'firstHazardS':firstHazard,'peakArmSeatN':max_arm,
        'peakOtherFloorN':max_other,'peakTiltDeg':max_tilt,
        'bothSupportLostSamples':lost,'settledAtEnd':quietS>=1.,
        'longestSettledS':longestQuietS,'finalX_m':lastobs['xPosition'],
        'finalV_mps':lastobs['xSpeed'],'finalTilt_deg':lastobs['rootTiltDeg'],
        'finalSeatN':lastobs['pelvisSeatN'],'finalFeetN':lastobs['feetFloorN'],
        'sumChannelExcitationSeconds':support.channelExcitationSeconds,
        'sumSquaredChannelExcitationSeconds':support.squaredChannelExcitationSeconds,
        'peakAdditionalMuscleDose':support.peakChannelDose,
        'activeUpdates':support.activeUpdates,'abortUpdates':support.abortUpdates,
        'controlEvents':support.history,'trace':trace}


def main():
    a=argparse.ArgumentParser()
    a.add_argument('--indices',type=int,nargs='+',default=[0]);a.add_argument('--seconds',type=float,default=40.)
    a.add_argument('--out',type=Path,required=True);a.add_argument('--stop-on-hazard',action='store_true')
    a.add_argument('--hip-max',type=float,default=CONFIG['hipMax']);a.add_argument('--full-recruit-at',type=float,default=CONFIG['fullRecruitAtM'])
    opts=a.parse_args()
    agent,old,lock=r577.baseline.frozen.frozen();scenes=r577.baseline.frozen.scenarios(lock)
    conf={**CONFIG,'hipMax':opts.hip_max,'fullRecruitAtM':opts.full_recruit_at}
    result={'schema':'lucid.r580.matched-scenario-research.v1','notHeldout':True,'results':[]}
    for i in opts.indices:
        scene=scenes[i]
        pb,ref,neutral,saved=phys.paired_scene(scene['seatHalfWidthM'],scene['friction'])
        measured=phys.initial_observation(pb,saved,ref,neutral,scene['forceN']*scene['direction'])
        choice=agent.decide(measured,'restore_supported_equilibrium')['choice']
        outcome=rollout(scene,choice,opts.seconds,conf,opts.stop_on_hazard)
        result['results'].append({'sceneIndex':i,'harness':scene,'choiceAt60ms':choice,'result':outcome})
        opts.out.parent.mkdir(parents=True,exist_ok=True)
        opts.out.write_text(json.dumps(result,indent=2,allow_nan=False))
        print(f'R580 scene={i} complete={outcome["complete"]} hazard={outcome["hazard"]} '+
              f'settled={outcome["settledAtEnd"]} x={outcome["finalX_m"]:.6f} tilt={outcome["finalTilt_deg"]:.3f} '+
              f'effort={outcome["sumChannelExcitationSeconds"]:.5f}',flush=True)
if __name__=='__main__':main()
