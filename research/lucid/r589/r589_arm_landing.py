#!/usr/bin/env python3
"""Muscle-controlled bilateral arm descent and contact: no global joint damping,
no geometry, seat/contact, root locks, replayed scripted pose, or rendered edits.
Cloned native R586 SKIN78/MuJoCo model; no modifications to frozen files.
"""
from __future__ import annotations
import sys,os,math,json,time,argparse
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(p) for p in (
    HERE.parent/'r588', HERE.parent/'r586', HERE.parent/'r585',
    Path('/mnt/data/BioRig_R588_CONTACT_REPAIR'),
    Path('/mnt/data/BioRig_R586_WORK'),Path('/mnt/data/BioRig_R585_REPAIR')) if p.is_dir()]
from r588_probe import ledger
import r586_effort as r586

DT=.002
# Frozen exploratory candidate chosen after paired local contact and head gates.
# Separate left/right gains are grounded in actual left/right contact responses.
VERIFIED_PROFILE={
    'target_deg':-28.,'arrival_s':1.2,'kp':20.,'kd':8.,
    'max_extra':.2,'release_at':1.2,'fade_duration':.7,
    'side_profiles':{'left':{'target_deg':-28.,'arrival_s':1.1,
                             'kp':16.,'kd':8.,'max_extra':.18}}}

def smooth(z):
    z=float(np.clip(z,0,1))
    return z*z*(3-2*z)

class ArmLanding:
 def __init__(self,pb,target_deg=-31.,arrival_s=1.,kp=20.,kd=8.,max_extra=.45,release_at=100.,fade_duration=1.,opposing=True,side_profiles=None):
    self.pb=pb;self.target=math.radians(target_deg);self.arrival_s=arrival_s
    self.kp=kp;self.kd=kd;self.max_extra=max_extra;self.release_at=release_at;self.opposing=opposing
    self.info={}
    self.fade_duration=fade_duration
    self.side_profiles=side_profiles or {}
    self.moment_ids={}
    self.refs={}
    for side in ('left','right'):
      self.refs[side]=(pb.hinge_qadr[side+'Shoulder.abductionAdduction'],pb.hinge_dadr[side+'Shoulder.abductionAdduction'])
      self.moment_ids[side]={name:mj.mj_name2id(pb.model,mj.mjtObj.mjOBJ_ACTUATOR,'m_'+side+'_'+name)
            for name in ('deltoid_middle','pectoralis_major')}
    self.effort=0.;self.max_extra_used=0.;self.update_count=0
 def update(self,d,base,t):
    m=self.pb.model
    moment=r586.r585.muscle_moment_matrix(d,m.nu,m.nv)
    extra=base.copy()
    for side in ('left','right'):
      cfg=self.side_profiles.get(side,{})
      target=math.radians(cfg.get('target_deg',math.degrees(self.target)))
      arrival=cfg.get('arrival_s',self.arrival_s)
      kp=cfg.get('kp',self.kp)
      kd=cfg.get('kd',self.kd)
      max_extra=cfg.get('max_extra',self.max_extra)
      z=float(np.clip(t/arrival,0,1))
      desired=target*smooth(z)
      desired_speed=(target*(6*z-6*z*z)/arrival) if t<arrival else 0.
      qadr,dof=self.refs[side]
      q=float(d.qpos[qadr]);v=float(d.qvel[dof])
      desired_torque=kp*(desired-q)+kd*(desired_speed-v)
      a=self.moment_ids[side]
      # Bounded action handoff: after movement has settled, progressively
      # return shoulder control to the inherited muscle controller rather
      # than forcing an indefinitely held extra activation.
      if t>=self.release_at:
        factor=1.-smooth((t-self.release_at)/self.fade_duration)
        desired_torque*=factor
      # Compute local torque per actuator excitation from *actual* current
      # native muscle gain; no assumed constant torque-to-activation ratio.
      muscle='deltoid_middle' if desired_torque>=0 else 'pectoralis_major'
      idx=a[muscle]
      gain=mj.mju_muscleGain(d.actuator_length[idx],d.actuator_velocity[idx],m.actuator_lengthrange[idx],m.actuator_acc0[idx],m.actuator_gainprm[idx,:9])
      per_exc=float(moment[idx,dof]*gain)
      if abs(per_exc)<.1:
        amp=0.
      else:
        amp=np.clip(desired_torque/per_exc,0.,max_extra)
      extra[idx]=np.clip(base[idx]+amp,0.,.8)
      self.effort+=amp*.01
      self.max_extra_used=max(self.max_extra_used,amp)
      self.info[side]={'targetDeg':math.degrees(desired),'actualDeg':math.degrees(q),'velocityDegS':math.degrees(v),'extra':float(amp),'torqueDemandNm':float(desired_torque),'torquePerExcNm':per_exc,'targetSpeedDegS':math.degrees(desired_speed),'channel':muscle}
    self.update_count+=1
    return extra


def run(seconds=3, push=0.,candidate=True,arm_params=None,on_frame=None, stride=5,save_trace=True,thumb_solref_s=None):
    pb=r586.r585.prior.make_body('seated');m=pb.model
    for side in ('left','right'):
        sid=mj.mj_name2id(m,mj.mjtObj.mjOBJ_SITE,f's_{side}_sternocleidomastoid_1');m.site_pos[sid,2]=-.025
    m.opt.noslip_iterations=6;m.opt.noslip_tolerance=1e-6
    if thumb_solref_s is not None:
      for gi in range(m.ngeom):
        body=mj.mj_id2name(m,mj.mjtObj.mjOBJ_BODY,int(m.geom_bodyid[gi])) or ''
        if 'Thumb' in body:
          m.geom_solref[gi]=[thumb_solref_s,2.]
          m.geom_priority[gi]=2
    qref=r586.r585.prior.reset(pb);d=pb.data
    neutral=(d.xpos[pb.body_id['Head']]-d.xpos[pb.body_id['Hip']])[[0,2]].copy()
    allocator=r586.MomentConstrainedAllocator(pb,kp=.5,kd=.5,regular=.1)
    arm=ArmLanding(pb,**(VERIFIED_PROFILE if arm_params is None else arm_params)) if candidate else None
    hinges=np.array(sorted(pb.hinge_dadr.values()),int)
    head_cmd=np.zeros(len(allocator.ids));arm_cmd=np.zeros(m.nu);samples=[]
    highest={'left':0.,'right':0.}; transitions={'left':0,'right':0};last={'left':False,'right':False}
    steps=round(seconds/m.opt.timestep)
    for k in range(steps+1):
      t=k*m.opt.timestep
      if k%stride==0 or k==steps:
        arms=ledger(pb,d)
        for side in ('left','right'):
          load=arms[side]['contactN'];highest[side]=max(highest[side],load)
          active=load>1.
          if samples and active!=last[side]:transitions[side]+=1
          last[side]=active
        if save_trace:
          samples.append({'tS':round(t,4),'arms':arms,'headDeg':r586.r585.angle(pb,d),
            'pelvisX_m':float(d.qpos[0]),'tiltDeg':r586.r585.core.root_tilt_deg(pb,d),
            'shoulder':{side:{'qDeg':round(math.degrees(d.qpos[arm.refs[side][0]]),3),
                        'vDegS':round(math.degrees(d.qvel[arm.refs[side][1]]),3)}
                        for side in ('left','right')} if arm else None,
            'armCommand':arm.info.copy() if arm else None})
      if on_frame is not None and (k%50==0 or k==steps):on_frame(pb,d,t,ledger(pb,d))
      if k==steps:break
      difference=np.zeros(m.nv);mj.mj_differentiatePos(m,difference,1.,d.qpos,qref)
      wanted=np.zeros(m.nv);wanted[hinges]=np.clip(10*difference[hinges]-.8*d.qvel[hinges],-8.,8.)
      pts,n=r586.r585.core.foot_for_data(pb,d)
      support=r586.r585.loaded_support_target(d.subtree_com[pb.body_id['Hip']].copy(),pts,n)
      base=r586.r585.controller_excitation(r586.r585.muscle_moment_matrix(d,m.nu,m.nv),wanted,m,d,pb,neutral,'upright_com',support)
      if k%5==0:
        head_cmd,_=allocator.update(d,base)
        if arm:arm_cmd=arm.update(d,base,t)
      d.ctrl[:]=base
      if arm:
        for side in ('left','right'):
          for idx in arm.moment_ids[side].values():
            d.ctrl[idx]=arm_cmd[idx]
      d.ctrl[allocator.ids]=head_cmd
      d.qfrc_applied[:]=r586.r585.core.passive_end_for_data(pb,d)
      d.xfrc_applied[:]=0.
      if .8<=t<.92:d.xfrc_applied[pb.body_id['Hip'],0]=push
      mj.mj_step(m,d)
    return {'schema':'lucid.r589.muscle-landing-research.v1','candidate':candidate,
        'durationS':seconds,'pushN':push,'params':arm_params,
        'peakArmN':highest,'transitions':transitions,
        'finalArmLoadN':{s:arms[s]['contactN'] for s in ('left','right')},
        'maxHeadDeg':max([s['headDeg'] for s in samples]) if samples else None,
        'finalPelvisX_m':float(d.qpos[0]),
        'armExtraExcitationSeconds':arm.effort if arm else 0.,
        'armMaxExtraExcitation':arm.max_extra_used if arm else 0.,'samples':samples}

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--seconds',type=float,default=3.);p.add_argument('--push',type=float,default=0.)
 p.add_argument('--target',type=float,default=-31.);p.add_argument('--arrival',type=float,default=1.)
 p.add_argument('--kp',type=float,default=20.);p.add_argument('--kd',type=float,default=8.)
 p.add_argument('--max-extra',type=float,default=.45);p.add_argument('--baseline',action='store_true')
 p.add_argument('--profile',choices=('verified','custom'),default='verified')
 p.add_argument('--out',type=Path,required=True)
 a=p.parse_args()
 start=time.monotonic()
 ret=run(a.seconds,push=a.push,candidate=not a.baseline,
    arm_params=VERIFIED_PROFILE if a.profile=='verified' else
    {'target_deg':a.target,'arrival_s':a.arrival,'kp':a.kp,'kd':a.kd,'max_extra':a.max_extra})
 a.out.write_text(json.dumps(ret,indent=2,allow_nan=False))
 print('R589',a.seconds,'results',ret['peakArmN'],ret['transitions'],ret['finalArmLoadN'],'head',ret['maxHeadDeg'],'pelvis',ret['finalPelvisX_m'],'effort',ret['armExtraExcitationSeconds'],'wall',round(time.monotonic()-start,2),flush=True)
