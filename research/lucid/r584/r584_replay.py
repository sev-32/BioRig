#!/usr/bin/env python3
"""R584 exact same-scene no-slip replay using the frozen R583 measurement loop.

Test harness only. `r583_friction_probe` remains unchanged. The temporary
injection is restored in finally; execute serially (not thread-safe).
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/'r583'),str(HERE.parent/'r582'),str(HERE.parent/'r580'),str(HERE.parent/'r577')]
import r583_friction_probe as legacy
from r584_solver_config import configure


def replay(seconds=12.,iterations=6,render=False):
    previous=legacy.set_friction
    try:
        legacy.set_friction=lambda model,_mode:configure(model,iterations)
        result,frames=legacy.run('original',seconds,render=render)
    finally:
        legacy.set_friction=previous
    result['noSlipIterations']=iterations
    result['researchOnly']=True
    return result,frames


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--seconds',type=float,default=12.)
    p.add_argument('--iterations',type=int,default=6)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    result,_=replay(args.seconds,args.iterations)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,allow_nan=False))
    last=result['trace'][-1]
    print('R584',args.seconds,'s, no-slip',args.iterations,'end x',result['endX_m'],
          'seat slip',last['contacts']['research_seat']['loadedSlipMps'],
          'foot slip',last['contacts']['ground']['loadedSlipMps'])
if __name__=='__main__':main()
