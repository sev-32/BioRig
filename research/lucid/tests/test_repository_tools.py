"""Fast offline integrity tests for BioRig LUCID source and trace checker."""
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from audit_latency import inspect_record, compare
from bootstrap import extract_checked

def fixture(index=0, lag=0, arm=0.0):
    samples = [dict(timeS=i*.02, rootTiltDeg=5.0, armsSeatN=arm,
                    otherFloorN=0.0, pelvisSeatN=300., feetFloorN=300.,
                    settledNow=(i>=340)) for i in range(401)]
    return dict(schema='lucid.r575.latency-physical-branch.v1', researchOnly=True,
                productionModified=False, delayMs=lag, observedAtMs=60-lag,
                chosenAction='R28', seconds=8.0, trace=samples, index=index,
                hazard=False, settledAtEnd=True, peakRootTiltDeg=5.0,
                peakArmSeatN=arm, peakOtherFloorN=0., bothSupportLossSamples=0,
                initialSHA256='same_state', scene={'forceN':120},
                r574ControllerSHA256='same_policy',r575SourceSHA256='same_source')

class OfflineChecks(unittest.TestCase):
    def test_valid_trace(self):
        self.assertTrue(inspect_record(fixture())['settled'])
    def test_clock_tamper(self):
        r=fixture();r['trace'][100]['timeS']+=.001
        with self.assertRaisesRegex(ValueError, 'clock'):inspect_record(r)
    def test_derived_hazard_tamper(self):
        r=fixture(arm=50.)
        with self.assertRaisesRegex(ValueError, 'hazard'):inspect_record(r)
    def test_loss_of_support(self):
        r=fixture()
        for i in range(4):r['trace'][i]['pelvisSeatN']=0.;r['trace'][i]['feetFloorN']=0.
        with self.assertRaisesRegex(ValueError,'support-loss'):inspect_record(r)
    def test_missing_zero_delay_not_imputed(self):
        report=compare([fixture(1,20)])
        self.assertEqual(report['matchedDelayContrasts'],[])
        self.assertEqual(report['missingZeroDelayScenes'],[1])
    def test_matched_zero_lag(self):
        a=fixture(4,0);b=fixture(4,20)
        self.assertEqual(len(compare([a,b])['matchedDelayContrasts']),1)
    def test_mismatched_initial_state_rejected(self):
        a=fixture(4,0);b=fixture(4,20);b['initialSHA256']='other'
        with self.assertRaisesRegex(ValueError,'unmatched'):compare([a,b])
    def test_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate'):compare([fixture(),fixture()])
    def test_zip_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'unsafe.zip'
            with ZipFile(p,'w') as z:z.writestr('../escaped','bad')
            with self.assertRaisesRegex(ValueError,'unsafe'):extract_checked(p,Path(tmp)/'out')
    def test_zip_exact_file_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'ok.zip';dest=Path(tmp)/'out'
            with ZipFile(p,'w') as z:z.writestr('a/b.txt','value')
            self.assertEqual(extract_checked(p,dest),1)
            self.assertEqual(extract_checked(p,dest),1)
            self.assertEqual((dest/'a/b.txt').read_text(),'value')
            (dest/'a/b.txt').write_text('changed')
            with self.assertRaises(FileExistsError):extract_checked(p,dest)

if __name__=='__main__':unittest.main(verbosity=2)
