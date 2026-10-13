#!/usr/bin/env python3
"""R586 research: cost-aware neck muscle allocation with native torque envelope.

Immutable R585 baseline and inherited MuJoCo physical assets are never edited.
A candidate activation is accepted ONLY if its predicted generalized moments
on all six neck/head DOFs closely reproduce the established R585 reference.
This is not a claim of validated metabolic efficiency or owner acceptance.
"""
from __future__ import annotations
import argparse, json, time, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'r585'))
import numpy as np
import mujoco as mj
from scipy.optimize import linprog
import r585_neck_repair as r585
SCALES=np.array([8.,6.,3.,9.,4.,2.5])

class MomentConstrainedAllocator(r585.NeckAllocator):
    def __init__(self,pb,**kw):
        kw.pop('torque_tolerance_Nm',None)
        kw.pop('slew_limit_per_update',None)
        super().__init__(pb,**kw)
        self.torque_tolerance_Nm=np.asarray([.04,.04,.03,.04,.03,.02])
        self.slew_limit_per_update=.20
        self.last_eff=np.zeros(len(self.ids))
        self.fallbacks=0
        self.infeasible=0
        self.reference_activation_integral=0.
        self.optimized_activation_integral=0.
        self.reference_torque_error_max=0.
        self.peak_slew=0.
        self.steps=0
        self.last_torque_errors=np.zeros(6)

    def update(self,d,base):
        ref,diagnostics=super().update(d,base)
        m=self.pb.model
        mom=r585.muscle_moment_matrix(d,m.nu,m.nv)
        gains=np.array([mj.mju_muscleGain(d.actuator_length[i],d.actuator_velocity[i],m.actuator_lengthrange[i],m.actuator_acc0[i],m.actuator_gainprm[i,:9]) for i in self.ids])
        A=mom[self.ids,:][:,self.dof].T*gains[None,:]
        required=A@ref
        last=self.last_eff
        n=len(ref)
        tolerance=self.torque_tolerance_Nm
        H=np.vstack((np.hstack((A,np.zeros((6,n)))),np.hstack((-A,np.zeros((6,n)))),
                     np.hstack((np.eye(n),-np.eye(n))),np.hstack((-np.eye(n),-np.eye(n)))))
        limits=np.r_[required+tolerance,-required+tolerance,last,-last]
        slew=self.slew_limit_per_update
        bounds=[(max(0.,float(last[i]-slew)),min(self.max_activation,float(last[i]+slew))) for i in range(n)]+[(0.,None)]*n
        # Gentle temporal penalty discourages control chatter without keeping
        # unnecessary antagonistic co-contraction alive indefinitely.
        cost=np.r_[np.ones(n),np.full(n,.09)]
        out=linprog(cost,A_ub=H,b_ub=limits,bounds=bounds,method='highs',options={'time_limit':.05})
        if out.success and np.all(np.isfinite(out.x)):
            val=np.clip(out.x[:n],0.,self.max_activation)
            err=np.abs(A@val-required)
            if np.all(err <= tolerance+1.e-6):
                u=val
            else:
                self.fallbacks+=1
                u=ref.copy()
        else:
            self.infeasible+=1
            u=ref.copy()
        self.last_torque_errors=A@u-required
        self.reference_torque_error_max=max(self.reference_torque_error_max,float(np.max(np.abs(self.last_torque_errors))))
        self.peak_slew=max(self.peak_slew,float(np.max(np.abs(u-last))))
        self.last_eff=u.copy()
        self.steps+=1
        # R585 updates every 0.01 simulator seconds, so activation seconds are
        # summed over the actual controller updates, not every physics substep.
        self.reference_activation_integral+=float(ref.sum())*.01
        self.optimized_activation_integral+=float(u.sum())*.01
        return u,diagnostics|{'optimized':True,'instantActivation':float(u.sum()),'referenceActivation':float(ref.sum()),'netTorqueError':self.last_torque_errors.tolist()}


def run(cfg=None,secs=4.,push_N=0.,on_frame=None,collect_stride=100):
    # R585 physical reference in same cold-start seated scene, same no-slip
    # contact solver and *same corrected SCM muscle sites*.
    cfg=cfg or dict(kp=.5,kd=.5,regular=.1)
    pb=r585.prior.make_body('seated');m=pb.model
    for side in ('left','right'):
        site=mj.mj_name2id(m,mj.mjtObj.mjOBJ_SITE,f's_{side}_sternocleidomastoid_1')
        m.site_pos[site,2]=-.025
    m.opt.noslip_iterations=6;m.opt.noslip_tolerance=1e-6
    qref=r585.prior.reset(pb);d=pb.data
    neutral=(d.xpos[pb.body_id['Head']]-d.xpos[pb.body_id['Hip']])[[0,2]].copy()
    allocator=MomentConstrainedAllocator(pb,**cfg)
    hinges=np.array(sorted(pb.hinge_dadr.values()),int)
    command=np.zeros(len(allocator.ids));samples=[]
    steps=round(secs/m.opt.timestep)
    for k in range(steps+1):
        t=k*m.opt.timestep
        if k%collect_stride==0 or k==steps:
            loads=r585.core.contact_for(pb,d)
            record={'timeS':round(t,3),'headThoraxDeg':r585.angle(pb,d),
                    'headJointDeg':np.rad2deg(d.qpos[allocator.qadr]).tolist(),
                    'pelvisX_m':float(d.qpos[0]),'rootTiltDeg':r585.core.root_tilt_deg(pb,d),
                    'seatArmsN':float(loads['seatArmsN']),'otherFloorN':float(loads['floorOtherN']),
                    'headMuscleTotalExcitation':float(command.sum()),
                    'netTorqueErrorNm':allocator.last_torque_errors.tolist()}
            samples.append(record)
        if on_frame is not None and (k%200==0 or k==steps):on_frame(pb,d,record)
        if k==steps:break
        difference=np.zeros(m.nv);mj.mj_differentiatePos(m,difference,1.,d.qpos,qref)
        wanted=np.zeros(m.nv);wanted[hinges]=np.clip(10*difference[hinges]-.8*d.qvel[hinges],-8.,8.)
        pts,n=r585.core.foot_for_data(pb,d)
        support=r585.loaded_support_target(d.subtree_com[pb.body_id['Hip']].copy(),pts,n)
        base=r585.controller_excitation(r585.muscle_moment_matrix(d,m.nu,m.nv),wanted,m,d,pb,neutral,'upright_com',support)
        if k%5==0:command,_=allocator.update(d,base)
        d.ctrl[:]=base;d.ctrl[allocator.ids]=command
        d.qfrc_applied[:]=r585.core.passive_end_for_data(pb,d);d.xfrc_applied[:]=0.
        if .8<=t<.92:d.xfrc_applied[pb.body_id['Hip'],0]=push_N
        mj.mj_step(m,d)
    return {'schema':'lucid.r586.moment-constrained-research.v1','secs':secs,'pushN':push_N,
            'maxHeadAngleDeg':max(x['headThoraxDeg'] for x in samples),
            'endHeadAngleDeg':samples[-1]['headThoraxDeg'],
            'maxPelvisTiltDeg':max(x['rootTiltDeg'] for x in samples),
            'maxArmSeatN':max(x['seatArmsN'] for x in samples),
            'maxOtherFloorN':max(x['otherFloorN'] for x in samples),
            'referenceNeckExcitationSeconds':allocator.reference_activation_integral,
            'newNeckExcitationSeconds':allocator.optimized_activation_integral,
            'maxTorqueDeviationNm':allocator.reference_torque_error_max,
            'peakMuscleActivationStep':allocator.peak_slew,
            'optimizerInfeasibleSteps':allocator.infeasible,'optimizerFallbacks':allocator.fallbacks,
            'optimizationUpdates':allocator.steps,'samples':samples}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=4.);p.add_argument('--push',type=float,default=0.)
    p.add_argument('--out',type=Path,default=HERE/'R586_EXPERIMENT.json')
    a=p.parse_args();started=time.monotonic();res=run(secs=a.seconds,push_N=a.push)
    a.out.write_text(json.dumps(res,indent=2,allow_nan=False))
    print('R586',a.seconds,'s','headmax',res['maxHeadAngleDeg'],'final',res['endHeadAngleDeg'],
          'new effort',res['newNeckExcitationSeconds'],'ref',res['referenceNeckExcitationSeconds'],
          'fallbacks',res['optimizerFallbacks'],'infeasible',res['optimizerInfeasibleSteps'],
          'wall',time.monotonic()-started,flush=True)
