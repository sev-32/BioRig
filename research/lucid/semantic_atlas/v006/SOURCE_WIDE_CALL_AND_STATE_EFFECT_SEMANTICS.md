# BioRig / LUCID — V006: source-wide call and state-effect semantics

**Scope:** all 45,243 static call sites extracted from 656 available Python sources in the frozen V003 19-archive inventory. This document describes syntax-grounded relationships, **not actual runtime call targets**, program execution or biomechanical performance. The same source archives and earlier V003/V004/V005 checkpoints remain unchanged.

## 1. What the new relationship layer means

The prior V003 matrix enumerated every file pair (7,795,264 cells); it did not establish the real behavior of every pair. V006 **adds a reasoned binding candidate for every one of the 45,243 extracted call expressions**, distinguishing explicit local names, `self` methods, imported symbols, builtin spelling, external calls, dynamic object calls, and unresolved constructs. **An absent static edge is not evidence that modules are independent.**

The line-level record is `SOURCE_WIDE_CALLSITE_BINDINGS.jsonl.gz`, with one indexed record per original call. Its evidence is reproducible using `build_source_wide_calls.py`. Each record carries file ID, line number, literal expression, status, proposed destination(s), and a warning about what cannot be inferred.

### Source-wide category totals

| Classification | Call sites | Meaning |
|---|---:|---|
| `ATTRIBUTE_OR_DYNAMIC_CALL` | 15,182 | Member or expression call requiring dynamic object/class resolution. |
| `PYTHON_BUILTIN_NAME_CANDIDATE` | 13,562 | Name spells a Python builtin; shadowing possible. |
| `EXTERNAL_LIBRARY_ATTRIBUTE` | 7,231 | Call syntax appears to address e.g. NumPy, SciPy or MuJoCo; external behavior not in atlas. |
| `IMPORT_NAMED_SYMBOL_STATIC_CANDIDATE` | 3,360 | A matching from-import and target declaration; import aliasing and load environment unproven. |
| `LOCAL_TOPLEVEL_STATIC_CANDIDATE` | 2,555 | One top-level function or class with same name in same archived module; rebinding unproven. |
| `SELF_METHOD_UNRESOLVED` | 1,761 | No matching same-class method declaration in source; inherited/dynamic dispatch possible. |
| `IMPORT_DECLARED_UNRESOLVED` | 949 | An import declaration exists but no unique archived definition is established. |
| `UNRESOLVED` | 331 | Identifier has no verified local/import/builtin destination. |
| `SELF_METHOD_STATIC_CANDIDATE` | 299 | One matching lexical method in enclosing class; inheritance/object identity unproven. |
| `COMPLEX_CALL_EXPRESSION` | 7 | Higher-order/chained call cannot be classified from simple binding form. |
| `LEXICALLY_NESTED_STATIC_CANDIDATE` | 3 | One matching nested definition contains the syntax site; binding remains provisional. |
| `AMBIGUOUS_IMPORTED_SYMBOL` | 3 | Several matching source identities under imports; no unique static binding. |

**Static one-candidate sites: 6,217 / 45,243.** Their aggregated graph contains 1,995 typed, file-to-file candidate edges. **This is not a measurement of executable-code coverage.** The unresolved remainder includes fully functional external packages and dynamically dispatched code.

## 2. Candidate callee effects: beyond import names

Every one-candidate expression is looked up by exact **destination file ID and declaration line** in the existing V003 function-effect catalog. This binds **4,774 declared function-body instances**, of which 3,858 contain some syntactic assignment. Assignments to local loop variables are not physical side effects.

The `DIRECT_CALLEE_EFFECTS.jsonl.gz` has one record per call site. For each candidate function it records direct read expressions, direct assignment expressions, return expressions, raise syntax, and whether a field write names an actual qualified property (e.g. `d.ctrl[:]`) instead of a local variable called `ctrl`.

| Qualified write field in a candidate callee | Static candidate instances |
|---|---:|
| `ctrl` | 331 |
| `qfrc_applied` | 293 |
| `xfrc_applied` | 277 |
| `qpos` | 55 |
| `qvel` | 32 |
| `act` | 29 |
| `time` | 21 |
| `geom_solref` | 14 |
| `geom_friction` | 8 |

**Qualification matters:** the statement `ctrl = np.zeros(...)` writes a local buffer; it is not by itself a write to MuJoCo `data.ctrl`. The report counts qualified property syntax separately. A field named `d.ctrl` still requires object identity verification to establish that `d` is truly MuJoCo data.

## 3. Selected source-grounded dependency witnesses

These examples demonstrate what the new edges can responsibly say; **candidate** means conditional on runtime binding and actual execution.

### R590 restored-state driver, not arm landing

Source identity: `f02755` — `CHECKPOINT:BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13:r590_rest_restart.py`. Found **1 file-level static candidate edges** originating here, without asserting any executes.

- Source line 56: `continue_native|setup` → `f02755` `r590_rest_restart.py` (LOCAL_TOPLEVEL_STATIC_CANDIDATE; 2 sites in the aggregated group).

### SKIN78 runtime construction

Source identity: `f02756` — `CHECKPOINT:BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13:r590_render_settled.py`. Found **2 file-level static candidate edges** originating here, without asserting any executes.

- Source line 27: `Renderer` → `f00108` `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/render.py` (IMPORT_NAMED_SYMBOL_STATIC_CANDIDATE; 1 sites in the aggregated group).
- Source line 25: `CausalRig|RigConfig` → `f00150` `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/pipeline.py` (IMPORT_NAMED_SYMBOL_STATIC_CANDIDATE; 2 sites in the aggregated group).

### SKIN78 restored-state renderer

Source identity: `f02757` — `CHECKPOINT:BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13:r590_render_rest_restart.py`. Found **3 file-level static candidate edges** originating here, without asserting any executes.

- Source line 21: `Renderer` → `f00108` `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/render.py` (IMPORT_NAMED_SYMBOL_STATIC_CANDIDATE; 1 sites in the aggregated group).
- Source line 19: `CausalRig|RigConfig` → `f00150` `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/pipeline.py` (IMPORT_NAMED_SYMBOL_STATIC_CANDIDATE; 2 sites in the aggregated group).
- Source line 49: `render` → `f02757` `r590_render_rest_restart.py` (LOCAL_TOPLEVEL_STATIC_CANDIDATE; 2 sites in the aggregated group).

### Original engine game integration

Source identity: `f00071` — `R574_FROZEN:LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/game_network.py`. Found **3 file-level static candidate edges** originating here, without asserting any executes.

- Source line 61: `ReplicatedActorState.validate` → `f00071` `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/game_network.py` (SELF_METHOD_STATIC_CANDIDATE; 1 sites in the aggregated group).
- Source line 62: `WorldBodyState` → `f00127` `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/game_runtime.py` (IMPORT_NAMED_SYMBOL_STATIC_CANDIDATE; 1 sites in the aggregated group).
- Source line 88: `profile_for_npc_distance` → `f00144` `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/game_profiles.py` (IMPORT_NAMED_SYMBOL_STATIC_CANDIDATE; 1 sites in the aggregated group).

### Original conditional steering rule

Source identity: `f00068` — `R574_FROZEN:LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/core_steering_governor.py`. Found **1 file-level static candidate edges** originating here, without asserting any executes.

- Source line 48: `SteeringDecision` → `f00068` `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/core_steering_governor.py` (LOCAL_TOPLEVEL_STATIC_CANDIDATE; 7 sites in the aggregated group).

## 4. Do not confuse lexical connectivity with an intentional movement agent

**Example: R590.** At the source level, `r590_settled_capture.py` delegates the whole uninterrupted simulation to `r589.run`. Our simple call resolver categorizes `r589.run` as an **attribute/dynamic** call: a Python import object named `r589` does not, merely by spelling, prove its identity. V004 separately reviewed the actual import and code path. `r590_rest_restart.py` independently reconstructs state and loops over the inherited posture command + R586 neck allocation; it does not instantiate or execute `ArmLanding` in its restart path. V006 deliberately does not erase that reviewed distinction when no simple lexical edge exists.

**Example: rendering.** Constructor-looking calls to `RigConfig`, `CausalRig` and `Renderer` can be statically associated with the original `lucid_bcr` declarations. That does not prove that VTK successfully rendered a particular character in a particular run. Such a claim requires exact native qpos/time-state receipts and an actual SKIN78 frame.

**Example: physical actuation.** A declared function may write an array called `ctrl` or explicitly target `d.ctrl`. Neither observation is sufficient to conclude the native muscle experienced the command without testing the active MuJoCo model and actuation delay. Direct `d.ctrl` assignment, muscle activation (`d.act`), and realized contact forces are three different causal events.

## 5. Practical scientific meaning — plain-language control chain

An **intent** specifies what outcome the body should achieve and what should not happen. A **planner** may choose a target posture or hand endpoint. A **whole-body allocator** converts target joint/body moments into muscle commands subject to available muscle moment arms and competing contacts. Native MuJoCo integrates dynamic state, muscle activation, gravity and contact constraints. The original SKIN78 renderer deforms the surface from native articulated posture. Each arrow is a separate interface contract, not a synonym for the others.

For example, **“move the hand to a target while remaining seated”** is not proven merely because the goal code exists or the head remains stable. Evidence must link a goal instance to actual actuator commands, state evolution, hand-target error, seat/foot contact response, and a native surface animation. No version of the static atlas asserts that complete closed-loop functionality is already established.

## 6. Version identity and context safety

The frozen R574 archive contains earlier R-series modules and original `lucid_bcr` modules. R575–R590 ZIPs also repeat earlier source. All graph records carry **archive file IDs**, not just basenames. A static match must therefore never silently mean “the newest version ran this old class.” Historical branch manifests, runtime environment setup and qpos/act model identity must be checked separately.

V005 verified the 96 archived Python source instances for R575–R590 (69 distinct SHA-256 contents), and it keeps R583 code as **remote-only** until imported with evidence. Neither chronology nor matching filenames proves inheritance.

## 7. Unresolved verification obligations

1. Re-resolve ambiguous relative imports, runtime sys.path changes, class inheritance, composed object methods and monkeypatching in a **version-specific working tree**.
2. Instrument live reads/writes and actual call stacks in reproducible native simulations.
3. Relate call paths to model joints, actuators, muscles, contacts, units and physical frames; a variable name is insufficient.
4. Extend human-authored semantic interpretation to all remaining historical functions/physics equations instead of equating syntactic tags with understanding.
5. Reconcile remote-only source blobs and all Git revisions not present in the 19 archives; never manufacture missing files.
6. Validate user-visible natural motion from actual Skin78 renders, never from numeric or static source results alone.

## 8. Integrity and reproducibility

`build_source_wide_calls.py` resolves against the *pinned immutable V003 inputs*. `build_direct_callee_effects.py` links direct effects against `SYMBOL_SIDE_EFFECT_CONTRACTS.json.gz`. `verify_v006.py` re-reads every output and checks referenced declaration identities, complete one-row-per-call coverage, expected source hashes, edge totals, and nested V005 archive SHA. All scripts are read-only with respect to LUCID source and Git branches.

**Status: V006 reproducible static causal map. Not 100% runtime semantics, and not permission to change any original controller.**
