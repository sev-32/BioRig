#!/usr/bin/env python3
"""Real EGL/MuJoCo 3.15 side sequence at 0,12,20,30,40 seconds; native rig."""
import os,sys,json,hashlib
os.environ.setdefault('MUJOCO_GL','egl')
from pathlib import Path
import numpy as np
import mujoco as mj
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import r577_tonic_support as r
TIMES=(0.,12.,20.,30.,40.)
W,H=550,480
OUT=ROOT/'R577_NATIVE_SCENE00_40S_EVOLUTION.png'

def capture():
    scene={'seatHalfWidthM':.131,'friction':.82,'forceN':0.,'direction':1.}
    pb,ref,neu,saved=r.phys.paired_scene(.131,.82)
    d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
    early=r.phys.TimedPulse(pb.model,'none');tonic=r.TonicSupport(pb.model)
    cam=mj.MjvCamera();mj.mjv_defaultCamera(cam)
    cam.type=mj.mjtCamera.mjCAMERA_FREE
    cam.lookat[:]=[.03,.53,-.1];cam.distance=1.95;cam.azimuth=110.;cam.elevation=-15.
    frames=[];values=[]
    with mj.Renderer(pb.model,width=W,height=H) as renderer:
        for k in range(round(max(TIMES)/r.DT)+1):
            t=k*r.DT
            if any(abs(t-x)<1e-8 for x in TIMES):
                obs=r.phys.sense(pb,d)
                renderer.update_scene(d,camera=cam)
                frames.append(Image.fromarray(renderer.render()).convert('RGB'))
                values.append({'timeS':t,'rootTiltDeg':obs['rootTiltDeg'],
                  'xPositionM':obs['xPosition'],'lateralSpeedMps':obs['xSpeed'],
                  'pelvisSeatN':obs['pelvisSeatN'],'feetFloorN':obs['feetFloorN'],
                  'armsSeatN':obs['armsSeatN'],'tonicDose':tonic.amplitude})
            if k==round(max(TIMES)/r.DT):break
            if k%r.baseline.UPDATE_STEPS==0:
                obs=r.phys.sense(pb,d);early.update(t,obs);tonic.update(t,obs)
            cmd=np.clip(early.output()+tonic.output(),0,.04)
            r.phys.plant.step_perturbed(pb,d,ref,neu,cmd,np.zeros(3))
    return frames,values

def main():
    frames,values=capture()
    img=Image.new('RGB',(W,len(frames)*(H+52)),(17,20,26))
    d=ImageDraw.Draw(img)
    for i,(frame,obs) in enumerate(zip(frames,values)):
        y=i*(H+52)
        d.text((12,y+9),f"R577 / NATIVE MUJOCO / {obs['timeS']:.0f} s / tilt {obs['rootTiltDeg']:.1f} deg",fill=(233,238,243))
        d.text((12,y+29),f"lateral x {obs['xPositionM']:.4f} m  |  seat {obs['pelvisSeatN']:.0f} N  |  feet {obs['feetFloorN']:.0f} N  |  dose {obs['tonicDose']:.3f}",fill=(171,197,216))
        img.paste(frame,(0,y+52))
    img.save(OUT,optimize=True)
    receipt={'schema':'lucid.r577.renderer.native.v1','renderer':'MuJoCo 3.15 EGL',
        'modelSource':'Frozen R574, unmodified; R577 proprioceptive tonic overlay',
        'scene00':{'width':.131,'friction':.82,'forceN':0},
        'timestampsS':list(TIMES),'frames':values,'output':OUT.name,
        'outputSHA256':hashlib.sha256(OUT.read_bytes()).hexdigest()}
    (ROOT/'R577_NATIVE_RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
    print('WROTE',OUT,'bytes',OUT.stat().st_size,'sha',receipt['outputSHA256'],flush=True)
if __name__=='__main__':main()
