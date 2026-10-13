#!/usr/bin/env python3
"""24s native R589 muscle plant, 12s physical settling -> 12s steady-state camera.

No pose keyframes, no joint teleportation, no seat-geometry or material edits.
The rig physically traverses the complete 24 seconds in MuJoCo; the 12-24s
segment is only redefined as the next **experiment** time window.
The full 0-12s warmup remains part of documented runtime and event history.
"""
from __future__ import annotations
import os,sys,json,hashlib,time
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
CANDIDATES=[HERE.parent/'r589',
    Path(os.environ.get('BIORIG_RESEARCH_ROOT','/does-not-exist'))/'r589',
    Path('/mnt/data/BioRig_R589_ACTIVE_ARM_LANDING')]
SOURCE_DIR=next((x for x in CANDIDATES if (x/'r589_arm_landing.py').is_file()),None)
if SOURCE_DIR is None:
    raise FileNotFoundError('R589 source must be in a sibling research/lucid/r589 directory')
sys.path.insert(0,str(SOURCE_DIR))
import r589_arm_landing as reference
T_SETTLE=12.;T_FINAL=24.;FRAME_INTERVAL=.4
samples=[];states=[];times=[];head=[]

def on_frame(pb,d,t,arms):
    if t<T_SETTLE-1e-8 or t>T_FINAL+1e-8:return
    # R589 callback every 0.1s; capture actual steps on the .4s grid.
    if abs(t/FRAME_INTERVAL-round(t/FRAME_INTERVAL))>1e-6: return
    states.append({'qpos':d.qpos.copy(),'qvel':d.qvel.copy(),'act':d.act.copy(),
                   'timeS':t,'stateSHA256':hashlib.sha256(d.qpos.tobytes()+d.qvel.tobytes()+d.act.tobytes()).hexdigest()})
    times.append(t)
    samples.append({'tS':round(t,3),'leftN':float(arms['left']['contactN']),
      'rightN':float(arms['right']['contactN']),
      'leftGeoms':arms['left']['geoms'],'rightGeoms':arms['right']['geoms']})
    head.append(reference.r586.r585.angle(pb,d))

start=time.monotonic()
result=reference.run(T_FINAL,candidate=True,arm_params=reference.VERIFIED_PROFILE,
                     on_frame=on_frame,stride=5,save_trace=True)
assert len(states)==31,(len(states),times)
assert abs(times[0]-12)<1e-7 and abs(times[-1]-24)<1e-7
assert all(np.isfinite(s['qpos']).all() for s in states)
npz=HERE/'R590_SETTLED_CONTINUOUS_NATIVE_QPOS.npz'
np.savez_compressed(npz,qpos=np.stack([s['qpos'] for s in states]),qvel=np.stack([s['qvel'] for s in states]),
                     act=np.stack([s['act'] for s in states]),timeS=np.array(times))
# Measure transitions from native high-rate R589 10-ms contact samples.
last={'left':None,'right':None};events={'left':0,'right':0};peaks={'left':0.,'right':0.}
for row in result['samples']:
    if row['tS']<12-1e-6:continue
    for side in ('left','right'):
        load=float(row['arms'][side]['contactN']); peaks[side]=max(peaks[side],load)
        touching=load>1.
        if last[side] is not None and touching!=last[side]:events[side]+=1
        last[side]=touching
initial12=next(row for row in result['samples'] if abs(row['tS']-12)<1e-6)
metric={'schema':'lucid.r590.post-settling-continuation.v1','plantSource':'R589 exact native source; no model modifications',
        'warmupS':12,'measurementS':12,'totalPhysicalS':24,
        'initialArmContactN':{s:initial12['arms'][s]['contactN'] for s in ('left','right')},
        'measuredPeakArmN':peaks,'contactTransitions12to24':events,
        'full24PeakArmN':result['peakArmN'],'full24MaxHeadDeg':result['maxHeadDeg'],
        'full24PelvisX_m':result['finalPelvisX_m'],
        '12to24MaxHeadDeg':max(head),'12to24FinalHeadDeg':head[-1],
        'frames':len(states),'npzSHA256':hashlib.sha256(npz.read_bytes()).hexdigest(),
        'qposSHA256':[hashlib.sha256(s['qpos'].tobytes()).hexdigest() for s in states],
        'sampledContactForceN':samples,'wallSeconds':round(time.monotonic()-start,2),
        'reproducibilityNote':'No reset or teleport at t=12; continuous 24s native MuJoCo physics. This is a steady-state observation window, not a redesigned starting pose.'}
(HERE/'R590_SETTLED_12TO24_NATIVE_RECEIPT.json').write_text(json.dumps(metric,indent=2,allow_nan=False))
print('R590_NATIVE_24S_COMPLETE',json.dumps({k:metric[k] for k in ('measuredPeakArmN','contactTransitions12to24','full24MaxHeadDeg','12to24MaxHeadDeg','full24PelvisX_m','wallSeconds')},indent=2),flush=True)
