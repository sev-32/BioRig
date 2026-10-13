#!/usr/bin/env python3
"""R584: native no-slip contact solver A/B physical test.

No change to the source MJCF, geom/material coefficients, muscle controller,
trajectory, root forces, geometry, masses, warmup or frozen R574 intent.
Only MjModel.opt.noslip_iterations differs. Experimental research branch.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from pathlib import Path
from dataclasses import asdict
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/'r583'),str(HERE.parent/'r582'),str(HERE.parent/'r580'),str(HERE.parent/'r577')]
import numpy as np
import mujoco as mj
from PIL import Image,ImageDraw
import r583_friction_probe as friction
import r582_controller as control

DT=control.DT
SCENES={'undisturbed':{'seatHalfWidthM':.131,'friction':.82,'forceN':0.,'direction':1.}}
NO_SLIP_ITERS=6

def contact_material_fingerprint(model):
    return hashlib.sha256(np.concatenate((model.geom_friction.flatten(),
        model.geom_solref.flatten(),model.geom_solimp.flatten(),
        model.geom_size.flatten(),model.body_mass.flatten())).tobytes()).hexdigest()

def setup(scene, noslip_iterations):
    pb,ref,neutral,saved=control.phy.paired_scene(scene['seatHalfWidthM'],scene['friction'])
    initial=control.phy.plant.sha_state(pb.data)
    material=contact_material_fingerprint(pb.model)
    assert pb.model.opt.noslip_iterations==0, 'inherited model unexpectedly enables no-slip solver'
    assert isinstance(noslip_iterations,int) and 0<=noslip_iterations<=20
    pb.model.opt.noslip_iterations=noslip_iterations
    pb.model.opt.noslip_tolerance=1e-6
    assert contact_material_fingerprint(pb.model)==material,'contact material changed!'
    data=mj.MjData(pb.model);mj.mj_copyData(data,pb.model,saved)
    mj.mj_forward(pb.model,data)
    return pb,ref,neutral,data,initial,material

def experiment(scene, seconds=12., noslip_iterations=0,
               render_every=.5, render=False, early_choice='none', extra_control=True,
               trace_interval=.2):
    if seconds<=0:raise ValueError('seconds must be positive')
    pb,ref,neutral,data,initial,material=setup(scene,noslip_iterations)
    model=pb.model
    early=control.phy.TimedPulse(model,early_choice)
    ctl=control.SignedWrenchAllocator(model)
    images=[];trace=[];peaktilt=peakarm=peakother=0.;bothlost=0
    settled_run=0.;longest_settled=0.;firsthazard=None
    camera=mj.MjvCamera();mj.mjv_defaultCamera(camera)
    camera.type=mj.mjtCamera.mjCAMERA_FREE
    camera.lookat[:]=[.02,.52,-.16];camera.distance=1.8;camera.azimuth=110.;camera.elevation=-15.
    renderer=None
    if render:
        # All three changes are cosmetic, never applied to inertial, contact
        # or state variables. Hide floor plane only to expose the foot geometry.
        model.vis.headlight.ambient[:]=[.85,.85,.85]
        model.vis.headlight.diffuse[:]=[1.,1.,1.]
        model.geom_rgba[0]=[.38,.55,.75,.18]
        for gi in range(2,model.ngeom):
            if model.geom_rgba[gi,3]>.01:
                model.geom_rgba[gi,:3]=np.clip(.28+model.geom_rgba[gi,:3]*.85,.28,.91)
        renderer=mj.Renderer(model,width=500,height=455)
    step_every=round(.04/DT)
    trace_jump=round(trace_interval/DT)
    render_jump=round(render_every/DT)
    sample_every=round(.02/DT)
    total=round(seconds/DT)
    last=None
    try:
      for k in range(total+1):
        t=k*DT
        if k%sample_every==0 or k==total:
            o=control.phy.sense(pb,data);last=o
            peaktilt=max(peaktilt,o['rootTiltDeg'])
            peakarm=max(peakarm,o['armsSeatN']);peakother=max(peakother,o['otherFloorN'])
            bothlost+=int(o['pelvisSeatN']<5 and o['feetFloorN']<5)
            quiet=bool(t>=.16 and control.inherited.r577.baseline.settling.is_settled(o))
            settled_run=settled_run+.02 if quiet else 0.
            longest_settled=max(longest_settled,settled_run)
            hazard=peaktilt>=45 or peakarm>=50 or peakother>=50 or bothlost>=3
            if hazard and firsthazard is None:firsthazard=t
        if (k%trace_jump==0 or k==total):
            support=friction.slip_and_forces(model,data)
            trace.append({'tS':round(t,4),'x_m':last['xPosition'],'vx_mps':last['xSpeed'],
                'tilt_deg':last['rootTiltDeg'],'seatN':last['pelvisSeatN'],'feetN':last['feetFloorN'],
                'armN':last['armsSeatN'],'seatSlip_mps':support['research_seat']['loadedSlipMps'],
                'footSlip_mps':support['ground']['loadedSlipMps'],
                'seatMu':support['research_seat']['muEffectiveMax'],
                'footMu':support['ground']['muEffectiveMax'],
                'extraHipDose':ctl.hip if extra_control else 0,
                'extraObliqueDose':ctl.trunk if extra_control else 0})
        if renderer is not None and (k%render_jump==0 or k==total):
            renderer.update_scene(data,camera=camera)
            images.append((t,Image.fromarray(renderer.render()).convert('RGB')))
        if k==total:break
        if k%step_every==0:
            o=control.phy.sense(pb,data)
            early.update(t,o)
            if extra_control:ctl.update(t,o,model,data)
        delta=np.clip(early.output()+ctl.output(),0.,control.phy.plant.MAX_EXTRA) if extra_control else early.output()
        applied=np.array([scene['forceN']*scene['direction'] if t<control.phy.plant.PUSH_S else 0.,0.,0.])
        control.phy.plant.step_perturbed(pb,data,ref,neutral,delta,applied)
    finally:
        if renderer:renderer.close()
    assert control.phy.plant.sha_state(pb.data)==initial
    assert contact_material_fingerprint(model)==material
    return {
        'schema':'lucid.r584.noslip-native.v1','researchOnly':True,
        'duration_s':seconds,'complete':True,'initialSHA256':initial,
        'materialSHA256':material,'noslipIterations':noslip_iterations,
        'scene':scene,'frozenEarlyChoice':early_choice,'additionalMuscleControl':extra_control,
        'hazard':firsthazard is not None,'hazardAt_s':firsthazard,'settledAtEnd':settled_run>=1.,
        'longestSettled_s':longest_settled,'maxTilt_deg':peaktilt,'peakArm_N':peakarm,
        'peakOtherFloor_N':peakother,'supportLossSamples':bothlost,
        'finalX_m':last['xPosition'],'finalV_mps':last['xSpeed'],
        'finalTilt_deg':last['rootTiltDeg'],
        'muscleChannelExcitationSeconds':ctl.channelEffort if extra_control else 0.,
        'trace':trace
    },images

def animated_comparison(runs, frames, interval_s, filename):
    assert len(runs)==2
    frame_count=min(len(frames[name]) for name in runs)
    chosen=list(runs)
    out=[]
    for i in range(frame_count):
        composite=Image.new('RGB',(1000,494),(18,22,28))
        d=ImageDraw.Draw(composite)
        for j,name in enumerate(chosen):
            t,frame=frames[name][i]
            record=min(runs[name]['trace'],key=lambda v:abs(v['tS']-t))
            x=j*500
            d.text((x+7,6),f'{name.upper()} | {t:4.1f} s | lateral x {record["x_m"]:.4f} m',fill='#ffffff')
            d.text((x+7,22),f'seat slip {1000*(record["seatSlip_mps"] or 0):.3f} mm/s | foot {1000*(record["footSlip_mps"] or 0):.3f} mm/s',fill='#d5e6f5')
            composite.paste(frame,(x,39))
        out.append(composite)
    out[0].save(filename,save_all=True,append_images=out[1:],duration=int(interval_s*1000),loop=0,optimize=True)
    return {'file':str(filename),'sha256':hashlib.sha256(filename.read_bytes()).hexdigest(),
            'frames':len(out),'frameDurationS':interval_s}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--seconds',type=float,default=12.)
    p.add_argument('--render-every',type=float,default=.4)
    p.add_argument('--render',action='store_true')
    p.add_argument('--without-extra-muscles',action='store_true')
    p.add_argument('--outdir',type=Path,default=HERE/'results')
    p.add_argument('--modes',nargs='+',type=int,default=[0,NO_SLIP_ITERS])
    args=p.parse_args()
    args.outdir.mkdir(parents=True,exist_ok=True)
    runs={};images={}
    for count in args.modes:
        key=f'noslip_{count}'
        outcome,ims=experiment(SCENES['undisturbed'],args.seconds,count,args.render_every,args.render,
                                extra_control=not args.without_extra_muscles)
        runs[key]=outcome;images[key]=ims
        (args.outdir/f'{key}_{int(args.seconds)}s.json').write_text(json.dumps(outcome,indent=2,allow_nan=False))
        print(key, 'end_x',round(outcome['finalX_m'],7),'hazard',outcome['hazard'],
           'settled',outcome['settledAtEnd'],'controller_effort_s',outcome['muscleChannelExcitationSeconds'],flush=True)
    if args.render and len(args.modes)==2:
        path=args.outdir/'R584_NATIVE_NOSLIP_ANIMATED_BEFORE_AFTER.gif'
        rec=animated_comparison(runs,images,args.render_every,path)
        (args.outdir/'R584_RENDER_RECEIPT.json').write_text(json.dumps(rec,indent=2))
        print('GIF',rec,flush=True)
    summary={k:{q:v for q,v in value.items() if q!='trace'} for k,value in runs.items()}
    (args.outdir/'R584_SUMMARY.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
if __name__=='__main__':main()
