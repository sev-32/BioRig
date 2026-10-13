#!/usr/bin/env python3
"""Native SKIN78: physically settled scene under matched 0 and +120 N pushes.
Frames loaded byte-for-byte from native MuJoCo qpos; no pose interpolation.
Original T-pose shown separately as cause analysis, with matching camera.
"""
from __future__ import annotations
import os,sys,hashlib,json
from pathlib import Path
import numpy as np,mujoco as mj,vtk
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
PROJECT=Path(os.environ['BIORIG_WORKSPACE']) if os.environ.get('BIORIG_WORKSPACE') else next((d for d in (HERE,*HERE.parents) if (d/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG').is_dir()),Path('/mnt/data/BioRig_SKIN78_BRIDGE'))
sys.path[:0]=[str(PROJECT/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG'),
                str(HERE.parent/'r586'),str(HERE.parent/'r585'),
                '/mnt/data/BioRig_R586_WORK','/mnt/data/BioRig_R585_REPAIR']
from lucid_bcr.pipeline import CausalRig,RigConfig
from lucid_bcr.render import Renderer
import r586_effort as r586
rig=CausalRig(RigConfig(realization='reference',deformation='canonical',muscles=False,demand=False,support='none'))
assert rig.a.skin_sha256=='88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10'
renderer=Renderer(width=490,height=590);renderer.set_ground(0.,size=2.2,on=True)
pb=r586.r585.prior.make_body('seated');r586.r585.prior.reset(pb)
gid=mj.mj_name2id(pb.model,mj.mjtObj.mjOBJ_GEOM,'research_seat')
c=pb.data.geom_xpos[gid];sz=pb.model.geom_size[gid]
box=vtk.vtkCubeSource();box.SetCenter(*map(float,c))
box.SetXLength(float(sz[0]*2));box.SetYLength(float(sz[1]*2));box.SetZLength(float(sz[2]*2))
mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(box.GetOutputPort())
seat=vtk.vtkActor();seat.SetMapper(mapper);seat.GetProperty().SetColor(.22,.43,.51);seat.GetProperty().SetOpacity(.62)
renderer.ren.AddActor(seat)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',17)

def render(q):
    commands,hand,pos=pb.read_state(qpos=q)
    pose=rig.comp.compile(commands,extra_local=rig.art.hand.local_rotations(hand),placement=pos,validate=False)
    vertices,_=rig._deform(pose)
    assert np.isfinite(vertices).all()
    return renderer.render(vertices,view='threequarter',scale=1.)

sources={};frames={};traces={}
for name,push in [('SETTLED / NO PUSH',0),('SETTLED / +120 N',120)]:
    npz=HERE/f'R590_RESTART_PUSH_{push:+d}N_QPOS.npz'
    result=json.loads((HERE/f'R590_RESTART_WITH_STATES_{push:+d}N_12S.json').read_text())
    assert hashlib.sha256(npz.read_bytes()).hexdigest()==result['capturedQposSHA256']
    z=np.load(npz)
    assert len(z['qpos'])==len(z['timeS'])==31
    assert np.max(np.abs(z['timeS']-np.arange(31)*.4))<1e-7
    sources[name]=result
    frames[name]=[render(q) for q in z['qpos']]
    traces[name]=z['timeS']
    print('SKIN_NATIVE_CAPTURE',name,len(frames[name]),flush=True)

# Deterministic original neutral pose equals R589 physical t=0 qpos.
before=pb.data.qpos.copy()
old=render(before);new=frames['SETTLED / NO PUSH'][0]
comparison=Image.new('RGB',(1010,680),(13,17,24));draw=ImageDraw.Draw(comparison)
for col,(title,im,sub) in enumerate([
    ('BEFORE / ARTIFICIAL ARMS-OUT START',old,'R589 original first physical frame'),
    ('R590 / PHYSICALLY SETTLED START',new,'After 12s real muscle and contact settling')]):
    x=col*505
    draw.text((x+10,9),title,font=bold,fill=(241,245,248))
    draw.text((x+10,33),sub,font=font,fill=(171,221,226))
    comparison.paste(im,(x+7,72))
comparison.save(HERE/'R590_REAL_SKIN78_STARTUP_CAUSE.png',optimize=True)

composed=[]
for i in range(31):
    panel=Image.new('RGB',(1010,680),(13,17,24));draw=ImageDraw.Draw(panel)
    for col,name in enumerate(('SETTLED / NO PUSH','SETTLED / +120 N')):
        x=col*505;t=traces[name][i]
        s=next((s for s in sources[name]['samples'] if abs(s['relativeS']-t)<1e-6),None)
        assert s is not None
        draw.text((x+12,9),'R590  '+name,font=bold,fill=(238,242,246))
        draw.text((x+12,33),f'Native time {t:.1f}s | head {s["headDeg"]:.2f} deg',font=font,fill=(159,222,226))
        draw.text((x+12,54),f'Arm-seat left {s["leftArmN"]:.1f}N / right {s["rightArmN"]:.1f}N',font=font,fill=(208,216,227))
        panel.paste(frames[name][i],(x+7,80))
    composed.append(panel)
    if i%10==0:print('COMPOSE',i,flush=True)
gif=HERE/'R590_REAL_SKIN78_REST_START_NO_PUSH_VS_120N.gif'
composed[0].save(gif,save_all=True,append_images=composed[1:],duration=150,loop=0,optimize=True)
for k in (0,10,20,30):composed[k].save(HERE/f'R590_RESTART_NATIVE_{int(round(k*.4)):02d}S.png',optimize=True)
audit={'schema':'lucid.r590.native-rendered-physical-clone.v1','originalSkinSHA256':rig.a.skin_sha256,
'gifSHA256':hashlib.sha256(gif.read_bytes()).hexdigest(),'gifFrames':31,
'physicalStateFiles':{name:result['capturedQposSHA256'] for name,result in sources.items()},
'initialPoseComparison':'Original t0 arms-out vs real physical t12 rest-start; both original SKIN78',
'rootPoseOrSkinEdited':False,'noInterpolation':True,'noGeneratedImages':True,
'finalHead':{name:result['samples'][-1]['headDeg'] for name,result in sources.items()}}
(HERE/'R590_RESTART_SKIN_RENDER_AUDIT.json').write_text(json.dumps(audit,indent=2))
print('R590_NATIVE_GIF',gif,gif.stat().st_size,'SHA',audit['gifSHA256'],flush=True)
renderer.ren.RemoveActor(seat);renderer.ren.RemoveAllViewProps();renderer.win.Finalize();sys.stdout.flush();os._exit(0)
