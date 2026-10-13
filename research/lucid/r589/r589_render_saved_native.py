#!/usr/bin/env python3
"""Render exactly captured continuous native MuJoCo qpos, original SKIN78.
No pose interpolation, physics rerunning, animation synthesizer, or modified mesh.
"""
import os,sys,json,hashlib
from pathlib import Path
import numpy as np,mujoco as mj,vtk
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),'/mnt/data/BioRig_R586_WORK','/mnt/data/BioRig_R585_REPAIR']
import r586_effort as r586
PROJECT=Path(os.environ.get('BIORIG_WORKSPACE','/mnt/data/BioRig_SKIN78_BRIDGE'))
sys.path.insert(0,str(PROJECT/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG'))
from lucid_bcr.pipeline import CausalRig,RigConfig
from lucid_bcr.render import Renderer
rig=CausalRig(RigConfig(realization='reference',deformation='canonical',muscles=False,demand=False,support='none'))
assert rig.a.skin_sha256=='88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10'
renderer=Renderer(width=480,height=560);renderer.set_ground(0.,size=2.2,on=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)

pb=r586.r585.prior.make_body('seated');r586.r585.prior.reset(pb)
sid=mj.mj_name2id(pb.model,mj.mjtObj.mjOBJ_GEOM,'research_seat')
c=pb.data.geom_xpos[sid];sz=pb.model.geom_size[sid]
box=vtk.vtkCubeSource();box.SetCenter(*map(float,c))
box.SetXLength(float(sz[0]*2));box.SetYLength(float(sz[1]*2));box.SetZLength(float(sz[2]*2))
mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(box.GetOutputPort())
actor=vtk.vtkActor();actor.SetMapper(mapper)
actor.GetProperty().SetColor(.22,.43,.51);actor.GetProperty().SetOpacity(.62)
renderer.ren.AddActor(actor)

imgs={};meta={}
for label in ('R587','R589'):
 path=HERE/f'{label}_NATIVE_12S_QPOS.npz'
 z=np.load(path);q=z['qpos'];t=z['timeS']
 assert len(q)==len(t)==31
 receipt=json.loads((HERE/f'{label}_NATIVE_12S_CAPTURE_RECEIPT.json').read_text())
 assert receipt['npzSHA256']==hashlib.sha256(path.read_bytes()).hexdigest()
 frames=[]
 for i,qs in enumerate(q):
  assert hashlib.sha256(qs.tobytes()).hexdigest()==receipt['frameSHA256'][i]
  cmds,hand,placement=pb.read_state(qpos=qs)
  pose=rig.comp.compile(cmds,extra_local=rig.art.hand.local_rotations(hand),placement=placement,validate=False)
  verts,_=rig._deform(pose)
  assert np.all(np.isfinite(verts))
  frames.append(renderer.render(verts,view='threequarter',scale=1.))
  if i%10==0:print('SKIN',label,i,float(t[i]),flush=True)
 imgs[label]=frames;meta[label]=receipt
output=[]
for i in range(31):
 im=Image.new('RGB',(990,662),(12,17,24));draw=ImageDraw.Draw(im)
 for j,label in enumerate(('R587','R589')):
  x=j*495
  obs=meta[label]['snapshots'][i]
  draw.text((x+9,8),f'{label} | '+('ORIGINAL ARM IMPACT' if label=='R587' else 'MUSCLE-DECELERATED LANDING'),font=bold,fill=(235,240,246))
  draw.text((x+9,31),f"Native {obs['timeS']:g}s | right-seat {obs['rightArmLoadN']:.1f} N",font=font,fill=(162,230,225))
  draw.text((x+9,53),f"left-seat {obs['leftArmLoadN']:.1f} N | canonical SKIN78",font=font,fill=(205,215,228))
  im.paste(imgs[label][i],(x+7,82))
 output.append(im)
p=HERE/'R589_NATIVE_SKIN78_12S_COMPARE.gif'
output[0].save(p,save_all=True,append_images=output[1:],duration=[200]*16+[600]*15,loop=0,optimize=True)
for i in (0,3,8,15,22,30):output[i].save(HERE/f'R589_12S_FRAME_{i:02}.png')
receipt={'schema':'lucid.r589.render-trace-linked.v1','meshSHA256':rig.a.skin_sha256,
         'frameCountPerRun':len(output),'nativeMuJoCoStateBytesVerified':True,
         'physicsReceiptsSHA256':{n:hashlib.sha256((HERE/f'{n}_NATIVE_12S_CAPTURE_RECEIPT.json').read_bytes()).hexdigest() for n in ('R587','R589')},
         'gif':p.name,'gifSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),
         'imagesGeneratedByAI':False,'poseInterpolationUsed':False}
(HERE/'R589_12S_RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
print('R589_REAL_SKIN78_PROOF',p,p.stat().st_size,receipt['gifSHA256'],flush=True)
renderer.ren.RemoveAllViewProps();renderer.win.Finalize();sys.stdout.flush();os._exit(0)
