#!/usr/bin/env python3
"""R582 signed-wrench hip/oblique correction on frozen native LUCID plant.

Development experiment, NOT production or heldout evidence. A causal feedback
loop uses sensed root displacement+speed, center of mass relative to measured
seat/foot signed contact wrench and support load. Named muscles only, no direct root forces.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'r580'),str(HERE.parent/'r577')]
import r580_adaptive_synergy as inherited
from r582_wrench import sense_wrench
phy=inherited.phys
DT=inherited.DT
CONFIG={'onsetS':1.4,'positionGateM':.008,
        'hipNominal':.025,'hipMax':.033,'hipPositionTargetM':.026,
        'hipPositionGain_perM':.9,'hipVelocityGain_perMps':.18,
        'obliqueNominal':.014,'obliqueMax':.030,
        'comProjectedDeadbandM':.0045,'obliqueComGain_perM':1.2,
        'obliquePositionGain_perM':.8,
        'hipSlewPer40ms':.003,'obliqueSlewPer40ms':.002,
        'minSupportLoadN':50.,'abortArmSeatN':15.,'abortTiltDeg':35.,
        'decisionSeconds':.04}

class SignedWrenchAllocator:
 def __init__(self,model,config=None):
    self.c={**CONFIG,**(config or {})}
    c=self.c
    assert 0<=c['hipNominal']<=c['hipMax']<=phy.plant.MAX_EXTRA
    assert 0<=c['obliqueNominal']<=c['obliqueMax']<=phy.plant.MAX_EXTRA
    assert c['decisionSeconds']>0 and c['hipSlewPer40ms']>0 and c['obliqueSlewPer40ms']>0
    self.channels={}
    for side in ('left','right'):
        ids={}
        for semantic,suffix in [('hip','gluteus_medius'),('trunk','external_oblique')]:
            i=mj.mj_name2id(model,mj.mjtObj.mjOBJ_ACTUATOR,'m_'+side+'_'+suffix)
            if i<0:raise ValueError('missing '+suffix)
            ids[semantic]=i
        self.channels[side]=ids
    self.command=np.zeros(model.nu)
    self.hip=self.trunk=0.
    self.channelEffort=0.;self.squaredEffort=0.;self.abortUpdates=0
    self.updateCount=0;self.lastSupport=None;self.history=[]
 def update(self,t,observation,model,data):
    c=self.c
    support=sense_wrench(model,data)
    self.lastSupport=support
    x=float(observation['xPosition']);v=float(observation['xSpeed'])
    finite=bool(np.isfinite([x,v,float(observation['rootTiltDeg'])]).all())
    safe=bool(finite and support.valid_projection
        and np.isfinite(support.com_minus_projected_reaction_m)
        and support.normal_vertical_reaction_N>=c['minSupportLoadN']
        and float(observation['armsSeatN'])<c['abortArmSeatN']
        and float(observation['rootTiltDeg'])<c['abortTiltDeg'])
    engaged=safe and t>=c['onsetS'] and abs(x)>=c['positionGateM']
    side='left' if x>=0 else 'right'
    hip_target=trunk_target=0.
    if engaged:
        outward_vel=max(0.,np.sign(x)*v)
        excess=max(0.,abs(x)-c['hipPositionTargetM'])
        hip_target=np.clip(c['hipNominal']+c['hipPositionGain_perM']*excess+
                    c['hipVelocityGain_perMps']*outward_vel,0.,c['hipMax'])
        # COM-to-projected-reaction error (includes signed friction and free moments) must point toward the same outward side;
        # otherwise trunk stimulation is kept at nominal, avoiding reflex sign-flip.
        bad_com=max(0.,np.sign(x)*support.com_minus_projected_reaction_m-c['comProjectedDeadbandM'])
        trunk_target=np.clip(c['obliqueNominal']+c['obliqueComGain_perM']*bad_com+
                  c['obliquePositionGain_perM']*excess,0.,c['obliqueMax'])
    self.hip=float(np.clip(hip_target,self.hip-c['hipSlewPer40ms'],self.hip+c['hipSlewPer40ms']))
    self.trunk=float(np.clip(trunk_target,self.trunk-c['obliqueSlewPer40ms'],self.trunk+c['obliqueSlewPer40ms']))
    self.command[:]=0.
    self.command[self.channels[side]['hip']]=self.hip
    self.command[self.channels[side]['trunk']]=self.trunk
    self.channelEffort+=float(self.command.sum())*c['decisionSeconds']
    self.squaredEffort+=float(self.command@self.command)*c['decisionSeconds']
    self.abortUpdates+=int(not safe)
    self.updateCount+=1
    if self.updateCount%25==0:
        self.history.append({'timeS':round(t,3),'rootX_m':x,'rootV_mps':v,
          'comMinusProjected_m':support.com_minus_projected_reaction_m,
                    'comMinusVerticalPressure_m':support.com_minus_pressure_m,
                    'shearX_N':support.total_lateral_shear_N,
                    'contactMomentCOM_Z_Nm':support.moment_about_com_world_Nm[2],'verticalLoad_N':support.normal_vertical_reaction_N,
          'hipDose':self.hip,'obliqueDose':self.trunk,'safe':safe})
 def output(self):return self.command

def rollout(scene,choice='none',seconds=12.,config=None,trace_step_s=.2,stop_on_hazard=False):
    if choice not in ('none','R28') or seconds<=0:raise ValueError('invalid inputs')
    pb,ref,neutral,saved=phy.paired_scene(scene['seatHalfWidthM'],scene['friction'])
    original=phy.plant.sha_state(pb.data)
    d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
    early=phy.TimedPulse(pb.model,choice)
    controller=SignedWrenchAllocator(pb.model,config)
    sampleStep=round(.02/DT);updateStep=round(.04/DT);jump=max(1,round(trace_step_s/.02))
    maxarm=maxfloor=maxtilt=0.;loss=0;settledS=longest=0.;firstHazard=None;last=None
    trace=[];sample_i=0;steps=round(seconds/DT)
    release=max((start+hold+.12 for start,group,hold,amp in early.profile),default=0.)
    for k in range(steps+1):
        t=k*DT
        if k%sampleStep==0 or k==steps:
            o=phy.sense(pb,d);last=o
            maxarm=max(maxarm,float(o['armsSeatN']))
            maxfloor=max(maxfloor,float(o['otherFloorN']))
            maxtilt=max(maxtilt,float(o['rootTiltDeg']))
            loss+=int(o['pelvisSeatN']<5 and o['feetFloorN']<5)
            settled=bool(t>=release+.16 and inherited.r577.baseline.settling.is_settled(o))
            settledS=settledS+.02 if settled else 0.
            longest=max(longest,settledS)
            hazard=maxarm>=50 or maxfloor>=50 or maxtilt>=45 or loss>=3
            if hazard and firstHazard is None:firstHazard=t
            if sample_i%jump==0 or k==steps:
                support=sense_wrench(pb.model,d)
                trace.append({'tS':round(t,3),'rootX_m':o['xPosition'],
                    'rootV_mps':o['xSpeed'],'rootTilt_deg':o['rootTiltDeg'],
                    'seatN':o['pelvisSeatN'],'feetN':o['feetFloorN'],'armN':o['armsSeatN'],
                    'hipDose':controller.hip,'trunkDose':controller.trunk,
                    'comMinusProjected_m':support.com_minus_projected_reaction_m,
                    'comMinusVerticalPressure_m':support.com_minus_pressure_m,
                    'shearX_N':support.total_lateral_shear_N,
                    'contactMomentCOM_Z_Nm':support.moment_about_com_world_Nm[2],'projectedReactionX_m':support.projected_reaction_x_at_plane_m,
                    'verticalReaction_N':support.normal_vertical_reaction_N,'settled':settled})
            sample_i+=1
            if stop_on_hazard and hazard:break
        if k==steps:break
        if k%updateStep==0:
            o=phy.sense(pb,d)
            early.update(t,o)
            controller.update(t,o,pb.model,d)
        extra=np.clip(early.output()+controller.output(),0.,phy.plant.MAX_EXTRA)
        applied=np.array([scene['forceN']*scene['direction'] if t<phy.plant.PUSH_S else 0.,0.,0.])
        phy.plant.step_perturbed(pb,d,ref,neutral,extra,applied)
    assert phy.plant.sha_state(pb.data)==original
    sup=sense_wrench(pb.model,d)
    return {'schema':'lucid.r582.signed-wrench.native.v1','researchOnly':True,
      'notHeldOut':True,'projectedReactionNotStabilityMargin':True,
      'config':controller.c,'frozenChoice':choice,'initialSHA256':original,
      'requestedSeconds':seconds,'observedSeconds':round(t,3),'complete':abs(t-seconds)<1e-7,
      'hazard':firstHazard is not None,'firstHazardS':firstHazard,
      'peakRootTilt_deg':maxtilt,'peakArm_N':maxarm,'peakFloor_N':maxfloor,
      'bothSupportLossSamples':loss,'settledAtEnd':settledS>=1.,'longestSettledSeconds':longest,
      'finalRootX_m':last['xPosition'],'finalRootV_mps':last['xSpeed'],
      'finalTilt_deg':last['rootTiltDeg'],'finalSeatN':last['pelvisSeatN'],
      'finalFeetN':last['feetFloorN'],'finalCOMminusProjected_m':sup.com_minus_projected_reaction_m,
      'finalCOMminusVerticalPressure_m':sup.com_minus_pressure_m,
      'finalShearX_N':sup.total_lateral_shear_N,
      'finalWrenchMomentCOMz_Nm':sup.moment_about_com_world_Nm[2],
      'finalProjectedReactionX_m':sup.projected_reaction_x_at_plane_m,'finalCOMx_m':sup.com_world_m[0],
      'muscleChannelExcitationSeconds':controller.channelEffort,
      'squaredChannelExcitationSeconds':controller.squaredEffort,
      'abortUpdates':controller.abortUpdates,'controlEvents':controller.history,'trace':trace}

def main():
 p=argparse.ArgumentParser();p.add_argument('--indices',type=int,nargs='+',default=[0]);p.add_argument('--seconds',type=float,default=12.)
 p.add_argument('--out',type=Path,required=True);p.add_argument('--stop-on-hazard',action='store_true')
 args=p.parse_args()
 agent,_,lock=inherited.r577.baseline.frozen.frozen()
 scenes=inherited.r577.baseline.frozen.scenarios(lock)
 rows=[]
 for i in args.indices:
    sc=scenes[i];pb,ref,neu,saved=phy.paired_scene(sc['seatHalfWidthM'],sc['friction'])
    sensed=phy.initial_observation(pb,saved,ref,neu,sc['forceN']*sc['direction'])
    choice=agent.decide(sensed,'restore_supported_equilibrium')['choice']
    result=rollout(sc,choice,args.seconds,stop_on_hazard=args.stop_on_hazard)
    rows.append({'index':i,'scene':sc,'choice':choice,'result':result})
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps({'schema':'lucid.r582.development.v1','rows':rows},indent=2,allow_nan=False))
    print('R582',i,args.seconds,'hazard',result['hazard'],'settled',result['settledAtEnd'],
          'x',result['finalRootX_m'],'tilt',result['finalTilt_deg'],'effort',result['muscleChannelExcitationSeconds'],flush=True)
if __name__=='__main__':main()
