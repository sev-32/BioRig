#!/usr/bin/env python3
"""Real SKIN78 native R587 against isolated R588 arm collision/passive-damping experiment.
31 captured frames per condition, 0-3 seconds, no interpolation, no pose edit.
"""
import os,sys,time,hashlib,json
from pathlib import Path
import numpy as np, mujoco as mj,vtk
from PIL import Image, ImageDraw,ImageFont
from r588_probe import run
HERE=Path(__file__).resolve().parent
PROJECT=next((p for p in (HERE,*HERE.parents) if (p/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG').is_dir()),None)
if PROJECT is None and os.getenv('BIORIG_WORKSPACE'):PROJECT=Path(os.environ['BIORIG_WORKSPACE'])
if PROJECT is None:PROJECT=Path('/mnt/data/BioRig_SKIN78_BRIDGE')
ROOT=PROJECT/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG'
sys.path.insert(0,str(ROOT))
from lucid_bcr.pipeline import CausalRig,RigConfig
from lucid_bcr.render import Renderer
rig=CausalRig(RigConfig(realization='reference',deformation='canonical',muscles=False,demand=False,support='none'))
assert rig.a.skin_sha256=='88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10'
renderer=Renderer(width=480,height=570);renderer.set_ground(0.,size=2.2,on=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',19)


def build_seat(pb):
    gid=mj.mj_name2id(pb.model,mj.mjtObj.mjOBJ_GEOM,'research_seat')
    c=pb.data.geom_xpos[gid];dims=pb.model.geom_size[gid]
    box=vtk.vtkCubeSource();box.SetCenter(*map(float,c));box.SetXLength(float(dims[0]*2));box.SetYLength(float(dims[1]*2));box.SetZLength(float(dims[2]*2))
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(box.GetOutputPort());actor=vtk.vtkActor();actor.SetMapper(mapper)
    actor.GetProperty().SetColor(.22,.43,.51);actor.GetProperty().SetOpacity(.62)
    renderer.ren.AddActor(actor);return actor

frames={};snapshots={};receipts={}
for label,kw in [('R587 BASELINE',{}),('R588 CANDIDATE',{'thumb_time':.05,'thumb_damping':2.,'limb_damping_mult':10.})]:
    pictures=[];measured=[];seat=[None]
    def capture(pb,d,t,arms):
        if seat[0] is None:seat[0]=build_seat(pb)
        commands,hand,placement=pb.read_state(qpos=d.qpos)
        pose=rig.comp.compile(commands,extra_local=rig.art.hand.local_rotations(hand),placement=placement,validate=False)
        verts,_=rig._deform(pose)
        assert np.isfinite(verts).all()
        img=renderer.render(verts,view='threequarter',scale=1.)
        pictures.append(img)
        measured.append({'tS':round(t,3),'leftArmSeatN':arms['left']['contactN'],'rightArmSeatN':arms['right']['contactN'],
            'leftBodyContacts':arms['left']['geoms'],'rightBodyContacts':arms['right']['geoms'],
            'headDeg':float(np.degrees(np.arccos(np.clip((np.trace(d.xmat[pb.body_id['Spine02']].reshape(3,3).T @ d.xmat[pb.body_id['Head']].reshape(3,3))-1)*.5,-1,1))))})
    tic=time.monotonic();report=run(3.,on_frame=capture,**kw)
    print('RENDERED',label,len(pictures),'wall',round(time.monotonic()-tic,1),flush=True)
    renderer.ren.RemoveActor(seat[0]);frames[label]=pictures;snapshots[label]=measured;receipts[label]=report
assert all(len(x)==31 for x in frames.values())
result=[]
for i in range(31):
    im=Image.new('RGB',(990,685),(12,17,24));d=ImageDraw.Draw(im)
    for j,name in enumerate(frames):
        x=j*495;m=snapshots[name][i]
        d.text((x+10,8),name,fill=(233,244,251),font=bold)
        d.text((x+10,33),f"t {m['tS']:.1f}s | RIGHT arm seat {m['rightArmSeatN']:.1f} N",fill=(167,230,225),font=font)
        d.text((x+10,54),f"LEFT arm seat {m['leftArmSeatN']:.1f} N | head {m['headDeg']:.2f} deg",fill=(202,212,228),font=font)
        im.paste(frames[name][i],(x+7,88))
    result.append(im)
p=HERE/'R588_SKIN78_ARM_CONTACT_BEFORE_AFTER.gif'
result[0].save(p,save_all=True,append_images=result[1:],duration=115,loop=0,optimize=True)
for i in [0,2,3,4,5,6,8,12,20,30]:result[i].save(HERE/f'R588_SKIN78_FRAME_{i:02}.png')
(HERE/'R588_RENDER_RECEIPT.json').write_text(json.dumps({'skinSHA256':rig.a.skin_sha256,'framesEach':31,
    'realWorldMuJoCo':True,'noArtOrPoseInterpolation':True,'readings':snapshots,
    'config':{'limbDampingMult':10,'thumbCollisionSolref':[.05,2.]},
    'gifSHA256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2))
print('ANIMATION DONE',p,'bytes',p.stat().st_size,'SHA',hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
renderer.ren.RemoveAllViewProps();renderer.win.Finalize();sys.stdout.flush();os._exit(0)
