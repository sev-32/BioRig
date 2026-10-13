import unittest,sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from r587_whole_body_gate import inspect_native,check_render

class WholeBodyGateTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.evidence=json.loads((HERE/'R587_24S_NO_PUSH.json').read_text())
  def test_24_second_native_physics(self):
    gate=inspect_native(self.evidence)
    self.assertTrue(gate['physicalQuantitiesPass'])
    self.assertFalse(gate['fullBodyBiomechanicsApproved'])
  def test_head_collapse_rejected(self):
    data=json.loads(json.dumps(self.evidence))
    data['samples'][35]['headThoraxDeg']=84.
    self.assertFalse(inspect_native(data)['gates']['headToThoraxDeg'])
  def test_slip_and_pelvis_drift_rejected(self):
    data=json.loads(json.dumps(self.evidence))
    data['samples'][-1]['pelvisX_m']=.06
    self.assertFalse(inspect_native(data)['gates']['absPelvisX_m'])
  def test_hidden_impact_rejected(self):
    data=json.loads(json.dumps(self.evidence))
    data['samples'][7]['otherFloorN']=200
    self.assertFalse(inspect_native(data)['gates']['otherFloorN'])
  def test_empty_missing_short_horizon_invalid(self):
    with self.assertRaises(ValueError):inspect_native({'secs':24,'samples':[]})
    with self.assertRaises(ValueError):inspect_native({'secs':12,'samples':self.evidence['samples']})
  def test_pushed_24_second_native_physics(self):
    push=json.loads((HERE/'R587_24S_PUSH120.json').read_text())
    self.assertEqual(push['pushN'],120)
    gate=inspect_native(push)
    self.assertTrue(gate['physicalQuantitiesPass'])
    self.assertLess(push['maxHeadAngleDeg'],5.)
    self.assertLess(push['maxArmSeatN'],50.)
  def test_real_native_push_render(self):
    receipt=HERE/'R587_SKIN78_24S_PUSH120_NATIVE_RECEIPT.json'
    gif=HERE/'R587_SKIN78_24S_PUSH120_NATIVE_ANIMATION.gif'
    if not receipt.is_file() or not gif.is_file():self.skipTest('Physical pushed render still running')
    push=json.loads((HERE/'R587_24S_PUSH120.json').read_text())
    check=check_render(push,json.loads(receipt.read_text()),gif)
    self.assertEqual(check['nativeFrames'],61)
  def test_real_native_render(self):
    receipt=HERE/'R587_SKIN78_24S_NATIVE_RECEIPT.json'
    gif=HERE/'R587_SKIN78_24S_NATIVE_ANIMATION.gif'
    if not receipt.is_file() or not gif.is_file():self.skipTest('Visual render still running')
    check=check_render(self.evidence,json.loads(receipt.read_text()),gif)
    self.assertTrue(check['continuousNativeTimelineValidated'])
    self.assertEqual(check['nativeFrames'],61)

if __name__=='__main__':unittest.main()
