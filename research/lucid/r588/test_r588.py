"""Real MuJoCo arm-seat collision regression; no Actions, no pose teleportation."""
import json,unittest,os,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from r588_probe import run

def arm_metrics(result,side):
    a=np.asarray([float(s['arms'][side]['contactN']) for s in result['samples']])
    return {'peakN':float(np.max(a)),'contactTransitions':int(np.count_nonzero(np.diff((a>.2).astype(int)))),
            'finalN':float(a[-1])}

class ArmContactRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=run(3.)
        cls.candidate=run(3.,thumb_time=.05,thumb_damping=2.,limb_damping_mult=10.)
    def test_existing_r587_bug_reproduced(self):
        a=arm_metrics(self.original,'right')
        self.assertGreater(a['peakN'],200.)
        self.assertGreaterEqual(a['contactTransitions'],10)
        self.assertLess(a['finalN'],1.)
    def test_candidate_reduces_both_initial_impacts(self):
        for side in ['left','right']:
            old=arm_metrics(self.original,side)
            new=arm_metrics(self.candidate,side)
            self.assertLess(new['peakN'],50.,(side,new))
            self.assertLess(new['peakN'],old['peakN']*.25)
    def test_candidate_righthand_landing_chatter(self):
        a=arm_metrics(self.candidate,'right')
        self.assertLessEqual(a['contactTransitions'],3)
        self.assertGreater(a['finalN'],2.)
        self.assertGreater(arm_metrics(self.candidate,'left')['finalN'],2.)
    def test_head_preserved_at_3s(self):
        self.assertLess(self.candidate['maxHeadDeg'],5)
        self.assertEqual(self.candidate['optimizerFallbacks'],0)
    def test_no_external_root_locking(self):
        self.assertEqual(self.candidate['params']['push'],0.)
        self.assertEqual(self.candidate['params']['seat_half_width'],None)
        self.assertIsNone(self.candidate['params']['seat_solref'])
        self.assertEqual(self.candidate['params']['thumb_time'],.05)
    def test_12s_longer_risk_is_explicit_in_audit(self):
        file=HERE/'R588_AUDIT.json'
        if not file.is_file():self.skipTest('Audit not supplied')
        d=json.loads(file.read_text())
        self.assertFalse(d['promotionAllowed'])
        self.assertIn('12s',d['longHorizon'])
        self.assertTrue(d['longHorizon']['12s']['leftArmEventuallyUnloaded'])
    @unittest.skipUnless(os.getenv('R588_FULL_12S')=='1','native optional 12s and push replay')
    def test_12s_physical_replay(self):
        for push in (0.,120.):
            d=run(12.,push=push,thumb_time=.05,thumb_damping=2.,limb_damping_mult=10.)
            self.assertLess(d['maxHeadDeg'],5.)
            self.assertLess(max(abs(s['rootTiltDeg']) for s in d['samples']),45.)
            self.assertLess(max(abs(s['pelvisX']) for s in d['samples']),.030)
if __name__=='__main__':unittest.main()
