# BioRig source-wide semantic reconstruction — exact checkpoint 001

This checkpoint is **fully indexed and integrity-tested**, not fully understood and not operationally accepted. It changes no controller or renderer code. All original input ZIPs remain immutable. GitHub Actions are unused.

## Completed verifiably in this phase

1. Pin and audit all available **19 original/checkpoint ZIP containers**: 2,792 entry instances, every entry SHA-256 individually recomputed against archive bytes, with version-scoped path and CRC32.
2. Index every actual line in the 658 code-file instances (656 Python + two HTML): **70,823 literal source lines**, retaining code text, function/class scope, syntax role, identifier references, units hints, and first-pass static semantic description.
3. Parse **656/656 Python files**, extracting 3,781 class/function declaration instances, 6,778 import sites and 45,243 call sites.
4. Extract 133,371 JSON key paths or schema locations across the readable JSON archives; arrays are sampled structurally, not every element decoded.
5. Build 3,468 procedure-level read/write/call/return/assertion records plus 3,373 explicit attribute mutation declarations. They are source-level evidence, **not proven runtime dataflow**.
6. Build full **2,792-by-2,792 file-pair uint8 matrix** with a value for all 7,795,264 directed positions. It identifies static import candidates, SHA-confirmed identical content, local call references and same-path conflicts. All not statically established relations are `0 = UNKNOWN`.
7. Repair apparent-version indexing so R40–R524 references nested inside the R552 workspace do not disappear into the R552 label. Preserve **126 distinct source path version markers** without asserting unverified chronology.
8. Write a source-grounded semantic system specification separating intent, planning, native muscle control, contact physics, canonical SKIN78 rendering, engine presentation, evidence and acceptance.
9. Curate 41 cross-module semantic/interface relationships with explicit epistemic statuses. Two R583 relationships are marked missing from the local archived ZIPs (though R583 files exist in GitHub research branch), not invented.
10. Create and run `verify_atlas.py`; 2,792 entry hashes, 70,823 source lines and 7,795,264 file-pair cells all checked **PASS**.

## Exactly what is still incomplete (must not be hidden)

- **All Git history and missing earlier/later branch content** have not been mirrored into this container. The connected GitHub research branch was separately inventoried at a pinned **116-file / 65-Python-file** tree. Source present *only* remotely needs independent byte-for-byte inclusion in later semantic-ledger batches, including R583.
- The 70,823 first-pass per-line semantics are algorithmic AST descriptions, not deep manual interpretations of every physical equation and state change. High-risk modules require manually reviewed causal contracts.
- Module import and lexical call references do not establish actual path-sensitive, temporal, reflective or solver-mediated dataflow. Runtime relationships and learned-model effects require instrumentation and replay.
- The 2,792² matrix is **complete as a pair-index universe** but has unknown entries for most pairs, by design. The phrase “100% relationship matrix” must not be used to imply 100% causal knowledge.
- JSON keypaths use structural recursion with only the first array member; model binaries, compressed `.npz`, `.joblib`, `.obj`, rendered media and `.whl` packages are hashed/inventoried, but their full internal numerical/mesh semantics remain to be reverse-indexed.
- Earlier progress descriptions contain inconsistent interpretations of whole-body balance, SKIN78 correctness, external disturbances and goal-directed movement. The source and actual behavior must be matched, not silently reconciled by narrative.
- The user-requested full direct and transitive dependency graph across all native physics states, control memory, activation delays, geometry frames and renderer mapping cannot be truthfully completed from static code alone. Typed dynamic probes and model-level schema audit remain necessary.

## Required future document layers (ordered)

1. **Runtime authority map**: identify the authoritative executable entry point for each branch and its exact model SHA; distinguish original `CausalRig` reference from native 84-muscle physics.
2. **Full-state ontology**: every field of `qpos`, `qvel`, `act`, `ctrl`, contact frames, sensor vectors, controller memory and render pose, with units, frame and mutation owner.
3. **Function-level semantic proof ledger**: review functions in priority order by read/write coupling, annotate their actual equations, boundary conditions, failure behaviors and parent/child symbols. The generated AST source-line ledger remains the immutable ground truth.
4. **Native relationship probes**: instrument actual dataflow and contact-solver/muscle causality; distinguish observed edge from guessed edge. Include traces and tests per connection.
5. **First-bad historical regression audit**: only identify a first-regressed version after comparing true source/code lineage and actual rendered physical states, not by inferring from a single later scene.
6. **Coherent task-level milestones**: keep posture/rest, reach, grasp, locomotion, balance and interaction distinct. Test intentional tasks using actual native skinned movement; do not call mere sitting “motor intelligence”.
7. **Cross-module review gates**: automatically fail promotion for missing SKIN78 proof, head/neck collapse, arm contact chatter, slip, controller state discontinuity, generated poses, invalid physical commands, mixed units, missing Git commit or failed replay.

## Reproduction

Source inputs are the original frozen R574 ZIP and the later BioRig/LUCID evidence ZIPs under `/mnt/data`. Run `python build_atlas.py`, then `python build_dataflow.py`, `python build_pair_matrix.py`, `python build_curated_links.py`, and finally `python verify_atlas.py` in an environment with Python 3.13 and NumPy. Scripts read archive text/bytes only; they do not import code from the project, launch MuJoCo, or mutate frozen source. See `COVERAGE_REPORT.json` for pinned SHA256 hashes of the input archives.

**Checkpoint policy:** leave a verified, downloadable source/code/docs artifact even though final semantic completeness is still open. Record unknowns rather than claiming completion. Preserve repository branch `research/lucid-r575-goal-intent`; no GitHub Actions.