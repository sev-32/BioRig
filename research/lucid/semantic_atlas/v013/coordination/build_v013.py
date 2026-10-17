#!/usr/bin/env python3
"""V013: reproduce signed muscle-pair mechanics and pin control-architecture evidence.
Pure analysis: reads V010 immutable native moment Jacobians; changes no physics model.
"""
from __future__ import annotations
import csv,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'source'
ARCHIVE=Path('/mnt/data/BioRig_LUCID_SEMANTIC_ATLAS_V010_NATIVE_84x102_MECHANICAL_RELATIONSHIPS_2026-10-13.zip')
ENTRY='V010/NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz'
THRESHOLD=1e-6
WITNESS_SPECS=[
 ('neuro.py',196,203,'class WholeBodyMuscleController','Whole-body task controller'),
 ('neuro.py',347,355,'B = (R * g[:, None]).T','Moment arms mapped to muscle force susceptibility'),
 ('neuro.py',476,511,'reach','Whole-body activation and competing constraints'),
 ('neuro.py',564,580,'a_des','Activation slew and excitation inversion'),
 ('muscle_impedance_r518.py',31,51,'MuscleImpedanceLayer','Delayed afferent recruitment'),
 ('muscle_impedance_r518.py',62,94,'self.held','Release dynamics and positive corrections'),
 ('adaptive_muscle_tone_r522.py',50,96,'want','Signed pressure/load-dependent redistribution'),
 ('joint_intent_r546.py',44,96,'low=np.maximum(-DELTA_LIMIT','Signed antagonist-release-capable QP'),
 ('r589_arm_landing.py',46,83,'extra[idx]=np.clip(base[idx]+amp','Arm landing adds to selected agonist only'),
 ('r590_rest_restart.py',55,87,'d.ctrl[allocator.ids]=head_ctrl','Seated replay base-plus-neck only'),
 ('r579_synergy.py',28,56,'self.command','Lateral trunk/hip synergy'),
 ('r580_adaptive_synergy.py',67,105,'self.command','Sensor-dependent bounded trunk/hip synergy'),
 ('muscle_allocator_r58.py',10,66,'against_task','Shared task conflict heuristic'),
]

def sha(raw: bytes):return hashlib.sha256(raw).hexdigest()

def make():
    z=zipfile.ZipFile(ARCHIVE)
    blob=z.read(ENTRY)
    with np.load(io.BytesIO(blob)) as n:
        J=n['momentJacobian'].copy();names=n['actuatorNames'].astype(str).tolist();dofs=n['dofNames'].astype(str).tolist()
        times=n['sourceTimesS'].copy();cases=n['cases'].astype(str).tolist()
    assert J.shape==(94,84,102) and np.isfinite(J).all()
    # Store exhaustive signed pair roles. Zero means 'not moment-coupled above
    # THIS threshold in THESE recorded states', not 'independent in all poses'.
    pair_same=np.zeros((84,84,102),dtype=np.uint8)
    pair_opp=np.zeros_like(pair_same)
    for j in range(102):
        v=J[:,:,j];valid=np.abs(v)>THRESHOLD
        for row in range(94):
            mask=np.logical_and(valid[row,:,None],valid[row,None,:]);sign=v[row,:,None]*v[row,None,:]
            pair_same[:,:,j]+=np.logical_and(mask,sign>0).astype(np.uint8)
            pair_opp[:,:,j]+=np.logical_and(mask,sign<0).astype(np.uint8)
    assert int(pair_opp.diagonal(axis1=0,axis2=1).sum())==0
    assert np.array_equal(pair_same,pair_same.transpose(1,0,2))
    assert np.array_equal(pair_opp,pair_opp.transpose(1,0,2))
    assert np.max(pair_same.astype(int)+pair_opp.astype(int))<=94
    np.savez_compressed(ROOT/'ALL_84x84x102_SIGNED_MUSCLE_PAIR_STATE_COUNTS.npz',same_sign_states=pair_same,
        opposing_sign_states=pair_opp,actuator_names=np.array(names),dof_names=np.array(dofs),
        state_count=np.array([94]),min_abs_moment_m_per_rad=np.array([THRESHOLD]))
    records=[];summary=[]
    for side in ('left','right'):
        j=dofs.index(f'{side}Elbow.flexionExtension')
        for flex in ('biceps','brachialis','brachioradialis'):
            a=names.index(f'm_{side}_{flex}');b=names.index(f'm_{side}_triceps')
            idx=(a,b)
            flex_moment=J[:,a,j];ext_moment=J[:,b,j]
            assert np.all(flex_moment<-THRESHOLD) and np.all(ext_moment>THRESHOLD)
            # Counterfactual *tensions in Newtons*, not activations.
            # Muscle actuator force in native convention is negative tension;
            # zero joint moment: J_f*1N + J_t*F_t = 0.
            ratio=-flex_moment/ext_moment
            compensated=J[:,a,:]+ratio[:,None]*J[:,b,:]
            assert np.max(abs(compensated[:,j]))<1e-14
            for k in range(94):
                v=compensated[k].copy();v[j]=0.
                shoulder=[dofs.index(f'{side}Shoulder.{axis}') for axis in ('flexionExtension','abductionAdduction','axialRotation')]
                records.append({'case':cases[k],'timeS':float(times[k]),'stateIndex':k,'side':side,'flexor':names[a],
                    'extensor':names[b],'elbowDof':dofs[j],
                    'flexorMomentMPerRad':float(flex_moment[k]),'extensorMomentMPerRad':float(ext_moment[k]),
                    'extensorTensionNPer1NFlexor':float(ratio[k]),
                    'elbowResidualNmPer1NFlexor':float(compensated[k,j]),
                    'shoulderLeakNmPer1NFlexor':float(np.linalg.norm(v[shoulder])),
                    'allOtherDofLeakNmPer1NFlexor':float(np.linalg.norm(v))})
            summary.append({'side':side,'flexor':names[a],'extensor':names[b],
                'bothOpposeCount':int(pair_opp[a,b,j]),'bothSameCount':int(pair_same[a,b,j]),
                'extensorTensionPer1NFlexorMin':float(ratio.min()),
                'extensorTensionPer1NFlexorMedian':float(np.median(ratio)),
                'extensorTensionPer1NFlexorMax':float(ratio.max()),
                'maxElbowBalanceResidualNm':float(np.max(abs(compensated[:,j]))),
                'maxResidualOtherDofNmPer1NFlexor':float(np.max(np.linalg.norm(np.delete(compensated,j,axis=1),axis=1)))})
    with (ROOT/'ELBOW_EQUAL_NET_TORQUE_COACTIVATION_94_POSES.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=records[0].keys());w.writeheader();w.writerows(records)
    (ROOT/'ELBOW_COACTIVATION_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    # Exact semantic anchors with source lines and individual source digests.
    witnesses=[]
    for filename,start,end,needle,semantic in WITNESS_SPECS:
        p=SRC/filename;raw=p.read_bytes();lines=raw.decode().splitlines()
        assert 1<=start<=end<=len(lines),(filename,start,end,len(lines))
        excerpt='\n'.join(lines[start-1:end]);assert needle in excerpt,(filename,needle)
        witnesses.append({'sourceFile':filename,'sourceSHA256':sha(raw),'startLine':start,'endLine':end,
            'semantic':semantic,'literalExcerptSHA256':sha(excerpt.encode()),'evidenceExcerpt':excerpt})
    (ROOT/'COORDINATION_SOURCE_WITNESSES.json').write_text(json.dumps(witnesses,indent=2)+'\n')
    receipt={'schema':'lucid.semantic-atlas.v013.muscle-coordination-source-and-mechanics.v1',
        'sourceV010Archive':ARCHIVE.name,'sourceV010SHA256':sha(ARCHIVE.read_bytes()),
        'sourceMomentEntry':ENTRY,'sourceMomentBytesSHA256':sha(blob),
        'nativeMeasurementStates':94,'nativeMuscles':84,'nativeDofs':102,'stateWisePairDofSlots':84*84*102*94,
        'storedPairDofBins':84*84*102,'pairSignThresholdMPerRad':THRESHOLD,
        'independentFlexorExtensorPairs':len(summary),'measuredCoactivationRows':len(records),
        'maxCounterfactualElbowMomentResidualNmPer1N':max(x['maxElbowBalanceResidualNm'] for x in summary),
        'sourceWitnesses':len(witnesses),
        'testScope':'frozen V010 native moment Jacobians; static mechanical tension counterfactual; no new MuJoCo rollout',
        'limitations':['no new excitation trajectory, joint stiffness, contact outcome, or dynamic coactivation validated',
                       'moment arms cannot be substituted for muscle gains, passive tension or activation','geometrically balancing elbow does not necessarily balance shoulder'],
        'frozenExecutablesUnchanged':True,'githubActions':False}
    (ROOT/'V013_AUDIT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt,summary

if __name__=='__main__':
    r,s=make();print(json.dumps(r,indent=2));print(json.dumps(s,indent=2))
