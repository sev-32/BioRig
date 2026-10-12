"""R578 structural, dimensional, and native physical regression gates."""
import sys,unittest,os,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r578_feedback as r
from r578_support import measure
class R578Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pb,cls.ref,cls.neutral,cls.saved=r.phys.paired_scene(.131,.82)
 def test_measured_com_center_valid_and_finite(self):
  m=measure(self.pb.model,self.pb.data)
  self.assertTrue(m.valid);self.assertGreater(m.measuredNormalLoad_N,50.)
  self.assertGreater(m.contactCount,0)
  self.assertAlmostEqual(m.comRelativeToPressure_m,m.comX_m-m.centerOfPressureX_m)
  self.assertTrue(np.isfinite(m.comX_m))
 def test_com_measurement_does_not_mutate_state(self):
  orig=r.phys.plant.sha_state(self.pb.data)
  for _ in range(4):measure(self.pb.model,self.pb.data)
  self.assertEqual(orig,r.phys.plant.sha_state(self.pb.data))
 def test_excitation_bounds(self):
  guard=r.SupportFeedback(self.pb.model)
  o=r.phys.sense(self.pb,self.pb.data)
  for t in (1.4,1.44,1.48,1.52,4.,4.04,4.08):
   guard.update(t,{**o,'xPosition':.032,'xSpeed':.001},self.pb,self.pb.data)
   self.assertTrue(np.isfinite(guard.amplitude))
   self.assertGreaterEqual(guard.amplitude,0.)
   self.assertLessEqual(guard.amplitude,.04)
   self.assertTrue(np.all(guard.output()<=.04))
 def test_sensed_contact_abort(self):
  guard=r.SupportFeedback(self.pb.model)
  o=r.phys.sense(self.pb,self.pb.data)
  o.update(xPosition=.032,armsSeatN=0.,rootTiltDeg=12.)
  for k in range(20):guard.update(4.+k*.04,o,self.pb,self.pb.data)
  self.assertGreater(guard.amplitude,0.)
  o['armsSeatN']=16.
  for k in range(12):guard.update(5.+k*.04,o,self.pb,self.pb.data)
  self.assertAlmostEqual(guard.amplitude,0.)
  self.assertGreater(guard.aborts,0)
 def test_invalid_configuration(self):
  with self.assertRaises(AssertionError):r.SupportFeedback(self.pb.model,{'doseCeiling':.08})
 @unittest.skipUnless(os.environ.get('R578_NATIVE')=='1','optional 12s physical replay')
 def test_native_12s_no_new_hazard(self):
  sc={'seatHalfWidthM':.131,'friction':.82,'forceN':0.,'direction':1.}
  out=r.run(sc,'none',12.,mode='pd',trace_interval=1.)
  self.assertTrue(out['complete']);self.assertFalse(out['hazard']);self.assertTrue(out['settledAtEnd'])
  self.assertAlmostEqual(out['finalX'],.027416591656757815,places=6)
if __name__=='__main__':unittest.main()
