#!/usr/bin/env python3
"""BioRig R27 portable audit of ORIGINAL R25 evidence, not a physics rerun.
Usage: python r27_portable_archive_check.py LUCID_BioRig_R25_CODE_AND_EVIDENCE_20261021.zip
"""
import sys,zipfile,json,itertools,hashlib
NAMES={'baseline540':'r17r21R24R25neutral540skin_step_late_540',
       'rejected540':'r17r21R24R25guard540skin_step_late_540',
       'guard270':'r17r21R24R25g100_270_step_late_270'}
PREFIX='LUCID_BioRig_Development/35_R25_CONTACT_FEASIBILITY/traces/'
def first_alarm(d,hip=.105,speed=.10,gap=.06,load=450):
 samples=d['samples'];run=0
 for i,s in enumerate(samples):
  t=s['t'];x=s['joints']['Hip'][0];j=max(0,i-3);dt=t-samples[j]['t']
  vx=(x-samples[j]['joints']['Hip'][0])/dt if dt>0 else None
  a=s['massAudit'];cp=a['cop'][0];dc=a['dcm'][0];fn=a['footLoadN']
  hit=(fn['R']>load and fn['L']<65 and cp is not None and dc-cp>gap
       and x>hip and vx is not None and vx>speed)
  run=run+1 if hit else 0
  if run>=3:return t
 return None
def check(archive):
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None, 'ZIP integrity failure'
  d={k:json.loads(z.read(PREFIX+v+'/telemetry.json')) for k,v in NAMES.items()}
 fall=d['rejected540']['summary']['fall_s'];assert fall is not None
 result={k:{'fall_s':v['summary']['fall_s'],'alarm_s':first_alarm(v),
            'hz':v['summary']['hz']} for k,v in d.items()}
 assert result['baseline540']['alarm_s'] is None
 assert result['guard270']['alarm_s'] is None
 assert .8<fall-result['rejected540']['alarm_s']<1.0
 n=0;times=[]
 for x,v,g,f in itertools.product([.085,.105,.125],[.08,.10,.16],[.04,.06,.08],[400,450,500]):
  a={k:first_alarm(data,x,v,g,f) for k,data in d.items()}
  if a['baseline540'] is None and a['guard270'] is None and a['rejected540'] is not None:
   n+=1;times.append(a['rejected540'])
 assert n==81
 return {'method':'retrospective in-sample heuristic, NOT a physics rerun',
         'r25_zip_sha256':hashlib.sha256(open(archive,'rb').read()).hexdigest(),
         'cases':result,'sensitivity_grid':{'tested':81,'separated':n,
           'first_alarm_min_s':min(times),'first_alarm_max_s':max(times)},
         'future_validation_required':True}
if __name__=='__main__':print(json.dumps(check(sys.argv[1]),indent=2))
