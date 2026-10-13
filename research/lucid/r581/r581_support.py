"""R581 measured support geometry: contact pressure, COM and reaction loads.

Pure observer: reads MuJoCo state without modifying it. Coordinates are world
X in metres; forces are N; only seat/ground normal's world-Y component counts
as vertical support. The 1D contact interval is NOT a stability polygon proof.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
import numpy as np
import mujoco as mj

@dataclass(frozen=True)
class SupportState:
    comX_m:float
    copX_m:float
    comMinusCop_m:float
    normalVertical_N:float
    contactMinX_m:float
    contactMaxX_m:float
    externalContactCount:int
    valid:bool

def sense_support(model,data):
    masses=np.asarray(model.body_mass,float)
    total=float(masses.sum())
    if total<=0 or not np.isfinite(total):raise ValueError('bad total mass')
    com=float(masses@np.asarray(data.xipos)[:,0]/total)
    ext={mj.mj_name2id(model,mj.mjtObj.mjOBJ_GEOM,n) for n in ('ground','research_seat')}
    if -1 in ext:raise ValueError('external support geom not found')
    reaction=np.zeros(6);load_sum=weighted=0.;contactxs=[];count=0
    for i in range(data.ncon):
        c=data.contact[i]
        if not (c.geom1 in ext or c.geom2 in ext):continue
        mj.mj_contactForce(model,data,i,reaction)
        # First 3 numbers in MuJoCo contact.frame give world normal direction.
        vert=abs(float(c.frame[1]))
        load=max(0.,float(reaction[0]))*vert
        if load<1e-9:continue
        x=float(c.pos[0])
        load_sum+=load;weighted+=x*load;contactxs.append(x);count+=1
    valid=load_sum>1e-6
    cop=weighted/load_sum if valid else float('nan')
    return SupportState(com,cop,com-cop if valid else float('nan'),load_sum,
                        min(contactxs) if valid else float('nan'),
                        max(contactxs) if valid else float('nan'),count,valid)
