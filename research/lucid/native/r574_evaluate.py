#!/usr/bin/env python3
"""R574 frozen goals-vs-aversions native MuJoCo evaluation.

Goal selection at 60ms has NO access to external impulse, geometry label, or
counterfactual future. All applied physics branches are cloned initial states.
"""
from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(ROOT/'R570_SAFETY_GENERALIZATION'))
import r574_intention as ctl
from r570_locked_eval import models as load_inherited_r569

def frozen():
    lock=json.loads((HERE/'R574_EVALUATION_LOCK.json').read_text())
    assert ctl.sha(HERE/'r574_intention.py')==lock['modelSourceSHA256']
    assert ctl.sha(HERE/'r574_evaluate.py')==lock['evaluationHarnessSHA256']
    for relative,expected in lock['trainingSourceSHA256'].items():
        assert ctl.sha(ROOT/relative)==expected,relative
    rows,pairs=ctl.all_training()
    model=ctl.OutcomeMemory().fit(pairs)
    prior,_,_=load_inherited_r569()
    return ctl.IntentionAgent(model),prior,lock

def scenarios(lock):
    return [{'seatHalfWidthM':width,'friction':lock['heldOut']['friction'],
         'forceN':force,'direction':sgn}
         for width in lock['heldOut']['seatHalfWidthsM']
         for force,sgn in lock['heldOut']['forceDirections']]

def evaluate(i,frozen_models=None):
    agent,old,lock=frozen_models or frozen()
    scene=scenarios(lock)[i]
    name=HERE/f'R574_LOCKED_SCENE_{i:02d}.json'
    if name.exists():raise FileExistsError(name)
    phy=ctl.phy
    pb,ref,neu,saved=phy.paired_scene(scene['seatHalfWidthM'],scene['friction'])
    original=phy.plant.sha_state(pb.data)
    applied=scene['forceN']*scene['direction']
    measured=phy.initial_observation(pb,saved,ref,neu,applied)
    selected=agent.decide(measured,'restore_supported_equilibrium')
    protect=agent.decide(measured,'preserve_safe_posture')
    oldchoice,oldreason,_,_=old.select(measured)
    action_set=set(('none',selected['choice'],protect['choice'],oldchoice))
    outcomes={action:phy.rollout(pb,saved,ref,neu,applied,action,seconds=8.,
                     traces=(action in ('none',selected['choice']))) for action in sorted(action_set)}
    assert original==phy.plant.sha_state(pb.data)
    n=outcomes['none'];c=outcomes[selected['choice']]
    record={
     'schema':'lucid.r574.locked-intention-trial.v1','index':i,
     'lockSHA256':ctl.sha(HERE/'R574_EVALUATION_LOCK.json'),
     'researchOnly':True,'productionModified':False,
     'harnessScene':scene,'initialPlantSHA256':original,
     'sensorObservation60ms':measured,
     'restoreDecision':selected,'protectDecision':protect,
     'R569Choice':oldchoice,'R569Reason':oldreason,
     'neutral':n,'R569':outcomes[oldchoice],
     'R574Restore':c,'R574Protect':outcomes[protect['choice']],
     'R574Rescue':bool(n['hazard'] and not c['hazard']),
     'R574SettledRescue':bool(n['hazard'] and not c['hazard'] and c['settledAtEnd']),
     'R574NewHazard':bool(not n['hazard'] and c['hazard'])}
    name.write_text(json.dumps(record,indent=2,allow_nan=False))
    print('R574 LOCKED',i,scene,'actions','R569',oldchoice,
        'restore',selected['choice'],'protect',protect['choice'],
        'hazard',n['hazard'],record['R569']['hazard'],c['hazard'],
        'settled',c['settledAtEnd'],flush=True)
    return record
if __name__=='__main__':
    import argparse
    cli=argparse.ArgumentParser();cli.add_argument('indices',type=int,nargs='+')
    a=cli.parse_args()
    models=frozen()
    for i in a.indices:evaluate(i,models)
