#!/usr/bin/env python3
"""R581 frozen-state anatomical actuator moment and causal response identification.

The native 84-muscle plant and R580 controller remain unmodified. Probe acts
on independent clones of ONE supported t=8s state. Online controller never
sees probe outcomes. Force-dependent qfrc is generalized force in SI units;
rotational DOFs measure N*m and are not directly interchangeable with x motion.
"""
from __future__ import annotations
import sys,json,argparse,hashlib
from pathlib import Path
import numpy as np
import mujoco as mj
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/'r580'),str(HERE.parent/'r578')]
import r580_adaptive_synergy as base
from r578_support import measure
phy=base.phys
GROUPS={
    'none':(),
    'left_hip_medius':('m_left_gluteus_medius',),
    'left_QL_iliolumbar':('m_left_quadratus_lumborum_iliolumbar',),
    'left_QL_iliocostal':('m_left_quadratus_lumborum_iliocostal',),
    'left_external_oblique':('m_left_external_oblique',),
    'right_hip_medius':('m_right_gluteus_medius',),
    'right_external_oblique':('m_right_external_oblique',),
    'left_hip_QL':('m_left_gluteus_medius','m_left_quadratus_lumborum_iliolumbar'),
    'left_hip_oblique':('m_left_gluteus_medius','m_left_external_oblique'),
}
JOINTS=('leftHip.abductionAdduction','rightHip.abductionAdduction',
        'spine01.lateralBend','spine02.lateralBend')

def actuator_ids(model,names):
    ids=[]
    for name in names:
        i=mj.mj_name2id(model,mj.mjtObj.mjOBJ_ACTUATOR,name)
        if i<0:raise ValueError(name)
        ids.append(i)
    return ids

def moment_snapshot(pb,d):
    """Per-unit-actual-actuator force moment arm, not torque estimate."""
    m=pb.model
    # MuJoCo 3.15 stores actuator moments in CSR sparse format: rows = actuators.
    matrix=np.zeros((m.nu,m.nv),dtype=float)
    for a in range(m.nu):
        lo=int(d.moment_rowadr[a]); nn=int(d.moment_rownnz[a])
        matrix[a,np.asarray(d.moment_colind[lo:lo+nn],dtype=int)]=d.actuator_moment[lo:lo+nn]
    dofs={name:int(m.jnt_dofadr[mj.mj_name2id(m,mj.mjtObj.mjOBJ_JOINT,name)]) for name in JOINTS}
    result={}
    for name,names in GROUPS.items():
        if not names:continue
        part=[]
        for n in names:
            a=actuator_ids(m,(n,))[0]
            part.append({'actuator':n,'actuatorIndex':a,
              'momentArmAtState_m':{joint:float(matrix[a,dof]) for joint,dof in dofs.items()},
              'actuatorForce_N':float(d.actuator_force[a]),
              'generalizedTorqueAtState_Nm':{joint:float(matrix[a,dof]*d.actuator_force[a]) for joint,dof in dofs.items()}})
        result[name]=part
    return result

def setup_frozen_state(at=8.):
    scene={'seatHalfWidthM':.131,'friction':.82,'forceN':0.,'direction':1.}
    pb,ref,neutral,saved=phy.paired_scene(scene['seatHalfWidthM'],scene['friction'])
    d=mj.MjData(pb.model)
    mj.mj_copyData(d,pb.model,saved)
    initial=phy.plant.sha_state(pb.data)
    ctl=base.AdaptiveSynergy(pb.model,{**base.CONFIG,'triggerPositionM':.0284,
       'fullRecruitAtM':.0308,'lookaheadS':1.,'hipMax':.029})
    for k in range(round(at/base.DT)):
        t=k*base.DT
        if k%round(.04/base.DT)==0:ctl.update(t,phy.sense(pb,d))
        phy.plant.step_perturbed(pb,d,ref,neutral,ctl.output(),np.zeros(3))
    assert phy.plant.sha_state(pb.data)==initial
    return pb,ref,neutral,d,initial

def run(at=8.,horizon=.5,dose=.025):
    pb,ref,neutral,saved,original=setup_frozen_state(at)
    moment=moment_snapshot(pb,saved)
    start_obs=phy.sense(pb,saved)
    start_support=measure(pb.model,saved)
    state_digest=hashlib.sha256(np.concatenate((saved.qpos,saved.qvel,saved.act,saved.ctrl)).tobytes()).hexdigest()
    outcomes=[]
    for name,names in GROUPS.items():
        d=mj.MjData(pb.model);mj.mj_copyData(d,pb.model,saved)
        ids=actuator_ids(pb.model,names)
        delta=np.zeros(pb.model.nu)
        delta[ids]=dose
        max_arm=0.
        for k in range(round(horizon/base.DT)):
            if k%10==0:max_arm=max(max_arm,phy.sense(pb,d)['armsSeatN'])
            phy.plant.step_perturbed(pb,d,ref,neutral,delta,np.zeros(3))
        o=phy.sense(pb,d); s=measure(pb.model,d)
        outcomes.append({'name':name,'channels':len(ids),
             'rootX_m':float(o['xPosition']),'rootVx_mps':float(o['xSpeed']),
             'rootTilt_deg':float(o['rootTiltDeg']),
             'comX_m':s.comX_m,'supportCOPx_m':s.centerOfPressureX_m,
             'comRelativeToCOP_m':s.comRelativeToPressure_m,
             'supportLoad_N':s.measuredNormalLoad_N,'armPeak_N':float(max_arm)})
        print(name,o['xPosition'],o['xSpeed'],o['rootTiltDeg'],flush=True)
    blank=outcomes[0]
    for o in outcomes:
        for field in ('rootX_m','rootVx_mps','rootTilt_deg','comX_m','comRelativeToCOP_m'):
            o['delta_'+field]=o[field]-blank[field]
    report={'schema':'lucid.r581.same-state-moment-and-physical-probe.v1',
        'researchOnly':True,'horizonS':horizon,'atS':at,'doseEachActiveChannel':dose,
        'unmodifiedPlantSHA256':original,'clonedStateSHA256':state_digest,
        'initialObservation':start_obs,'initialSupport':vars(start_support),
        'momentAtStartingState':moment,'experiments':outcomes,
        'notes':['Moment arms are local kinematic mappings, not commanded torque','Moment magnitudes multiplied by measured actuator_force give current N*m at rotating DOFs','Constant-dose probe measures dynamic effect over horizon, not asymptotic stability','Probe results are offline and may not enter online controller as a future-state oracle']}
    target=HERE/'R581_NATIVE_MOMENT_PROBE.json'
    target.write_text(json.dumps(report,indent=2,allow_nan=False))
    print('WROTE',target)
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--at',type=float,default=8.);p.add_argument('--seconds',type=float,default=.5)
    q=p.parse_args();run(q.at,q.seconds)
