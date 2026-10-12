#!/usr/bin/env python3
"""R576 research-contract tests; set R576_RUN_NATIVE=1 for paired 12s physics."""
import json, os, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r576_longhorizon as r

class TestR576(unittest.TestCase):
    def test_frozen_model_lock_unmodified(self):
        agent, old, lock=r.frozen.frozen()
        self.assertIsNotNone(agent)
        self.assertEqual(set(r.phy.OPTIONS), set(r.phy.PROFILES))
    def test_guard_does_not_mutate_inherited_rule(self):
        original=dict(r.settling.RULE)
        self.assertLess(original['firstAfterS'],1.8)
        pb,ref,neu,saved=r.phy.paired_scene(.131,.82)
        guard=r.make_guard(pb.model)
        self.assertEqual(guard.rule['firstAfterS'],1.8)
        self.assertEqual(guard.rule['maxPulses'],4)
        self.assertEqual(original,r.settling.RULE)
    def test_action_vocabulary_and_horizon_bound(self):
        scene={'seatHalfWidthM':.131,'friction':.82,'forceN':0.,'direction':1.}
        with self.assertRaises(ValueError):r.branch(scene,'made_up_action')
        with self.assertRaises(ValueError):r.branch(scene,'none',seconds=0.)
    def test_compact_receipt_is_not_promotion_evidence(self):
        p=HERE/'R576_SCENE00_COMPACT_RECEIPT.json'
        if not p.exists():self.skipTest('compact receipt missing from local research checkout')
        d=json.loads(p.read_text())
        self.assertEqual(d['evidenceClass'],'new-postlock-development-not-heldout')
        self.assertTrue(d['baseline']['hazard'])
        self.assertFalse(d['guarded']['hazard'])
        self.assertFalse(d['guarded']['settledAtEnd'])
        self.assertEqual(len(d['guarded']['postlockSupportPulses']),4)
    @unittest.skipUnless(os.environ.get('R576_RUN_NATIVE')=='1','optional 12s native physics')
    def test_scene00_12s_reproduction(self):
        d=json.loads((HERE/'R576_SCENE00_COMPACT_RECEIPT.json').read_text())
        got=r.compare([0],seconds=12.,trace=False)['results'][0]
        self.assertEqual(got['baseline']['initialSHA256'],d['pairedInitialSHA256'])
        for mode in ('baseline','guarded'):
            for key in ('hazard','settledAtEnd','bothSupportLossSamples'):
                self.assertEqual(got[mode][key],d[mode][key])
            for key in ('peakRootTiltDeg','peakArmSeatN','peakOtherFloorN','finalX'):
                self.assertAlmostEqual(got[mode][key],d[mode][key],places=6)

if __name__=='__main__':unittest.main()
