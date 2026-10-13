"""R589 native contact/head checks. No GitHub Actions, no skinned-image substitution."""
from __future__ import annotations
import json,hashlib,os,sys,unittest
from pathlib import Path
import numpy as np,mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r589_arm_landing as r

class R589MotorGates(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pb=r.r586.r585.prior.make_body('seated')
  r.r586.r585.prior.reset(cls.pb)
 def test_acts_on_real_muscles_not_root(self):
  a=r.ArmLanding(self.pb,**r.VERIFIED_PROFILE)
  self.assertEqual(set(a.moment_ids),{'left','right'})
  for side,channels in a.moment_ids.items():
   self.assertTrue(all(i>=0 for i in channels.values()))
   self.assertEqual(len(channels),2)
   self.assertGreater(a.refs[side][1],5)
 def test_moment_signs_supply_antagonistic_arm_torques(self):
  pb=self.pb;d=pb.data;m=pb.model
  mom=r.r586.r585.muscle_moment_matrix(d,m.nu,m.nv)
  a=r.ArmLanding(pb,**r.VERIFIED_PROFILE)
  for side in ('left','right'):
   shoulder=a.refs[side][1]
   for name,expected_sign in (('deltoid_middle',1),('pectoralis_major',-1)):
    i=a.moment_ids[side][name]
    gain=mj.mju_muscleGain(d.actuator_length[i],d.actuator_velocity[i],m.actuator_lengthrange[i],m.actuator_acc0[i],m.actuator_gainprm[i,:9])
    self.assertGreater(expected_sign*float(mom[i,shoulder]*gain),5)
 def test_bounded_action_nonmutating_and_velocity_feedback(self):
  pb=self.pb;d=pb.data
  digest=hashlib.sha256(d.qpos.tobytes()+d.qvel.tobytes()).hexdigest()
  agent=r.ArmLanding(pb,**r.VERIFIED_PROFILE)
  base=np.zeros(pb.model.nu)
  for t in (.05,.08,.1,.2,.3,.7,1.,2.,3.):
   action=agent.update(d,base,t)
   self.assertTrue(np.isfinite(action).all())
   self.assertGreaterEqual(float(action.min()),0)
   self.assertLessEqual(float(action.max()),.8+1e-9)
  self.assertEqual(digest,hashlib.sha256(d.qpos.tobytes()+d.qvel.tobytes()).hexdigest())
 def test_verified_profile_has_finite_active_to_base_handoff(self):
  self.assertEqual(r.VERIFIED_PROFILE['release_at'],1.2)
  self.assertEqual(r.VERIFIED_PROFILE['fade_duration'],.7)
  self.assertEqual(r.smooth(-1),0)
  self.assertEqual(r.smooth(2),1)
 def test_identical_native_initial_states_for_render(self):
  b=np.load(HERE/'R587_NATIVE_12S_QPOS.npz')
  c=np.load(HERE/'R589_NATIVE_12S_QPOS.npz')
  self.assertTrue(np.array_equal(b['qpos'][0],c['qpos'][0]))
  self.assertTrue(np.array_equal(b['timeS'],c['timeS']))
  self.assertEqual(len(b['qpos']),31)
  for name,z in [('R587',b),('R589',c)]:
   rec=json.loads((HERE/f'{name}_NATIVE_12S_CAPTURE_RECEIPT.json').read_text())
   self.assertEqual(len(rec['frameSHA256']),31)
   self.assertEqual(hashlib.sha256(z['qpos'][-1].tobytes()).hexdigest(),rec['frameSHA256'][-1])
 def test_12s_measured_receipt_and_skin_lock(self):
  d=json.loads((HERE/'R589_NATIVE_12S_CAPTURE_RECEIPT.json').read_text())['physicsSummary']
  self.assertAlmostEqual(d['peakArmN']['left'],35.89629388532487,places=5)
  self.assertAlmostEqual(d['peakArmN']['right'],10.987974917319386,places=5)
  self.assertLess(d['maxHeadDeg'],5)
  self.assertLess(abs(d['finalPelvisX_m']),.03)
  rr=json.loads((HERE/'R589_12S_RENDER_RECEIPT.json').read_text())
  self.assertEqual(rr['meshSHA256'],'88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10')
 @unittest.skipUnless(os.getenv('R589_NATIVE')=='1','explicit native 3s A/B replay')
 def test_native_3s_muscle_landing_beats_baseline(self):
  base=r.run(3.,candidate=False)
  new=r.run(3.,candidate=True)
  self.assertLess(new['peakArmN']['right'],base['peakArmN']['right']*.1)
  self.assertLess(new['peakArmN']['left'],base['peakArmN']['left']*.25)
  self.assertLess(new['maxHeadDeg'],5)
  self.assertLess(abs(new['finalPelvisX_m']),.03)
 @unittest.skipUnless(os.getenv('R589_NATIVE_12')=='1','explicit native 12s physical repeat')
 def test_native_12s_reproduction(self):
  new=r.run(12.,candidate=True)
  self.assertAlmostEqual(new['peakArmN']['right'],10.987974917319386,places=5)
  self.assertAlmostEqual(new['peakArmN']['left'],35.89629388532487,places=5)
  self.assertLess(new['maxHeadDeg'],5)

if __name__=='__main__':unittest.main()
