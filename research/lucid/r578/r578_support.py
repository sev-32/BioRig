"""Measured mass-centre vs active seat/floor support in world coordinates.

Independent fundamental: this module contains no policy, no muscle actuation,
no knowledge of disturbance metadata, and no future state. Metres/Newtons only.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
import numpy as np
import mujoco as mj

@dataclass(frozen=True)
class SupportMeasurement:
    comX_m:float
    centerOfPressureX_m:float
    comRelativeToPressure_m:float
    measuredNormalLoad_N:float
    contactCount:int
    valid:bool


def measure(model:mj.MjModel, data:mj.MjData)->SupportMeasurement:
    masses=np.asarray(model.body_mass, dtype=float)
    total=float(masses.sum())
    if total<=0 or not np.isfinite(total):
        raise ValueError('positive modeled body mass required')
    com=float(masses@np.asarray(data.xipos)[:,0]/total)
    weighted=0.
    total_force=0.
    count=0
    force=np.zeros(6,dtype=float)
    for i in range(data.ncon):
        c=data.contact[i]
        # Only externally-supported contacts, not internal body collisions.
        if 0 not in (c.geom1,c.geom2) and 1 not in (c.geom1,c.geom2):
            continue
        mj.mj_contactForce(model,data,i,force)
        load=max(0.,float(force[0]))
        if load<=0:continue
        weighted+=load*float(c.pos[0])
        total_force+=load
        count+=1
    valid=total_force>1e-8
    cop=float(weighted/total_force) if valid else float('nan')
    return SupportMeasurement(com, cop, com-cop if valid else float('nan'),total_force,count,valid)
