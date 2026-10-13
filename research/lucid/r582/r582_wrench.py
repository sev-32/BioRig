"""R582 | Pure observation of *signed* native external contact wrenches.

All quantities are world frame, SI metres/Newtons/Newton-metres. MuJoCo's
contact frame uses rows (normal, tangent1, tangent2) and contact forces are
for geom2; negate if the externally supported body is geom1. No model or data
mutation. World +Y is vertical in this specific inherited seated model.

A projection of the 3D resultant on world Y=0 is a *virtual equivalent
reaction*, not a dynamic-ZMP claim or a physical contact point when seat and
floor have different heights. It may lie outside the actual contact envelope.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import mujoco as mj

EXTERNAL_GEOMS=('research_seat','ground')

@dataclass(frozen=True)
class ContactWrench:
    com_world_m:tuple[float,float,float]
    force_on_body_world_N:tuple[float,float,float]
    moment_about_com_world_Nm:tuple[float,float,float]
    moment_about_projection_origin_world_Nm:tuple[float,float,float]
    pressure_centroid_x_m:float
    projected_reaction_x_at_plane_m:float
    com_minus_pressure_m:float
    com_minus_projected_reaction_m:float
    normal_vertical_reaction_N:float
    total_lateral_shear_N:float
    support_contact_count:int
    min_contact_x_m:float
    max_contact_x_m:float
    valid:bool
    valid_projection:bool


def world_wrench(frame, local_six, ext_is_geom1):
    """World force and couple acting **on the non-external geom**.

    Rotation: contact.frame rows are expressed in world coordinates.
    mj_contactForce returns the force/couple on geom2. When the external
    support is geom2, reaction on geom1 is the negative wrench.
    """
    R=np.asarray(frame,dtype=float).reshape(3,3)
    six=np.asarray(local_six,dtype=float).reshape(6)
    sign=1. if ext_is_geom1 else -1.
    return sign*(R.T@six[:3]),sign*(R.T@six[3:])


def sense_wrench(model:mj.MjModel,data:mj.MjData,projection_y_m=0.0)->ContactWrench:
    total_mass=float(np.sum(model.body_mass))
    if total_mass<=0 or not np.isfinite(total_mass):raise ValueError('nonpositive total mass')
    com=np.asarray(model.body_mass)@np.asarray(data.xipos)/total_mass
    externals={mj.mj_name2id(model,mj.mjtObj.mjOBJ_GEOM,n) for n in EXTERNAL_GEOMS}
    if -1 in externals:raise ValueError('required named seat or ground geom not found')
    force=np.zeros(3,dtype=float);about_com=np.zeros(3,dtype=float)
    local=np.zeros(6,dtype=float)
    vertical_sum=weighted_x=0.
    positions=[];count=0
    for i in range(data.ncon):
        c=data.contact[i]
        ext1=c.geom1 in externals;ext2=c.geom2 in externals
        if ext1==ext2:continue  # exclude internal body collisions and support-support
        mj.mj_contactForce(model,data,i,local)
        f,couple=world_wrench(c.frame,local,ext1)
        force+=f
        point=np.asarray(c.pos,dtype=float)
        about_com+=np.cross(point-com,f)+couple
        # Load-centroid uses only *upward* vertical force; tangential friction
        # acts through the true wrench but is not a pressure normal weight.
        upward=max(0.,float(f[1]))
        if upward>1e-9:
            count+=1
            positions.append(float(point[0]))
            vertical_sum+=upward
            weighted_x+=upward*point[0]
    valid=bool(count>0 and vertical_sum>1e-6)
    pressure=float(weighted_x/vertical_sum) if valid else float('nan')
    reference=np.array([0.,float(projection_y_m),0.])
    about_origin=about_com+np.cross(com-reference,force)
    # For a point reaction [x,0,z] on projection plane, M_z = x*F_y.
    valid_projection=bool(valid and force[1]>1e-6)
    projected=float(about_origin[2]/force[1]) if valid_projection else float('nan')
    return ContactWrench(tuple(float(v) for v in com),tuple(float(v) for v in force),
       tuple(float(v) for v in about_com),tuple(float(v) for v in about_origin),
       pressure,projected,float(com[0]-pressure) if valid else float('nan'),
       float(com[0]-projected) if valid_projection else float('nan'),
       vertical_sum,float(force[0]),count,min(positions) if valid else float('nan'),
       max(positions) if valid else float('nan'),valid,valid_projection)
