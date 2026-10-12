#!/usr/bin/env python3
"""Fast audit of completed R575 branches against locked R574 evidence.
This does NOT re-run the slow native-physics branches; see r575_latency.py.
"""
from pathlib import Path
import unittest, json, sys, math
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'R574_INTENTION_AND_AVERSION'))
import r574_intention as goal
class R575EvidenceChecks(unittest.TestCase):
    def load(self,index,delay):
        return json.loads((HERE/'measured'/f'scene_{index:02d}_lag_{delay:02d}ms_8s.json').read_text())
    def locked(self,index):
        return json.loads((ROOT/'R574_INTENTION_AND_AVERSION'/f'R574_LOCKED_SCENE_{index:02d}.json').read_text())
    def test_source_and_lock_not_changed(self):
        lock=json.loads((ROOT/'R574_INTENTION_AND_AVERSION/R574_EVALUATION_LOCK.json').read_text())
        self.assertEqual(goal.sha(ROOT/'R574_INTENTION_AND_AVERSION/r574_intention.py'),lock['modelSourceSHA256'])
        self.assertEqual(goal.sha(ROOT/'R574_INTENTION_AND_AVERSION/r574_evaluate.py'),lock['evaluationHarnessSHA256'])
    def test_zero_delay_reproduces_frozen_native_trace(self):
        r=self.load(4,0)
        old=self.locked(4)['R574Restore']
        for key in ('hazard','settledAtEnd','peakArmSeatN','peakRootTiltDeg','peakOtherFloorN','finalX','finalV','commandMax'):
            self.assertEqual(r[key],old[key],key)
        self.assertEqual(r['trace'],old['trace'])
    def test_measured_stale_20ms_scene_4_preserves_success(self):
        r=self.load(4,20)
        old=self.locked(4)['R574Restore']
        self.assertEqual(r['chosenAction'],'R28')
        self.assertEqual(r['trace'],old['trace'])
        self.assertFalse(r['hazard'])
        self.assertTrue(r['settledAtEnd'])
    def test_stale_scene_1_really_chose_inaction(self):
        prev=self.locked(1)
        self.assertEqual(prev['restoreDecision']['choice'],'R28')
        for latency in (20,40):
            r=self.load(1,latency)
            self.assertEqual(r['chosenAction'],'none')
            self.assertEqual(r['initialSHA256'],prev['initialPlantSHA256'])
            self.assertEqual(r['scene'],prev['harnessScene'])
            self.assertFalse(r['hazard'])
            self.assertTrue(r['settledAtEnd'])
    def test_all_samples_have_unmodified_production_and_8s_traces(self):
        for i,d in ((1,20),(1,40),(4,0),(4,20)):
            r=self.load(i,d)
            self.assertTrue(r['researchOnly'])
            self.assertFalse(r['productionModified'])
            self.assertEqual(len(r['trace']),401)
            self.assertEqual(r['trace'][-1]['timeS'],8.)
if __name__=='__main__':unittest.main(verbosity=2)
