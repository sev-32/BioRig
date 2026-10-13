"""R585 native validation: physical muscle moment authority, neck and full skin gates."""
import os,sys,unittest
from pathlib import Path
import numpy as np,mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r585_neck_repair as r

CONFIG=dict(kp=.5,kd=.5,regular=.1)

class R585Physical(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pb=r.prior.make_body('seated')
  r.prior.reset(cls.pb)
 def test_original_has_no_positive_nod_muscle_torque(self):
  m=self.pb.model;d=self.pb.data
  mom=r.muscle_moment_matrix(d,m.nu,m.nv)
  nod=self.pb.hinge_dadr['head.nod']
  self.assertEqual(int(np.sum(mom[:,nod] < -1e-5)),0)
 def test_scm_repair_restores_head_nod_antagonism(self):
  m=self.pb.model;d=self.pb.data
  sites=[]
  for side in ('left','right'):
   i=mj.mj_name2id(m,mj.mjtObj.mjOBJ_SITE,f's_{side}_sternocleidomastoid_1')
   sites.append(i)
  original=m.site_pos[sites].copy()
  try:
   for i in sites:m.site_pos[i,2]=-.025
   mj.mj_forward(m,d)
   mom=r.muscle_moment_matrix(d,m.nu,m.nv)
   nod=self.pb.hinge_dadr['head.nod']
   for side in ('left','right'):
    i=mj.mj_name2id(m,mj.mjtObj.mjOBJ_ACTUATOR,f'm_{side}_sternocleidomastoid')
    self.assertLess(mom[i,nod],-.005)
   self.assertEqual(m.nu,84)
  finally:
   m.site_pos[sites]=original
   mj.mj_forward(m,d)
 def test_no_root_actuators_or_applied_force(self):
  m=self.pb.model
  self.assertTrue(all(int(v)>=6 for v in self.pb.hinge_dadr.values()))
  self.assertEqual(m.nu,84)
 def test_original_fails_whole_body_visual_gate_at_4s(self):
  bad=r.run(CONFIG,secs=4,change_geometry=False,baseline=True)
  self.assertGreater(bad['maxAngleDeg'],70)
 def test_repaired_head_4s_physics(self):
  fixed=r.run(CONFIG,secs=4,change_geometry=True)
  self.assertLess(fixed['maxAngleDeg'],5)
  self.assertLess(fixed['lastAngleDeg'],.25)
  self.assertLess(fixed['maxArmN'],50)
  self.assertLess(fixed['maxOtherFloorN'],50)
 @unittest.skipUnless(os.getenv('R585_NATIVE_12S')=='1','optional long native physical replay')
 def test_repaired_head_12s_physics(self):
  fixed=r.run(CONFIG,secs=12,change_geometry=True)
  self.assertLess(fixed['maxAngleDeg'],5)
  self.assertLess(fixed['lastAngleDeg'],.1)
  self.assertLess(fixed['maxArmN'],50)
  self.assertLess(fixed['maxOtherFloorN'],50)
  self.assertLess(fixed['maxPelvisTiltDeg'],45)
 @unittest.skipUnless(os.getenv('R585_NATIVE_PUSH')=='1','optional pushed native physical replay')
 def test_repaired_head_120n_push(self):
  fixed=r.run(CONFIG,secs=12,change_geometry=True,push_N=120)
  self.assertLess(fixed['maxAngleDeg'],5)
  self.assertLess(fixed['maxArmN'],50)
  self.assertLess(fixed['maxOtherFloorN'],50)

if __name__=='__main__':unittest.main()
