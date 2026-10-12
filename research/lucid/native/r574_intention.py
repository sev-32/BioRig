#!/usr/bin/env python3
"""LUCID R574: explicit goal/aversion contract over bounded native muscle pulses.

The body has an externally specified intention, NOT a subjective wish.
The policy receives only current measured sensors at 60ms, and compares
learned outcomes of neutral continuation vs one historically well-observed
R28 muscle excitation. Simulator/harness metadata are evaluation-only.
Risk probabilities are small-data ExtraTrees frequencies, not guarantees.
"""
from pathlib import Path
import sys,json,hashlib
from dataclasses import dataclass,asdict
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'R572_PAIRED_FORCE_CALIBRATION'))
import r572_paired as evidence
phy=evidence.physics
ACTIONS=('none','R28')
FEATURE_NAMES=phy.SENSOR_NAMES
SCALE=phy.SCALE
@dataclass(frozen=True)
class GoalContract:
    name:str
    desire:str
    avoid:tuple
    fallWeight:float
    settleWeight:float
    armHazardWeight:float
    actionEffortCost:float
    benefitThreshold:float
    maxActionHazardChance:float
    maxSevereArmChance:float
    # These thresholds are run-time observations, not future truth.
    currentArmAbortN:float=10.0
    currentTiltAbortDeg:float=27.0
    maxNoveltyDistance:float=3.2

CONTRACTS={
 'restore_supported_equilibrium':GoalContract(
  name='restore_supported_equilibrium',
  desire='Be supported and quiet for >=1 second after pulse release',
  avoid=('Emergency tilt >=45 deg','Arm seat impact >=50 N',
         'Other-floor impact >=50 N','Unnecessary extra excitation',
         'Both seat and foot support lost'),
  fallWeight=2.0,settleWeight=.6,armHazardWeight=.25,
  actionEffortCost=.03,benefitThreshold=.17,
  maxActionHazardChance=.38,maxSevereArmChance=.35),
 'preserve_safe_posture':GoalContract(
  name='preserve_safe_posture',
  desire='Preserve existing safe support with minimum muscle intervention',
  avoid=('New emergency hazard','Unneeded muscle work',
         'Arm seat impact >=50 N','Loss of existing support'),
  fallWeight=2.0,settleWeight=.05,armHazardWeight=.35,
  actionEffortCost=.25,benefitThreshold=.24,
  maxActionHazardChance=.25,maxSevereArmChance=.25),
}
HOLDOUT={
 'seatHalfWidthsM':[.131,.175],
 'friction':.82,
 'forceDirections':[(0.,1.),(120.,-1.),(120.,1.),
                    (235.,-1.),(235.,1.),(365.,-1.),(365.,1.)],
 'horizonSeconds':8.0,
 'extensionSeconds':12.,
}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def all_training():
    rows=evidence.source_rows()
    assert len(rows)==36
    pairs=evidence.paired_rows(rows)
    assert len(pairs)==29
    return rows,pairs
def feature(obs):
    return np.array([float(obs[n]) for n in FEATURE_NAMES],float)/SCALE
class OutcomeMemory:
    """Separate predictions per treatment and desirable/undesirable terminal event."""
    def __init__(self):
        self.models={};self.X=None;self.training={}
    def fit(self,rows):
        self.training=rows
        self.X=np.array([feature(r['observed']) for r in rows])
        for action in ACTIONS:
            for event in ('hazard','settled','armSevere'):
                target='hazard' if event=='hazard' else (
                    'settledAtEnd' if event=='settled' else 'peakArmSeatN')
                labels=np.array([
                    int(r['branches'][action][target]>=50.) if event=='armSevere'
                    else int(r['branches'][action][target]) for r in rows])
                if len(set(labels))==1:self.models[(action,event)]=float(labels[0])
                else:
                    mdl=ExtraTreesClassifier(n_estimators=200,min_samples_leaf=2,
                        max_features=.9,random_state=600+len(
                        {'hazard':'haz','settled':'set','armSevere':'arm'}[event]
                        )+len(action),
                        n_jobs=1)
                    mdl.fit(self.X,labels)
                    self.models[(action,event)]=mdl
        return self
    def forecast(self,observation):
        x=feature(observation).reshape(1,-1)
        nearest=float(np.min(np.linalg.norm(self.X-x,axis=1)))
        out={}
        for a in ACTIONS:
            out[a]={}
            for e in ('hazard','settled','armSevere'):
                m=self.models[(a,e)]
                out[a][e]=float(m if isinstance(m,float) else m.predict_proba(x)[0,1])
        return out,nearest

def score(forecasts,contract):
    neutral=forecasts['none'];a=forecasts['R28']
    # Positive = action expected to advance the specified goal relative to inaction.
    return (contract.fallWeight*(neutral['hazard']-a['hazard'])
       +contract.settleWeight*(a['settled']-neutral['settled'])
       -contract.armHazardWeight*a['armSevere']
       -contract.actionEffortCost)

class IntentionAgent:
    def __init__(self,model):self.model=model
    def decide(self,observation,goal='restore_supported_equilibrium'):
        contract=CONTRACTS[goal]
        forecasts,nearest=self.model.forecast(observation)
        benefit=score(forecasts,contract)
        decision={'goal':goal,'desire':contract.desire,'avoid':list(contract.avoid),
                  'forecast':forecasts,'estimatedActionAdvantage':benefit,
                  'nearestTrainingDistance':nearest,
                  'observation60ms':observation}
        if observation['armsSeatN']>=contract.currentArmAbortN or observation['rootTiltDeg']>=contract.currentTiltAbortDeg:
            choice,why='none','current_measured_contact_or_tilt'
        elif nearest>contract.maxNoveltyDistance:
            choice,why='none','out_of_distributon'
        elif forecasts['R28']['hazard']>contract.maxActionHazardChance or forecasts['R28']['armSevere']>contract.maxSevereArmChance:
            choice,why='none','predicted_avoided_condition'
        elif benefit<contract.benefitThreshold:
            choice,why='none','no_expected_goal_advantage'
        else:
            choice,why='R28','expected_goal_advantage_within_vetoes'
        decision['choice']=choice;decision['reason']=why
        return decision
