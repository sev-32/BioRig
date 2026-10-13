#!/usr/bin/env python3
"""R588 read-only high-frequency native contact/actuator diagnostics for R587."""
from __future__ import annotations
import sys,json,argparse,time,os
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
def discover(name,legacy):
    options=[HERE.parent/name]
    if os.getenv('BIORIG_RESEARCH_ROOT'):options.insert(0,Path(os.environ['BIORIG_RESEARCH_ROOT'])/name)
    options.append(Path(legacy))
    for p in options:
        if p.is_dir():return str(p)
    raise FileNotFoundError(f'Restore {name} alongside R588')
sys.path[:0]=[discover('r586','/mnt/data/BioRig_R586_WORK'),discover('r585','/mnt/data/BioRig_R585_REPAIR')]
import r586_effort as r


def ledger(pb,d):
    m=pb.model
    seat=mj.mj_name2id(m,mj.mjtObj.mjOBJ_GEOM,'research_seat')
    sides={'left':{'contactN':0.,'count':0,'penetrationM':0.,'geoms':{},'forearmY':None},'right':{'contactN':0.,'count':0,'penetrationM':0.,'geoms':{},'forearmY':None}}
    f=np.zeros(6)
    for i in range(d.ncon):
        c=d.contact[i]
        if seat not in (c.geom1,c.geom2):continue
        other=int(c.geom2 if c.geom1==seat else c.geom1)
        body=mj.mj_id2name(m,mj.mjtObj.mjOBJ_BODY,int(m.geom_bodyid[other])) or ''
        if not any(x in body for x in ('Forearm','Hand','Wrist','Arm','Finger','Thumb')):continue
        side='left' if body.startswith('L_') else 'right' if body.startswith('R_') else None
        if side is None:continue
        mj.mj_contactForce(m,d,i,f)
        row=sides[side]
        row['contactN']+=abs(float(f[0]));row['count']+=1
        row['penetrationM']=max(row['penetrationM'],max(0.,-float(c.dist)))
        row['geoms'][body]=row['geoms'].get(body,0)+1
    for side,label in [('left','L_Forearm'),('right','R_Forearm')]:
        bid=mj.mj_name2id(m,mj.mjtObj.mjOBJ_BODY,label)
        if bid>=0:sides[side]['forearmY']=float(d.xpos[bid,1])
    return sides

def run(seconds=4.,push=0.,seat_solref=None,arm_solref=None,arm_priority=None,limb_damping_mult=1.,thumb_time=None,thumb_damping=2.,on_frame=None,damping_fade_end=None,seat_half_width=None,seat_round=False):
    pb=r.r585.prior.make_body('seated');m=pb.model
    for side in ('left','right'):
        site=mj.mj_name2id(m,mj.mjtObj.mjOBJ_SITE,f's_{side}_sternocleidomastoid_1')
        m.site_pos[site,2]=-.025
    m.opt.noslip_iterations=6;m.opt.noslip_tolerance=1e-6
    seatid=mj.mj_name2id(m,mj.mjtObj.mjOBJ_GEOM,'research_seat')
    if seat_round:
        m.geom_type[seatid]=mj.mjtGeom.mjGEOM_ELLIPSOID
    if seat_half_width is not None:
        if not .18 <= seat_half_width <= .28: raise ValueError('seat width out of physically plausible research range')
        m.geom_size[seatid,0]=seat_half_width
    if seat_solref is not None:
        m.geom_solref[seatid]=seat_solref
    if arm_solref is not None:
        for gi in range(m.ngeom):
            name=mj.mj_id2name(m,mj.mjtObj.mjOBJ_BODY,int(m.geom_bodyid[gi])) or ''
            if ('L_' in name or 'R_' in name) and any(s in name for s in ('Forearm','Hand','Wrist','Arm')):
                m.geom_solref[gi]=arm_solref
                if arm_priority is not None:m.geom_priority[gi]=arm_priority
    if thumb_time is not None:
        for gi in range(m.ngeom):
            body=mj.mj_id2name(m,mj.mjtObj.mjOBJ_BODY,int(m.geom_bodyid[gi])) or ''
            if 'Thumb' in body:
                m.geom_solref[gi]=[thumb_time,thumb_damping]
                m.geom_priority[gi]=2
    damp_ids=[adr for name,adr in pb.hinge_dadr.items() if any(s in name for s in ('Shoulder','Elbow','Wrist'))]
    original_damp=m.dof_damping[damp_ids].copy()
    if limb_damping_mult != 1.0:
        for name,adr in pb.hinge_dadr.items():
            if ('Shoulder' in name or 'Elbow' in name or 'Wrist' in name):
                m.dof_damping[adr]*=limb_damping_mult
    qref=r.r585.prior.reset(pb);d=pb.data
    neutral=(d.xpos[pb.body_id['Head']]-d.xpos[pb.body_id['Hip']])[[0,2]].copy()
    allocator=r.MomentConstrainedAllocator(pb,kp=.5,kd=.5,regular=.1)
    hinges=np.array(sorted(pb.hinge_dadr.values()),int)
    command=np.zeros(len(allocator.ids));samples=[];dt=m.opt.timestep
    steps=round(seconds/dt)
    for k in range(steps+1):
        t=k*dt
        if k%5==0 or k==steps:
            arms=ledger(pb,d)
            samples.append({'tS':round(t,4),'headThoraxDeg':r.r585.angle(pb,d),'pelvisX':float(d.qpos[0]),
                'rootTiltDeg':r.r585.core.root_tilt_deg(pb,d),'arms':arms,
                'seatN':float(r.r585.core.contact_for(pb,d)['seatPelvisN']) if hasattr(r.r585.core,'contact_for') else None})
        if abs(t-.27)<1e-7 and seconds<=.5:
            seat=mj.mj_name2id(m,mj.mjtObj.mjOBJ_GEOM,'research_seat')
            for ci in range(d.ncon):
                co=d.contact[ci]
                if seat not in (co.geom1,co.geom2):continue
                gi=int(co.geom1 if co.geom2==seat else co.geom2)
                body=mj.mj_id2name(m,mj.mjtObj.mjOBJ_BODY,int(m.geom_bodyid[gi]))
                if 'Thumb' in (body or '') or 'Hand' in (body or ''):
                    forces=np.zeros(6);mj.mj_contactForce(m,d,ci,forces)
                    print('IMPACT DETAIL',body,'position xyz',np.round(co.pos,5),'dist',round(co.dist,6),'force',np.round(forces[:3],2),'seat center',m.geom_pos[seat],'seat size',m.geom_size[seat],flush=True)
        if on_frame is not None and k%50==0:
            on_frame(pb,d,t,ledger(pb,d))
        if k==steps:break
        if damping_fade_end is not None and limb_damping_mult!=1.0:
            # Diagnostic-only temporary viscous resistance during landing.
            z=max(0.,min(1.,(t-0.35)/(damping_fade_end-.35)))
            z=z*z*(3-2*z)
            m.dof_damping[damp_ids]=original_damp*(limb_damping_mult*(1-z)+z)
        difference=np.zeros(m.nv);mj.mj_differentiatePos(m,difference,1.,d.qpos,qref)
        wanted=np.zeros(m.nv);wanted[hinges]=np.clip(10*difference[hinges]-.8*d.qvel[hinges],-8.,8.)
        pts,n=r.r585.core.foot_for_data(pb,d)
        support=r.r585.loaded_support_target(d.subtree_com[pb.body_id['Hip']].copy(),pts,n)
        base=r.r585.controller_excitation(r.r585.muscle_moment_matrix(d,m.nu,m.nv),wanted,m,d,pb,neutral,'upright_com',support)
        if k%5==0: command,_=allocator.update(d,base)
        d.ctrl[:]=base;d.ctrl[allocator.ids]=command
        d.qfrc_applied[:]=r.r585.core.passive_end_for_data(pb,d);d.xfrc_applied[:]=0.
        if .8<=t<.92:d.xfrc_applied[pb.body_id['Hip'],0]=push
        mj.mj_step(m,d)
    return {'seconds':seconds,'params':{'seat_solref':seat_solref,'arm_solref':arm_solref,'arm_priority':arm_priority,'push':push,'limb_damping_mult':limb_damping_mult,'thumb_time':thumb_time,'thumb_damping':thumb_damping,'damping_fade_end':damping_fade_end,'seat_half_width':seat_half_width,'seat_round':seat_round},'samples':samples,
      'maxHeadDeg':max(x['headThoraxDeg'] for x in samples), 'optimizerFallbacks':allocator.fallbacks}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=4.);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--seat-damping',type=float);p.add_argument('--arm-damping',type=float);p.add_argument('--arm-priority',type=int)
    p.add_argument('--push',type=float,default=0.);p.add_argument('--limb-damping-mult',type=float,default=1.);p.add_argument('--thumb-time',type=float);p.add_argument('--thumb-damping',type=float,default=2.);p.add_argument('--damping-fade-end',type=float);p.add_argument('--seat-half-width',type=float);p.add_argument('--seat-rounded',action='store_true');a=p.parse_args();tic=time.monotonic()
    out=run(a.seconds,push=a.push,seat_solref=[.015,a.seat_damping] if a.seat_damping is not None else None,
            arm_solref=[.01,a.arm_damping] if a.arm_damping is not None else None,arm_priority=a.arm_priority,limb_damping_mult=a.limb_damping_mult,thumb_time=a.thumb_time,thumb_damping=a.thumb_damping,damping_fade_end=a.damping_fade_end,seat_half_width=a.seat_half_width,seat_round=a.seat_rounded)
    a.out.write_text(json.dumps(out,indent=2));print('COMPLETE',a.out,'wall',time.monotonic()-tic,flush=True)
