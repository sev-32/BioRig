"""R582 bounded online allocator and native MuJoCo regression gates; no CI needed."""
import os,sys,unittest,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'r581')]
import r582_controller as r
from r582_wrench import sense_wrench

class TestR582Controller(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pb,cls.ref,cls.neutral,cls.saved=r.phy.paired_scene(.131,.82)
 def obs(self):
  return {**r.phy.sense(self.pb,self.pb.data), 'xPosition':.031,
          'xSpeed':.003,'rootTiltDeg':12.,'armsSeatN':0.}
 def test_independent_named_hip_and_trunk_channels(self):
  g=r.SignedWrenchAllocator(self.pb.model)
  for side in ('left','right'):
   self.assertEqual(len(g.channels[side]),2)
   self.assertNotEqual(g.channels[side]['hip'],g.channels[side]['trunk'])
 def test_wrench_observer_cannot_mutate_native_plant(self):
  digest=r.phy.plant.sha_state(self.pb.data)
  for k in range(10):
   m=sense_wrench(self.pb.model,self.pb.data)
   self.assertTrue(m.valid and m.valid_projection)
  self.assertEqual(digest,r.phy.plant.sha_state(self.pb.data))
 def test_bounded_output_and_separate_channels(self):
  g=r.SignedWrenchAllocator(self.pb.model)
  for k in range(20):g.update(2+k*.04,self.obs(),self.pb.model,self.pb.data)
  self.assertTrue(np.all(np.isfinite(g.output())))
  self.assertGreater(g.hip,0.)
  self.assertGreater(g.trunk,0.)
  self.assertLessEqual(g.hip,r.CONFIG['hipMax'])
  self.assertLessEqual(g.trunk,r.CONFIG['obliqueMax'])
  self.assertEqual(np.count_nonzero(g.output()),2)
 def test_contact_arm_abort_to_zero(self):
  g=r.SignedWrenchAllocator(self.pb.model)
  for k in range(20):g.update(2.+k*.04,self.obs(),self.pb.model,self.pb.data)
  bad={**self.obs(),'armsSeatN':16.}
  for k in range(30):g.update(4.+k*.04,bad,self.pb.model,self.pb.data)
  self.assertTrue(np.allclose(g.output(),0.))
  self.assertGreater(g.abortUpdates,0)
 def test_side_reversal_preserves_anatomical_channels(self):
  g=r.SignedWrenchAllocator(self.pb.model)
  o={**self.obs(),'xPosition':-.031,'xSpeed':-.003}
  for k in range(15):g.update(2.+k*.04,o,self.pb.model,self.pb.data)
  self.assertEqual(g.output()[g.channels['left']['hip']],0.)
  self.assertGreater(g.output()[g.channels['right']['hip']],0.)
 def test_invalid_configuration_and_unseen_action(self):
  with self.assertRaises(AssertionError):r.SignedWrenchAllocator(self.pb.model,{'hipMax':.20})
  with self.assertRaises(ValueError):r.rollout({},'unknown',12.)
 def test_40s_receipt_is_not_promotion(self):
  data=json.loads((HERE/'R582_AUDIT.json').read_text())
  self.assertFalse(data['promoted'])
  self.assertFalse(data['scene00_40s']['settledAtEnd'])
  self.assertFalse(data['scene00_40s']['hazard'])
  self.assertGreater(data['legacyVsSigned']['missedVerticalFrictionSupport_N'],100.)
 @unittest.skipUnless(os.environ.get('R582_NATIVE')=='1','optional native 12s scene04 replay')
 def test_native_pushed_recovery(self):
  _,_,lock=r.inherited.r577.baseline.frozen.frozen()
  sc=r.inherited.r577.baseline.frozen.scenarios(lock)[4]
  record=r.rollout(sc,'R28',12.,trace_step_s=1.)
  self.assertTrue(record['complete'])
  self.assertFalse(record['hazard'])
  self.assertTrue(record['settledAtEnd'])
  self.assertAlmostEqual(record['finalRootX_m'],.024263406669211004,places=6)
if __name__=='__main__':unittest.main()
