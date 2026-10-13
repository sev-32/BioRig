#!/usr/bin/env python3
"""Reproducible exact-source witness ledger and authority maps for BioRig V008.
No BioRig executable source is run or mutated. Static source evidence is not execution proof.
"""
from pathlib import Path
import ast,csv,hashlib,json,zipfile,collections
ROOT=Path('/mnt/data'); OUT=ROOT/'BioRig_SEMANTIC_ATLAS_008'; OUT.mkdir(exist_ok=True)
Z={
 'base':'LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip',
 'r585':'BioRig_LUCID_R585_PHYSICAL_NECK_REPAIR_CHECKPOINT_2026-10-13.zip',
 'r586':'BioRig_LUCID_R586_NATIVE_SKIN78_MUSCLE_EFFICIENCY_2026-10-13.zip',
 'r589':'BioRig_LUCID_R589_SKIN78_MUSCLE_LANDING_NATIVE_EVIDENCE_2026-10-13.zip',
 'r590':'BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13.zip',
}
P={
 'goal':('base','R574_INTENTION_AND_AVERSION/r574_intention.py'),
 'eval':('base','R574_INTENTION_AND_AVERSION/r574_evaluate.py'),
 'seat551':('base','LUCID_R552_WORKSPACE/R551_ACTIVE_RECOVERY/run_r551.py'),
 'plant':('base','LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py'),
 'planner':('base','LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/planner.py'),
 'skin':('base','LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/pipeline.py'),
 'neck585':('r585','R585/r585_neck_repair.py'),
 'neck586':('r586','research/lucid/r586/r586_effort.py'),
 'arm589':('r589','R589/r589_arm_landing.py'),
 'cap590':('r590','r590_settled_capture.py'),
 'replay590':('r590','r590_rest_restart.py'),
}
# The explicit semantic claim is human-reviewed; the literal match and hash are checked automatically.
# label, owner, matching snippet, meaning, evidence domain, limits
W=[
 ('G001','goal',"ACTIONS=('none','R28')",'Decision action universe comprises exactly two research options','goal','Cannot express arbitrary hand target'),
 ('G002','goal',"'restore_supported_equilibrium':GoalContract(",'Desired seated recovery outcome is declarative','goal','Policy desire is authored, not innate'),
 ('G003','goal',"currentArmAbortN:float=10.0",'Measured arm contact can veto action','safety','Threshold does not imply calibrated injury risk'),
 ('G004','goal','self.X=np.array([feature(r[\'observed\']) for r in rows])','Outcome learner uses observed sensor features','learning','No additional features inferred'),
 ('G005','goal','ExtraTreesClassifier(n_estimators=200','Forecast uses small-data tree ensemble','learning','Prediction not physics guarantee'),
 ('G006','goal','forecasts,nearest=self.model.forecast(observation)','Decision queries forecast and novelty','goal','Forecast is not action execution'),
 ('G007','goal',"choice,why='none','out_of_distributon'",'Novelty above threshold suppresses action','safety','Source typo preserved; no undocumented branch'),
 ('G008','goal',"choice,why='R28','expected_goal_advantage_within_vetoes'",'Positive selected choice is R28 only','goal','No more general action generation'),
 ('G009','eval','selected=agent.decide(measured,\'restore_supported_equilibrium\')','Held-out harness explicitly invokes agent decision','experiment','Not evidence seated R590 invokes it'),
 ('S001','seat551','from lucid_bcr.posture_stabilization_r51 import controller_excitation','R551 uses narrower posture controller','import','Import alone is not execution'),
 ('S002','seat551',"d.ctrl[:]=np.clip(base+delta,0,1)",'R551 applies a corrective pulse over all native actuator commands','actuation','Exact contact behavior only from runtime'),
 ('S003','seat551','d.xfrc_applied[pb.body_id["Hip"],:3]=push_world','R551 sets external world-space hip force','physics','No synthetic root lock implied'),
 ('S004','seat551','mj.mj_step(m,d)','R551 integrates real native physics','physics','Not proof of stable motion'),
 ('N001','plant','class WholeBodyMuscleController:','Separate full-body muscle controller exists in original code','control','Not automatically used by research seat loop'),
 ('N002','plant','self.free = np.nonzero(~arm)','Relaxed-arm mode can remove arm excitation variables','control','Conditional; not universal behavior'),
 ('N003','plant','B = (R * g[:, None]).T','Actuator gains and moment arms map muscle activation to generalized force','physics','Instantaneous approximation, not measured delivery'),
 ('N004','plant','xi = com[[0, 2]] + vcom[[0, 2]] / w0','COM capture uses x,z world horizontal axes','physics','Requires correct frame/unit interpretation'),
 ('N005','plant','self.u = self.excitation(a)','Whole-body controller converts desired activation into excitation output','actuation','Caller must write returned vector to active plant'),
 ('P001','planner','def plan(self, state:', 'Original planner computes motion references from state','planning','Plan output is not native execution'),
 ('K001','skin','self.real.step(target, dt)','Pipeline can realize pose without a forward native muscle step','rendering','Render-only realization is not causal locomotion'),
 ('K002','skin','self.pl.inverse_dynamics(np.array(self.qpos_hist)','Inverse muscle estimation starts from provided pose history','rendering','Not proof inferred muscles caused motion'),
 ('K003','skin','"label": "COMPLETE_CAUSAL_STATE','Original rig stores its own articulated snapshot contract','state','Not equivalent to full MuJoCo solver memory'),
 ('N585A','neck585','m.site_pos[sid,2]=-.025','R585 modifies model-local SCM attachment geometry in test model','geometry','Geometry change must be audited separately from control'),
 ('N585B','neck585','d.ctrl[:]=base','R585 first writes posture excitation','control','Later overwrite changes winner'),
 ('N585C','neck585','if not baseline:d.ctrl[ctl.ids]=command','R585 conditionally overwrites neck channels','control','Baseline switch matters'),
 ('N585D','neck585','mj.mj_step(m,d)','R585 physics runs after control assignment','physics','No guarantee head stable without evidence'),
 ('N586A','neck586','class MomentConstrainedAllocator','R586 has a distinct moment-constrained neck allocator','control','Reference moment is predicted not measured'),
 ('N586B','neck586','if k%5==0:command,_=allocator.update(d,base)','Neck allocation refreshes every five physics steps','timing','Command persists between refreshes'),
 ('N586C','neck586','d.ctrl[:]=base;d.ctrl[allocator.ids]=command','R586 neck channels override base on each physics step','control','No joint whole-body multiobjective optimum'),
 ('N586D','neck586','d.qfrc_applied[:]=r585.core.passive_end_for_data(pb,d)','Passive applied generalized joint forces have separate writer','physics','Not muscle excitation'),
 ('N586E','neck586','d.xfrc_applied[pb.body_id[\'Hip\'],0]=push_N','Optional lateral hip push acts as external force','physics','No proof robustness beyond tested force'),
 ('N586F','neck586','mj.mj_step(m,d)','Native physical response follows writes','physics','Rendered pose still requires native qpos'),
 ('A589A','arm589','VERIFIED_PROFILE={','R589 arm-descent parameters are a fixed experiment-specific profile','control','Not general target-language interface'),
 ('A589B','arm589','class ArmLanding:','R589 introduces an optional transient arm controller','control','Exists only when candidate truthy'),
 ('A589C','arm589','desired_torque=kp*(desired-q)+kd*(desired_speed-v)','Arm command compares desired and measured shoulder angle/speed','physics','Single-joint PD proxy is not a whole-body intention solver'),
 ('A589D','arm589','gain=mj.mju_muscleGain(','Uses native muscle gain at current actuator state','physics','Cannot assume constant force'),
 ('A589E','arm589','extra[idx]=np.clip(base[idx]+amp,0.,.8)','Shoulder excitation supplement is bounded','control','Only selected muscle channels'),
 ('A589F','arm589','arm=ArmLanding(pb,','R589 arm controller constructed only for candidate mode','branch','Mode dependent'),
 ('A589G','arm589','if arm:arm_cmd=arm.update(d,base,t)','R589 calls arm controller only if constructed','control','At update cadence, not every physics step'),
 ('A589H','arm589','d.ctrl[:]=base','R589 base writes all muscle channels first','control','Later writes may supersede'),
 ('A589I','arm589','d.ctrl[idx]=arm_cmd[idx]','R589 arm channels conditionally overwrite base','control','Neck channels override afterward'),
 ('A589J','arm589','d.ctrl[allocator.ids]=head_cmd','R589 neck correction has final muscle-command priority','control','Potential overlapping channels must be checked'),
 ('A589K','arm589','if .8<=t<.92:d.xfrc_applied[pb.body_id[\'Hip\'],0]=push','R589 push has bounded active interval','physics','No broad push generalization'),
 ('A589L','arm589','mj.mj_step(m,d)','R589 commands feed forward physics','physics','Skin render must be evaluated separately'),
 ('C590A','cap590','result=reference.run(T_FINAL,candidate=True','R590 continuous capture calls R589 run in candidate mode','runtime','Native measured contact must be checked'),
 ('C590B','cap590','states.append({\'qpos\':d.qpos.copy()','R590 capture explicitly copies native state','state','Snapshot not full solver state'),
 ('C590C','cap590','np.savez_compressed(npz,qpos=np.stack(','R590 stores sampled positions velocity and activation','serialization','qacc, warmstart, controller caches not included'),
 ('C590D','cap590','for row in result[\'samples\']:','R590 contact-transition measurement reads sampled R589 trace','measurement','Sampling not continuous contact proof'),
 ('R590A','replay590','import r589_arm_landing as original','Restart imports R589 module','import','Not an execution of ArmLanding'),
 ('R590B','replay590','phys=original.r586.r585','Restart accesses R585 through R589 -> R586 symbol chain','import','Symbols can be imported without running control'),
 ('R590C','replay590',"qref=phys.prior.reset(pb)",'Neutral seated reference captured before loading settled state','state','Source-specific reference not new optimization'),
 ('R590D','replay590',"d.qpos[:]=raw['qpos'][0]",'Copies saved positions into native plant','state','Position alone is not complete state'),
 ('R590E','replay590',"d.qvel[:]=raw['qvel'][0]",'Copies saved generalized velocities','state','Does not copy full integrator state'),
 ('R590F','replay590',"d.act[:]=raw['act'][0]",'Copies muscle activation state','state','Not same as excitation control inputs'),
 ('R590G','replay590','mj.mj_forward(m,d)','Recomputes derived native quantities after state assignment','physics','Warmstart identity not assured'),
 ('R590H','replay590','allocator.last_eff[j]=float(d.act[actadr])','Reconstructs optimization memory from current activation','state','Approximate memory restoration, not exact historical history'),
 ('R590I','replay590','base=phys.controller_excitation(','Restart invokes inherited seat posture controller directly','control','Does not call original WholeBodyMuscleController'),
 ('R590J','replay590','if k%5==0:head_ctrl,_=allocator.update(d,base)','Restart invokes R586 allocator through R589 symbolic chain','control','No `ArmLanding.update()` in this loop'),
 ('R590K','replay590','d.ctrl[:]=base;d.ctrl[allocator.ids]=head_ctrl','Restart only uses base and neck writes on native ctrl','control','ArmLanding absent from this path'),
 ('R590L','replay590','d.qfrc_applied[:]=phys.core.passive_end_for_data(pb,d)','Native applied generalized forces set from passive model','physics','Not equal to muscle command'),
 ('R590M','replay590','d.xfrc_applied[:]=0.','Clears external force per simulation step','physics','Later conditional push overrides zero'),
 ('R590N','replay590','if pushAtS<=t<pushAtS+.12:d.xfrc_applied[pb.body_id[\'Hip\'],0]=pushN','Push applied at hip for 120 ms','physics','Does not validate arbitrary disturbances'),
 ('R590O','replay590','mj.mj_step(m,d)','Plant advances from actual native muscle/controller outputs','physics','Source presence not physics accuracy proof'),
 ('R590P','replay590','frames_qpos.append(d.qpos.copy())','Render samples derive from native qpos','rendering','Sparse qpos samples can miss transient dynamics'),
 ('R590Q','replay590','support=phys.loaded_support_target(d.subtree_com','COM based support target reads native derived subtree_com','state','Only local posture controller uses this target'),
 ('R590R','replay590','mj.mj_differentiatePos(m,difference,1.,d.qpos,qref)','Reference qref used for posture error','state','Desired joint error is not a movement goal'),
 ('R590S','replay590',"neutral=(d.xpos[pb.body_id['Head']]-d.xpos[pb.body_id['Hip']])",'Original neutral horizontal head-hip displacement from reset pose','state','World horizontal position reference, not posture quaternion'),
 ('N585E','neck585','d.actuator_force[other]','R585 reads measured other-actuator force for demand','physics','Native actuator force does not prove anatomical calibration'),
 ('A589M','arm589','arms=ledger(pb,d)','Arm contact metrics derive from contact ledger function','measurement','Not identical to raw data.contact field'),
]

zipcache={k:zipfile.ZipFile(ROOT/name) for k,name in Z.items()}
cache={}
for key,(zname,path) in P.items():
    raw=zipcache[zname].read(path); s=raw.decode('utf-8');tree=ast.parse(s,filename=path)
    cache[key]={'zip':Z[zname],'path':path,'text':s,'lines':s.splitlines(),'sha256':hashlib.sha256(raw).hexdigest(),'tree':tree,'bytes':len(raw)}
records=[]
for id,key,anchor,meaning,kind,limit in W:
    src=cache[key];hits=[(i,line) for i,line in enumerate(src['lines'],1) if anchor in line]
    if len(hits)!=1:raise ValueError(f'Nonunique/missing source anchor {id} {key} {anchor!r} hits={len(hits)}')
    line,rawline=hits[0]
    enclosing=[n for n in ast.walk(src['tree']) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and n.lineno<=line<=n.end_lineno]
    enclosing.sort(key=lambda n:(n.end_lineno-n.lineno))
    scope='.'.join(reversed([n.name for n in enclosing])) if enclosing else '<module>'
    records.append({'id':id,'group':key,'archive':src['zip'],'path':src['path'],'sourceSHA256':src['sha256'],'line':line,'lineText':rawline,'scope':scope,'evidence':kind,'meaning':meaning,'boundary':limit,'status':'exact-source-text/AST; no runtime-branch proof unless explicitly observed'})
(OUT/'CONTROL_FLOW_LINE_WITNESSES.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
meta={name:{k:v for k,v in c.items() if k not in ('text','lines','tree')} | {'lineCount':len(c['lines'])} for name,c in cache.items()}
(OUT/'SOURCE_PINNED_MODULE_MANIFEST.json').write_text(json.dumps(meta,indent=2)+'\n')

# Explicit field-contract table: writers are source grounded, not inferred from identical variable strings.
fields=[
 ('data.qpos','native generalized position','mixed free-root metres/quaternion plus joint radians','R590D','C590B,R590P','MuJoCo model qpos layout','Reset/restore writer in R590; physics step also advances position'),
 ('data.qvel','native generalized velocity','mixed metres/sec and radians/sec','R590E','A589C,C590B','MuJoCo model qvel layout','No direct muscle influence without integration'),
 ('data.act','native actuator activation','dimensionless activation state','R590F','R590H,C590B','MuJoCo actuator-state layout','Activation != command; velocity and length dependent response'),
 ('data.ctrl','native muscle excitation control','nominal bounded excitation (dimensionless)','A589H,A589I,A589J,R590K','N586C','Base is overwritten by arm then neck only on continuous path'),
 ('data.qfrc_applied','applied generalized force','N or N.m per generalized velocity row','N586D,R590L','N586F,R590O','MuJoCo qfrc_applied vector','Externally supplied modeled/passive forces distinct from muscle tension'),
 ('data.xfrc_applied','externally applied world-body spatial force','N and N.m in spatial wrench representation','N586E,A589K,R590M,R590N','S003,R590O','MuJoCo xfrc_applied body-indexed array','Push must be interpreted in world vs native body conventions'),
 ('data.subtree_com','derived center of mass','world-frame metres','R590G,R590O','R590Q','MuJoCo forward-derived array','Not independently assigned here'),
 ('data.actuator_force','native actuator force','MuJoCo native actuator force units','R590G,R590O','N585E','Native forward state','Only specific muscle force semantics after gain/gear mapping'),
 ('data.actuator_length','muscle path length','metres / model actuator coordinate','R590G,R590O','A589D','MuJoCo actuator mechanism','Geometry dependent; model correctness not proven'),
 ('derived arm-seat ledger','measured arm-seat contact reaction','newtons derived from native contacts','R590G,R590O','A589M,C590D','MuJoCo collision engine','Contact transition sampling must preserve high-frequency data'),
 ('qref','seated reference generalized pose','MuJoCo qpos schema','R590C','R590R','R551 baseline reset','qref is a reference not current qpos'),
 ('neutral','head-to-hip horizontal posture reference','metres in world x,z','R590S','R590I','R590.setup neutral construction','Conflated with goal if not typed separately'),
 ('allocator.last_eff','memory of previous neck excitation','dimensionless per neck actuator','R590H','R590J','R586 neck controller memory','Reconstructed from physical act, not exact prior optimizer state'),
 ('controller sampling cadence','simulation timing and discrete control updates','s / number of physics substeps','N586B,R590J','R590O','Native timestep .002 in source','Control updates every five steps; contact sampled on separate cadence'),
]
with (OUT/'STATE_FIELD_OWNERSHIP_CONTRACTS.csv').open('w',newline='') as f:
    wr=csv.writer(f,lineterminator='\n');wr.writerow(['field','semantic meaning','units/frame','writer witness IDs','reader witness IDs','authority','failure mode']);wr.writerows(fields)

# The runtime provenance edges are manually grounded and pin witness endpoints.
E=[
 ('R574 policy','R574 experiment','choice none/R28','G008','G009','connected in evaluation only'),
 ('R574 policy','R590 restart','decision -> ctrl','G009','R590I','NOT CONNECTED BY THE INSPECTED ENTRYPOINT'),
 ('WholeBodyMuscleController','R590 restart','excitation output','N005','R590I','ALTERNATIVE CONTROLLER, NOT USED BY THIS ENTRYPOINT'),
 ('Original planner','R590 restart','foot/COM plan -> task rows','P001','R590I','NOT CONNECTED BY THE INSPECTED ENTRYPOINT'),
 ('R551 base posture','R585 base posture','excitation','S001','N585B','analogous module, code lineage via imports'),
 ('R585 posture','R586 posture','base excitation','N585B','N586C','same inherited module, neck override different'),
 ('R586 neck allocator','R589 neck update','head excitation','N586B','A589J','R589 imports/executes allocator'),
 ('R589 shoulder muscle','R589 d.ctrl override','arm excitation','A589G','A589I','only candidate and only selected channels'),
 ('R589 base command','R589 arm command','actuator channel priority','A589H','A589I','arm overwrites base'),
 ('R589 arm command','R589 neck command','actuator channel priority','A589I','A589J','neck final override, intersections must be tested'),
 ('R589 native loop','R590 continuous capture','physical state/time','A589L','C590A','continuous 24s includes R589 landing'),
 ('R590 settled snapshot','R590 replay setup','qpos/qvel/act','C590C','R590D','sampled state restore'),
 ('R590 replay posture','R590 replay neck','actuator command priority','R590I','R590K','base overwritten on neck indices'),
 ('R590 restart','R590 arm landing','optional muscle braking','R590A','A589G','NOT EXECUTED by inspected restart loop despite import'),
 ('R590 ctrl','MuJoCo step','excitation -> updated state','R590K','R590O','native plant feedback'),
 ('R590 step','R590 SKIN78 input','native qpos -> pose','R590O','R590P','qpos sampled, renderer separately invoked'),
 ('Original skin pipeline','R590 native model','pose and deformation','K001','R590P','DIFFERENT rendering path; shared canonical skin is not model-state identity'),
]
rows=[]; ids={r['id'] for r in records}
for a,b,p,wa,wb,assessment in E:
    assert wa in ids and wb in ids
    rows.append({'from':a,'to':b,'interface':p,'sourceWitness':wa,'destWitness':wb,'claim':assessment,'claimKind':'source-pinned trace / explicitly bounded negative'})
(OUT/'DIRECTED_RUNTIME_INTERFACE_EDGES.json').write_text(json.dumps(rows,indent=2)+'\n')
# A concise paper with the exact receipt and separately inspectable causal edges.
lines=['# BioRig / LUCID V008 — executable path, state ownership, and controller authority',
'', '**Status:** source-exact static evidence, not instrumented MuJoCo runtime. No BioRig executable file was changed.',
'',f'This audit pins **{len(records)} reviewed semantic claims** to exact raw archive bytes and AST scopes in **{len(cache)} distinct modules**, with **{len(fields)} state contracts** and **{len(rows)} directed, explicitly qualified cross-module links**.',
'', '## 1. The two R590 entrypoints are different experiments',
'', '### Continuous 24-second capture (`cap590`)',
'', 'The 24-second capture explicitly calls `reference.run(T_FINAL,candidate=True,...)` (C590A). In R589 that branch constructs `ArmLanding` (A589F), computes a shoulder-moment correction (A589C–E), refreshes it at the discrete controller cadence (A589G), and writes **base → arm → neck** muscle commands (A589H–J) before `mj_step` (A589L). The 12–24 second observation period is after an actual physical 0–12 second initial descent; later visual stability does not erase the early contact events.',
'', '### Restored 12-second evaluation (`replay590`)',
'', 'The restart imports R589 (R590A), but the active loop restores `qpos`, `qvel` and `act` (R590D–F), computes the inherited base controller directly (R590I), periodically updates R586 neck allocation (R590J), writes **base → neck** (R590K) and advances the native solver (R590O). **It does not construct or call `ArmLanding` in the inspected `continue_native` loop.** The import does not imply that transient arm control is active. This is a critical version-integration distinction.',
'', '## 2. What owns the actuator channel?',
'', 'The physical actuator command is `MjData.ctrl` (dimensionless excitation for these muscle actuators), not the desired joint angle, generalized torque, optimizer reference activation, or cached controller command. Within R589, individual arm channels can override the base posture controller; the neck vector writes last. Within R590 restart, there are no arm overwrites. These are *ordered program assignments*, not inferred runtime efficacy.',
'', 'A controller computing a correct `u` is not necessarily the controller whose `u` reaches the plant: the last write to each overlapping actuator channel before `mj_step` wins. The channel-overlap question is left open until actuator IDs and runtime indexing are inspected. The V008 matrix makes that missing check explicit instead of assuming disjoint arm/neck sets.',
'', '## 3. State is a typed causal boundary, not a single pose',
'', 'MuJoCo `qpos` (position), `qvel` (generalized velocity), `act` (internal muscle activation), and `ctrl` (excitation request) are different. `qfrc_applied` and `xfrc_applied` are separately supplied force channels. The restore copies position, velocity and activation but reconstructs some controller memory; it does not serialize all solver warmstarts, integrator internals or every stateful high-level component. `mj_forward` recomputes derived mechanical values. V004 established the concern; V008 pins the exact mutation sites and ownership in a queryable CSV.',
'', '## 4. The goal-to-motion pipeline is not joined in the inspected loop',
'', 'R574 `IntentionAgent.decide` can choose only `none` or `R28` (G001, G008) in a dedicated evaluation harness (G009). The original `WholeBodyMuscleController` is a richer full-body solver (N001–N005), and the original planner produces desired trajectories (P001). **None of these is invoked in the inspected R590 restart loop**; this is a negative finding scoped to that entrypoint, not a claim that the methods are unused everywhere or that old systems were better.',
'', '## 5. Activation is not force; a frame is not proof of forward causality',
'', 'The R589 arm correction measures current shoulder qpos/qvel (A589C), uses posture-dependent actuator gain (A589D), and writes bounded extra excitation (A589E). That is a limited physical local controller—not general intent. The original skin pipeline can realize prescribed joint targets and estimate inverse muscle demand (K001–K002), while actual R590 qpos snapshots come from native physics (R590P). Any generated animation must retain provenance to know which path produced it.',
'', '## 6. Source-pinned relationship map',
'', '| Upstream | Downstream | Relationship | Source evidence | Boundary |',
'|---|---|---|---|---|']
for e in rows:
 lines.append('| '+ ' | '.join([e['from'],e['to'],e['interface'],e['sourceWitness']+' / '+e['destWitness'],e['claim']])+' |')
lines.extend(['','## 7. Manually reviewed code witnesses', '', 'Each witness below is checked against the **exact source archive SHA**, exact text and line number in `CONTROL_FLOW_LINE_WITNESSES.json`. These statements do not claim branch coverage outside the evidence.', '', '| ID | Module:line | Scope | Physical / program meaning | Unproven boundary |','|---|---|---|---|---|'])
for w in records:
    lines.append('| '+ ' | '.join([w['id'],w['group']+':'+str(w['line']),w['scope'],w['meaning'].replace('|','/'),w['boundary'].replace('|','/')])+' |')
lines.extend(['','## 8. Remaining executable verification','',
 '1. Run instrumented MuJoCo traces from identical initial conditions to verify actual `data.ctrl` writer identity, muscle-channel intersections, and the post-step effect of activation delays.',
 '2. Materialize the complete native runtime (not just code) and compare exact checkpoint physics with the source trace; no such replay is asserted by this V008 artifact.',
 '3. Expand semantic reviews from the current source-pinned critical modules to every historical version and every archived line; the complete static line index already exists but full causal interpretation does not.',
 '4. Investigate optional native forward control of the original whole-body solver with protected modern regression gates; it must not silently replace later verified improvements.',
 '', '**Version invariants:** original R574 frozen; R585–R590 unchanged; no actions; no generated renders; no claim of universal controller competence.'])
(OUT/'CONTROL_AUTHORITY_AND_STATE_LIFECYCLE_PAPER.md').write_text('\n'.join(lines)+'\n')
summary={'schema':'biorig.semantic-atlas.v008','sourceModules':len(cache),'witnessCount':len(records),'stateFields':len(fields),'qualifiedEdges':len(rows),'sourceArchives':[{'archive':Z[k],'sha256':hashlib.sha256((ROOT/Z[k]).read_bytes()).hexdigest()} for k in Z], 'files':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in ['CONTROL_FLOW_LINE_WITNESSES.json','SOURCE_PINNED_MODULE_MANIFEST.json','DIRECTED_RUNTIME_INTERFACE_EDGES.json','STATE_FIELD_OWNERSHIP_CONTRACTS.csv','CONTROL_AUTHORITY_AND_STATE_LIFECYCLE_PAPER.md']},'verification':'Source SHA, literal anchors, AST parsing and unique matches verified. No physical runtime tests claimed.'}
(OUT/'V008_VERIFICATION_RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n')
print('built V008',len(records),'exact witnesses',len(fields),'typed state fields',len(rows),'edges',len(cache),'modules')
