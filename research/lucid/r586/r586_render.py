#!/usr/bin/env python3
"""Native R585 versus new R586 SKIN78 proof. Every frame is real MuJoCo physical state."""
import os,json,hashlib,time
from pathlib import Path
import numpy as np,mujoco as mj,vtk
from PIL import Image,ImageDraw,ImageFont
from r586_effort import run
from lucid_bcr.pipeline import CausalRig,RigConfig
from lucid_bcr.render import Renderer

HERE=Path(__file__).resolve().parent
REFERENCE=Path(os.environ.get('BIORIG_R585_REFERENCE_GIF',str(HERE.parent/'r585'/'R585_REAL_SKIN78_NECK_REPAIR_12S.gif')))
if not REFERENCE.is_file():
 raise FileNotFoundError(f'Provide original R585 native GIF as BIORIG_R585_REFERENCE_GIF: {REFERENCE}')
rig=CausalRig(RigConfig(realization='reference',deformation='canonical',muscles=False,demand=False,support='none'))
assert rig.a.skin_sha256=='88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10'
renderer=Renderer(width=500,height=610);renderer.set_ground(0.,size=2.2,on=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',17)
frames=[];meta=[];seat=[None];started=time.monotonic()
def capture(pb,data,obs):
 if seat[0] is None:
  i=mj.mj_name2id(pb.model,mj.mjtObj.mjOBJ_GEOM,'research_seat')
  center=pb.data.geom_xpos[i];dims=pb.model.geom_size[i]
  cube=vtk.vtkCubeSource();cube.SetCenter(*map(float,center))
  cube.SetXLength(float(2*dims[0]));cube.SetYLength(float(2*dims[1]));cube.SetZLength(float(2*dims[2]))
  mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(cube.GetOutputPort())
  seat[0]=vtk.vtkActor();seat[0].SetMapper(mapper)
  seat[0].GetProperty().SetColor(.22,.43,.51);seat[0].GetProperty().SetOpacity(.65)
  renderer.ren.AddActor(seat[0])
 commands,hand,placement=pb.read_state(qpos=data.qpos)
 pose=rig.comp.compile(commands,extra_local=rig.art.hand.local_rotations(hand),placement=placement,validate=False)
 vertices,_=rig._deform(pose)
 assert np.isfinite(vertices).all()
 frames.append(renderer.render(vertices,view='threequarter',scale=1.))
 meta.append({**obs,'nativeQposSHA256':hashlib.sha256(data.qpos.tobytes()).hexdigest()})
 if len(frames)%5==0:print('CAPTURE',len(frames),obs['timeS'],'head',obs['headThoraxDeg'],'wall',round(time.monotonic()-started,1),flush=True)

result=run(secs=12.,on_frame=capture)
assert len(frames)==31,(len(frames),'expected 31 physically sampled frames')
original=Image.open(REFERENCE);assert original.n_frames==31
merged=[]
for i,im in enumerate(frames):
 original.seek(i)
 old=original.convert('RGB').crop((510,0,1020,705))
 new=Image.new('RGB',(510,705),(11,16,23));d=ImageDraw.Draw(new)
 o=meta[i]
 d.text((8,8),'R586 EFFICIENT NECK REPAIR',fill=(235,242,247),font=bold)
 d.text((8,33),f"Native {o['timeS']:.1f}s | head-torso {o['headThoraxDeg']:.2f} deg",fill=(164,223,228),font=font)
 d.text((8,55),f"Pelvis {o['pelvisX_m']*1000:.1f} mm | original SKIN78",fill=(187,201,218),font=font)
 new.paste(im,(0,90))
 joined=Image.new('RGB',(1020,705),(11,16,23));joined.paste(old);joined.paste(new,(510,0))
 merged.append(joined)
out=HERE/'R586_NATIVE_SKIN78_VS_R585_12S.gif'
merged[0].save(out,save_all=True,append_images=merged[1:],duration=160,loop=0,optimize=True)
for i,tag in [(0,'START'),(10,'4S'),(20,'8S'),(30,'END')]:merged[i].save(HERE/f'R586_SKIN78_{tag}.png',optimize=True)
result['nativeGIF_SHA256']=hashlib.sha256(out.read_bytes()).hexdigest()
result['originalSkinSHA256']=rig.a.skin_sha256
result['frameQposHashes']=[x['nativeQposSHA256'] for x in meta]
result['framesPerCondition']=31
result['referenceSource']=str(REFERENCE)
(HERE/'R586_RENDER_RECEIPT.json').write_text(json.dumps(result,indent=2,allow_nan=False))
print('FINISHED',out,'bytes',out.stat().st_size,'SHA',result['nativeGIF_SHA256'],'wall',round(time.monotonic()-started,2),flush=True)
renderer.ren.RemoveAllViewProps();renderer.win.Finalize()
import sys
sys.stdout.flush();os._exit(0)
