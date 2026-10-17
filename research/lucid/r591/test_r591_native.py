#!/usr/bin/env python3
"""Locally executed gates, original frozen plant; no Github Actions."""
import os,sys,math,json,hashlib,unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),*[str(HERE/x) for x in ('r590','r589','r588','r586','r585')]]
import r591_balanced_muscle_experiment as experiment

class Tests(unittest.TestCase):
 def result(self,name):return json.loads((HERE/'out'/f'R591_{name}_MEASURED.json').read_text())
 def test_identical_initial_full_state(self):
  items=[self.result(n) for n in ('base','single','reciprocal','RELEASE_PLUS','RELEASE_MINUS','BASE_NEG')]
  self.assertEqual(len({r['initialStateSHA256'] for r in items}),1)
  self.assertEqual({r['physicalEngine'] for r in items},{'MuJoCo 3.15.0'})
  self.assertTrue(all(r['skinOriginalUnmodified'] for r in items))
 def test_tonic_preload_not_automatically_stable(self):
  self.assertGreater(self.result('paired_hold')['maxHoldDeviationRad'],self.result('base')['maxHoldDeviationRad'])
 def test_reciprocal_feedback_positive_disturbance(self):
  a,b=self.result('base'),self.result('RELEASE_PLUS')
  self.assertLess(b['maxHoldDeviationRad'],a['maxHoldDeviationRad']*.35)
  self.assertLess(b['maxHeadDeg'],5.0)
  self.assertLess(b['maxRightArmSeatN'],20.)
 def test_bidirectional_disturbance(self):
  a,b=self.result('BASE_NEG'),self.result('RELEASE_MINUS')
  self.assertLess(b['maxHoldDeviationRad'],a['maxHoldDeviationRad']*.65)
  self.assertLess(b['maxHeadDeg'],5.0)
 def test_relaxation_changes_an_actual_antagonist(self):
  a=self.result('RELEASE_NO')
  self.assertGreater(a['relaxationIntegral'],.02)
  self.assertAlmostEqual(a['additionalCommandIntegral'],0.,places=8)
  self.assertLess(a['meanTrackingErrorRad'],self.result('base_NO_KICK')['meanTrackingErrorRad']*.7)
 def test_source_physically_replays(self):
  a=experiment.run('release_feedback',3.,2.,0.,'VERIFY_FRESH',18.,2.)
  original=self.result('RELEASE_PLUS')
  for key in ('maxHoldDeviationRad','meanTrackingErrorRad','finalErrorRad','maxHeadDeg','relaxationIntegral'):
   self.assertAlmostEqual(a[key],original[key],delta=1e-10,msg=key)
 def test_render_provenance(self):
  r=json.loads((HERE/'out'/'R591_RENDER_RECEIPT.json').read_text())
  self.assertEqual(r['skinSHA256'],'88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10')
  for name,sha in r['qposFilesSHA256'].items():
   self.assertEqual(hashlib.sha256((HERE/'out'/f'R591_{name}_NATIVE_QPOS.npz').read_bytes()).hexdigest(),sha)
  gif=HERE/'out'/'R591_RECIPROCAL_RELEASE_NATIVE_SKIN78_COMPARISON.gif'
  self.assertEqual(hashlib.sha256(gif.read_bytes()).hexdigest(),r['gifSHA256'])

if __name__=='__main__':unittest.main(verbosity=2)
