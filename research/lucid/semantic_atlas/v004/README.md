# BioRig / LUCID semantic atlas — checkpoint V004

**Not a new controller. Not a version rollback. No GitHub Actions. No fictional completion claims.**

This checkpoint *extends* V003 and includes the original V003 ZIP unchanged. The authoritative executable scientific source continues to be the individually hashed original archives, especially R574 and later R585–R590 experiment checkpoints.

## Evidence completed here

- Pinned 28 directly inspected, runtime-critical source files with their **exact ZIP container path, archive member path, byte length and SHA-256**. Missing source anchors: zero among this selected set; the broader global archive/Git tree remains incompletely reconciled.
- Indexed **4,996 literal lines**, each keyed to exact source identity, enclosing AST scope and conservative statement/state meaning; verified all 4,996 back against source bytes. These are machine-tagged first-pass meanings, not 4,996 individually manually reviewed proofs.
- Extracted **4,169 statement instances, 3,048 static call sites, 287 import sites, 224 class+callable definitions** in the same selected set.
- Recorded **22 manually source-reviewed interface edges and observed negative direct-call facts**; linked to exact file and line spans. Runtime execution of all edges remains unverified, unless accompanied by prior independent physics evidence.
- Added **191 qualified callable boundaries**, **100 syntactic native state assignment sites**, and the full **28×28 typed relationship table**. Most pairs are labelled UNKNOWN, not “unrelated.”
- Documented, in detail, native state ownership (`qpos`, `qvel`, `act`, `ctrl`, applied forces, moment arms, solver state), time stepping, the separate R590 continuous/restart paths, R589 control handoff, R585/586 optimizer objectives, R574 two-action intent policy, canonical SKIN78 rendering and semantic acceptance failure modes.
- Source-verified three important open problems: specialized arm and neck actuator overrides are not a joint whole-body optimizer; R586's moment tolerance is an instantaneous command proxy not measured realized torque; R590 physical restart reconstructs rather than serializes complete controller memory.

## Files to read, in order

1. `CAUSAL_STATE_AND_CONTROLLER_CONTRACTS.md` — human-reviewed mechanical/semantic paper and exact source locations.
2. `RUNTIME_SOURCE_TRUTH_GRAPH.md` — directed, source-evidenced relationships and non-invocations.
3. `FUNCTION_BOUNDARY_AND_MUTATION_CATALOG.md` — per-function line ranges, arguments, and state write candidates.
4. `RUNTIME_28x28_VERIFIED_RELATIONSHIP_UNIVERSE.csv` — all studied module pairs; UNKNOWN explicitly means not established.
5. `CRITICAL_RUNTIME_EVERY_LINE_SEMANTIC_TAGS.jsonl.gz` — all 4,996 source lines with exact text, source hash and machine-syntax explanations.
6. `PINNED_RUNTIME_SOURCE_MANIFEST.json`, `VERIFIED_RUNTIME_RELATIONSHIPS.json` and remaining JSON files — auditable machine source.
7. `verify_v004.py`, `build_runtime_graph.py`, `build_runtime_lines.py`, `build_function_authority.py` — read-only regeneration and independent integrity checks.
8. `V003_FROZEN_ATLAS.zip` — unchanged pinned previous checkpoint: complete 2,792-archive-file manifest, 70,823-line first-pass source index and 2,792² all-pairs matrix.

## Actual coverage versus requested target

The requested target is source-anchored explanation of **every** historical code line, runtime state interaction and regression relationship. V003 indexes all 70,823 available source lines but only does syntactic first-pass semantic classification globally. V004 manually reviews critical physics/controller contracts and annotates all source lines of 28 selected modules, **not** all 656 Python files. Source-code indexing completeness is distinct from semantic causality completeness. The broader original reference includes 126 path-level version markers; these do not constitute a verified Git ancestry. Missing Git-only sources, unmodeled dynamic dispatch, MuJoCo physical model numeric params/binary semantics, full historical commits, and actual on-device render judgments remain open.

**Avoid accidental loss:** R574–R590 variants have not been merged or deleted; none of their executable sources were touched. The documentation is a separate GitHub research-branch subtree; no actions/workflows are used.

## Reproduction

Copy the pinned original ZIPs to `/mnt/data` as recorded in V003 and `PINNED_RUNTIME_SOURCE_MANIFEST.json`, then run:

```
python build_runtime_graph.py
python build_runtime_lines.py
python build_function_authority.py
python verify_v004.py
```

The scripts read archive bytes and AST only. They **do not** run the MuJoCo simulation, modify joints, render images or claim real behavioral verification. `verify_v004.py` independently checks V003 ZIP SHA-256, source byte hashes, per-line identity and relationship/call catalog references.

## Next necessary verification layers

1. Read the *full* serialized MuJoCo model and all physical actuator/muscle parameters; index named body/joint/actuator IDs, body masses, inertia, geometry/contact pairs, DOF frames and activation dynamics.
2. Build an **actual observed dataflow trace** for each tested active entry point (current `R590.restart`, `R589.run`, original whole-body `neuro.control`, original task pipeline). Record every final physical command and its writer, and categorize memory, goal and sensory authority separately.
3. Reconstruct exact historical Git commit lineage by source SHAs and source/behavioral diffs; document **first-bad** only after paired physical and genuine full-character skin replay, not by narrative.
4. Human semantic review of the remaining thousands of functions and 65k+ source lines with line-by-line code/units/assumptions/safety boundary annotations.
5. A closed-loop acceptance schema that differentiates supported rest, landing, reach, grasp, stepping, balance recovery and task planning; actual SKIN78 animation and native physics measurements are mandatory for claimed motor advances.
