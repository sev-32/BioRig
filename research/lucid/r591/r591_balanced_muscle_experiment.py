#!/usr/bin/env python3
"""R591 isolated anatomical elbow antagonist experiment on frozen R590 physical state.

No production model changes, no joint motor; voluntary flexion results exclusively
from native elbow muscle commands.  One external joint torque is applied for a
clearly identified diagnostic perturbation, not as a movement driver.
"""
import os, sys, json, math, hashlib, argparse
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE/x) for x in ('r590','r589','r588','r586','r585')]
import r590_rest_restart as r590

DT=.002

def smooth(x):
    x=np.clip(x,0.,1.); return x*x*(3-2*x)

def trajectory(t,q0):
    # First test intrinsic impedance at rest, then muscle-driven flex and return.
    amp=.20
    if t<.78:return q0,0.
    if t<1.55:
        z=(t-.78)/.77
        return q0+amp*smooth(z),amp*6*z*(1-z)/.77
    if t<1.95:return q0+amp,0.
    if t<2.65:
        z=(t-1.95)/.7
        return q0+amp*(1-smooth(z)),-amp*6*z*(1-z)/.7
    return q0,0.

def run(mode='reciprocal',seconds=3.,disturbance_Nm=2.0,coactivation=0.12, tag=None, hold_kp=10., hold_kd=2.0):
    assert mode in ('base','single','reciprocal','paired_hold','adaptive','release_feedback')
    pb,qref,neutral,allocator,hinges,raw=r590.setup()
    m=pb.model;d=pb.data
    joint='rightElbow.flexionExtension'
    dof=pb.hinge_dadr[joint];qidx=pb.hinge_qadr[joint]
    biceps=mj.mj_name2id(m,mj.mjtObj.mjOBJ_ACTUATOR,'m_right_biceps')
    triceps=mj.mj_name2id(m,mj.mjtObj.mjOBJ_ACTUATOR,'m_right_triceps')
    assert biceps>=0 and triceps>=0
    q0=float(d.qpos[qidx]);head_ctrl=np.zeros(len(allocator.ids));samples=[]
    frames=[];timeS=[];effort=0.;relaxation=0.;l1command=0.;baseline_delta=0.;maxhead=0.;maxcontact=0.
    # Initial physical state is bit-identical across arms tests.
    initial_hash=hashlib.sha256(np.concatenate([d.qpos,d.qvel,d.act]).tobytes()).hexdigest()
    for k in range(round(seconds/DT)+1):
        t=round(k*DT,8)
        if k%50==0 or k==round(seconds/DT):
            frames.append(d.qpos.copy());timeS.append(t)
        if k%10==0 or k==round(seconds/DT):
            arms=r590.original.ledger(pb,d)
            qtar,vtar=trajectory(t,q0)
            maxhead=max(maxhead,r590.phys.angle(pb,d))
            maxcontact=max(maxcontact,arms['right']['contactN'])
            samples.append(dict(tS=t,qRad=float(d.qpos[qidx]),qTargetRad=float(qtar),qVel=float(d.qvel[dof]),
                  rightArmSeatN=float(arms['right']['contactN']),
                  leftArmSeatN=float(arms['left']['contactN']),headDeg=float(r590.phys.angle(pb,d)),
                  pelvisX_m=float(d.qpos[0]),
                  bicepsActivation=float(d.act[m.actuator_actadr[biceps]]),
                  tricepsActivation=float(d.act[m.actuator_actadr[triceps]]),
                  bicepsCommand=float(d.ctrl[biceps]),tricepsCommand=float(d.ctrl[triceps]),
                  netRightElbowActuatorTorqueNm=float(d.qfrc_actuator[dof])))
        if k==round(seconds/DT): break
        diff=np.zeros(m.nv)
        mj.mj_differentiatePos(m,diff,1.,d.qpos,qref)
        wanted=np.zeros(m.nv)
        wanted[hinges]=np.clip(10*diff[hinges]-.8*d.qvel[hinges],-8.,8.)
        pts,n=r590.phys.core.foot_for_data(pb,d)
        support=r590.phys.loaded_support_target(d.subtree_com[pb.body_id['Hip']].copy(),pts,n)
        mom=r590.phys.muscle_moment_matrix(d,m.nu,m.nv)
        base=r590.phys.controller_excitation(mom,wanted,m,d,pb,neutral,'upright_com',support)
        if k%5==0:head_ctrl,_=allocator.update(d,base)
        d.ctrl[:]=base;d.ctrl[allocator.ids]=head_ctrl
        # Dynamically measured signed Nm/excitation. No nominal torque assumptions.
        lever=[]
        for idx in (biceps,triceps):
            gain=mj.mju_muscleGain(d.actuator_length[idx],d.actuator_velocity[idx],
                 m.actuator_lengthrange[idx],m.actuator_acc0[idx],m.actuator_gainprm[idx,:9])
            lever.append(float(mom[idx,dof]*gain))
        F,E=lever
        if not(F>0 and E<0):raise AssertionError((F,E))
        if mode!='base':
            # Balanced joint torque reserve for reciprocal and hold cases.
            coflex=float(coactivation) if mode in ('reciprocal','paired_hold','adaptive','release_feedback') else 0.
            coext=coflex*F/(-E)
            fc,ec=coflex,coext
            # Same voluntary target and servo across policies, different muscle recruitment.
            qtar,vtar=trajectory(t,q0)
            desired=np.clip(9*(qtar-d.qpos[qidx])+2.5*(vtar-d.qvel[dof]),-2.5,2.5)
            if mode in ('adaptive','release_feedback') and t<.78:
                desired=np.clip(hold_kp*(q0-d.qpos[qidx])-hold_kd*d.qvel[dof],-7.,7.)
            elif mode=='paired_hold' or t<.78:
                desired=0.
            if mode=='release_feedback':
                # Physiological reciprocal inhibition acts on the INHERITED
                # antagonistic command, not just the optional coactivation reserve.
                if desired>=0.:
                    available=min(max(0.,base[triceps]-.005),max(0.,base[triceps])*.85)
                    relax=min(available,desired/(-E))
                    ec-=relax
                    fc+=max(0.,desired-relax*(-E))/F
                else:
                    available=min(max(0.,base[biceps]-.005),max(0.,base[biceps])*.85)
                    relax=min(available,(-desired)/F)
                    fc-=relax
                    ec+=max(0.,-desired-relax*F)/(-E)
            elif mode=='single':
                if desired>=0:fc+=desired/F
                else:ec+=(-desired)/(-E)
            else:
                # Reciprocal relaxation FIRST, followed by further agonist recruitment.
                if desired>=0:
                    relax=min(ec,desired/(-E));ec-=relax
                    fc+=max(0.,desired-relax*(-E))/F
                else:
                    relax=min(fc,(-desired)/F);fc-=relax
                    ec+=max(0.,-desired-relax*F)/(-E)
            d.ctrl[biceps]=np.clip(base[biceps]+fc,0.,.8)
            d.ctrl[triceps]=np.clip(base[triceps]+ec,0.,.8)
            effort+= (max(fc,0.)+max(ec,0.))*DT
            relaxation+= (-min(fc,0.)-min(ec,0.))*DT
            l1command+=(abs(fc)+abs(ec))*DT
            baseline_delta+= abs(F*fc+E*ec-desired)*DT
        # Diagnostic external elbow torque during the HOLD, not voluntary movement.
        d.qfrc_applied[:]=r590.phys.core.passive_end_for_data(pb,d)
        if .34<=t<.47:d.qfrc_applied[dof]+=disturbance_Nm
        d.xfrc_applied[:]=0.
        mj.mj_step(m,d)
    arrays=dict(qpos=np.array(frames),timeS=np.array(timeS))
    stem=f'R591_{tag}' if tag else f'R591_{mode}'
    np.savez_compressed(HERE/'out'/f'{stem}_NATIVE_QPOS.npz',**arrays)
    errors=[abs(x['qRad']-x['qTargetRad']) for x in samples if .8<x['tS']<2.65]
    # Disturbance: deviation from original initial angle around pulse end.
    kick=[abs(x['qRad']-q0) for x in samples if .32<=x['tS']<=.78]
    settled=[x for x in samples if 2.7<=x['tS']<=3.]
    result=dict(mode=mode,physicalEngine='MuJoCo '+mj.__version__,seconds=seconds,
         timestepS=float(m.opt.timestep),initialStateSHA256=initial_hash,
         skinOriginalUnmodified=True, externalDiagnosticDisturbanceNm=disturbance_Nm,coactivation=coactivation,hold_kp=hold_kp,hold_kd=hold_kd,
         q0Rad=q0, maxHoldDeviationRad=max(kick),meanTrackingErrorRad=float(np.mean(errors)),
         finalErrorRad=float(abs(d.qpos[qidx]-q0)),
         finalMeanDeviationRad=float(np.mean([abs(x['qRad']-q0) for x in settled])),
         maxHeadDeg=maxhead,maxRightArmSeatN=maxcontact,additionalCommandIntegral=effort,
         relaxationIntegral=relaxation,absCommandIntegral=l1command,
         torqueAllocationErrorIntegral=baseline_delta,framesSHA256=hashlib.sha256((HERE/'out'/f'{stem}_NATIVE_QPOS.npz').read_bytes()).hexdigest(),
         sampledTimeSeries=samples)
    (HERE/'out'/f'{stem}_MEASURED.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    print('RESULT',mode,{k:round(result[k],5) for k in ('maxHoldDeviationRad','meanTrackingErrorRad','finalErrorRad','maxHeadDeg','maxRightArmSeatN','additionalCommandIntegral','torqueAllocationErrorIntegral')},flush=True)
    return result

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--mode',default='reciprocal',choices=['base','single','reciprocal','paired_hold','adaptive','release_feedback']);a.add_argument('--seconds',type=float,default=3.);a.add_argument('--disturbance',type=float,default=2.);a.add_argument('--coactivation',type=float,default=.12);a.add_argument('--tag',default=None);a.add_argument('--hold-kp',type=float,default=10.);a.add_argument('--hold-kd',type=float,default=2.);args=a.parse_args()
    run(args.mode,args.seconds,args.disturbance,args.coactivation,args.tag,args.hold_kp,args.hold_kd)
