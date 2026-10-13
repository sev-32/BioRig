"""R580 typed motor/safety contract tests, plus optional native 12s replay."""
import sys,unittest,os,json
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import r580_adaptive_synergy as r
LATE={**r.CONFIG,'triggerPositionM':.0284,'fullRecruitAtM':.0308,'lookaheadS':1.,'hipMax':.029}

class TestR580(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pb,cls.ref,cls.neu,cls.saved=r.phys.paired_scene(.131,.82)
    def observation(self):
        return {**r.phys.sense(self.pb,self.pb.data),'xPosition':.032,
            'xSpeed':.0007,'armsSeatN':0.,'rootTiltDeg':12.}
    def test_physical_actuator_identity(self):
        guard=r.AdaptiveSynergy(self.pb.model,LATE)
        for side in ('left','right'):
            names=tuple(mj.mj_id2name(self.pb.model,mj.mjtObj.mjOBJ_ACTUATOR,i) for i in guard.groups[side])
            self.assertEqual(len(names),4)
            self.assertEqual(names[2],f'm_{side}_gluteus_medius')
    def test_bounded_and_side_selected(self):
        g=r.AdaptiveSynergy(self.pb.model,LATE)
        for i in range(20):g.update(2.+i*.04,self.observation())
        self.assertLessEqual(np.max(g.output()),.029+1e-10)
        self.assertGreater(g.output()[g.groups['left'][2]],0.)
        self.assertTrue(all(g.output()[j]==0 for j in g.groups['right']))
        o={**self.observation(),'xPosition':-.032,'xSpeed':-.0007}
        g.update(2.9,o)
        self.assertTrue(all(g.output()[j]==0 for j in g.groups['left']))
        self.assertGreater(g.output()[g.groups['right'][2]],0.)
    def test_current_state_drives_intervention(self):
        g=r.AdaptiveSynergy(self.pb.model,LATE)
        low={**self.observation(),'xPosition':.024,'xSpeed':0.}
        for i in range(10):g.update(2.+i*.04,low)
        low_trunk=g.trunkFraction;low_dose=g.hipDose
        fast=self.observation()
        for i in range(10):g.update(3.+i*.04,fast)
        self.assertGreater(g.trunkFraction,low_trunk)
        self.assertGreater(g.hipDose,low_dose)
    def test_abort_ramps_down(self):
        g=r.AdaptiveSynergy(self.pb.model,LATE)
        for i in range(20):g.update(2.+i*.04,self.observation())
        hazard={**self.observation(),'armsSeatN':16.}
        for i in range(30):g.update(3.+i*.04,hazard)
        self.assertAlmostEqual(g.hipDose,0.)
        self.assertTrue(np.allclose(g.output(),0.))
        self.assertGreater(g.abortUpdates,0)
    def test_r574_plant_unchanged(self):
        g=r.AdaptiveSynergy(self.pb.model,LATE)
        before=r.phys.plant.sha_state(self.pb.data)
        g.update(3.,self.observation())
        self.assertEqual(before,r.phys.plant.sha_state(self.pb.data))
    def test_config_validation(self):
        with self.assertRaises(AssertionError):r.AdaptiveSynergy(self.pb.model,{'hipMax':.10})
        with self.assertRaises(AssertionError):r.AdaptiveSynergy(self.pb.model,{'fullRecruitAtM':.01})
    def test_receipt_validation(self):
        p=HERE/'R580_AUDIT.json'
        if not p.exists():self.skipTest('audit missing')
        d=json.loads(p.read_text())
        self.assertFalse(d['promoted'])
        self.assertFalse(d['validation']['sixtySecondCompleted'])
    @unittest.skipUnless(os.environ.get('R580_NATIVE')=='1','optional 12s native replay')
    def test_native_scene04_rescue(self):
        _,_,lock=r.r577.baseline.frozen.frozen()
        s=r.r577.baseline.frozen.scenarios(lock)[4]
        o=r.rollout(s,'R28',12.,LATE,False,trace_period=1.)
        self.assertTrue(o['complete']);self.assertFalse(o['hazard']);self.assertTrue(o['settledAtEnd'])
        self.assertAlmostEqual(o['finalX_m'],.024246629385171182,places=6)
if __name__=='__main__':unittest.main()
