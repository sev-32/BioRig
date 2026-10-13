#!/usr/bin/env python3
"""Actual fixed-camera MuJoCo 3.15 EGL, transparent seat visual inspection.

Frames are sampled from same native continuous R581 40-second simulation.
Only rendering rgba/lighting/camera altered; contact/dynamics unchanged.
"""
import os,sys,json,hashlib
os.environ.setdefault('MUJOCO_GL','egl')
from pathlib import Path
import numpy as np
import mujoco as mj
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r581_controller as r
from r581_support import sense_support
TIMES=(0.,12.,25.,30.,40.)
W,H=550,420

def main():
    pb,ref,neu,saved=r.phy.paired_scene(.131,.82)
    init_hash=r.phy.plant.sha_state(pb.data)
    pb.model.vis.headlight.ambient[:]=[.88,.88,.88]
    pb.model.vis.headlight.diffuse[:]=[1.,1.,1.]
    pb.model.geom_rgba[0]=[.36,.57,.78,.19]
    for gi in range(2,pb.model.ngeom):
        if pb.model.geom_rgba[gi,3]>.01:
            pb.model.geom_rgba[gi,:3]=np.clip(.28+pb.model.geom_rgba[gi,:3]*.85,.28,.91)
    d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
    controller=r.ContactAllocator(pb.model)
    early=r.phy.TimedPulse(pb.model,'none')
    camera=mj.MjvCamera();mj.mjv_defaultCamera(camera)
    camera.type=mj.mjtCamera.mjCAMERA_FREE
    camera.lookat[:]=[.02,.52,-.16];camera.distance=1.65
    camera.azimuth=110.;camera.elevation=-15.
    frames=[];measured=[]
    with mj.Renderer(pb.model,width=W,height=H) as renderer:
        for k in range(round(TIMES[-1]/r.DT)+1):
            t=k*r.DT
            if any(abs(t-v)<1e-8 for v in TIMES):
                o=r.phy.sense(pb,d);sup=sense_support(pb.model,d)
                renderer.update_scene(d,camera=camera)
                frames.append(Image.fromarray(renderer.render()).convert('RGB'))
                measured.append({'timeS':t,'rootX_m':o['xPosition'],
                   'tilt_deg':o['rootTiltDeg'],'seatN':o['pelvisSeatN'],
                   'feetN':o['feetFloorN'],'hipDose':controller.hip,
                   'trunkDose':controller.trunk,
                   'comMinusCOP_m':sup.comMinusCop_m,
                   'comX_m':sup.comX_m,'copX_m':sup.copX_m})
                print('CAPTURE',t,'root',o['xPosition'],'com-cop',sup.comMinusCop_m,flush=True)
            if k==round(TIMES[-1]/r.DT):break
            if k%round(.04/r.DT)==0:
                o=r.phy.sense(pb,d)
                early.update(t,o);controller.update(t,o,pb.model,d)
            delta=np.clip(early.output()+controller.output(),0.,r.phy.plant.MAX_EXTRA)
            r.phy.plant.step_perturbed(pb,d,ref,neu,delta,np.zeros(3))
    assert init_hash==r.phy.plant.sha_state(pb.data)
    panel=Image.new('RGB',(W*2,(H+58)*3),(19,23,28))
    draw=ImageDraw.Draw(panel)
    for i,(frame,o) in enumerate(zip(frames,measured)):
        x=(i%2)*W;y=(i//2)*(H+58)
        draw.text((x+10,y+7),f'R581 NATIVE MUJOCO | {o["timeS"]:g}s | tilt {o["tilt_deg"]:.2f} deg',fill=(234,242,248))
        draw.text((x+10,y+25),f'pelvis x {o["rootX_m"]:.4f}m | COM-COP {o["comMinusCOP_m"]:.4f}m',fill=(186,213,228))
        draw.text((x+10,y+42),f'seat {o["seatN"]:.0f}N | hip {o["hipDose"]:.3f} | trunk {o["trunkDose"]:.3f}',fill=(173,197,210))
        panel.paste(frame,(x,y+58))
    path=HERE/'R581_NATIVE_40S_INSPECTION.png';panel.save(path,optimize=True)
    receipt={'schema':'lucid.r581.native-render.v1','renderer':'MuJoCo 3.15 EGL',
      'scene':'R574 frozen scene00, zero push','timesS':TIMES,
      'camera':{'azimuthDeg':110,'elevationDeg':-15,'distanceM':1.65},
      'visualOnly':True,'sourcePhysicsUnmodified':True,
      'states':measured,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'bytes':path.stat().st_size}
    (HERE/'R581_RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
    print('WROTE',path,receipt['sha256'])
if __name__=='__main__':main()
