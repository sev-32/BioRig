"""R585 experimental physically bounded six-DOF muscle allocation. Frozen plant untouched.
No coordinate clamp, joint/root torque injection, or externally applied hold.
"""
import sys,math,json,time,os,hashlib
from pathlib import Path
import numpy as np,mujoco as mj
from scipy.optimize import lsq_linear
HERE=Path(__file__).resolve().parent
R=Path(os.environ['BIORIG_WORKSPACE']) if os.environ.get('BIORIG_WORKSPACE') else next((p for p in (HERE,*HERE.parents) if (p/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG').is_dir()), None)
if R is None:raise RuntimeError('Restore original frozen archive to ./runtime or set BIORIG_WORKSPACE')
sys.path[:0]=[str(R/'runtime/LUCID_R552_WORKSPACE/R551_ACTIVE_RECOVERY'),str(R/'runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG'),str(R/'runtime/LUCID_R552_WORKSPACE/R543_MULTICONTACT_LEARNING')]
import run_r551 as core,run_r543 as prior
from lucid_bcr.contact_flight_r46 import muscle_moment_matrix
from lucid_bcr.posture_stabilization_r51 import controller_excitation
from lucid_bcr.contact_grounded_r48 import loaded_support_target
NAMES=('neck.flexionExtension','neck.lateralBend','neck.axialRotation','head.nod','head.tilt','head.turn')
FAMILIES=('neck_extensors','suboccipitals','sternocleidomastoid','longus_colli','upper_trapezius')

def angle(pb,d):
 a=d.xmat[pb.body_id['Head']].reshape(3,3);b=d.xmat[pb.body_id['Spine02']].reshape(3,3)
 return float(np.degrees(np.arccos(np.clip((np.trace(b.T@a)-1)*.5,-1,1))))

class NeckAllocator:
 def __init__(self,pb,kp=1,kd=1,regular=.2,gain_scale=1.,max_activation=.8):
  m=pb.model;self.pb=pb;self.kp=kp;self.kd=kd;self.regular=regular;self.gain_scale=gain_scale;self.max_activation=max_activation
  self.dof=np.asarray([pb.hinge_dadr[n] for n in NAMES],dtype=int)
  self.qadr=np.asarray([pb.hinge_qadr[n] for n in NAMES],dtype=int)
  self.ids=np.asarray([mj.mj_name2id(m,mj.mjtObj.mjOBJ_ACTUATOR,'m_'+side+'_'+fam) for side in ('left','right') for fam in FAMILIES],dtype=int)
  assert min(self.ids)>=0
  self.last=np.full(len(self.ids),.1)
  self.history=[]
 def update(self,d,base):
  m=self.pb.model
  moment=muscle_moment_matrix(d,m.nu,m.nv)
  q=d.qpos[self.qadr];v=d.qvel[self.dof]
  kp=np.asarray([34,26,10,22,16,9])*self.kp
  kd=np.asarray([8,5,2,4,3,1.5])*self.kd
  # Current bias includes gravity & Coriolis; passive already supplies restorative joint torques.
  demand=d.qfrc_bias[self.dof]-d.qfrc_passive[self.dof]-kp*q-kd*v
  # All unmodified actuators supply native forces; do not override them.
  other=np.setdiff1d(np.arange(m.nu),self.ids)
  demand-=moment[other,:][:,self.dof].T@d.actuator_force[other]
  strength=np.asarray([mj.mju_muscleGain(d.actuator_length[i],d.actuator_velocity[i],m.actuator_lengthrange[i],m.actuator_acc0[i],m.actuator_gainprm[i,:9]) for i in self.ids])
  matrix=moment[self.ids,:][:,self.dof].T*strength[None,:]
  # Torque channels normalized to balance gains in N m.
  scales=np.asarray([8.,6.,3.,9.,4.,2.5])
  a=matrix/scales[:,None];b=demand/scales
  k=self.regular
  AA=np.vstack([a,np.sqrt(k)*np.eye(len(self.ids))])
  bb=np.concatenate([b,np.sqrt(k)*self.last])
  fit=lsq_linear(AA,bb,bounds=(0.,self.max_activation),method='bvls',tol=1e-7,max_iter=50)
  target=fit.x
  self.last=target
  # Controller excitation used for just those anatomical muscles; normal low-level remains unchanged elsewhere.
  return target,{'angle':angle(self.pb,d),'demand':demand.tolist(),'realisableTorque':(matrix@target).tolist(), 'residual':float(np.linalg.norm(a@target-b)), 'q':q.tolist()}

def run(cfg,secs=4,change_geometry=False,save=False,on_frame=None,baseline=False,push_N=0.,push_onset_s=.8):
 pb=prior.make_body('seated');m=pb.model
 if change_geometry:
  for side in ('left','right'):
   sid=mj.mj_name2id(m,mj.mjtObj.mjOBJ_SITE,f's_{side}_sternocleidomastoid_1')
   m.site_pos[sid,2]=-.025
 pb.model.opt.noslip_iterations=6;pb.model.opt.noslip_tolerance=1e-6
 qref=prior.reset(pb);d=pb.data
 neutral=(d.xpos[pb.body_id['Head']]-d.xpos[pb.body_id['Hip']])[[0,2]].copy()
 ctl=NeckAllocator(pb,**cfg)
 hinges=np.array(sorted(pb.hinge_dadr.values()),int)
 samples=[];allctrl=[];dt=m.opt.timestep
 command=np.zeros(len(ctl.ids))
 for tstep in range(round(secs/dt)+1):
  t=tstep*dt
  if tstep%50==0 or tstep==round(secs/dt):
   sample={'tS':round(t,3),'headThoraxDeg':angle(pb,d),'neck_deg':np.rad2deg(d.qpos[ctl.qadr]).tolist(), 'neck_vel_deg_s':np.rad2deg(d.qvel[ctl.dof]).tolist(), 'pelvisX_m':float(d.qpos[0]),'headExcitation':command.tolist(),'timeS':t, 'pelvisTiltDeg':core.root_tilt_deg(pb,d), 'contactLoads':core.contact_for(pb,d)}
   samples.append(sample)
  if on_frame is not None and (tstep%200==0 or tstep==round(secs/dt)):
   on_frame(pb,d,sample)
  if tstep==round(secs/dt):break
  difference=np.zeros(m.nv);mj.mj_differentiatePos(m,difference,1.,d.qpos,qref)
  wanted=np.zeros(m.nv);wanted[hinges]=np.clip(10*difference[hinges]-.8*d.qvel[hinges],-8.,8.)
  pts,n=core.foot_for_data(pb,d)
  support=loaded_support_target(d.subtree_com[pb.body_id['Hip']].copy(),pts,n)
  base=controller_excitation(muscle_moment_matrix(d,m.nu,m.nv),wanted,m,d,pb,neutral,'upright_com',support)
  if not baseline and tstep%5==0:
   command,diag=ctl.update(d,base)
   allctrl.append({'tS':t,'residual':diag['residual']})
  d.ctrl[:]=base
  if not baseline:d.ctrl[ctl.ids]=command
  d.qfrc_applied[:]=core.passive_end_for_data(pb,d);d.xfrc_applied[:]=0.
  if push_onset_s <= t < push_onset_s+.12:
   d.xfrc_applied[pb.body_id['Hip'],0]=push_N
  mj.mj_step(m,d)
 maxangle=max(s['headThoraxDeg'] for s in samples)
 out={'cfg':cfg,'geometryVariant':change_geometry,'pushN':push_N,'maxAngleDeg':maxangle, 'maxArmN':max(x['contactLoads']['seatArmsN'] for x in samples), 'maxOtherFloorN':max(x['contactLoads']['floorOtherN'] for x in samples), 'maxPelvisTiltDeg':max(x['pelvisTiltDeg'] for x in samples),'lastAngleDeg':samples[-1]['headThoraxDeg'],'samples':samples,'controls':allctrl}
 return out

if __name__=='__main__':
 configs=[('baseline_inverse',dict(kp=.5,kd=.5,regular=.1)),('weak',dict(kp=1,kd=.6,regular=.2)),('strong',dict(kp=1.8,kd=1.2,regular=.2)),('damped',dict(kp=1,kd=2,regular=.15)),('lowcost',dict(kp=1,kd=1,regular=2))]
 out={}
 for geom in [False,True]:
  for name,cfg in configs:
   tick=time.monotonic()
   got=run(cfg,4,change_geometry=geom)
   out[f'{name}_geom{geom}']=got
   print(name,'geom',geom,'MAX',round(got['maxAngleDeg'],1),'last',round(got['lastAngleDeg'],1),'wall',round(time.monotonic()-tick,1))
 Path('/mnt/data/BioRig_R585_REPAIR/neck_allocator_results.json').write_text(json.dumps(out,indent=2))
