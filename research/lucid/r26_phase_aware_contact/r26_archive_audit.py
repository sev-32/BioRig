#!/usr/bin/env python3
"""Reproducible BioRig R26 observations directly from the uploaded R25 ZIP.
No dynamics executed; no mutations; no topology reconstruction.
Requires only Python standard library.
"""
import argparse, bisect, hashlib, json, zipfile
from pathlib import Path

PREFIX = 'LUCID_BioRig_Development/35_R25_CONTACT_FEASIBILITY/traces/'
CASES = {
 'baseline540':'r17r21R24R25neutral540skin_step_late_540',
 'guard540':'r17r21R24R25guard540skin_step_late_540',
 'guard270':'r17r21R24R25g100_270_step_late_270',
}
# Exploratory multi-signal thresholds: no physiological or out-of-sample validation.
CONFIG = {'x_m':0.15,'abs_vx_mps':0.25,'margin_m':-0.10,
          'abs_lumbar_deg':15.,'consecutive_samples':3}

def analyze_case(data, label):
 samples=data['samples'];summary=data['summary'];trans=summary['transitions'];
 transitions=[p['t'] for p in trans];prior=None; streak=0;first_alert=None;
 first_margin=None; minimum_margin=None; max_x=0; max_lum=0; alert_phase=None
 for p in samples:
  t=float(p['t']);x=float(p['joints']['Hip'][0]);lum=float(p['q']['spine01.lateralBend'])
  margin=p['massAudit']['dcmSupportMarginM']
  if prior is not None:
   dt=t-prior[0]
   if dt<=0:raise ValueError('non-increasing observation timestamps')
   vx=(x-prior[1])/dt
  else:vx=None
  max_x=max(max_x,abs(x));max_lum=max(max_lum,abs(lum))
  if margin is not None:
   minimum_margin=margin if minimum_margin is None else min(minimum_margin,margin)
   if first_margin is None and margin<-.05:first_margin=t
  alert=(vx is not None and abs(x)>CONFIG['x_m'] and abs(vx)>CONFIG['abs_vx_mps']
         and margin is not None and margin<CONFIG['margin_m']
         and abs(lum)>CONFIG['abs_lumbar_deg'])
  streak=streak+1 if alert else 0
  if first_alert is None and streak>=CONFIG['consecutive_samples']:
   first_alert=t;alert_phase=trans[max(0,bisect.bisect_right(transitions,t)-1)]['state']
  prior=(t,x)
 fall=summary['fall_s']
 return {'case':label,'physics_hz':summary['hz'],'samples':len(samples),
   'fall_s':fall,'first_alert_s':first_alert,'first_alert_phase':alert_phase,
   'lead_to_recorded_fall_s':fall-first_alert if fall is not None and first_alert is not None else None,
   'first_margin_below_minus_50mm_s':first_margin,'min_margin_m':minimum_margin,
   'max_abs_pelvis_x_m':max_x,'max_abs_lumbar_deg':max_lum}

def analyze_archive(path):
 b=Path(path).read_bytes();sha=hashlib.sha256(b).hexdigest()
 with zipfile.ZipFile(path) as z:
  if z.testzip() is not None:raise ValueError('ZIP CRC failure')
  rows={}
  for label,dirname in CASES.items():
   member=PREFIX+dirname+'/telemetry.json';raw=z.read(member)
   rows[label]=analyze_case(json.loads(raw),label)
   rows[label]['source_member']=member
   rows[label]['source_sha256']=hashlib.sha256(raw).hexdigest()
 return {'archive_sha256':sha,'method':'retrospective recorded data only',
         'not_independent_simulation':True,'heuristic_not_validated':True,
         'thresholds':CONFIG,'cases':rows}

def self_test(out):
 a=out['cases'];assert a['baseline540']['fall_s'] is None
 assert a['baseline540']['first_alert_s'] is None
 assert a['guard270']['fall_s'] is None and a['guard270']['first_alert_s'] is None
 assert a['guard540']['fall_s'] is not None
 assert a['guard540']['first_alert_s'] is not None
 assert a['guard540']['lead_to_recorded_fall_s']>.15
 assert a['guard540']['physics_hz']==540 and a['guard270']['physics_hz']==270
 assert all(a[k]['first_margin_below_minus_50mm_s'] is not None for k in a)
 print('R26 archived-evidence assertions: PASS (not new dynamics validation)')

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('archive',help='Exact R25 code-and-evidence ZIP path')
 p.add_argument('--out',help='Optional JSON audit output path')
 p.add_argument('--self-test',action='store_true')
 args=p.parse_args();result=analyze_archive(args.archive)
 if args.self_test:self_test(result)
 if args.out:Path(args.out).write_text(json.dumps(result,indent=2)+'\n')
 for k,v in result['cases'].items():
  print(k,'fall_s=',v['fall_s'],'first_alert_s=',v['first_alert_s'],
        'lead_s=',v['lead_to_recorded_fall_s'])
if __name__=='__main__':main()
