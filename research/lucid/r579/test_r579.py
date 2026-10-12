"""Contract and optional native physics gates for experimental muscle synergy."""
import os,sys,unittest
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r579_controller as r

class TestR579(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pb,cls.ref,cls.neu,cls.saved=r.r577.phys.paired_scene(.131,.82)
    def test_masks_match_named_muscles(self):
        a=r.Synergy(self.pb.model,'hip_only')
        for side in ('left','right'):
            mask=a.masks[side]
            ids=np.flatnonzero(mask)
            self.assertEqual(len(ids),1)
            name=mj.mj_id2name(self.pb.model,mj.mjtObj.mjOBJ_ACTUATOR,int(ids[0]))
            self.assertEqual(name,f'm_{side}_gluteus_medius')
    def test_weighted_mask_bounded(self):
        a=r.Synergy(self.pb.model,'hip_trunk_20pct')
        self.assertEqual(sorted(np.round(a.masks['left'][a.masks['left']>0],2)),[.2,.2,.2,1.])
        self.assertLessEqual(max(a.masks['left']),1.)
    def test_mirror_mask(self):
        a=r.Synergy(self.pb.model,'hip_trunk_20pct')
        self.assertEqual(np.count_nonzero(a.masks['left']),4)
        self.assertEqual(np.count_nonzero(a.masks['right']),4)
        self.assertEqual(np.dot(a.masks['left'],a.masks['right']),0.)
    def test_no_frozen_state_mutation(self):
        before=r.r577.phys.plant.sha_state(self.pb.data)
        a=r.Synergy(self.pb.model,'hip_only')
        a.update(4.,{**r.r577.phys.sense(self.pb,self.pb.data),'xPosition':.032,'armsSeatN':0,'rootTiltDeg':12})
        self.assertEqual(before,r.r577.phys.plant.sha_state(self.pb.data))
    def test_bad_profiles_rejected(self):
        with self.assertRaises(ValueError):r.Synergy(self.pb.model,'made_up')
        with self.assertRaises(ValueError):r.rollout({},'none','made_up')
    @unittest.skipUnless(os.environ.get('R579_NATIVE')=='1','optional 12s native MuJoCo replay')
    def test_scene00_native_12s(self):
        scene={'seatHalfWidthM':.131,'friction':.82,'forceN':0.,'direction':1.}
        previous=r.r577.TonicSupport
        out=r.rollout(scene,'none','hip_only',12.)
        self.assertIs(previous,r.r577.TonicSupport)
        self.assertTrue(out['complete']);self.assertFalse(out['hazard'])
        self.assertTrue(out['settledAtEnd'])
        self.assertAlmostEqual(out['finalX'],.027471,places=5)
        self.assertAlmostEqual(out['sumChannelExcitationSeconds'],.26132,places=4)
if __name__=='__main__':unittest.main()
