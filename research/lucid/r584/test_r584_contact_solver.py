"""R584 no-slip contact physics acceptance gates; no GitHub Actions."""
from __future__ import annotations
import os,unittest
import numpy as np
import mujoco as mj
import r584_contact_solver as r

class TestContactSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene=r.SCENES['undisturbed']
    def test_frozen_material_and_inertial_geometry_untouched(self):
        original,*_=r.setup(self.scene,0)
        corrected,*_=r.setup(self.scene,6)
        self.assertEqual(r.contact_material_fingerprint(original.model),r.contact_material_fingerprint(corrected.model))
        self.assertEqual(original.model.opt.noslip_iterations,0)
        self.assertEqual(corrected.model.opt.noslip_iterations,6)
        self.assertEqual(original.model.ngeom,corrected.model.ngeom)
        self.assertEqual(original.model.nu,84)
        for geom,expected in (('research_seat',.82),('ground',1.)):
            i=mj.mj_name2id(corrected.model,mj.mjtObj.mjOBJ_GEOM,geom)
            self.assertAlmostEqual(corrected.model.geom_friction[i,0],expected)
    def test_seeded_initial_clone(self):
        pb0,ref,n,d0,sha0,fingerprint=r.setup(self.scene,0)
        pb6,ref,n,d6,sha6,fingerprint6=r.setup(self.scene,6)
        self.assertEqual(sha0,sha6)
        self.assertEqual(fingerprint,fingerprint6)
        self.assertTrue(np.array_equal(d0.qpos,d6.qpos))
        self.assertTrue(np.array_equal(d0.qvel,d6.qvel))
    def test_invalid_solver_iteration(self):
        with self.assertRaises(AssertionError):r.setup(self.scene,-1)
        with self.assertRaises(AssertionError):r.setup(self.scene,100)
    @unittest.skipUnless(os.getenv('R584_NATIVE')=='1','requires explicit real MuJoCo runtime')
    def test_native_12s_slip_reduction(self):
        base,_=r.experiment(self.scene,12,0)
        fixed,_=r.experiment(self.scene,12,6)
        self.assertEqual(base['initialSHA256'],fixed['initialSHA256'])
        self.assertEqual(base['materialSHA256'],fixed['materialSHA256'])
        self.assertFalse(fixed['hazard'])
        self.assertTrue(fixed['settledAtEnd'])
        self.assertLess(fixed['finalX_m'],base['finalX_m'])
        self.assertLess(fixed['trace'][-1]['seatSlip_mps'],base['trace'][-1]['seatSlip_mps']*.02)
        self.assertLess(fixed['trace'][-1]['footSlip_mps'],base['trace'][-1]['footSlip_mps']*.05)
        self.assertAlmostEqual(fixed['finalX_m'],.0158217622165869,places=6)
    @unittest.skipUnless(os.getenv('R584_NATIVE')=='1','requires explicit real MuJoCo runtime')
    def test_native_pushed_scene04(self):
        _,_,lock=r.control.inherited.r577.baseline.frozen.frozen()
        scene=r.control.inherited.r577.baseline.frozen.scenarios(lock)[4]
        fixed,_=r.experiment(scene,12,6,early_choice='R28')
        self.assertFalse(fixed['hazard'])
        self.assertTrue(fixed['settledAtEnd'])
        self.assertAlmostEqual(fixed['finalX_m'],.014303984811247346,places=6)
    @unittest.skipUnless(os.getenv('R584_LONG')=='1','requires explicit real 40s MuJoCo runtime')
    def test_native_40s_no_additional_corrective_muscle(self):
        fixed,_=r.experiment(self.scene,40,6,extra_control=False)
        self.assertFalse(fixed['hazard'])
        self.assertTrue(fixed['settledAtEnd'])
        self.assertEqual(fixed['muscleChannelExcitationSeconds'],0.)
        self.assertAlmostEqual(fixed['finalX_m'],.01599346793540552,places=6)
if __name__=='__main__':unittest.main()
