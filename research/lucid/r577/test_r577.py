#!/usr/bin/env python3
import json,os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import r577_tonic_support as r

class TestR577(unittest.TestCase):
 def setUp(self):
  # Only 0.8s warmup. This is an inherited native MuJoCo physical plant.
  self.scene={'seatHalfWidthM':.131,'friction':.82,'forceN':0.,'direction':1.}
  pb,ref,neu,saved=r.phys.paired_scene(.131,.82)
  self.pb=pb;self.obs=r.phys.sense(pb,pb.data)
 def test_dose_and_abort_rate_limit(self):
  ctl=r.TonicSupport(self.pb.model)
  o=dict(self.obs,xPosition=.020,xSpeed=.01,rootTiltDeg=15.,armsSeatN=0.)
  ctl.update(1.,o);self.assertEqual(ctl.amplitude,0.)
  for i in range(10):ctl.update(1.4+i*.04,o)
  self.assertAlmostEqual(ctl.amplitude,.025)
  self.assertEqual(ctl.lastGroup,'left')
  self.assertLessEqual(max(ctl.output()),r.phys.plant.MAX_EXTRA)
  o['armsSeatN']=16.
  ctl.update(1.8,o);self.assertAlmostEqual(ctl.amplitude,.022)
  for i in range(9):ctl.update(1.84+.04*i,o)
  self.assertEqual(ctl.amplitude,0.)
  self.assertEqual(ctl.lastGroup,None)
 def test_negative_displacement_uses_opposite_muscles(self):
  ctl=r.TonicSupport(self.pb.model)
  o=dict(self.obs,xPosition=-.02,xSpeed=-.01,rootTiltDeg=15.,armsSeatN=0.)
  ctl.update(2.,o)
  self.assertEqual(ctl.lastGroup,'right')
 def test_configuration_bounds(self):
  with self.assertRaises(AssertionError):r.TonicSupport(self.pb.model,{**r.CONFIG,'tonicDose':.1})
 def test_frozen_reference_is_reachable(self):
  self.assertTrue((r.baseline.ROOT/'R574_INTENTION_AND_AVERSION'/'R574_EVALUATION_LOCK.json').is_file())
 def test_invalid_action_rejected(self):
  with self.assertRaises(ValueError):r.rollout(self.scene,'MISSING',seconds=.002)
 @unittest.skipUnless(os.environ.get('R577_RUN_NATIVE')=='1','optional native physical 40s replay')
 def test_native_40s_scene00(self):
  p=Path(__file__).resolve().parent/'R577_DEVELOPMENT_RECEIPT.json'
  expected=json.loads(p.read_text())['scene00_40s']
  got=r.rollout(self.scene,'none',40.,True)
  self.assertEqual(got['initialSHA256'],expected['initialSHA256'])
  self.assertFalse(got['hazard']);self.assertFalse(got['settledAtEnd'])
  self.assertAlmostEqual(got['finalTiltDeg'],expected['finalTiltDeg'],places=6)
  self.assertAlmostEqual(got['finalX'],expected['finalX'],places=6)
if __name__=='__main__':unittest.main()
