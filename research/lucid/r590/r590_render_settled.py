#!/usr/bin/env python3
"""Original Skin78 / VTK renderer using EXACT 12-24s native MuJoCo qpos.
No interpolated poses, no image-generation, no physics/body modification.
"""
from __future__ import annotations
import os,sys,hashlib,json
from pathlib import Path
import numpy as np,mujoco as mj,vtk
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
HERE=ROOT
PROJECT=Path(os.environ['BIORIG_WORKSPACE']) if os.environ.get('BIORIG_WORKSPACE') else next((d for d in (HERE,*HERE.parents) if (d/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG').is_dir()),Path('/mnt/data/BioRig_SKIN78_BRIDGE'))
sys.path[:0]=[str(PROJECT/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG'),
                str(HERE.parent/'r586'),str(HERE.parent/'r585'),
                '/mnt/data/BioRig_R586_WORK','/mnt/data/BioRig_R585_REPAIR']
from lucid_bcr.pipeline import CausalRig,RigConfig
from lucid_bcr.render import Renderer
import r586_effort as r586
record=json.loads((ROOT/'R590_SETTLED_12TO24_NATIVE_RECEIPT.json').read_text())
source=ROOT/'R590_SETTLED_CONTINUOUS_NATIVE_QPOS.npz'
assert hashlib.sha256(source.read_bytes()).hexdigest()==record['npzSHA256']
z=np.load(source);qpos=z['qpos'];ts=z['timeS']
assert len(qpos)==len(ts)==31 and abs(ts[0]-12)<1e-8 and abs(ts[-1]-24)<1e-8
assert all(hashlib.sha256(qpos[k].tobytes()).hexdigest()==record['qposSHA256'][k] for k in range(31))
rig=CausalRig(RigConfig(realization='reference',deformation='canonical',muscles=False,demand=False,support='none'))
assert rig.a.skin_sha256=='88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10'
renderer=Renderer(width=550,height=650)
renderer.set_ground(0.,size=2.2,on=True)
pb=r586.r585.prior.make_body('seated');r586.r585.prior.reset(pb)
gid=mj.mj_name2id(pb.model,mj.mjtObj.mjOBJ_GEOM,'research_seat')
c=pb.data.geom_xpos[gid];sz=pb.model.geom_size[gid]
box=vtk.vtkCubeSource();box.SetCenter(*map(float,c))
box.SetXLength(float(sz[0]*2));box.SetYLength(float(sz[1]*2));box.SetZLength(float(sz[2]*2))
mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(box.GetOutputPort())
seat=vtk.vtkActor();seat.SetMapper(mapper);seat.GetProperty().SetColor(.22,.43,.51);seat.GetProperty().SetOpacity(.62)
renderer.ren.AddActor(seat)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
frames=[];metrics=[]
for i,(t,qp) in enumerate(zip(ts,qpos)):
    commands,hand,pos=pb.read_state(qpos=qp)
    pose=rig.comp.compile(commands,extra_local=rig.art.hand.local_rotations(hand),placement=pos,validate=False)
    verts,_=rig._deform(pose)
    assert np.isfinite(verts).all()
    rendered=renderer.render(verts,view='threequarter',scale=1.)
    canvas=Image.new('RGB',(570,740),(12,17,24))
    draw=ImageDraw.Draw(canvas)
    stamp=record['sampledContactForceN'][i]
    draw.text((16,12),f'R590 | PHYSICALLY SETTLED SKIN78',font=bold,fill=(235,241,247))
    draw.text((16,38),f'Native time {t:.1f}s  |  since settled: {t-12:.1f}s',font=font,fill=(165,227,218))
    draw.text((16,58),f'Left arm-seat {stamp["leftN"]:.1f}N   Right {stamp["rightN"]:.1f}N',font=font,fill=(211,218,228))
    canvas.paste(rendered,(10,82))
    frames.append(canvas)
    metrics.append({'timeS':float(t),'leftN':float(stamp['leftN']),'rightN':float(stamp['rightN'])})
    if i%10==0:print('NATIVE_SKIN78',i,round(t,1),flush=True)
path=ROOT/'R590_REAL_SKIN78_SETTLED_12TO24.gif'
frames[0].save(path,save_all=True,append_images=frames[1:],duration=160,loop=0,optimize=True)
for i in (0,10,20,30):frames[i].save(ROOT/f'R590_REAL_SKIN78_{round(ts[i]):02d}S.png',optimize=True)
receipt={'schema':'lucid.r590.original-skin-actual-native-qpos.v1','gifFile':path.name,
    'gifSHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'actualNativeFrames':31,
    'SKIN78meshSha':rig.a.skin_sha256,'zeroInterpolation':True,'physicsWindowS':[12,24],
    'labelingTimeBase':'Physical simulation still runs from t=0 T-pose. This visual uses only actual late physical states.'}
(ROOT/'R590_SKIN_RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
print('GIF_READY',path,path.stat().st_size,'sha256',receipt['gifSHA256'],flush=True)
renderer.ren.RemoveActor(seat);renderer.ren.RemoveAllViewProps();renderer.win.Finalize();sys.stdout.flush();os._exit(0)
