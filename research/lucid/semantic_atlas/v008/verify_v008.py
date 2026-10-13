#!/usr/bin/env python3
"""Independent V008 source-line, claim-key, controller-write-order and hash verification."""
from pathlib import Path
import ast,collections,csv,hashlib,json,zipfile
ROOT=Path('/mnt/data'); OUT=ROOT/'BioRig_SEMANTIC_ATLAS_008'
w=json.loads((OUT/'CONTROL_FLOW_LINE_WITNESSES.json').read_text())
manifest=json.loads((OUT/'SOURCE_PINNED_MODULE_MANIFEST.json').read_text())
receipt=json.loads((OUT/'V008_VERIFICATION_RECEIPT.json').read_text())
ids=[r['id'] for r in w];assert len(ids)==len(set(ids))
cache={}
for key,meta in manifest.items():
 archive=ROOT/meta['zip']
 assert archive.is_file(),archive
 with zipfile.ZipFile(archive) as z:raw=z.read(meta['path'])
 assert hashlib.sha256(raw).hexdigest()==meta['sha256']
 text=raw.decode('utf-8');node=ast.parse(text,filename=meta['path'])
 cache[key]=(text.splitlines(),node)
for r in w:
 src=manifest[r['group']]
 assert (r['archive'],r['path'],r['sourceSHA256'])==(src['zip'],src['path'],src['sha256'])
 lines,node=cache[r['group']]
 assert lines[r['line']-1]==r['lineText'],r['id']
 assert sum(x==r['lineText'] for x in lines)==1, r['id'] # no duplicate exact source witness
 assert 1<=r['line']<=len(lines)
with (OUT/'STATE_FIELD_OWNERSHIP_CONTRACTS.csv').open(newline='') as f:
 rows=list(csv.DictReader(f))
for row in rows:
 for key in ['writer witness IDs','reader witness IDs']:
  for witness in row[key].split(','):
   assert witness in ids,(row['field'],witness)
edges=json.loads((OUT/'DIRECTED_RUNTIME_INTERFACE_EDGES.json').read_text())
for e in edges:assert e['sourceWitness'] in ids and e['destWitness'] in ids
# Inspector-specific AST validation. No run-time execution is claimed.
class Calls(ast.NodeVisitor):
 def __init__(self):self.full=[]
 def visit_Call(self,n):
  self.full.append((n.lineno,ast.unparse(n.func)));self.generic_visit(n)

def fn(tree,name):return next(n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
def write_lines(fnnode,expr='d.ctrl'):
 found=[]
 for n in ast.walk(fnnode):
  if isinstance(n,(ast.Assign,ast.AugAssign,ast.AnnAssign)):
   tg=n.targets if isinstance(n,ast.Assign) else [n.target]
   for t in tg:
    txt=ast.unparse(t)
    if txt.startswith(expr):found.append((n.lineno,txt))
 return sorted(found)
replay=fn(cache['replay590'][1],'continue_native'); armrun=fn(cache['arm589'][1],'run');cap=cache['cap590'][1]
replaycalls=Calls();replaycalls.visit(replay)
armcalls=Calls();armcalls.visit(armrun)
assert not any('ArmLanding' in n or 'arm.update' in n for _,n in replaycalls.full)
assert any(n.endswith('allocator.update') for _,n in replaycalls.full)
assert any(n.endswith('arm.update') for _,n in armcalls.full)
assert any(n.endswith('mj_step') for _,n in replaycalls.full)
assert any(n.endswith('mj_step') for _,n in armcalls.full)
arm_w=write_lines(armrun);restart_w=write_lines(replay)
assert len(arm_w)==3 and len(restart_w)==2,(arm_w,restart_w)
assert arm_w[0][0]<arm_w[1][0]<arm_w[2][0]
assert restart_w[0][0]==restart_w[1][0]
assert 'allocator.ids' in arm_w[-1][1] and 'allocator.ids' in restart_w[-1][1]
for name,sha in receipt['files'].items():
 assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==sha,name
report={'status':'PASS','verifiedSourceModules':len(manifest),'verifiedSourceLineWitnesses':len(w),'fieldContracts':len(rows),'sourceAnchoredDirectedEdges':len(edges),'R589ActuatorWriteOrder':arm_w,'R590RestartActuatorWriteOrder':restart_w,'R589ArmLandingUpdateCallObservedStatic':True,'R590RestartArmLandingCallObservedStatic':False,'R590RestartNeckAllocatorCallObservedStatic':True,'runtimeExecuted':False,'noSourceCodeModified':True}
(OUT/'VERIFICATION_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
