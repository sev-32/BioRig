#!/usr/bin/env python3
"""Genuine MuJoCo R584 paired states rendered with ORIGINAL canonical Skin78.
No fabricated poses, no motion interpolation, no replaced mesh/weights.
"""
from pathlib import Path
import sys,hashlib,json,time,os
HERE=Path(__file__).resolve().parent
PROJECT=next((p for p in (HERE,*HERE.parents)
              if (p/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG').is_dir()),None)
if PROJECT is None:
    raise RuntimeError('Restore original frozen R574 archive to repository-root runtime/ first')
sys.path[:0]=[str(HERE.parent/'r582'),str(HERE.parent/'r580'),
    str(HERE.parent/'r577'),str(HERE.parent/'r576'),
    str(PROJECT/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG')]
import mujoco as mj,numpy as np,vtk
from PIL import Image,ImageDraw,ImageFont
from lucid_bcr.pipeline import CausalRig,RigConfig
from lucid_bcr.render import Renderer
import r582_controller as control

FRAME_STEPS=150
SIMULATION_STEPS=6000
EXPECTED_SKIN_SHA='88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10'
EXPECTED_INITIAL_SHA='3baf94ca375e535d72bacccdee2c43141e7d2a3a156539257274de1862339c24'

def add_real_seat(renderer,pb):
    sid=mj.mj_name2id(pb.model,mj.mjtObj.mjOBJ_GEOM,'research_seat')
    c=pb.data.geom_xpos[sid];a=pb.model.geom_size[sid]
    box=vtk.vtkCubeSource()
    box.SetCenter(*[float(v) for v in c])
    box.SetXLength(float(a[0]*2));box.SetYLength(float(a[1]*2))
    box.SetZLength(float(a[2]*2))
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(box.GetOutputPort())
    actor=vtk.vtkActor();actor.SetMapper(mapper)
    actor.GetProperty().SetColor(.24,.46,.57)
    actor.GetProperty().SetOpacity(.62)
    actor.GetProperty().SetSpecular(.28)
    renderer.ren.AddActor(actor)
    return actor

def skin_image(rig,renderer,pb,data):
    commands,hand,placement=pb.read_state(qpos=data.qpos)
    pose=rig.comp.compile(commands,extra_local=rig.art.hand.local_rotations(hand),
        placement=placement,validate=False)
    verts,_=rig._deform(pose)
    assert np.isfinite(verts).all()
    return renderer.render(verts,view='threequarter',scale=1.)

def capture_condition(name,iterations,rig,renderer):
    pb,ref,neutral,saved=control.phy.paired_scene(.131,.82)
    initial=control.phy.plant.sha_state(pb.data)
    assert initial==EXPECTED_INITIAL_SHA
    model=pb.model
    assert model.opt.noslip_iterations==0
    digestBefore=hashlib.sha256(
        np.concatenate([model.geom_friction.ravel(),model.geom_solref.ravel(),
            model.geom_solimp.ravel(),model.geom_size.ravel(),model.body_mass.ravel()]).tobytes()).hexdigest()
    model.opt.noslip_iterations=iterations
    model.opt.noslip_tolerance=1e-6
    digestAfter=hashlib.sha256(
        np.concatenate([model.geom_friction.ravel(),model.geom_solref.ravel(),
            model.geom_solimp.ravel(),model.geom_size.ravel(),model.body_mass.ravel()]).tobytes()).hexdigest()
    assert digestBefore==digestAfter
    d=mj.MjData(model);mj.mj_copyData(d,model,saved);mj.mj_forward(model,d)
    seat=add_real_seat(renderer,pb)
    frames=[];states=[]
    extra=np.zeros(model.nu)
    for k in range(SIMULATION_STEPS+1):
        t=k*control.DT
        if k%FRAME_STEPS==0 or k==SIMULATION_STEPS:
            im=skin_image(rig,renderer,pb,d)
            obs=control.phy.sense(pb,d)
            frames.append(im)
            states.append({'tS':round(t,3),'rootX_m':float(obs['xPosition']),
                'tiltDeg':float(obs['rootTiltDeg']),
                'seatN':float(obs['pelvisSeatN']),
                'feetN':float(obs['feetFloorN']),
                'stateSHA256':hashlib.sha256(d.qpos.tobytes()).hexdigest()})
        if k==SIMULATION_STEPS:break
        # Inherited low-level stabilizer remains active. No added R582 control.
        control.phy.plant.step_perturbed(pb,d,ref,neutral,extra,np.zeros(3))
    assert initial==control.phy.plant.sha_state(pb.data)
    renderer.ren.RemoveActor(seat)
    return frames,{'startSHA256':initial,'noslip_iterations':iterations,
        'materialSHA256':digestBefore,'states':states}

def run():
    rig=CausalRig(RigConfig(realization='reference',deformation='canonical',
        muscles=False,demand=False,support='none'))
    assert rig.a.skin_sha256==EXPECTED_SKIN_SHA
    renderer=Renderer(width=510,height=610)
    renderer.set_ground(0.,size=2.2,on=True)
    states={};pictures={}
    for name,n in [('ORIGINAL CONTACT',0),('R584 NO-SLIP',6)]:
        pictures[name],states[name]=capture_condition(name,n,rig,renderer)
    assert states['ORIGINAL CONTACT']['startSHA256']==states['R584 NO-SLIP']['startSHA256']
    frameCount=len(pictures['ORIGINAL CONTACT'])
    assert frameCount==len(pictures['R584 NO-SLIP'])==41
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
    bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',17)
    composed=[]
    for k in range(frameCount):
        image=Image.new('RGB',(1040,695),(12,17,24))
        draw=ImageDraw.Draw(image)
        for j,name in enumerate(pictures):
            x=6+j*520;s=states[name]['states'][k]
            draw.text((x+8,8),name,fill='#F1F5FA',font=bold)
            draw.text((x+8,34),
                f"Native {s['tS']:.1f}s / X {s['rootX_m']*1000:.1f} mm / tilt {s['tiltDeg']:.1f} deg",
                fill='#BEE8EC',font=font)
            draw.text((x+8,54),
                f"Seat {s['seatN']:.0f} N / feet {s['feetN']:.0f} N / SKIN78",
                fill='#D5DEEA',font=font)
            image.paste(pictures[name][k],(x,82))
        composed.append(image)
    gif=HERE/'R584_SKIN78_NATIVE_CONTACT_SIDE_BY_SIDE.gif'
    composed[0].save(gif,save_all=True,append_images=composed[1:],
        duration=150,loop=0,optimize=True)
    for k,label in [(0,'START'),(20,'MID'),(len(composed)-1,'END')]:
        composed[k].save(HERE/f'R584_SKIN78_NATIVE_{label}.png')
    receipt={'schema':'biorig.r584.skin78-real-native-frames.v1',
        'mujocoVersion':mj.__version__,'skinSHA256':rig.a.skin_sha256,
        'captureIntervalS':FRAME_STEPS*control.DT,
        'physicalHorizonS':SIMULATION_STEPS*control.DT,'frames':frameCount,
        'noPoseInterpolation':True,'sameFrozenBaselineController':True,
        'onlyContactDifference':'noslip_iterations 0 vs 6',
        'conditions':states,'gifSHA256':hashlib.sha256(gif.read_bytes()).hexdigest()}
    (HERE/'R584_SKIN78_NATIVE_RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
    print('VALID SKIN78 NATIVE CAPTURES:',str(gif),'frames',frameCount,flush=True)
    # Avoid headless VTK teardown hang after all verification/artifacts are written.
    renderer.ren.RemoveAllViewProps()
    renderer.win.Finalize()
    os._exit(0)

if __name__=='__main__':
    run()
