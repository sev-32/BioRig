#!/usr/bin/env python3
"""SKIN78 renderer. Three groups use unmodified native qpos captured from MuJoCo."""
import os,sys,json,hashlib
from pathlib import Path
import numpy as np,mujoco as mj,vtk
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;OUT=HERE/'out'
sys.path[:0]=[str(HERE/x) for x in ('r590','r589','r588','r586','r585')]
from lucid_bcr.pipeline import CausalRig,RigConfig
from lucid_bcr.render import Renderer
import r590_rest_restart as r590
rig=CausalRig(RigConfig(realization='reference',deformation='canonical',muscles=False,demand=False,support='none'))
assert rig.a.skin_sha256=='88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10'
renderer=Renderer(width=450,height=545)
renderer.set_ground(0.,size=2.2,on=True)
pb,qref,neutral,allocator,hinges,raw=r590.setup()
gid=mj.mj_name2id(pb.model,mj.mjtObj.mjOBJ_GEOM,'research_seat')
c=pb.data.geom_xpos[gid];sz=pb.model.geom_size[gid]
box=vtk.vtkCubeSource();box.SetCenter(*map(float,c));box.SetXLength(float(sz[0]*2));box.SetYLength(float(sz[1]*2));box.SetZLength(float(sz[2]*2))
mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(box.GetOutputPort())
actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(.22,.43,.51);actor.GetProperty().SetOpacity(.62)
renderer.ren.AddActor(actor)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
case=[('NO EXTRA MUSCLE CONTROL','base'),('SINGLE-AGONIST MOTOR','single'),('RECIPROCAL RELEASE + FEEDBACK','RELEASE_PLUS')]
frames={};trace={}
for label,code in case:
 npz=OUT/f'R591_{code}_NATIVE_QPOS.npz';z=np.load(npz)
 r=json.loads((OUT/f'R591_{code}_MEASURED.json').read_text())
 assert hashlib.sha256(npz.read_bytes()).hexdigest()==r['framesSHA256']
 frames[code]=[];trace[code]=r
 for i in range(0,len(z['timeS']),2):
  q=z['qpos'][i];time=float(z['timeS'][i])
  cmds,hand,pos=pb.read_state(qpos=q)
  pose=rig.comp.compile(cmds,extra_local=rig.art.hand.local_rotations(hand),placement=pos,validate=False)
  verts,_=rig._deform(pose)
  assert np.all(np.isfinite(verts))
  frames[code].append((time,renderer.render(verts,view='threequarter',scale=1.)))
 print('NATIVE SKIN78',code,len(frames[code]),flush=True)
images=[]
for i in range(len(frames[case[0][1]])):
 panel=Image.new('RGB',(3*463,640),(14,18,26));draw=ImageDraw.Draw(panel)
 for j,(label,code) in enumerate(case):
  t,img=frames[code][i];x=463*j
  series=trace[code]['sampledTimeSeries']
  measured=min(series,key=lambda s:abs(s['tS']-t))
  draw.text((x+10,8),label,font=bold,fill=(230,240,245))
  draw.text((x+10,34),f"Native physics t={t:.1f}s | elbow {measured['qRad']*180/np.pi:.1f} deg",font=font,fill=(152,220,231))
  draw.text((x+10,57),f"Head {measured['headDeg']:.2f} deg | flex/extend via MUSCLES",font=font,fill=(202,208,220))
  panel.paste(img,(x+6,86))
 images.append(panel)
 for target in [0,3,5,8]:
  if i==target:panel.save(OUT/f'R591_ACTUAL_NATIVE_FRAME_{i:02d}.png',optimize=True)
gif=OUT/'R591_RECIPROCAL_RELEASE_NATIVE_SKIN78_COMPARISON.gif'
images[0].save(gif,save_all=True,append_images=images[1:],duration=185,loop=0,optimize=True)
receipt={'nativePhysics':'mujoco 3.15.0','skinSHA256':rig.a.skin_sha256,'frameCount':len(images),
   'gifSHA256':hashlib.sha256(gif.read_bytes()).hexdigest(),'renderFromUnmodifiedQpos':True,
   'qposFilesSHA256':{code:trace[code]['framesSHA256'] for _,code in case},
   'noGeneratedOrInterpolatedPoses':True}
(OUT/'R591_RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
print('GIF',gif, gif.stat().st_size,receipt['gifSHA256'],flush=True)
renderer.ren.RemoveAllViewProps();renderer.win.Finalize();sys.stdout.flush();os._exit(0)
