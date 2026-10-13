"""Real Skin78 native MuJoCo head-repair proof; 31 continuous physical captures per condition."""
import os,sys,json,hashlib,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path(os.environ['BIORIG_WORKSPACE']) if os.environ.get('BIORIG_WORKSPACE') else next((p for p in (HERE,*HERE.parents) if (p/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG').is_dir()),None)
if ROOT is None:raise RuntimeError('Restore original R574 runtime or set BIORIG_WORKSPACE')
sys.path[:0]=[str(Path(__file__).resolve().parent),str(ROOT/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG')]
import numpy as np,mujoco as mj,vtk
from PIL import Image,ImageDraw,ImageFont
from lucid_bcr.pipeline import CausalRig,RigConfig
from lucid_bcr.render import Renderer
from r585_neck_repair import run
OUT=HERE
T0=time.monotonic()
rig=CausalRig(RigConfig(realization='reference',deformation='canonical',muscles=False,demand=False,support='none'))
renderer=Renderer(width=500,height=610)
renderer.set_ground(0.,size=2.2,on=True)
print('SKIN78 canonical',rig.a.nv,rig.a.skin_sha256,flush=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',17)

def make_seat(pb):
 sid=mj.mj_name2id(pb.model,mj.mjtObj.mjOBJ_GEOM,'research_seat')
 center=pb.data.geom_xpos[sid];a=pb.model.geom_size[sid]
 box=vtk.vtkCubeSource();box.SetCenter(*map(float,center))
 box.SetXLength(float(a[0]*2));box.SetYLength(float(a[1]*2));box.SetZLength(float(a[2]*2))
 mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(box.GetOutputPort())
 actor=vtk.vtkActor();actor.SetMapper(mapper)
 actor.GetProperty().SetColor(.22,.43,.51);actor.GetProperty().SetOpacity(.65)
 renderer.ren.AddActor(actor)
 return actor

pictures={};meta={}
for label,modified in [('ORIGINAL NECK',False),('R585 PHYSICAL REPAIR',True)]:
 images=[];states=[];seat=[None]
 def frame(pb,d,s):
  if seat[0] is None:seat[0]=make_seat(pb)
  cmds,hand,place=pb.read_state(qpos=d.qpos)
  pose=rig.comp.compile(cmds,extra_local=rig.art.hand.local_rotations(hand),placement=place,validate=False)
  verts,_=rig._deform(pose)
  assert np.isfinite(verts).all()
  im=renderer.render(verts,view='threequarter',scale=1.)
  images.append(im)
  o=s.copy();o['qposSHA256']=hashlib.sha256(d.qpos.tobytes()).hexdigest()
  states.append(o)
  if len(images)%10==0:print('CAPTURE',label,len(images),s['tS'],round(s['headThoraxDeg'],2),'wall',round(time.monotonic()-T0,2),flush=True)
 result=run(dict(kp=.5,kd=.5,regular=.1),secs=12,change_geometry=modified,on_frame=frame,baseline=not modified)
 assert len(images)==31,(label,len(images))
 assert all(np.isfinite(p['headThoraxDeg']) for p in states)
 if modified:assert result['maxAngleDeg'] < 6.0, result['maxAngleDeg']
 renderer.ren.RemoveActor(seat[0])
 pictures[label]=images
 meta[label]={'state':states,'headMaxDeg':result['maxAngleDeg'],'finalHeadDeg':result['lastAngleDeg'],'geomSCMvariant':modified}
 print('FINISHED',label,result['maxAngleDeg'],len(images),'time',time.monotonic()-T0,flush=True)

# Compose matching physical-state capture, not interpolated frames.
combined=[]
for i in range(31):
 panel=Image.new('RGB',(1020,705),(11,16,23));d=ImageDraw.Draw(panel)
 for j,(label,pics) in enumerate(pictures.items()):
  x=10+510*j;state=meta[label]['state'][i]
  d.text((x+8,8),label,fill=(235,242,247),font=bold)
  d.text((x+8,33),f"Native {state['tS']:.1f}s | head-torso {state['headThoraxDeg']:.2f} deg",fill=(164,223,228),font=font)
  d.text((x+8,55),f"pelvis x {state['pelvisX_m']*1000:.1f} mm | original SKIN78",fill=(187,201,218),font=font)
  panel.paste(pics[i],(x,90))
 combined.append(panel)
anim=OUT/'R585_REAL_SKIN78_NECK_REPAIR_12S.gif'
combined[0].save(anim,save_all=True,append_images=combined[1:],duration=160,loop=0,optimize=True)
for i,name in [(0,'START'),(10,'4S'),(20,'8S'),(30,'END')]:
 combined[i].save(OUT/f'R585_SKIN78_{name}.png')
receipt={'schema':'lucid.r585.real-mujoco-skin78.v1','durationS':12,'framesPerCondition':31,'dtCaptureS':.4,
  'mujocoVersion':mj.__version__,'skinSHA256':rig.a.skin_sha256,
  'nativePhysicalStateForEveryFrame':True,'noInterpolationOrGeneratedFrames':True,
  'actualHeadToTorsoAngles':meta,
  'artifact':anim.name,'sha256':hashlib.sha256(anim.read_bytes()).hexdigest()}
(OUT/'R585_SKIN78_NATIVE_RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
print('FINISHED ANIMATION',anim,anim.stat().st_size,receipt['sha256'],flush=True)
renderer.ren.RemoveAllViewProps();renderer.win.Finalize();sys.stdout.flush()
os._exit(0)
