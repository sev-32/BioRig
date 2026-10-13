"""R582 independent real-plant and synthetic contact-frame invariance gates."""
from pathlib import Path
import sys,unittest,math
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'r581')]
import r581_controller as ref
from r582_wrench import world_wrench,sense_wrench
class TestSignedWrench(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pb,cls.r,cls.neutral,cls.saved=ref.phy.paired_scene(.131,.82)
  cls.d=mj.MjData(cls.pb.model);mj.mj_copyData(cls.d,cls.pb.model,cls.saved)
 def test_action_reaction_swapped_geom_order(self):
  # Normal originally +X; reversing geom order changes normal and sign.
  w=np.array([10.,3.,-2.,.5,-.25,.75])
  force1,moment1=world_wrench(np.eye(3),w,True)
  flipped=np.diag([-1.,-1.,1.])
  reverse_w=np.array([10.,3.,-2.,.5,-.25,.75])
  # Flipped R creates changed tangent axes; rotate local wrench by flipped
  # and negate for swapped geom to recreate the original world wrench.
  reverse_w[:3]=-(flipped @ force1)
  reverse_w[3:]=-(flipped @ moment1)
  f2,m2=world_wrench(flipped,reverse_w,False)
  np.testing.assert_allclose(force1,f2,atol=1e-12)
  np.testing.assert_allclose(moment1,m2,atol=1e-12)
 def test_rotation_world_wrench(self):
  R=np.array([[0.,1.,0.],[-1.,0.,0.],[0.,0.,1.]])
  local=np.array([4.,5.,6.,1.,2.,3.])
  f,t=world_wrench(R,local,True)
  np.testing.assert_allclose(f,[ -5.,4.,6.])
  np.testing.assert_allclose(t,[-2.,1.,3.])
 def test_unchanged_plant_state(self):
  before=ref.phy.plant.sha_state(self.d)
  for _ in range(5):sense_wrench(self.pb.model,self.d)
  self.assertEqual(ref.phy.plant.sha_state(self.d),before)
 def test_reaction_has_physical_units_and_weight(self):
  w=sense_wrench(self.pb.model,self.d)
  mass=float(sum(self.pb.model.body_mass))
  self.assertTrue(w.valid and w.valid_projection)
  self.assertGreater(w.support_contact_count,10)
  self.assertLess(abs(w.force_on_body_world_N[1]-mass*9.81),.08*mass*9.81)
  self.assertAlmostEqual(w.force_on_body_world_N[1],w.normal_vertical_reaction_N,places=7)
  self.assertAlmostEqual(w.com_minus_pressure_m,w.com_world_m[0]-w.pressure_centroid_x_m,places=12)
  self.assertAlmostEqual(w.com_minus_projected_reaction_m,w.com_world_m[0]-w.projected_reaction_x_at_plane_m,places=12)
 def test_projected_moment_identity(self):
  w=sense_wrench(self.pb.model,self.d)
  f=w.force_on_body_world_N;m=w.moment_about_projection_origin_world_Nm
  self.assertAlmostEqual(w.projected_reaction_x_at_plane_m,m[2]/f[1],places=12)
  # M_z about COM: (x0-COMx)*Fy - (y0-COMy)*Fx + residual torsion.
  self.assertTrue(np.isfinite(w.moment_about_com_world_Nm).all())
 def test_nonzero_projection_height_changes_virtual_point_only(self):
  a=sense_wrench(self.pb.model,self.d,projection_y_m=0.)
  b=sense_wrench(self.pb.model,self.d,projection_y_m=.452)
  self.assertAlmostEqual(a.normal_vertical_reaction_N,b.normal_vertical_reaction_N)
  self.assertAlmostEqual(a.com_world_m[0],b.com_world_m[0])
  self.assertAlmostEqual(b.projected_reaction_x_at_plane_m-a.projected_reaction_x_at_plane_m,
                         .452*a.total_lateral_shear_N/a.force_on_body_world_N[1],places=12)
if __name__=='__main__':unittest.main()
