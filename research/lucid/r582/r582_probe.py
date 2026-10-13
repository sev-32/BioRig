"""Native 40s diagnostic: real R581 controller and identical cloned initial state."""
import sys,json,time
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'r581')]
import r581_controller as ref
from r582_wrench import sense_wrench

def probe(horizon=40):
 scene={'seatHalfWidthM':.131,'friction':.82,'forceN':0.,'direction':1.}
 pb,q0,neu,saved=ref.phy.paired_scene(.131,.82)
 d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
 early=ref.phy.TimedPulse(pb.model,'none');ctl=ref.ContactAllocator(pb.model)
 results=[];start=time.monotonic();snapshots={}
 for k in range(round(horizon/ref.DT)+1):
  t=k*ref.DT
  if k%round(1/ref.DT)==0:
   w=sense_wrench(pb.model,d);obs=ref.phy.sense(pb,d)
   r={'t':round(t,3),'rootX':obs['xPosition'],'vx':obs['xSpeed'],'tiltDeg':obs['rootTiltDeg'],
      'comX':w.com_world_m[0],'pressureX':w.pressure_centroid_x_m,
      'reactionEquivalentX':w.projected_reaction_x_at_plane_m,
      'comMinusPressure':w.com_minus_pressure_m,
      'comMinusProjected':w.com_minus_projected_reaction_m,
      'loadY':w.normal_vertical_reaction_N,'shearX':w.total_lateral_shear_N,
      'netTorqueCOMz':w.moment_about_com_world_Nm[2],
      'hipDose':ctl.hip,'obliqueDose':ctl.trunk}
   results.append(r)
   if t==horizon:
    from r581_support import sense_support
    old=sense_support(pb.model,d)
    print('OLD PRESSURE',old,flush=True)
    ext={'research_seat','ground'}
    for j in range(d.ncon):
     c=d.contact[j]
     n1=mj.mj_id2name(pb.model,mj.mjtObj.mjOBJ_GEOM,c.geom1);n2=mj.mj_id2name(pb.model,mj.mjtObj.mjOBJ_GEOM,c.geom2)
     if (n1 in ext)==(n2 in ext):continue
     loc=np.zeros(6);mj.mj_contactForce(pb.model,d,j,loc)
     fr=np.asarray(c.frame).reshape(3,3)
     sg=1 if n1 in ext else -1
     wr=sg*fr.T@loc[:3]
     oldload=max(0.,loc[0])*abs(float(c.frame[1]))
     if oldload>5 or abs(wr[1])>5:
      print('CONTACT',j,n1,n2,'pos',round(float(c.pos[0]),4),'normalY',round(float(c.frame[1]),3),'oldload',round(oldload,3),'forceY',round(float(wr[1]),3),'forceX',round(float(wr[0]),3),flush=True)
   print('R581 native',t,'x',round(r['rootX'],5),'pressuregap',round(r['comMinusPressure'],5),'projectedgap',round(r['comMinusProjected'],5),'shear',round(r['shearX'],2),'walltime',round(time.monotonic()-start,1),flush=True)
   if t in (12,25,35):
    snap=mj.MjData(pb.model);mj.mj_copyData(snap,pb.model,d);snapshots[t]=snap
  if k==round(horizon/ref.DT):break
  if k%round(.04/ref.DT)==0:
   o=ref.phy.sense(pb,d);early.update(t,o);ctl.update(t,o,pb.model,d)
  out=np.clip(early.output()+ctl.output(),0,ref.phy.plant.MAX_EXTRA)
  ref.phy.plant.step_perturbed(pb,d,q0,neu,out,np.zeros(3))
 target=HERE/'R582_R581_NATIVE_WRENCH_40S.json'
 target.write_text(json.dumps({'schema':'lucid.r582.native-signed-contact-wrench.v1','baseline':'unchanged R581', 'nativeMuJoCo':'3.15.0','frames':results},indent=2,allow_nan=False))
 return pb,q0,neu,snapshots,results
if __name__=='__main__':probe()
