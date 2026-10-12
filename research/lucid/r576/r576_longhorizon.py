#!/usr/bin/env python3
"""R576: post-lock, sensed-state late-support research on the frozen R574 plant.

FROZEN R574/R575 source, model locks, training and physics are unmodified.
This experiment *adds* a separate R562-derived bounded support guard only when
requested, retaining the already selected R574 early action. Harness force,
scene width, future trajectories and counterfactual results are not observed by
online controllers. A 12-second safety result is NOT asymptotic stability.
"""
from __future__ import annotations
import argparse, json, sys, hashlib
from pathlib import Path
import numpy as np
import mujoco as mj

HERE = Path(__file__).resolve().parent
ROOT = HERE / 'runtime'
sys.path[:0] = [str(ROOT/'R574_INTENTION_AND_AVERSION'),
               str(ROOT/'R562_SETTLING_CONTROL')]
import r574_evaluate as frozen
import r562_settling as settling

phy = frozen.ctl.phy
DT = phy.DT
SAMPLE_STEPS = round(.020 / DT)
UPDATE_STEPS = round(.040 / DT)
assert (SAMPLE_STEPS, UPDATE_STEPS) == (10, 20)


def make_guard(model):
    """Reuse R562 measured drift trigger and bounded pulses; no new classifier."""
    rule = dict(settling.RULE)
    # A late guard cannot rewrite the frozen R574 60 ms choice or R28 waveform.
    rule['firstAfterS'] = 1.8
    return settling.SettlingCoordinator(model, 'neutral', rule=rule)


def branch(scene, selected, seconds=12., guarded=False, trace=False):
    if selected not in ('none', 'R28'):
        raise ValueError('Frozen R574 only permits none or R28')
    if seconds <= 0:
        raise ValueError('seconds must be positive')
    pb, ref, neutral, saved = phy.paired_scene(scene['seatHalfWidthM'], scene['friction'])
    original = phy.plant.sha_state(pb.data)
    d = mj.MjData(pb.model)
    mj.mj_copyData(d, pb.model, saved)
    early = phy.TimedPulse(pb.model, selected)
    guard = make_guard(pb.model) if guarded else None
    max_arm = max_floor = max_tilt = 0.
    loss = 0
    settled_run = longest = 0.
    sampled = []
    steps = round(seconds/DT)
    release = max((start+hold+.12 for start,group,hold,amp in early.profile),default=0.)
    for k in range(steps+1):
        t = k * DT
        if k % SAMPLE_STEPS == 0 or k == steps:
            obs = phy.sense(pb,d)
            max_arm = max(max_arm, obs['armsSeatN'])
            max_floor = max(max_floor, obs['otherFloorN'])
            max_tilt = max(max_tilt, obs['rootTiltDeg'])
            loss += int(obs['pelvisSeatN'] < 5. and obs['feetFloorN'] < 5.)
            # A pulse in progress invalidates settling even if posture looks quiet.
            active = bool(guard is not None and guard.active_since is not None)
            quiet = bool(t >= release+.16 and not active and phy.settle.is_settled(obs))
            settled_run = settled_run + .020 if quiet else 0.
            longest = max(longest,settled_run)
            if trace and (k % (SAMPLE_STEPS*5) == 0 or k==steps):
                sampled.append({'timeS':round(t,3), 'settledNow':quiet, **obs})
        if k == steps: break
        if k % UPDATE_STEPS == 0:
            observation = phy.sense(pb,d)  # explicitly CURRENT measurements
            early.update(t,observation)
            if guard is not None: guard.update(t,observation)
        extra = early.output() if guard is None else np.clip(early.output()+guard.output(),0.,.04)
        applied = scene['forceN']*scene['direction']
        push = np.array([applied if t<phy.plant.PUSH_S else 0.,0.,0.])
        phy.plant.step_perturbed(pb,d,ref,neutral,extra,push)
    assert original == phy.plant.sha_state(pb.data), 'original plant data was mutated'
    return {'schema':'lucid.r576.long-horizon-postlock.v1',
            'experimental':bool(guarded), 'frozenR574Choice':selected,
            'horizonS':seconds, 'initialSHA256':original,
            'peakRootTiltDeg':max_tilt, 'peakArmSeatN':max_arm,
            'peakOtherFloorN':max_floor, 'bothSupportLossSamples':loss,
            'hazard':bool(max_arm>=50 or max_floor>=50 or max_tilt>=45 or loss>=3),
            'settledAtEnd':bool(settled_run>=1.),
            'longestSettledS':longest, 'finalX':float(d.qpos[0]),
            'finalV':float(d.qvel[0]), 'finalTiltDeg':float(phy.plant.root_tilt_deg(pb,d)),
            'postlockSupportPulses':[] if guard is None else guard.pulses,
            'trace100ms':sampled if trace else None}


def compare(indices,seconds=12.,trace=False):
    agent, inherited, lock = frozen.frozen()
    scenes = frozen.scenarios(lock)
    results=[]
    for i in indices:
        scene = scenes[i]
        pb,ref,neu,saved = phy.paired_scene(scene['seatHalfWidthM'],scene['friction'])
        measured = phy.initial_observation(pb,saved,ref,neu,scene['forceN']*scene['direction'])
        selected = agent.decide(measured,'restore_supported_equilibrium')['choice']
        baseline=branch(scene,selected,seconds,False,trace)
        guarded=branch(scene,selected,seconds,True,trace)
        assert baseline['initialSHA256']==guarded['initialSHA256']
        results.append({'index':i,'scene':scene,'decision60ms':selected,
                        'baseline':baseline,'guarded':guarded})
        print(f"scene={i:02} action={selected:4} {seconds:g}s baseline hazard={baseline['hazard']} settled={baseline['settledAtEnd']} guard hazard={guarded['hazard']} settled={guarded['settledAtEnd']} pulses={len(guarded['postlockSupportPulses'])}",flush=True)
    return {'schema':'lucid.r576.postlock-paired-12s.v1',
            'researchOnly':True,'notFrozenPromotionEvidence':True,
            'horizonS':seconds,'indexSet':list(indices),
            'frozenR574LockSHA256':frozen.ctl.sha(ROOT/'R574_INTENTION_AND_AVERSION/R574_EVALUATION_LOCK.json'),
            'results':results}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--indices',type=int,nargs='+',default=list(range(14)))
    parser.add_argument('--seconds',type=float,default=12.)
    parser.add_argument('--trace',action='store_true')
    parser.add_argument('--out',type=Path,required=True)
    opt=parser.parse_args()
    data=compare(opt.indices,opt.seconds,opt.trace)
    opt.out.parent.mkdir(parents=True,exist_ok=True)
    opt.out.write_text(json.dumps(data,indent=2,allow_nan=False))
    print('WROTE',opt.out,flush=True)
