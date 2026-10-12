#!/usr/bin/env python3
"""True MuJoCo offscreen headless captures, frozen scene00 vs R576 guard.
No generated art, no joint/root teleportation, no collision/inertia changes.
"""
import os,sys,json
os.environ.setdefault('MUJOCO_GL','egl')
from pathlib import Path
import numpy as np
import mujoco as mj
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import r576_longhorizon as r

TIMES=(8.,10.,11.,12.)
WIDTH,HEIGHT=550,480
OUTPUT=ROOT/'R576_NATIVE_SCENE00_12S_COMPARISON.png'

def capture(guarded):
    scene={'seatHalfWidthM':.131,'friction':.82,'forceN':0.,'direction':1.}
    pb,ref,neutral,saved=r.phy.paired_scene(.131,.82)
    initial=r.phy.plant.sha_state(pb.data)
    d=mj.MjData(pb.model)
    mj.mj_copyData(d,pb.model,saved)
    early=r.phy.TimedPulse(pb.model,'none')
    guard=r.make_guard(pb.model) if guarded else None
    pb.model.vis.headlight.ambient[:]=[.45,.45,.45]
    pb.model.vis.headlight.diffuse[:]=[.9,.9,.9]
    pb.model.geom_rgba[0,:]=[.4,.55,.8,.15]
    pb.model.geom_rgba[1,:]=[.2,.22,.26,1.]
    cam=mj.MjvCamera();mj.mjv_defaultCamera(cam)
    cam.type=mj.mjtCamera.mjCAMERA_FREE
    cam.lookat[:]=[.03,.53,-.1];cam.distance=1.95;cam.azimuth=110.;cam.elevation=-15.
    frames=[];state=[]
    with mj.Renderer(pb.model,width=WIDTH,height=HEIGHT) as renderer:
        for k in range(round(TIMES[-1]/r.DT)+1):
            t=k*r.DT
            if any(abs(t-x)<1e-7 for x in TIMES):
                obs=r.phy.sense(pb,d)
                renderer.update_scene(d,camera=cam)
                img=Image.fromarray(renderer.render()).convert('RGB')
                frames.append(img)
                state.append({'timeS':t,'mode':'late-support guard' if guarded else 'frozen R574',
                    'tiltDeg':obs['rootTiltDeg'],'xPositionM':obs['xPosition'],
                    'pelvisSeatN':obs['pelvisSeatN'],'armsSeatN':obs['armsSeatN']})
            if k==round(TIMES[-1]/r.DT):break
            if k%r.UPDATE_STEPS==0:
                obs=r.phy.sense(pb,d)
                early.update(t,obs)
                if guard is not None:guard.update(t,obs)
            delta=early.output() if guard is None else np.clip(early.output()+guard.output(),0,.04)
            r.phy.plant.step_perturbed(pb,d,ref,neutral,delta,np.zeros(3))
    assert initial==r.phy.plant.sha_state(pb.data)
    return frames,state

def main():
    columns=[capture(False),capture(True)]
    hrow=HEIGHT+44
    panel=Image.new('RGB',(2*WIDTH,len(TIMES)*hrow),(18,21,26))
    draw=ImageDraw.Draw(panel)
    for j,(frames,states) in enumerate(columns):
        for i,(im,obs) in enumerate(zip(frames,states)):
            x=j*WIDTH;y=i*hrow
            draw.text((x+12,y+6),f"{'FROZEN R574' if j==0 else 'R576 GUARDED'} | {obs['timeS']:.0f}s | tilt {obs['tiltDeg']:.1f} deg",fill=(240,244,248))
            draw.text((x+12,y+24),f"lateral x {obs['xPositionM']:.3f} m | seat {obs['pelvisSeatN']:.0f} N",fill=(179,196,207))
            panel.paste(im,(x,y+44))
    panel.save(OUTPUT,optimize=True)
    (ROOT/'R576_NATIVE_SCENE00_RENDER_RECEIPT.json').write_text(json.dumps({'renderer':'MuJoCo 3.15.0, EGL', 'scene':'R574 scene00', 'camera':'fixed azimuth110 elevation-15 distance1.95', 'frameMeasurements':[row for col in columns for row in col[1]],'file':OUTPUT.name},indent=2))
    print('WROTE',OUTPUT,OUTPUT.stat().st_size)

if __name__=='__main__':main()
