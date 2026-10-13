#!/usr/bin/env python3
"""Reproducibly instantiate a *physically settled* 84-muscle state.

Source: exactly captured MuJoCo state at t=12 s from an uninterrupted R589
24-second run; no pose authoring, no root constraints, no synthetic forces.
Acceptance requires independent replay to stay close to the same uninterrupted
physical continuation; do not confuse an assigned qpos with a valid stable state.
"""
from __future__ import annotations
import os,sys,json,hashlib,time
from pathlib import Path
import numpy as np,mujoco as mj
HERE=Path(__file__).resolve().parent
CANDIDATES=[HERE.parent/'r589',
    Path(os.environ.get('BIORIG_RESEARCH_ROOT','/does-not-exist'))/'r589',
    Path('/mnt/data/BioRig_R589_ACTIVE_ARM_LANDING')]
SOURCE_DIR=next((x for x in CANDIDATES if (x/'r589_arm_landing.py').is_file()),None)
if SOURCE_DIR is None:
    raise FileNotFoundError('R589 source must be in a sibling research/lucid/r589 directory')
sys.path.insert(0,str(SOURCE_DIR))
import r589_arm_landing as original
phys=original.r586.r585
DT=.002
SNAPSHOT=HERE/'R590_SETTLED_CONTINUOUS_NATIVE_QPOS.npz'

def setup():
    raw=np.load(SNAPSHOT)
    pb=phys.prior.make_body('seated');m=pb.model
    for side in ('left','right'):
        sid=mj.mj_name2id(m,mj.mjtObj.mjOBJ_SITE,f's_{side}_sternocleidomastoid_1')
        m.site_pos[sid,2]=-.025
    m.opt.noslip_iterations=6;m.opt.noslip_tolerance=1e-6
    qref=phys.prior.reset(pb)
    d=pb.data
    # Reference belongs to the original seated start, not the settled snapshot.
    neutral=(d.xpos[pb.body_id['Head']]-d.xpos[pb.body_id['Hip']])[[0,2]].copy()
    assert len(raw['qpos'][0])==m.nq
    assert len(raw['qvel'][0])==m.nv
    assert len(raw['act'][0])==m.na
    d.qpos[:]=raw['qpos'][0]
    d.qvel[:]=raw['qvel'][0]
    d.act[:]=raw['act'][0]
    d.time=12.
    mj.mj_forward(m,d)
    allocator=original.r586.MomentConstrainedAllocator(pb,kp=.5,kd=.5,regular=.1)
    # Resume actuator regularization close to current *physical* muscle activation.
    for j, idx in enumerate(allocator.ids):
        actadr=int(m.actuator_actadr[idx])
        if actadr>=0:
            allocator.last_eff[j]=float(d.act[actadr])
            allocator.last[j]=float(d.act[actadr])
    hinges=np.array(sorted(pb.hinge_dadr.values()),int)
    return pb,qref,neutral,allocator,hinges,raw

def continue_native(seconds=4.,pushN=0.,pushAtS=.8,save_frames=False):
    pb,qref,neutral,allocator,hinges,raw=setup();d=pb.data;m=pb.model
    head_ctrl=np.zeros(len(allocator.ids))
    frames_qpos=[];frames_times=[]
    samples=[];max_arm=0.;max_head=0.;last_contact={'left':None,'right':None};trans={'left':0,'right':0}
    for k in range(round(seconds/m.opt.timestep)+1):
        t=k*m.opt.timestep
        if k%5==0 or k==round(seconds/m.opt.timestep):
            arms=original.ledger(pb,d)
            h=phys.angle(pb,d);max_head=max(max_head,h)
            for side in ('left','right'):
                current=arms[side]['contactN']>1.
                if last_contact[side] is not None and last_contact[side]!=current:trans[side]+=1
                last_contact[side]=current
                max_arm=max(max_arm,arms[side]['contactN'])
            if k%200==0 or k==round(seconds/m.opt.timestep):
                if save_frames:
                    frames_qpos.append(d.qpos.copy());frames_times.append(t)
                samples.append({'relativeS':round(t,3),'physicalS':round(12+t,3),
                'headDeg':h,'pelvisX_m':float(d.qpos[0]),
                'leftArmN':arms['left']['contactN'],'rightArmN':arms['right']['contactN']})
        if k==round(seconds/m.opt.timestep):break
        difference=np.zeros(m.nv);mj.mj_differentiatePos(m,difference,1.,d.qpos,qref)
        wanted=np.zeros(m.nv);wanted[hinges]=np.clip(10*difference[hinges]-.8*d.qvel[hinges],-8.,8.)
        pts,n=phys.core.foot_for_data(pb,d)
        support=phys.loaded_support_target(d.subtree_com[pb.body_id['Hip']].copy(),pts,n)
        base=phys.controller_excitation(phys.muscle_moment_matrix(d,m.nu,m.nv),wanted,m,d,pb,neutral,'upright_com',support)
        if k%5==0:head_ctrl,_=allocator.update(d,base)
        d.ctrl[:]=base;d.ctrl[allocator.ids]=head_ctrl
        d.qfrc_applied[:]=phys.core.passive_end_for_data(pb,d)
        d.xfrc_applied[:]=0.
        if pushAtS<=t<pushAtS+.12:d.xfrc_applied[pb.body_id['Hip'],0]=pushN
        mj.mj_step(m,d)
    frame_digest=None
    if save_frames:
        out=HERE/f'R590_RESTART_PUSH_{int(pushN):+d}N_QPOS.npz'
        np.savez_compressed(out,qpos=np.asarray(frames_qpos),timeS=np.asarray(frames_times))
        frame_digest=hashlib.sha256(out.read_bytes()).hexdigest()
    return {'schema':'lucid.r590.restarted-physical-seated-state.v1',
      'capturedQposSHA256':frame_digest,'seconds':seconds,
      'pushN':pushN,'peakArmN':max_arm,'maxHeadDeg':max_head,'transitions':trans,
      'finalPelvisX_m':float(d.qpos[0]),'samples':samples,
      'initialQposSHA256':hashlib.sha256(raw['qpos'][0].tobytes()).hexdigest()}

if __name__=='__main__':
    out=continue_native(4.)
    (HERE/'R590_RESUMED_4S_NATIVE.json').write_text(json.dumps(out,indent=2,allow_nan=False))
    continuous=json.loads((HERE/'R590_SETTLED_12TO24_NATIVE_RECEIPT.json').read_text())
    print('RESUME_METRICS', {k:out[k] for k in ('peakArmN','maxHeadDeg','transitions','finalPelvisX_m')},flush=True)
    print('CONTINUOUS_HISTORY',['(t12-24 no contacts transitions)',continuous['contactTransitions12to24']],flush=True)
