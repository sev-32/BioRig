#!/usr/bin/env python3
"""Persist reproducible *native MuJoCo qpos* for SKIN78 rendering separately.
Physical states are captured during continuous simulation, not reconstructed
from pose keys, not interpolated, not altered after simulation.
"""
import os,json,sys,hashlib,time
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from r589_arm_landing import run
profile={'target_deg':-28.,'arrival_s':1.2,'kp':20.,'kd':8.,'max_extra':.2,
    'release_at':1.2,'fade_duration':.7,
    'side_profiles':{'left':{'target_deg':-28.,'arrival_s':1.1,'kp':16.,'kd':8.,'max_extra':.18}}}
for label,candidate in [('R587',False),('R589',True)]:
    ts=[];qs=[];metrics=[]
    def cb(pb,d,t,arms):
        n=round(t*10)
        if t<=3.000001 and n%2!=0:return
        if t>3.000001 and n%6!=0:return
        ts.append(t);qs.append(d.qpos.copy());
        metrics.append({'timeS':round(t,3),'leftArmLoadN':float(arms['left']['contactN']),
        'rightArmLoadN':float(arms['right']['contactN'])})
    t0=time.monotonic()
    out=run(12.,candidate=candidate,arm_params=profile if candidate else None,on_frame=cb)
    assert len(ts)==31,(label,len(ts),ts)
    assert np.all(np.isfinite(qs))
    npz=HERE/f'{label}_NATIVE_12S_QPOS.npz'
    np.savez_compressed(npz,qpos=np.stack(qs),timeS=np.asarray(ts,dtype=float))
    out.pop('samples',None)
    document={'schema':'lucid.r589.actual-native-physics-state.v1','mode':label,
        'recordedEveryFrameFromNativeMuJoCo':True,'noPoseInterpolation':True,
        'frameSHA256':[hashlib.sha256(x.tobytes()).hexdigest() for x in qs],
        'snapshots':metrics,'physicsSummary':out,
        'npzFile':npz.name,'npzSHA256':hashlib.sha256(npz.read_bytes()).hexdigest()}
    (HERE/f'{label}_NATIVE_12S_CAPTURE_RECEIPT.json').write_text(json.dumps(document,indent=2))
    print('CAPTURE_OK',label,'FRAME',len(qs),'peak',out['peakArmN'],'head',out['maxHeadDeg'],
        'wall',round(time.monotonic()-t0,2),'sha',document['npzSHA256'],flush=True)
