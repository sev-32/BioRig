#!/usr/bin/env python3
"""R587 physical and rendered-state acceptance gate.

Explicitly prevents past false positives from pelvis-only "settled" labels.
Numeric pass does not imply visual, anatomical or clinical validation.
"""
from __future__ import annotations
from pathlib import Path
import json,math,hashlib,argparse

LIMITS={'headToThoraxDeg':5.,'pelvisTiltDeg':45.,'armSeatN':50.,
        'otherFloorN':50.,'absPelvisX_m':.030}

def inspect_native(result, minimum_duration=24.):
    readings=result.get('samples',[])
    if not readings: raise ValueError('Missing physical state readings')
    if not result.get('secs',0)>=minimum_duration:raise ValueError('Insufficient duration')
    if not len(readings)>=int(minimum_duration/.2):raise ValueError('Sample density too sparse')
    if abs(readings[-1]['timeS']-result['secs'])>1e-6:raise ValueError('No endpoint sample')
    head=max(float(x['headThoraxDeg']) for x in readings)
    tilt=max(abs(float(x['rootTiltDeg'])) for x in readings)
    arm=max(float(x['seatArmsN']) for x in readings)
    floor=max(float(x['otherFloorN']) for x in readings)
    root=max(abs(float(x['pelvisX_m'])) for x in readings)
    quant={'headToThoraxDeg':head,'pelvisTiltDeg':tilt,'armSeatN':arm,
           'otherFloorN':floor,'absPelvisX_m':root}
    if not all(math.isfinite(v) for v in quant.values()):raise ValueError('Nonfinite physics')
    gates={k:quant[k]<limit for k,limit in LIMITS.items()}
    gates['optimizerZeroFallbacks']=result.get('optimizerFallbacks',-1)==0
    gates['optimizerZeroInfeasible']=result.get('optimizerInfeasibleSteps',-1)==0
    return {'schema':'lucid.r587.full-body-physics-gate.v1','durationS':result['secs'],
        'limits':LIMITS,'observedMax':quant,'gates':gates,
        'physicalQuantitiesPass':all(gates.values()),'visualReview':'REQUIRED',
        'fullBodyBiomechanicsApproved':False,
        'caveats':['Sampled measurements do not establish anatomical fatigue or muscle energetics',
                   'Skin78 full-motion must be inspected before visual approval',
                   'Seat/foot support load continuity and true contact microslip need separate testing']}

def check_render(physics,render,animation_path):
    state=render.get('nativeFrames',[])
    if len(state)!=61:raise ValueError('Expected 61 real time-sampled SKIN78 frames over 24s')
    if any(abs(s['timeS']-i*.4)>1.e-6 for i,s in enumerate(state)):
        raise ValueError('Native frame times absent or interpolated')
    if render.get('originalSkinSHA256')!='88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10':
        raise ValueError('Not the original locked SKIN78 mesh')
    if abs(float(render.get('pushN',float('nan')))-float(physics.get('pushN',float('nan'))))>1e-9:
        raise ValueError('Physical render uses different push than independent replay')
    samples={round(float(r['timeS']),3):r for r in physics['samples']}
    for s in state:
        if len(s['nativeQposSHA256'])!=64:raise ValueError('Missing native MuJoCo qpos digest')
        t=round(float(s['timeS']),3)
        physical=samples.get(t)
        if physical is None:raise ValueError('Rendered timestamp missing in independent native replay')
        if abs(s['headToTorsoDeg']-physical['headThoraxDeg'])>1e-6:
            raise ValueError('Rendered head posture disagrees with independent physics')
        if abs(s['pelvisX_m']-physical['pelvisX_m'])>1e-6:
            raise ValueError('Rendered pelvis posture disagrees with independent physics')
    file=Path(animation_path)
    sha=hashlib.sha256(file.read_bytes()).hexdigest()
    if sha!=render['animatedGIF_SHA256']:raise ValueError('Animated render hash mismatch')
    return {'nativeFrames':len(state),'rendererSHA256':sha,'continuousNativeTimelineValidated':True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--physics',type=Path,required=True)
    p.add_argument('--render-receipt',type=Path,required=True)
    p.add_argument('--animation',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    opts=p.parse_args()
    result=json.loads(opts.physics.read_text())
    render=json.loads(opts.render_receipt.read_text())
    gate=inspect_native(result)
    gate['render']=check_render(result,render,opts.animation)
    opts.out.write_text(json.dumps(gate,indent=2,allow_nan=False))
    print('24S Native Physics:',gate['physicalQuantitiesPass'], 'real SKIN78 frames:',gate['render']['nativeFrames'])

if __name__=='__main__':main()
