#!/usr/bin/env python3
"""Actual MuJoCo 3.15 EGL capture for R578 feedback, *no generated images*.
Freeze camera and display each true physics state from one continuous run.
"""
import os,sys,json,hashlib
os.environ.setdefault('MUJOCO_GL','egl')
from pathlib import Path
import numpy as np
import mujoco as mj
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r578_feedback as r
TIMES=(0.,12.,20.,30.,40.)
W,H=550,480
TUNING={**r.CONFIG,'rootTargetM':.023,'kpRootPerM':1.2,'kpComPerM':.3}

def capture():
    sc={'seatHalfWidthM':.131,'friction':.82,'forceN':0.,'direction':1.}
    pb,ref,neu,saved=r.phys.paired_scene(.131,.82)
    d=mj.MjData(pb.model)
    mj.mj_copyData(d,pb.model,saved)
    initial=r.phys.plant.sha_state(pb.data)
    early=r.phys.TimedPulse(pb.model,'none')
    feedback=r.SupportFeedback(pb.model,TUNING)
    cam=mj.MjvCamera();mj.mjv_defaultCamera(cam)
    cam.type=mj.mjtCamera.mjCAMERA_FREE
    cam.lookat[:]=[.03,.53,-.1];cam.distance=1.95;cam.azimuth=110.;cam.elevation=-15.
    frames=[];values=[]
    with mj.Renderer(pb.model,width=W,height=H) as render:
        for k in range(round(max(TIMES)/r.DT)+1):
            t=k*r.DT
            if any(abs(t-x)<1e-7 for x in TIMES):
                obs=r.phys.sense(pb,d)
                render.update_scene(d,camera=cam)
                frame=Image.fromarray(render.render()).convert('RGB')
                frames.append(frame)
                values.append({'timeS':round(t,3),'xPositionM':obs['xPosition'],
                   'rootTiltDeg':obs['rootTiltDeg'],'armsSeatN':obs['armsSeatN'],
                   'pelvisSeatN':obs['pelvisSeatN'],'feetFloorN':obs['feetFloorN'],
                   'muscleAdditionalDose':feedback.amplitude})
            if k==round(max(TIMES)/r.DT):break
            if k%r.inherited.baseline.UPDATE_STEPS==0:
                obs=r.phys.sense(pb,d)
                early.update(t,obs)
                feedback.update(t,obs,pb,d)
            extra=np.clip(early.output()+feedback.output(),0.,.04)
            r.phys.plant.step_perturbed(pb,d,ref,neu,extra,np.zeros(3))
    assert initial==r.phys.plant.sha_state(pb.data)
    return frames,values

def main():
    frames,values=capture()
    img=Image.new('RGB',(W,len(frames)*(H+52)),(17,20,26))
    draw=ImageDraw.Draw(img)
    for i,(frame,obs) in enumerate(zip(frames,values)):
        y=i*(H+52)
        draw.text((12,y+9),f"R578 NATIVE MUJOCO {obs['timeS']:.0f}s | tilt {obs['rootTiltDeg']:.1f}deg",fill=(233,238,243))
        draw.text((12,y+29),f"lateral x {obs['xPositionM']:.4f}m | seat {obs['pelvisSeatN']:.0f}N | feet {obs['feetFloorN']:.0f}N | dose {obs['muscleAdditionalDose']:.3f}",fill=(171,197,216))
        img.paste(frame,(0,y+52))
    output=HERE/'R578_NATIVE_40S_EVOLUTION.png'
    img.save(output,optimize=True)
    receipt={'schema':'lucid.r578.native-render.v1','renderer':'MuJoCo 3.15 EGL',
      'camera':{'azimuth':110.,'elevation':-15.,'distance':1.95},
      'scene':'R574 locked scene 00, zero push',
      'feedbackConfig':TUNING,'frames':values,'outputFile':output.name,
      'outputSHA256':hashlib.sha256(output.read_bytes()).hexdigest()}
    (HERE/'R578_RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
    print('R578 NATIVE RENDER',output,output.stat().st_size,receipt['outputSHA256'],flush=True)
if __name__=='__main__':main()
