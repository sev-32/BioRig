"""R581 observer/allocator structural gates and optional native physical replay."""
import os,sys,unittest
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r581_controller as c
import r581_moment_probe as p
from r581_support import sense_support

class TestR581(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.pb,cls.ref,cls.neutral,cls.saved=c.phy.paired_scene(.131,.82)
 def state(self):
    return c.phy.sense(self.pb,self.pb.data)
 def test_observer_has_valid_units_and_named_external_support(self):
    s=sense_support(self.pb.model,self.pb.data)
    self.assertTrue(s.valid)
    self.assertGreater(s.normalVertical_N,200.)
    self.assertTrue(np.isfinite([s.comX_m,s.copX_m,s.comMinusCop_m]).all())
    self.assertAlmostEqual(s.comMinusCop_m,s.comX_m-s.copX_m,places=12)
    self.assertLessEqual(s.contactMinX_m,s.contactMaxX_m)
 def test_observer_never_mutates_plant(self):
    digest=c.phy.plant.sha_state(self.pb.data)
    for _ in range(3):sense_support(self.pb.model,self.pb.data)
    self.assertEqual(c.phy.plant.sha_state(self.pb.data),digest)
 def test_named_joint_mechanics_are_sparse_and_nontrivial(self):
    d=self.pb.data
    snap=p.moment_snapshot(self.pb,d)
    hip=snap['left_hip_medius'][0]
    oblique=snap['left_external_oblique'][0]
    self.assertLess(hip['momentArmAtState_m']['leftHip.abductionAdduction'],0)
    self.assertEqual(hip['momentArmAtState_m']['spine01.lateralBend'],0)
    self.assertLess(oblique['momentArmAtState_m']['spine01.lateralBend'],0)
    self.assertEqual(oblique['momentArmAtState_m']['leftHip.abductionAdduction'],0)
 def test_separate_hip_and_trunk_actuation_bounded(self):
    a=c.ContactAllocator(self.pb.model)
    o={**self.state(),'xPosition':.033,'xSpeed':.005,'armsSeatN':0.,'rootTiltDeg':12.}
    for k in range(20):a.update(2.+k*.04,o,self.pb.model,self.pb.data)
    self.assertLessEqual(a.hip,c.CONFIG['hipMax'])
    self.assertLessEqual(a.trunk,c.CONFIG['obliqueMax'])
    self.assertEqual(np.count_nonzero(a.output()),2)
    self.assertGreater(a.output()[a.channels['left']['hip']],0)
    self.assertGreater(a.output()[a.channels['left']['trunk']],0)
 def test_anti_side_mirror_no_crossactivation(self):
    a=c.ContactAllocator(self.pb.model)
    o={**self.state(),'xPosition':-.033,'xSpeed':-.005,'armsSeatN':0.,'rootTiltDeg':12.}
    for k in range(12):a.update(2.+k*.04,o,self.pb.model,self.pb.data)
    self.assertEqual(a.output()[a.channels['left']['hip']],0.)
    self.assertGreater(a.output()[a.channels['right']['hip']],0.)
 def test_contact_safety_abort(self):
    a=c.ContactAllocator(self.pb.model)
    o={**self.state(),'xPosition':.032,'xSpeed':.002,'armsSeatN':0.,'rootTiltDeg':12.}
    for k in range(20):a.update(2.+k*.04,o,self.pb.model,self.pb.data)
    self.assertGreater(a.hip,0.)
    for k in range(20):a.update(3.+k*.04,{**o,'armsSeatN':16.},self.pb.model,self.pb.data)
    self.assertTrue(np.allclose(a.output(),0))
    self.assertGreater(a.abortUpdates,0)
 def test_configuration_and_action_limits(self):
    with self.assertRaises(AssertionError):c.ContactAllocator(self.pb.model,{'hipMax':.2})
    with self.assertRaises(AssertionError):c.ContactAllocator(self.pb.model,{'obliqueMax':.2})
    with self.assertRaises(ValueError):c.rollout({},'illegal_choice')
 @unittest.skipUnless(os.environ.get('R581_NATIVE')=='1','enable native MuJoCo 12s replay')
 def test_native_scene04_pushed_recovery(self):
    _,_,lock=c.inherited.r577.baseline.frozen.frozen()
    sc=c.inherited.r577.baseline.frozen.scenarios(lock)[4]
    d=c.rollout(sc,'R28',seconds=12.,trace_step_s=1.)
    self.assertTrue(d['complete']);self.assertFalse(d['hazard']);self.assertTrue(d['settledAtEnd'])
    self.assertAlmostEqual(d['finalRootX_m'],.024352956629376664,places=6)
if __name__=='__main__':unittest.main()
