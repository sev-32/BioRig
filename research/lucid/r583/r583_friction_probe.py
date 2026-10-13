#!/usr/bin/env python3
"""R583: measured real contact grip/slip, cloned physical friction experiments.

Test-only MuJoCo contact variants. R574/R582 source and baseline remain frozen.
Contact friction is NOT a passive hold/lock: real pelvis/feet may still slide.
No GitHub Actions. Offscreen EGL captures directly from native MuJoCo states.
"""
from __future__ import annotations
import os,sys,json,hashlib,argparse
os.environ.setdefault('MUJOCO_GL','egl')
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/'r582'),str(HERE.parent/'r580'),str(HERE.parent/'r577')]
import numpy as np
import mujoco as mj
from PIL import Image, ImageDraw
import r582_controller as r

# MuJoCo effective pair uses per-geom priorities/combination; verify on actual
# generated contacts rather than assuming a parameter equals effective grip.
MODES={'ice':1e-5,'original':None,'high_grip':2.0}
SUPPORT_GEOMS=('research_seat','ground')
SAMPLE_FRAMES=(0,2,4,6,8,10,12)


def set_friction(model,mode):
    assert mode in MODES
    if mode=='ice':
        # Both sides of each contact must be changed; mixing often uses MAX.
        model.geom_friction[:,0]=MODES[mode]
    elif mode=='high_grip':
        for name in SUPPORT_GEOMS:
            gid=mj.mj_name2id(model,mj.mjtObj.mjOBJ_GEOM,name)
            model.geom_friction[gid,0]=MODES[mode]


def slip_and_forces(model,data):
    ext={mj.mj_name2id(model,mj.mjtObj.mjOBJ_GEOM,n):n for n in SUPPORT_GEOMS}
    grouped={n:dict(normalN=0.,shearN=0.,sumLoadedSlipMps=0.,weightN=0.,contacts=0.,muObserved=[]) for n in SUPPORT_GEOMS}
    f=np.zeros(6)
    nv=model.nv
    jp=np.zeros((3,nv));jr=np.zeros((3,nv))
    je=np.zeros((3,nv));jre=np.zeros((3,nv))
    for i in range(data.ncon):
        c=data.contact[i]
        if c.geom1 in ext:
            label=ext[c.geom1]
            external=int(c.geom1);moving=int(c.geom2)
        elif c.geom2 in ext:
            label=ext[c.geom2]
            external=int(c.geom2);moving=int(c.geom1)
        else: continue
        mj.mj_contactForce(model,data,i,f)
        norm=max(float(f[0]),0.)
        if norm <= 1e-7:continue
        # Joint Jacobian gives actual velocity of the moving body point at
        # this contact, not pelvis/root velocity or a visually inferred slip.
        bp=int(model.geom_bodyid[moving]); be=int(model.geom_bodyid[external])
        mj.mj_jac(model,data,jp,jr,c.pos,bp)
        mj.mj_jac(model,data,je,jre,c.pos,be)
        relative=(jp-je)@data.qvel
        n=np.asarray(c.frame).reshape(3,3)[0]
        slip=relative - n*np.dot(relative,n)
        g=grouped[label]
        g['contacts']+=1
        g['normalN']+=norm
        g['shearN']+=float(np.linalg.norm(f[1:3]))
        g['sumLoadedSlipMps']+=norm*float(np.linalg.norm(slip))
        g['weightN']+=norm
        g['muObserved'].append(float(c.friction[0]))
    for v in grouped.values():
        v['loadedSlipMps']=v['sumLoadedSlipMps']/v['weightN'] if v['weightN'] else None
        v['muEffectiveMin']=min(v['muObserved']) if v['muObserved'] else None
        v['muEffectiveMax']=max(v['muObserved']) if v['muObserved'] else None
        v['shearToNormal']=v['shearN']/v['normalN'] if v['normalN'] else None
        del v['sumLoadedSlipMps'];del v['weightN'];del v['muObserved']
    return grouped


def run(mode, duration=12, render=True):
    scene={'seatHalfWidthM':.131,'friction':.82,'forceN':0.,'direction':1.}
    pb,ref,neutral,saved=r.phy.paired_scene(scene['seatHalfWidthM'],scene['friction'])
    init=r.phy.plant.sha_state(pb.data)
    model=pb.model
    set_friction(model,mode)
    d=mj.MjData(model);mj.mj_copyData(d,model,saved)
    mj.mj_forward(model,d)
    early=r.phy.TimedPulse(model,'none')
    ctl=r.SignedWrenchAllocator(model)
    frames=[];snapshots=[];trace=[]
    cam=mj.MjvCamera();mj.mjv_defaultCamera(cam)
    cam.type=mj.mjtCamera.mjCAMERA_FREE
    cam.lookat[:]=[.02,.52,-.16];cam.distance=1.80;cam.azimuth=110.;cam.elevation=-15.
    # visuals: no physics variation; cosmetic only.
    model.vis.headlight.ambient[:]=[.85,.85,.85]
    model.vis.headlight.diffuse[:]=[1.,1.,1.]
    model.geom_rgba[0]=[.38,.55,.75,.18]
    for gi in range(2,model.ngeom):
        if model.geom_rgba[gi,3]>.01:
            model.geom_rgba[gi,:3]=np.clip(.28+model.geom_rgba[gi,:3]*.85,.28,.91)
    renderer=mj.Renderer(model,width=490,height=455) if render else None
    peaktilt=peakarm=peakother=0.
    try:
        steps=round(duration/r.DT)
        for k in range(steps+1):
            t=k*r.DT
            if k%round(.2/r.DT)==0 or k==steps:
                o=r.phy.sense(pb,d)
                contact=slip_and_forces(model,d)
                peaktilt=max(peaktilt,o['rootTiltDeg'])
                peakarm=max(peakarm,o['armsSeatN'])
                peakother=max(peakother,o['otherFloorN'])
                trace.append({'tS':round(t,3),'rootX_m':o['xPosition'],'rootV_mps':o['xSpeed'],
                              'tiltDeg':o['rootTiltDeg'],'hipDose':ctl.hip,'obliqueDose':ctl.trunk,
                              'seatN':o['pelvisSeatN'],'feetN':o['feetFloorN'],'contacts':contact})
                if (abs(t-round(t)) < 1e-9 and int(round(t)) in SAMPLE_FRAMES) or k==steps:
                    if renderer:
                        renderer.update_scene(d,camera=cam)
                        frames.append((t,Image.fromarray(renderer.render()).convert('RGB')))
                    snapshots.append(trace[-1])
            if k==steps:break
            if k%round(.04/r.DT)==0:
                o=r.phy.sense(pb,d);early.update(t,o)
                ctl.update(t,o,model,d)
            cmd=np.clip(early.output()+ctl.output(),0.,r.phy.plant.MAX_EXTRA)
            r.phy.plant.step_perturbed(pb,d,ref,neutral,cmd,np.zeros(3))
    finally:
        if renderer:renderer.close()
    assert r.phy.plant.sha_state(pb.data)==init
    result={'mode':mode,'durationS':duration,'initSHA':init,'endX_m':trace[-1]['rootX_m'],
            'endRootTiltDeg':trace[-1]['tiltDeg'],'peakTiltDeg':peaktilt,'peakArmN':peakarm,
            'peakOtherFloorN':peakother,'controllerMuscleExcitationSeconds':ctl.channelEffort,
            'trace':trace,'frameTimesS':[t for t,_ in frames]}
    return result, frames


def render_comparison(all_frames,results,seconds):
    frame_times=[0,2,4,6,8,10,12]
    frame_times=[t for t in frame_times if t<=seconds]
    out=[]
    for stamp in frame_times:
        pic=Image.new('RGB',(490*len(MODES),490),(22,25,30))
        d=ImageDraw.Draw(pic)
        for j,mode in enumerate(MODES):
            frame=next((im for t,im in all_frames[mode] if abs(t-stamp)<.001),None)
            if frame is None:continue
            row=next(item for item in results[mode]['trace'] if abs(item['tS']-stamp)<.001)
            x=j*490
            d.text((x+8,6),f'{mode.upper()} | {stamp:g}s | tilt {row["tiltDeg"]:.1f} deg',fill=(239,241,245))
            d.text((x+8,23),f'pelvis x {row["rootX_m"]:.3f}m | seat slip {row["contacts"]["research_seat"]["loadedSlipMps"] or 0:.3f}m/s',fill=(205,220,232))
            pic.paste(frame,(x,35))
        out.append(pic)
    path=HERE/'R583_FRICTION_SIDE_BY_SIDE_NATIVE.gif'
    out[0].save(path,save_all=True,append_images=out[1:],duration=900,loop=0,optimize=True)
    return path


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--seconds',type=float,default=12.)
    p.add_argument('--mode',choices=[*MODES,'all'],default='all')
    p.add_argument('--render',action='store_true')
    arg=p.parse_args()
    modes=list(MODES) if arg.mode=='all' else [arg.mode]
    results={};frames={}
    for mode in modes:
        result,ims=run(mode,arg.seconds,arg.render)
        results[mode]=result;frames[mode]=ims
        (HERE/f'R583_{mode}_trace.json').write_text(json.dumps(result,indent=2,allow_nan=False))
        print('COMPLETE',mode,'x',result['endX_m'],'tilt',result['endRootTiltDeg'],
          'peak tilt',result['peakTiltDeg'],'excitation*s',result['controllerMuscleExcitationSeconds'],flush=True)
    (HERE/'R583_FRICTION_AUDIT.json').write_text(json.dumps({'schema':'lucid.r583.contact-friction-native.v1',
        'note':'Only friction changes after identical baseline R574 warmup. No controller / geometric changes.',
        'modes':list(MODES),'durationS':arg.seconds,
        'results':{m:{k:v for k,v in r.items() if k!='trace'} for m,r in results.items()}},indent=2,allow_nan=False))
    if arg.render and len(modes)==len(MODES):
        fn=render_comparison(frames,results,arg.seconds)
        print('GIF',fn,fn.stat().st_size,'sha256',hashlib.sha256(fn.read_bytes()).hexdigest(),flush=True)


if __name__=='__main__':main()
