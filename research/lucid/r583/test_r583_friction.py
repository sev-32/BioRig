"""R583: native effective-friction, loaded contact-slip and clone regression."""
from __future__ import annotations
import os,unittest
import numpy as np
import mujoco as mj
import r583_friction_probe as r

class FrictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pb,cls.ref,cls.neu,cls.saved=r.r.phy.paired_scene(.131,.82)
    def test_friction_actually_present_in_original_model(self):
        m=self.pb.model
        seat=mj.mj_name2id(m,mj.mjtObj.mjOBJ_GEOM,'research_seat')
        floor=mj.mj_name2id(m,mj.mjtObj.mjOBJ_GEOM,'ground')
        self.assertAlmostEqual(float(m.geom_friction[seat,0]),.82)
        self.assertAlmostEqual(float(m.geom_friction[floor,0]),1.0)
        observed=r.slip_and_forces(m,self.saved)
        self.assertAlmostEqual(observed['research_seat']['muEffectiveMax'],.82)
        self.assertAlmostEqual(observed['ground']['muEffectiveMax'],1.)
    def test_nonzero_contact_shear_and_finite_slip(self):
        g=r.slip_and_forces(self.pb.model,self.saved)
        for s in ('research_seat','ground'):
            self.assertGreater(g[s]['normalN'],100)
            self.assertGreater(g[s]['shearN'],10)
            self.assertGreater(g[s]['contacts'],0)
            self.assertGreater(g[s]['loadedSlipMps'],0)
            self.assertTrue(np.isfinite(g[s]['loadedSlipMps']))
    def test_ice_requires_both_surfaces_to_change(self):
        pb,_,_,saved=r.r.phy.paired_scene(.131,.82)
        r.set_friction(pb.model,'ice')
        d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
        mj.mj_forward(pb.model,d)
        g=r.slip_and_forces(pb.model,d)
        self.assertAlmostEqual(g['research_seat']['muEffectiveMax'],1e-5)
        self.assertAlmostEqual(g['ground']['muEffectiveMax'],1e-5)
    def test_high_grip_effective_friction(self):
        pb,_,_,saved=r.r.phy.paired_scene(.131,.82)
        r.set_friction(pb.model,'high_grip')
        d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
        mj.mj_forward(pb.model,d)
        g=r.slip_and_forces(pb.model,d)
        self.assertAlmostEqual(g['research_seat']['muEffectiveMax'],2.)
        self.assertAlmostEqual(g['ground']['muEffectiveMax'],2.)
    def test_pure_observer_does_not_mutate_physics(self):
        h=r.r.phy.plant.sha_state(self.saved)
        for i in range(3):r.slip_and_forces(self.pb.model,self.saved)
        self.assertEqual(r.r.phy.plant.sha_state(self.saved),h)
    @unittest.skipUnless(os.environ.get('R583_NATIVE')=='1','optional 12s native high-grip replay')
    def test_12s_high_grip_physics(self):
        result,_=r.run('high_grip',12,render=False)
        self.assertAlmostEqual(result['endX_m'],.01766636539569495,places=6)
        self.assertLess(result['peakTiltDeg'],45.)
        self.assertEqual(result['initSHA'],'3baf94ca375e535d72bacccdee2c43141e7d2a3a156539257274de1862339c24')
if __name__=='__main__':unittest.main()
