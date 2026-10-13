"""R590 tests: full native state provenance and contact-safe settled restart.
Only local execution; NEVER GitHub Actions or model source changes.
"""
from __future__ import annotations
import sys,os,json,hashlib,unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r590_rest_restart as r

class R590Gates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((HERE/'R590_SETTLED_12TO24_NATIVE_RECEIPT.json').read_text())
        cls.zero=json.loads((HERE/'R590_RESTART_WITH_STATES_+0N_12S.json').read_text())
        cls.pushed=json.loads((HERE/'R590_RESTART_WITH_STATES_+120N_12S.json').read_text())
        cls.snap=np.load(HERE/'R590_SETTLED_CONTINUOUS_NATIVE_QPOS.npz')

    def test_physical_settling_is_continuous(self):
        self.assertEqual(self.doc['warmupS'],12)
        self.assertEqual(self.doc['measurementS'],12)
        self.assertEqual(self.doc['totalPhysicalS'],24)
        self.assertEqual(self.doc['frames'],31)
        self.assertLess(self.doc['12to24MaxHeadDeg'],.25)
        self.assertEqual(self.doc['contactTransitions12to24'],{'left':0,'right':0})

    def test_every_native_pose_matches_fingerprint(self):
        self.assertEqual(len(self.snap['qpos']),31)
        self.assertAlmostEqual(float(self.snap['timeS'][0]),12.)
        self.assertAlmostEqual(float(self.snap['timeS'][-1]),24.)
        for i,qpos in enumerate(self.snap['qpos']):
            self.assertEqual(hashlib.sha256(qpos.tobytes()).hexdigest(),self.doc['qposSHA256'][i])
        p=HERE/'R590_SETTLED_CONTINUOUS_NATIVE_QPOS.npz'
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),self.doc['npzSHA256'])

    def test_restarted_physically_equal_starts(self):
        z=np.load(HERE/'R590_RESTART_PUSH_+0N_QPOS.npz')
        x=np.load(HERE/'R590_RESTART_PUSH_+120N_QPOS.npz')
        self.assertTrue(np.array_equal(z['qpos'][0],x['qpos'][0]))
        self.assertTrue(np.array_equal(z['qpos'][0],self.snap['qpos'][0]))
        self.assertEqual(self.zero['initialQposSHA256'],self.pushed['initialQposSHA256'])
        self.assertTrue(np.allclose(z['timeS'],np.arange(31)*.4,atol=1e-6))

    def test_no_push_complete_12s_with_no_arm_chatter(self):
        z=self.zero
        self.assertAlmostEqual(z['seconds'],12)
        self.assertLess(z['maxHeadDeg'],.3)
        self.assertLess(z['peakArmN'],10)
        self.assertEqual(z['transitions'],{'left':0,'right':0})
        self.assertLess(abs(z['finalPelvisX_m']),.03)

    def test_120n_push_retains_full_body_stability(self):
        z=self.pushed
        self.assertEqual(z['pushN'],120)
        self.assertLess(z['maxHeadDeg'],.3)
        self.assertLess(z['peakArmN'],10)
        self.assertEqual(z['transitions'],{'left':0,'right':0})
        self.assertLess(abs(z['finalPelvisX_m']),.03)
        self.assertGreater(abs(z['finalPelvisX_m']-self.zero['finalPelvisX_m']),1e-6)

    def test_render_is_from_actual_locked_mesh(self):
        rec=json.loads((HERE/'R590_RESTART_SKIN_RENDER_AUDIT.json').read_text())
        self.assertEqual(rec['originalSkinSHA256'],'88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10')
        self.assertEqual(rec['gifFrames'],31)
        self.assertTrue(rec['noInterpolation']);self.assertTrue(rec['rootPoseOrSkinEdited'] is False)
        self.assertEqual(hashlib.sha256((HERE/'R590_REAL_SKIN78_REST_START_NO_PUSH_VS_120N.gif').read_bytes()).hexdigest(),rec['gifSHA256'])

    def test_no_pretend_bilateral_rest_contact(self):
        # Left forearm legitimately rests on the seat; right hand hangs freely.
        self.assertGreater(self.doc['initialArmContactN']['left'],1.)
        self.assertLess(self.doc['initialArmContactN']['right'],1.)
        self.assertLess(self.doc['measuredPeakArmN']['left'],10.)
        self.assertEqual(self.doc['measuredPeakArmN']['right'],0.)

    @unittest.skipUnless(os.getenv('R590_NATIVE_REPLAY')=='1','optional genuine 2s MuJoCo physical replay')
    def test_native_restored_controller_state_has_no_contact_spike(self):
        out=r.continue_native(seconds=2.,pushN=0.)
        self.assertLess(out['maxHeadDeg'],.5)
        self.assertLess(out['peakArmN'],12)
        self.assertEqual(out['transitions'],{'left':0,'right':0})
        self.assertAlmostEqual(out['finalPelvisX_m'],self.snap['qpos'][5,0],delta=.0005)

if __name__=='__main__':unittest.main()
