#!/usr/bin/env python3
"""Actual MuJoCo/EGL fixed-camera scene, four physical times; no generated art."""
import os,sys,json,hashlib
from pathlib import Path
os.environ.setdefault('MUJOCO_GL','egl')
import numpy as np
import mujoco as mj
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r579_controller as r
TIMES=(0.,4.,8.,12.)
W,H=600,460
PROFILE='hip_trunk_20pct'

def main():
    pb,ref,neu,saved=r.r577.phys.paired_scene(.131,.82)
    pb.model.vis.headlight.ambient[:]=[.86,.86,.86]
    pb.model.vis.headlight.diffuse[:]=[1.,1.,1.]
    pb.model.geom_rgba[0]=[.38,.55,.75,.18]
    for geom in range(2,pb.model.ngeom):
        if pb.model.geom_rgba[geom,3]>.01:
            pb.model.geom_rgba[geom,:3]=np.clip(.28+pb.model.geom_rgba[geom,:3]*.85,.28,.91)
    d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
    original=r.r577.phys.plant.sha_state(pb.data)
    early=r.r577.phys.TimedPulse(pb.model,'none')
    support=r.Synergy(pb.model,PROFILE)
    camera=mj.MjvCamera();mj.mjv_defaultCamera(camera)
    camera.type=mj.mjtCamera.mjCAMERA_FREE
    camera.lookat[:]=[.02,.52,-.16];camera.distance=1.65
    camera.azimuth=110.;camera.elevation=-15.
    images=[];snapshots=[]
    with mj.Renderer(pb.model,width=W,height=H) as renderer:
        for k in range(round(TIMES[-1]/r.r577.DT)+1):
            t=k*r.r577.DT
            if any(abs(t-time)<1.e-7 for time in TIMES):
                obs=r.r577.phys.sense(pb,d)
                renderer.update_scene(d,camera=camera)
                images.append(Image.fromarray(renderer.render()).convert('RGB'))
                snapshots.append({'timeS':t,'rootTiltDeg':obs['rootTiltDeg'],
                    'xPositionM':obs['xPosition'],'seatN':obs['pelvisSeatN'],
                    'feetN':obs['feetFloorN'],'armSeatN':obs['armsSeatN'],
                    'tonicExcitation':support.amplitude})
            if k==round(TIMES[-1]/r.r577.DT):break
            if k%r.r577.baseline.UPDATE_STEPS==0:
                obs=r.r577.phys.sense(pb,d)
                early.update(t,obs);support.update(t,obs)
            delta=np.clip(early.output()+support.output(),0.,.04)
            r.r577.phys.plant.step_perturbed(pb,d,ref,neu,delta,np.zeros(3))
    assert original==r.r577.phys.plant.sha_state(pb.data)
    panel=Image.new('RGB',(W*2,(H+54)*2),(18,22,29))
    draw=ImageDraw.Draw(panel)
    for i,(im,o) in enumerate(zip(images,snapshots)):
        x=(i%2)*W;y=(i//2)*(H+54)
        draw.text((x+14,y+11),f'R579 / NATIVE MUJOCO / {o["timeS"]:g} s / tilt {o["rootTiltDeg"]:.2f} deg',fill=(233,239,245))
        draw.text((x+14,y+32),f'x {o["xPositionM"]:.4f} m | seat {o["seatN"]:.0f} N | feet {o["feetN"]:.0f} N',fill=(175,200,216))
        panel.paste(im,(x,y+54))
    path=HERE/'R579_NATIVE_SCENE00_12S_GRID.png'
    panel.save(path,optimize=True)
    receipt={'schema':'lucid.r579.real-render.v1','profile':PROFILE,'nativeRenderer':'MuJoCo 3.15 EGL',
             'renderTimesS':TIMES,'physicalScene':{'seatHalfWidthM':.131,'friction':.82,'forceN':0},
             'frozenModelUnmodified':True,'snapshots':snapshots,
             'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
    (HERE/'R579_RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
    print('NATIVE R579 RENDER',path,'bytes',path.stat().st_size,'SHA256',receipt['sha256'],flush=True)
if __name__=='__main__':main()
