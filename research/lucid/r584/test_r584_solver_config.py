"""Standalone R584 solver physics contract and optional native replay."""
from __future__ import annotations
import os,unittest
from pathlib import Path
import numpy as np
import mujoco as mj
from r584_solver_config import configure,material_digest
from r584_replay import replay,legacy

class TestNoSlipConfiguration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pb,cls.ref,cls.neutral,cls.saved=legacy.r.phy.paired_scene(.131,.82)
    def test_only_solver_option_changes(self):
        m=self.pb.model
        initial=material_digest(m)
        self.assertEqual(m.opt.noslip_iterations,0)
        result=configure(m,6)
        self.assertEqual(result['noSlipIterations'],6)
        self.assertEqual(result['materialAndMassSHA256'],initial)
        self.assertEqual(material_digest(m),initial)
    def test_contact_material_is_original(self):
        pb,_,_,_=legacy.r.phy.paired_scene(.131,.82)
        configure(pb.model)
        for name,mu in [('research_seat',.82),('ground',1.)]:
            i=mj.mj_name2id(pb.model,mj.mjtObj.mjOBJ_GEOM,name)
            self.assertAlmostEqual(pb.model.geom_friction[i,0],mu)
    def test_bad_iterations_are_rejected(self):
        pb,_,_,_=legacy.r.phy.paired_scene(.131,.82)
        for bad in (-1,100,1.1,'six'):
            with self.assertRaises(ValueError):configure(pb.model,bad)
        for bad in (0.,-1.,float('nan')):
            with self.assertRaises(ValueError):configure(pb.model,6,bad)
    @unittest.skipUnless(os.getenv('R584_NATIVE')=='1','explicit native 12s replay')
    def test_native_12s_contact_slip(self):
        previous=legacy.set_friction
        result,_=replay(12.,6,False)
        self.assertIs(legacy.set_friction,previous)
        self.assertAlmostEqual(result['endX_m'],.0158217622165869,places=6)
        self.assertLess(result['trace'][-1]['contacts']['research_seat']['loadedSlipMps'],1e-4)
        self.assertLess(result['trace'][-1]['contacts']['ground']['loadedSlipMps'],2e-4)
if __name__=='__main__':unittest.main()
