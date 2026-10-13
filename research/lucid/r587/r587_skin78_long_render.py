#!/usr/bin/env python3
"""New 24-second SKIN78 VTK captures of real native MuJoCo R586 physics.

No pose interpolation or artistic reconstruction; original SKIN78 mesh SHA checked.
R586 motor controller and R585 muscle geometry preserved, no root hold.
"""
from pathlib import Path
import os,sys,json,hashlib,time
HERE=Path(__file__).resolve().parent
# Locate the immutable original runtime and sibling research modules from repo root.
PROJECT=next((p for p in (HERE,*HERE.parents)
              if (p/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG').is_dir()),None)
if PROJECT is None:raise RuntimeError('Restore original R574 runtime into repository root ./runtime')
os.environ.setdefault('BIORIG_WORKSPACE',str(PROJECT))
sys.path[:0]=[str(HERE),str(HERE.parent/'r586'),str(HERE.parent/'r585'),
  str(PROJECT/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG'),
  str(PROJECT/'runtime/LUCID_R552_WORKSPACE/R551_ACTIVE_RECOVERY'),
  str(PROJECT/'runtime/LUCID_R552_WORKSPACE/R543_MULTICONTACT_LEARNING')]
import numpy as np, mujoco as mj, vtk
from PIL import Image,ImageDraw,ImageFont
from r586_effort import run
from lucid_bcr.pipeline import CausalRig,RigConfig
from lucid_bcr.render import Renderer

PUSH_N=float(os.environ.get('R587_PUSH_N','0'))
TAG='R587_SKIN78_24S_PUSH120' if abs(PUSH_N-120)<1e-6 else 'R587_SKIN78_24S'
EXPECTED_SKIN_SHA='88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(FONT,15)
bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',17)
rig=CausalRig(RigConfig(realization='reference',deformation='canonical',muscles=False,demand=False,support='none'))
assert rig.a.skin_sha256==EXPECTED_SKIN_SHA
renderer=Renderer(width=510,height=610)
renderer.set_ground(0.,size=2.2,on=True)
images=[];records=[];seat=[None];started=time.monotonic()

def capture(pb,d,obs):
    if seat[0] is None:
        i=mj.mj_name2id(pb.model,mj.mjtObj.mjOBJ_GEOM,'research_seat')
        center=pb.data.geom_xpos[i]
        dims=pb.model.geom_size[i]
        box=vtk.vtkCubeSource();box.SetCenter(*[float(x) for x in center])
        box.SetXLength(float(dims[0]*2));box.SetYLength(float(dims[1]*2));box.SetZLength(float(dims[2]*2))
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(box.GetOutputPort())
        seat[0]=vtk.vtkActor();seat[0].SetMapper(mapper)
        seat[0].GetProperty().SetColor(.22,.43,.51)
        seat[0].GetProperty().SetOpacity(.65)
        renderer.ren.AddActor(seat[0])
    commands,hand,placement=pb.read_state(qpos=d.qpos)
    pose=rig.comp.compile(commands,extra_local=rig.art.hand.local_rotations(hand),placement=placement,validate=False)
    verts,_=rig._deform(pose)
    if not np.isfinite(verts).all(): raise AssertionError('nonfinite Skin78 vertex')
    image=renderer.render(verts,view='threequarter',scale=1.)
    actual_head=float(obs['headThoraxDeg'])
    if actual_head>5.: raise AssertionError(f'bad physical neck orientation {actual_head:.2f} deg at {obs["timeS"]:.2f}s')
    draw_panel=Image.new('RGB',(570,710),(12,18,26))
    draw=ImageDraw.Draw(draw_panel)
    draw.text((14,8),'R587  |  NATIVE SKIN78  |  24s ' + ('+120N HIP PUSH' if PUSH_N else 'BALANCE CHECK'),font=bold,fill=(237,245,250))
    draw.text((14,34),f'Physical time {obs["timeS"]:5.1f} s     Neck relative to torso {actual_head:5.2f} deg',font=font,fill=(162,229,226))
    draw.text((14,56),f'Pelvis x {obs["pelvisX_m"]*1000:5.1f} mm   |   Arms on seat {obs["seatArmsN"]:5.1f} N',font=font,fill=(188,211,232))
    draw_panel.paste(image,(30,82))
    images.append(draw_panel)
    records.append({'timeS':float(obs['timeS']),'headToTorsoDeg':actual_head,
        'pelvisX_m':float(obs['pelvisX_m']),'rootTiltDeg':float(obs['rootTiltDeg']),
        'armSeat_N':float(obs['seatArmsN']),'otherFloor_N':float(obs['otherFloorN']),
        'nativeQposSHA256':hashlib.sha256(d.qpos.tobytes()).hexdigest()})
    if len(images)%10==0: print('R587 native SKIN78 rendered',len(images),'physical_t',obs['timeS'],'wall',round(time.monotonic()-started,1),flush=True)

result=run(secs=24.,push_N=PUSH_N,on_frame=capture)
assert len(images)==61,(len(images),'expected 61 native frames sampled every 0.4s')
assert result['maxHeadAngleDeg']<5
assert result['maxArmSeatN']<50
assert result['maxOtherFloorN']<50
assert result['optimizerFallbacks']==0
anim=HERE/(TAG+'_NATIVE_ANIMATION.gif')
images[0].save(anim,save_all=True,append_images=images[1:],duration=100,loop=0,optimize=True)
# Four genuine native timestamps in one panel for clients not playing GIFs.
selected=[0,20,40,60]
sheet=Image.new('RGB',(1140,1420),(12,18,26))
for idx,i in enumerate(selected): sheet.paste(images[i],((idx%2)*570,(idx//2)*710))
stills=HERE/(TAG+'_ACTUAL_TIMESTAMPS.png');sheet.save(stills,optimize=True)
result['renderer']='Original SKIN78 mesh, native MuJoCo 3.15 physical state, VTK'
result['originalSkinSHA256']=rig.a.skin_sha256
result['nativeCapturePeriodS']=.4
result['nativeFrames']=records
result['animatedGIF_SHA256']=hashlib.sha256(anim.read_bytes()).hexdigest()
result['stillPanelSHA256']=hashlib.sha256(stills.read_bytes()).hexdigest()
receipt=HERE/(TAG+'_NATIVE_RECEIPT.json')
receipt.write_text(json.dumps(result,indent=2,allow_nan=False))
print('FINISHED GIF',str(anim),'size',anim.stat().st_size,'SHA',result['animatedGIF_SHA256'],flush=True)
print('FINISHED PANEL',str(stills),'size',stills.stat().st_size,flush=True)
renderer.ren.RemoveAllViewProps();renderer.win.Finalize()
sys.stdout.flush();os._exit(0)
