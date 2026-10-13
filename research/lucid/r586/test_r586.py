"""R586 source, native motion, contact, torque-envelope and SKIN78 gates.
No GitHub Actions; native tests explicitly invoked with R586_NATIVE=1.
"""
from __future__ import annotations
import os,json,hashlib,unittest
from pathlib import Path
import numpy as np,mujoco as mj
import r586_effort as r

HERE=Path(__file__).resolve().parent

class TestR586(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pb=r.r585.prior.make_body('seated')
        cls.ref=r.r585.prior.reset(cls.pb)
        cls.ids=r.MomentConstrainedAllocator(cls.pb,kp=.5,kd=.5,regular=.1).ids
    def test_six_mechanical_joint_axes_and_ten_named_muscles(self):
        c=r.MomentConstrainedAllocator(self.pb,kp=.5,kd=.5,regular=.1)
        self.assertEqual(len(c.dof),6)
        self.assertEqual(len(c.ids),10)
        self.assertEqual(len(set(map(int,c.ids))),10)
        self.assertTrue(all(int(d)<self.pb.model.nv for d in c.dof))
        self.assertTrue(all(int(i)<self.pb.model.nu for i in c.ids))
    def test_no_virtual_root_actuation(self):
        c=r.MomentConstrainedAllocator(self.pb,kp=.5,kd=.5,regular=.1)
        self.assertEqual(self.pb.model.nu,84)
        self.assertTrue(all(int(d)>=6 for d in c.dof))
        self.assertEqual(c.max_activation,.8)
    def test_optimizer_envelope_and_bounded_slew(self):
        c=r.MomentConstrainedAllocator(self.pb,kp=.5,kd=.5,regular=.1)
        self.assertTrue(np.all(c.torque_tolerance_Nm>0))
        self.assertLessEqual(max(c.torque_tolerance_Nm),.04)
        self.assertGreater(c.slew_limit_per_update,0)
        self.assertLessEqual(c.slew_limit_per_update,.20)
    def test_frozen_r585_source_is_untouched(self):
        p=Path(r.r585.__file__).resolve()
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),
                         'c356fd555e114360d31ff5466e15d71edf32b3cb7dcfeea7daa529e12c017c6e')
    def test_captured_native_skin78_frame_hashes(self):
        receipt=json.loads((HERE/'R586_RENDER_RECEIPT.json').read_text())
        self.assertEqual(receipt['framesPerCondition'],31)
        if 'frameQposHashes' in receipt:
            self.assertEqual(len(receipt['frameQposHashes']),31)
        self.assertEqual(receipt['originalSkinSHA256'],
                         '88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10')
        gif=HERE/'R586_NATIVE_SKIN78_VS_R585_12S.gif'
        if gif.is_file():
            self.assertEqual(hashlib.sha256(gif.read_bytes()).hexdigest(),receipt['nativeGIF_SHA256'])
        else:
            self.assertEqual(len(receipt['nativeGIF_SHA256']),64)
    def test_existing_physical_receipts_no_false_completion(self):
        outcome=json.loads((HERE/'R586_12S.json').read_text())
        self.assertLess(outcome['maxHeadAngleDeg'],5.)
        self.assertLess(outcome['maxPelvisTiltDeg'],45.)
        self.assertLess(outcome['maxArmSeatN'],50.)
        self.assertLess(outcome['maxOtherFloorN'],50.)
        self.assertEqual(outcome['optimizerFallbacks'],0)
        self.assertEqual(outcome['optimizerInfeasibleSteps'],0)
        self.assertLess(outcome['newNeckExcitationSeconds'],outcome['referenceNeckExcitationSeconds'])
    @unittest.skipUnless(os.getenv('R586_NATIVE')=='1','optional native 12-second replay')
    def test_real_native_unpushed_12s(self):
        outcome=r.run(secs=12.)
        self.assertLess(outcome['maxHeadAngleDeg'],5.)
        self.assertLess(outcome['maxArmSeatN'],50.)
        self.assertLess(outcome['maxOtherFloorN'],50.)
        self.assertLess(abs(outcome['samples'][-1]['pelvisX_m']),.03)
        self.assertAlmostEqual(outcome['endHeadAngleDeg'],.11584545349418755,places=5)
    @unittest.skipUnless(os.getenv('R586_NATIVE_PUSH')=='1','optional native 120N push replay')
    def test_real_native_pushed_12s(self):
        outcome=r.run(secs=12.,push_N=120.)
        self.assertLess(outcome['maxHeadAngleDeg'],5.)
        self.assertLess(outcome['maxArmSeatN'],50.)
        self.assertLess(outcome['maxOtherFloorN'],50.)
        self.assertLess(abs(outcome['samples'][-1]['pelvisX_m']),.03)
        self.assertAlmostEqual(outcome['endHeadAngleDeg'],.11669658133149108,places=5)
if __name__=='__main__':unittest.main()
