#!/usr/bin/env python3
"""Rebuild V013 from immutable R574 sources and V010 native moment-arm receipts.
Only analyzes model relationships; never edits native assets or invokes visual simulation.
"""
from __future__ import annotations
import ast, csv, hashlib, io, json, math, re, sys, zipfile
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
DATA=Path('/mnt/data')
SRC=DATA/'LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip'
MECH=DATA/'BioRig_LUCID_SEMANTIC_ATLAS_V010_NATIVE_84x102_MECHANICAL_RELATIONSHIPS_2026-10-13.zip'
LATE={579:DATA/'BioRig_LUCID_R579_NATIVE_SYNERGY_CODE_EVIDENCE_2026-10-12.zip',580:DATA/'BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip',589:DATA/'BioRig_LUCID_R589_SKIN78_MUSCLE_LANDING_NATIVE_EVIDENCE_2026-10-13.zip'}
ORIGINAL={
'neuro':'LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py',
'impedance':'LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/muscle_impedance_r518.py',
'load_synergy':'LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/load_bearing_synergy_r520.py',
'adaptive_tone':'LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/adaptive_muscle_tone_r522.py',
'memory':'LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/motor_synergy_memory_r516.py',
'allocator':'LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/muscle_allocator_r58.py',
}
LATER={
'r579':'research/lucid/r579/r579_synergy.py',
'r580':'research/lucid/r580/r580_adaptive_synergy.py',
'r589':'R589/r589_arm_landing.py',
}
SHA=lambda b:hashlib.sha256(b).hexdigest()

def csv_write(path,rows,header):
 with (ROOT/path).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=header);w.writeheader();w.writerows(rows)

def load_sources():
 samples={}; manifest=[]
 with zipfile.ZipFile(SRC) as z:
  for alias,path in ORIGINAL.items():
   b=z.read(path);samples[alias]=b.decode('utf-8');manifest.append(dict(alias=alias,archive=SRC.name,path=path,sha256=SHA(b),sourceLines=len(samples[alias].splitlines())))
 for ver,zfile in LATE.items():
  with zipfile.ZipFile(zfile) as z:
   alias='r'+str(ver); path=LATER[alias]
   b=z.read(path);samples[alias]=b.decode('utf-8');manifest.append(dict(alias=alias,archive=zfile.name,path=path,sha256=SHA(b),sourceLines=len(samples[alias].splitlines())))
 return samples,manifest

def blocks_and_lines(sources,manifest):
 # AST + source block ledger, with every nonblank line attached to a block, not merely filename.
 rows=[]; blocks=[]; annotations={
 'neuro':{
 (1,19):'Purpose: full-body, bounded muscle+GRF solve. No direct joint motor outputs.',
 (32,94):'NeuroParams parameter contract: equilibrium, COM, contact, orientation, effort and relaxed-arm defaults.',
 (196,256):'WholeBodyMuscleController state: target q and orientation, independent DOFs, free/fixed muscle masks, COM and feet support.',
 (347,387):'Single coupled dynamics solve: mass, bias, signed muscle gain, tendon moment, GRF decision variables, task-row assembly.',
 (389,403):'Stance-foot non-slip and orientation task rows constrain the whole-body solution.',
 (404,459):'COM capture and pelvis/thorax/head angular control tasks couple position to stabilization.',
 (460,477):'Swing-foot, hinge posture task and velocity damping compete/cooperate in one muscle solve.',
 (478,535):'Low-effort regularizer and prioritized/weighted bounded allocation. Desired muscle activations then converted to excitation.',
 (557,580):'Native activation-rise/fall latency, reachable activation set and computed excitation mapping.'},
 'impedance':{(13,29):'Bounded delayed stretch/load gain settings.',(31,61):'Regional muscle sensory mask and delayed feedback state.',(62,96):'Stretch/tension-feedback recruitment and filtered release; excitation additive to teacher.'},
 'load_synergy':{(20,37):'Reciprocal relaxation bounds and kinetics.',(39,56):'Signed native-tendon synergies with delayed joint velocities.',(57,95):'Recruits muscles resisting motion; conditionally releases movement-driving antagonists, respecting tonic floor.',(96,137):'Combines teacher + ground, delayed joint responses, excitation/inhibition, support safety gate.'},
 'adaptive_tone':{(33,49):'Calf and hip region masks and delayed load-sensing state.',(50,101):'Load/pressure/calf-tone feedback and bilateral redistribution with clipped excitation.'},
 'r579':{(20,26):'Weights four fixed lateral muscles, not full-body synergy.',(28,75):'Lateral-support dose; compares group profiles and effort.'},
 'r580':{(42,66):'Adaptive four-muscle lateral group on native model.',(67,105):'Pelvis position-speed driven urgency and signed-side recruitment.',(108,165):'R574 decision + bounded lateral support merged as extra excitation and applied to R551 native physics.'},
 'r589':{(19,26):'Fixed two-sided arm landing phase profile.',(32,85):'Per-side one-muscle signed shoulder torque correction; no multi-DOF arm co-contraction solve.',(88,150):'Base every 2ms, arm and neck overrides every 10ms, native physics and contact readout.'},
 }
 for man in manifest:
  alias=man['alias']; src=sources[alias]; lines=src.splitlines(); tree=ast.parse(src)
  items=[]
  for node in ast.walk(tree):
   if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
    items.append((node.lineno,node.end_lineno,node.name,node.__class__.__name__))
  items.sort(key=lambda a:(a[1]-a[0],a[0]))
  for begin,end,name,kind in items:
   blocks.append(dict(sourceAlias=alias,startLine=begin,endLine=end,symbol=name,kind=kind,sourceSHA256=man['sha256']))
  def region(n):
   for (a,b),sem in annotations.get(alias,{}).items():
    if a<=n<=b:return sem
   return 'Source statement; retain literal code and AST scope. Full behavioral semantics not manually established for this line.'
  for n,line in enumerate(lines,1):
   enclosing=next((name for start,end,name,_ in items if start<=n<=end),'module')
   typ='blank' if not line.strip() else ('comment' if line.lstrip().startswith('#') else 'code-or-docstring')
   rows.append(dict(sourceAlias=alias,line=n,text=line,scope=enclosing,kind=typ,reviewedBlockSemantics=region(n),sourceSHA256=man['sha256']))
 csv_write('NINE_MODULE_EXACT_SOURCE_LINE_AND_BLOCK_SEMANTICS.csv',rows,['sourceAlias','line','text','scope','kind','reviewedBlockSemantics','sourceSHA256'])
 csv_write('NINE_MODULE_FUNCTION_CLASS_BOUNDARY_LEDGER.csv',blocks,['sourceAlias','startLine','endLine','symbol','kind','sourceSHA256'])
 return dict(lineCount=len(rows),functionClassBlocks=len(blocks),semanticBlockRegions=sum(len(v) for v in annotations.values()))

def calculate(mech):
 with zipfile.ZipFile(mech) as z:
  raw=z.read('V010/NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz')
  with np.load(io.BytesIO(raw)) as obj:
   M=obj['momentJacobian'].copy();names=list(map(str,obj['actuatorNames']));dofs=list(map(str,obj['dofNames'])); cases=list(map(str,obj['cases']))
 assert M.shape==(94,84,102)
 # zero-count is not proof of no general relationship. threshold is explicitly a sampled-pose numerical gate.
 gate=1e-8
 opposite=np.zeros((84,84),np.int32);same=np.zeros((84,84),np.int32);both=np.zeros((84,84),np.int32)
 for state in M:
  for row in state.T:
   active=np.nonzero(np.abs(row)>gate)[0]
   if len(active)==0:continue
   s=np.sign(row[active]);idx=np.ix_(active,active)
   both[idx]+=1
   opposite[idx]+=(s[:,None]!=s[None,:])
   same[idx]+=(s[:,None]==s[None,:])
 assert np.array_equal(opposite+same,both)
 assert np.all(opposite.diagonal()==0)
 records=[]
 for i in range(84):
  for j in range(84):
   if i==j:mode='same actuator'
   elif both[i,j]==0:mode='no shared nonzero coordinate at 94 samples (not globally absent)'
   elif opposite[i,j] and same[i,j]:mode='task-dependent mixed signs across coordinates/poses'
   elif opposite[i,j]:mode='opposing on every sampled shared nonzero interaction'
   else:mode='same signed influence on every sampled shared nonzero interaction'
   records.append(dict(actuatorA=i,muscleA=names[i],actuatorB=j,muscleB=names[j],sharedNonzeroCoordinateStatePairs=int(both[i,j]),opposingSignedPairs=int(opposite[i,j]),sameSignedPairs=int(same[i,j]),classification=mode))
 csv_write('ALL_7056_ACTUATOR_PAIR_COORDINATION_EDGES.csv',records,list(records[0]))
 # Sparse, fully reproducible statistics for elbow and shoulder couplings across all 94 captured poses.
 goalnames=['m_left_biceps','m_left_brachialis','m_left_triceps','m_left_brachioradialis','m_right_biceps','m_right_brachialis','m_right_triceps','m_right_brachioradialis']
 assert all(x in names for x in goalnames)
 rows=[]
 for side in ('left','right'):
  elbow=dofs.index(side+'Elbow.flexionExtension');shoulder=dofs.index(side+'Shoulder.flexionExtension');
  for k in range(94):
   # Convention: tendon force is negative, so generalized moment is (-moment_arm) * positive tension.
   values={n:float(-M[k,names.index('m_'+side+'_'+n),elbow]) for n in ('biceps','brachialis','triceps','brachioradialis')}
   # Use native per-unit TENSION moments, NOT per-unit activation. This is an isometric static decomposition only.
   b=values['biceps']; t=values['triceps'];ratio=-b/t if abs(t)>1e-10 else float('nan')
   b_sh=float(-M[k,names.index('m_'+side+'_biceps'),shoulder]);t_sh=float(-M[k,names.index('m_'+side+'_triceps'),shoulder])
   # 100 N tensile biceps, triceps tension adjusted to net zero elbow torque.
   residual=100*(b_sh+ratio*t_sh)
   rows.append(dict(side=side,poseIndex=k,poseCase=cases[k],elbowDof=elbow,shoulderDof=shoulder,
    bicepsElbowNmPerN=b,brachialisElbowNmPerN=values['brachialis'],tricepsElbowNmPerN=t,
    brachioradialisElbowNmPerN=values['brachioradialis'],tricepsToBicepsTensionRatioForZeroElbowMoment=ratio,
    residualShoulderNmWith100NBicepsAndBalancedElbow=residual,
    samePoseNumericalElbowMomentNmFor100NBiceps=100*b,
    remainingElbowMomentNmWithTricepsTensionBalance=100*(b+t*ratio)))
 csv_write('94_POSE_BILATERAL_ELBOW_COACTIVATION_BALANCE.csv',rows,list(rows[0]))
 ratios=np.array([r['tricepsToBicepsTensionRatioForZeroElbowMoment'] for r in rows]);res=np.array([r['residualShoulderNmWith100NBicepsAndBalancedElbow'] for r in rows]);error=np.array([r['remainingElbowMomentNmWithTricepsTensionBalance'] for r in rows]);
 assert np.all(np.isfinite(ratios)) and np.all(ratios>0)
 assert np.max(np.abs(error))<1e-12
 # Count coupling states not just signed pairs: robust evidence labels.
 return dict(poses=94,actuators=84,dofs=102,directedMusclePairs=84*84,positiveSharedPairEntries=int(np.count_nonzero(both)),oppositionPairEntries=int(np.count_nonzero(opposite)),mixedPairEntries=int(np.count_nonzero((opposite>0)&(same>0))),
  sampleThresholdMetresPerRadian=gate,
  bicepsToTricepsTensionBalanceRatio={'minimum':float(ratios.min()),'maximum':float(ratios.max()),'mean':float(ratios.mean())},
  shoulderResidualNmUnder100NBiceps={'minimum':float(res.min()),'maximum':float(res.max()),'meanAbs':float(np.abs(res).mean())},
  elbowMomentResidualMaxNm=float(np.abs(error).max()),
  sourceV010NativeMatrixSHA256=SHA(raw),
  note='Opposition and coactivation are potential mechanical relationships, not measured voluntary muscle force, neural intent or tested stiffening. Sign conventions from native tendon moment Jacobian, muscle tension assumed positive in examples.')

def main():
 samples,manifest=load_sources()
 stats=blocks_and_lines(samples,manifest)
 results=calculate(MECH)
 receipt={'schema':'lucid.biorig.semantic-atlas-v013.biomechanical-coordination.v1','frozenR574SHA256':SHA(SRC.read_bytes()),'frozenV010SHA256':SHA(MECH.read_bytes()),'sources':manifest,'lineSemantics':stats,'nativeGeometryAnalysis':results,'sourceFilesEdited':False,'newNativePhysicsRollouts':0}
 (ROOT/'V013_RECEIPT.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'lineSemantics':stats,'elbow':results},indent=2))
if __name__=='__main__':main()
