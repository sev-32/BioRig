#!/usr/bin/env python3
"""R579 constrained muscle synergy atop the unmodified R577 native plant.

A different weight for each independently named actuator, identical R577
proprioceptive trigger, ramp, safety gate and base R574 muscle controller.
Weights were chosen after a same-state *offline* probe; the online controller
never observes probe outcomes or future trajectories. Development-only.
"""
import sys
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/'r577'),str(HERE.parent/'r576')]
import r577_tonic_support as r577
import run_r551 as r551

PROFILES={'r577_full':(1.,1.,1.,1.),
          'hip_only':(0.,0.,1.,0.),
          'hip_trunk_20pct':(.2,.2,1.,.2),
          'hip_trunk_50pct':(.5,.5,1.,.5)}

class Synergy(r577.TonicSupport):
    def __init__(self, model, profile):
        super().__init__(model)
        if profile not in PROFILES:raise ValueError(profile)
        self.profile=profile
        self.weights=PROFILES[profile]
        self.actualChannelIntegral=0.
        self.actualSquaredIntegral=0.
        masks={}
        for side in ('left','right'):
            mask=np.zeros(model.nu)
            for name,weight in zip(r551.GROUPS[side+'_lateral'],self.weights):
                actuator=mj.mj_name2id(model,mj.mjtObj.mjOBJ_ACTUATOR,name)
                if actuator<0:raise KeyError(name)
                mask[actuator]=weight
            masks[side]=mask
        self.masks=masks

    def update(self,t,obs):
        super().update(t,obs)
        self.actualChannelIntegral+=float(self.command.sum())*.04
        self.actualSquaredIntegral+=float(self.command@self.command)*.04


def rollout(scene, choice, profile, seconds=12., trace=False,
            stop_on_hazard=False):
    """Reuses the verified R577 loop with temporary, exception-safe injection.

    Do not concurrently call this function from threads (temporary module ref).
    Each real MuJoCo physical rollout reinstantiates and clones its own state.
    """
    if profile not in PROFILES:raise ValueError(profile)
    if choice not in ('none','R28'):raise ValueError(choice)
    original=r577.TonicSupport
    controllers=[]
    def build(model):
        c=Synergy(model,profile)
        controllers.append(c)
        return c
    try:
        r577.TonicSupport=build
        outcome=r577.rollout(scene,choice,seconds=seconds,tonic=True,
                  trace_interval=.1 if trace else 1.,stop_on_hazard=stop_on_hazard)
    finally:
        r577.TonicSupport=original
    assert len(controllers)==1
    controller=controllers[0]
    result={**outcome,'schema':'lucid.r579.synergy-research.v1',
            'profile':profile,'weights':PROFILES[profile],
            'sumChannelExcitationSeconds':controller.actualChannelIntegral,
            'sumSquaredChannelExcitationSeconds':controller.actualSquaredIntegral,
            'researchOnly':True}
    if not trace:result.pop('trace',None)
    return result


def main():
    import argparse,json
    p=argparse.ArgumentParser()
    p.add_argument('--scene',type=int,default=0)
    p.add_argument('--seconds',type=float,default=12.)
    p.add_argument('--profile',choices=list(PROFILES),default='hip_only')
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--trace',action='store_true')
    p.add_argument('--stop-on-hazard',action='store_true')
    a=p.parse_args()
    agent,_,lock=r577.baseline.frozen.frozen()
    scene=r577.baseline.frozen.scenarios(lock)[a.scene]
    pb,ref,neutral,saved=r577.phys.paired_scene(scene['seatHalfWidthM'],scene['friction'])
    obs=r577.phys.initial_observation(pb,saved,ref,neutral,scene['forceN']*scene['direction'])
    choice=agent.decide(obs,'restore_supported_equilibrium')['choice']
    result=rollout(scene,choice,a.profile,a.seconds,a.trace,a.stop_on_hazard)
    out={'sceneIndex':a.scene,'scene':scene,'R574SensedDecision':choice,'outcome':result}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,allow_nan=False))
    print('R579',a.profile,'scene',a.scene,'seconds',result['observedHorizonS'],
          'hazard',result['hazard'],'settled',result['settledAtEnd'],
          'x',result['finalX'],'effort',result['sumChannelExcitationSeconds'])
if __name__=='__main__':main()
