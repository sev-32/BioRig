#!/usr/bin/env python3
"""Local one-factor probe of native muscle authority at a cloned, supported state.

Only reads current MuJoCo state; probes are offline research and do not feed the
active policy. All branches share an identical saved state at t=8 seconds.
"""
import json, sys, hashlib
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/'r577'),str(HERE.parent/'r578'),str(HERE.parent/'r576')]
import r577_tonic_support as r577
import run_r551 as r551
from r578_support import measure
phys=r577.phys
DT=r577.DT

def groups(model):
    listed={
        'none':(),
        'full_lateral':r551.GROUPS['left_lateral'],
        'ql_iliolumbar':(r551.GROUPS['left_lateral'][0],),
        'ql_iliocostal':(r551.GROUPS['left_lateral'][1],),
        'hip_glut_medius':(r551.GROUPS['left_lateral'][2],),
        'external_oblique':(r551.GROUPS['left_lateral'][3],),
        'ql_pair':r551.GROUPS['left_lateral'][:2],
        'trunk_triplet':r551.GROUPS['left_lateral'][:2]+r551.GROUPS['left_lateral'][3:],
        'left_extension':r551.GROUPS['left_extension'],
        'right_extension':r551.GROUPS['right_extension'],
    }
    result={}
    for name,names in listed.items():
        mask=np.zeros(model.nu)
        for n in names:
            aid=mj.mj_name2id(model,mj.mjtObj.mjOBJ_ACTUATOR,n)
            if aid<0:raise KeyError(n)
            mask[aid]=1.
        result[name]=mask
    return result

def run_probes(at=8.,horizon=.8,dose=.025):
    scene={'seatHalfWidthM':.131,'friction':.82,'forceN':0.,'direction':1.}
    pb,ref,neutral,saved=phys.paired_scene(scene['seatHalfWidthM'],scene['friction'])
    d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
    warm=r577.TonicSupport(pb.model)
    for k in range(round(at/DT)):
        t=k*DT
        if k%r577.baseline.UPDATE_STEPS==0:
            warm.update(t,phys.sense(pb,d))
        phys.plant.step_perturbed(pb,d,ref,neutral,warm.output(),np.zeros(3))
    start_obs=phys.sense(pb,d)
    state=mj.MjData(pb.model);mj.mj_copyData(state,pb.model,d)
    print('probe state', {k:start_obs[k] for k in ('xPosition','xSpeed','rootTiltDeg','pelvisSeatN','feetFloorN')}, flush=True)
    rows=[]
    for name,mask in groups(pb.model).items():
        alt=mj.MjData(pb.model);mj.mj_copyData(alt,pb.model,state)
        add=dose*mask
        peakarm=0
        for k in range(round(horizon/DT)):
            # Constant action for short authority probing, not long-horizon policy.
            if k%10==0:
                peakarm=max(peakarm,float(phys.sense(pb,alt)['armsSeatN']))
            phys.plant.step_perturbed(pb,alt,ref,neutral,add,np.zeros(3))
        o=phys.sense(pb,alt)
        s=measure(pb.model,alt)
        rows.append({'name':name,'muscles':int(mask.sum()),'xM':o['xPosition'],
          'vxMps':o['xSpeed'],'tiltDeg':o['rootTiltDeg'],
          'seatN':o['pelvisSeatN'],'feetN':o['feetFloorN'],
          'maxArmSeatN':peakarm,'comPressureOffsetM':s.comRelativeToPressure_m})
        print(name, 'x=',round(o['xPosition'],7),'v=',round(o['xSpeed'],7),
              'tilt=',round(o['rootTiltDeg'],4),'arm=',round(peakarm,2),flush=True)
    anchor=next(row for row in rows if row['name']=='none')
    for row in rows:
        row['deltaXvsNoneM']=row['xM']-anchor['xM']
        row['deltaVvsNoneMps']=row['vxMps']-anchor['vxMps']
    doc={'schema':'lucid.r579.authority-probe.v1','scientificScope':'same-state local 0.8s perturbed muscle response',
       'decisionSource':'offline finite difference; no future state exposed to online policy',
       'startTimeS':at,'horizonS':horizon,'additionalExcitation':dose,'initialSHA256':phys.plant.sha_state(state),
       'initialObservation':start_obs,'rows':rows}
    out=HERE/'R579_NATIVE_AUTHORITY_PROBE.json'
    out.write_text(json.dumps(doc,indent=2,allow_nan=False))
    print('wrote',out,flush=True)
    return doc

if __name__=='__main__':run_probes()
