#!/usr/bin/env python3
"""Native MuJoCo 3.15 EGL renderer with identical controller/scene as R580 LATE 40s.
Visual-only transparent seat, fixed inspection camera; no dynamics changes.
"""
import os,sys,json,hashlib
os.environ.setdefault('MUJOCO_GL','egl')
from pathlib import Path
import numpy as np
import mujoco as mj
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r580_adaptive_synergy as r
TIMES=(0.,20.,30.,40.)
W,H=600,480
CONFIG={**r.CONFIG,'triggerPositionM':.0284,'fullRecruitAtM':.0308,'lookaheadS':1.,'hipMax':.029}

def main():
    pb,ref,neu,saved=r.phys.paired_scene(.131,.82)
    # Visual tuning only. No contact, dynamics, inertial or model-collision edits.
    pb.model.vis.headlight.ambient[:]=[.86,.86,.86]
    pb.model.vis.headlight.diffuse[:]=[1.,1.,1.]
    pb.model.geom_rgba[0]=[.38,.55,.75,.18]
    for gi in range(2,pb.model.ngeom):
        if pb.model.geom_rgba[gi,3]>.01:
            pb.model.geom_rgba[gi,:3]=np.clip(.28+pb.model.geom_rgba[gi,:3]*.85,.28,.91)
    d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
    unchanged=r.phys.plant.sha_state(pb.data)
    early=r.phys.TimedPulse(pb.model,'none')
    ctl=r.AdaptiveSynergy(pb.model,CONFIG)
    cam=mj.MjvCamera();mj.mjv_defaultCamera(cam)
    cam.type=mj.mjtCamera.mjCAMERA_FREE
    cam.lookat[:]=[.02,.52,-.16];cam.distance=1.65;cam.azimuth=110.;cam.elevation=-15.
    frames=[];state=[]
    with mj.Renderer(pb.model,width=W,height=H) as renderer:
        for k in range(round(TIMES[-1]/r.DT)+1):
            t=k*r.DT
            if any(abs(t-q)<1e-8 for q in TIMES):
                obs=r.phys.sense(pb,d)
                renderer.update_scene(d,camera=cam)
                frames.append(Image.fromarray(renderer.render()).convert('RGB'))
                state.append({'tS':t,'rootXM':obs['xPosition'],'vxMps':obs['xSpeed'],
                  'tiltDeg':obs['rootTiltDeg'],'seatN':obs['pelvisSeatN'],
                  'feetN':obs['feetFloorN'],'armSeatN':obs['armsSeatN'],
                  'hipDose':ctl.hipDose,'trunkFraction':ctl.trunkFraction})
                print('capture',t,obs['xPosition'],obs['rootTiltDeg'],flush=True)
            if k==round(TIMES[-1]/r.DT):break
            if k%round(.04/r.DT)==0:
                obs=r.phys.sense(pb,d)
                early.update(t,obs);ctl.update(t,obs)
            cmd=np.clip(early.output()+ctl.output(),0.,r.phys.plant.MAX_EXTRA)
            r.phys.plant.step_perturbed(pb,d,ref,neu,cmd,np.zeros(3))
    assert unchanged==r.phys.plant.sha_state(pb.data)
    panel=Image.new('RGB',(W*2,(H+50)*2),(17,20,25))
    draw=ImageDraw.Draw(panel)
    for i,(im,obs) in enumerate(zip(frames,state)):
        x=(i%2)*W;y=(i//2)*(H+50)
        draw.text((x+10,y+7),f'R580 native MuJoCo | {obs["tS"]:g}s | tilt {obs["tiltDeg"]:.2f} deg',fill=(239,243,247))
        draw.text((x+10,y+26),f'x {obs["rootXM"]:.4f}m | seat {obs["seatN"]:.0f}N | hip dose {obs["hipDose"]:.3f} | trunk {obs["trunkFraction"]:.2f}',fill=(176,200,213))
        panel.paste(im,(x,y+50))
    path=HERE/'R580_NATIVE_40S_LATE.png'
    panel.save(path,optimize=True)
    receipt={'schema':'lucid.r580.native-EGL-image.v1','renderer':'MuJoCo 3.15 EGL',
             'real_physical_steps':round(TIMES[-1]/r.DT),'config':CONFIG,'frames':state,
             'nativeModelUnmodified':True,'imageSHA256':hashlib.sha256(path.read_bytes()).hexdigest()}
    (HERE/'R580_RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
    print('OUTPUT',path,receipt['imageSHA256'])
if __name__=='__main__':main()
