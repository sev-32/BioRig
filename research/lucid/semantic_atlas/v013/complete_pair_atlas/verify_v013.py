#!/usr/bin/env python3
"""Independent source/CSV/geometry verifier; no simulation changes."""
from __future__ import annotations
import csv,io,json,zipfile,hashlib
from pathlib import Path
import numpy as np
from build_v013 import ROOT, SRC, MECH, LATE, ORIGINAL, LATER

def read_csv(name):
 with (ROOT/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def test():
 r=json.loads((ROOT/'V013_RECEIPT.json').read_text());source={}
 with zipfile.ZipFile(SRC) as z:
  for k,p in ORIGINAL.items():source[k]=z.read(p)
 for ver,p in LATE.items():
  with zipfile.ZipFile(p) as z:source['r'+str(ver)]=z.read(LATER['r'+str(ver)])
 for f in r['sources']:
  assert hashlib.sha256(source[f['alias']]).hexdigest()==f['sha256'],f['alias']
 lines=read_csv('NINE_MODULE_EXACT_SOURCE_LINE_AND_BLOCK_SEMANTICS.csv')
 assert len(lines)==r['lineSemantics']['lineCount']==1636
 for x in lines:
  literal=source[x['sourceAlias']].decode('utf-8').splitlines()[int(x['line'])-1]
  assert literal==x['text'],(x['sourceAlias'],x['line'])
 matrix=read_csv('ALL_7056_ACTUATOR_PAIR_COORDINATION_EDGES.csv')
 elbow=read_csv('94_POSE_BILATERAL_ELBOW_COACTIVATION_BALANCE.csv')
 assert len(matrix)==84*84 and len(elbow)==94*2
 with zipfile.ZipFile(MECH) as z:
  raw=z.read('V010/NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz')
  assert hashlib.sha256(raw).hexdigest()==r['nativeGeometryAnalysis']['sourceV010NativeMatrixSHA256']
  with np.load(io.BytesIO(raw)) as a:
   M=a['momentJacobian'].copy(); names=list(map(str,a['actuatorNames']));dofs=list(map(str,a['dofNames']))
 gate=r['nativeGeometryAnalysis']['sampleThresholdMetresPerRadian']
 pairs={(int(x['actuatorA']),int(x['actuatorB'])):x for x in matrix}
 assert len(pairs)==7056
 opp=np.zeros((84,84),np.int32);same=np.zeros((84,84),np.int32)
 for state in M:
  for row in state.T:
   active=np.nonzero(np.abs(row)>gate)[0]
   if not len(active):continue
   s=np.sign(row[active]);inds=np.ix_(active,active)
   opp[inds]+=(s[:,None]!=s[None,:]);same[inds]+=(s[:,None]==s[None,:])
 for (i,j),x in pairs.items():
  assert x['muscleA']==names[i] and x['muscleB']==names[j]
  assert int(x['opposingSignedPairs'])==opp[i,j]
  assert int(x['sameSignedPairs'])==same[i,j]
  assert int(x['sharedNonzeroCoordinateStatePairs'])==opp[i,j]+same[i,j]
 err=0.
 for x in elbow:
  k=int(x['poseIndex']);side=x['side'];ei=dofs.index(side+'Elbow.flexionExtension');si=dofs.index(side+'Shoulder.flexionExtension')
  b=-M[k,names.index('m_'+side+'_biceps'),ei];t=-M[k,names.index('m_'+side+'_triceps'),ei];ratio=-b/t
  shoulder=100*(-M[k,names.index('m_'+side+'_biceps'),si]-ratio*M[k,names.index('m_'+side+'_triceps'),si])
  err=max(err,abs(float(x['tricepsToBicepsTensionRatioForZeroElbowMoment'])-ratio),abs(float(x['residualShoulderNmWith100NBicepsAndBalancedElbow'])-shoulder))
 assert err<1e-12,err
 assert r['nativeGeometryAnalysis']['oppositionPairEntries']==int(np.count_nonzero(opp))
 assert r['nativeGeometryAnalysis']['mixedPairEntries']==int(np.count_nonzero((opp>0)&(same>0)))
 print(json.dumps({'pass':True,'sourceModules':len(source),'literalLines':len(lines),'allDirectedMusclePairs':len(matrix),'poseElbowRows':len(elbow),'maxIndependentDifference':err,'sourceArchiveSHA256Matched':True,'nativeMatrixSHA256Matched':True},indent=2))
 return True
if __name__=='__main__':test()
