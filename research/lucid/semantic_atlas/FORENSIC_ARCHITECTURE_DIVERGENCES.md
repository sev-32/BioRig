# Source-established architecture divergences that explain the apparent regression

**This is not an allegation about hidden model changes.** These are specific, independently readable differences in the supplied frozen original R574 archive and the later checkpoint source. They are candidates for regression tracing. Calling one the *first* regression requires actual historical code ancestry plus matching native replays.

## 1. A richer original full-body muscle-control architecture exists, but the R551 seated lane takes a narrower route

**R552 workspace source:** `lucid_bcr/neuro.py:1–19` describes a whole-body, bounded least-squares controller simultaneously choosing 84 muscle activations and ground reaction force variables. It explicitly includes COM, pelvis/thorax/head orientation, foot slip, contact support, posture targets and an effort penalty. Its `NeuroParams` specify independent head, trunk, pelvis, COM, ground friction, fatigue and priority weights. This is **source evidence for a richer architecture**, not evidence that all of it worked on any particular bench.

**R551 seated source:** `LUCID_R552_WORKSPACE/R551_ACTIVE_RECOVERY/run_r551.py:21–25` imports `contact_grounded_r48.loaded_support_target`, `contact_flight_r46.muscle_moment_matrix` and `posture_stabilization_r51.controller_excitation`—**not** `WholeBodyMuscleController` from `lucid_bcr/neuro.py`. At `run_r551.py:75–92`, `step_perturbed` forms joint-error tracking demand, estimates foot support, invokes `controller_excitation`, adds a bounded pulse to `d.ctrl`, then advances native MuJoCo.

**Meaning:** the seated R551→R574 evaluation line is not evidence that the richer whole-body QP, core steering system, planning layer or learned memory is participating. It follows a narrow inherited path. A long sequence of improvements in the seated experiment may not integrate earlier whole-body systems. **This is an architectural divergence worth consolidating and regression-testing; it is not proof that switching controllers without measurements would help.**

## 2. The original goal/planning system is broader than R574's two-action policy

**Game contract:** `lucid_bcr/game_intent.py:31–66` represents desired world velocity, facing, stance, locomotion mode, jump/mantle/vault, lean and urgency; converts to typed locomotion goal.

**Planner:** `lucid_bcr/planner.py:1–9` says it proposes timed foot contacts and COM/DCM references and never directly emits joint targets. It explicitly disclaims a validated gait controller.

**Core primitives:** `lucid_bcr/core_steering.py:7–24` names hold, shift, raise, lower, rotate, absorb/create momentum, redistribute load, protect, brace, create clearance and settle. `core_steering_runtime.py:49–66` applies spatial targets to an existing controller's COM and segment orientation tasks.

**R574 narrowed policy:** `R574_INTENTION_AND_AVERSION/r574_intention.py:20` restricts actions to `none` or `R28`. Lines 40–57 describe two goal contracts and lines 68–99 train a small outcome predictor using fixed paired action evidence. That is a meaningful bounded research problem, but **it cannot express the entire intent ontology or general reaching/locomotion objective** by itself.

**Meaning:** The architecture for task-level movement exists in the historical source, but there is a gap between abstract intent and the specific seated native controller's executable action vocabulary. A necessary integration document must map this gap before writing any new intentional motion task.

## 3. The explicit whole-body acceptance gate became materially narrower

**R541 research curriculum:** `LUCID_R552_WORKSPACE/R541_DEVELOPMENTAL_CURRICULUM/curriculum_r541.py:96–135` classifies a physical episode with duration, external-assistance prohibition, motor-lock prohibition, cold-start status, loaded foot support, COM inside support, capture margin, nonfoot collisions, head-to-hip lean, root tilt, joint return, COM speed and invalid-physics veto. In particular:

- Lines 122–125 fail quiet episodes that exceed 15° head-hip lean or fail to recover it;
- Lines 109–111 reject external assistance, forbidden joint motors or an invalid cold start;
- Line 135 hard-codes `ownerVisualApproval=False`, `productionApproved=False`.

**R562 seated acceptance:** `R562_SETTLING_CONTROL/r562_settling.py:38–46` checks root X position/velocity, root tilt and angular speed, seat load, foot load and unexpected impact. It has **no head-to-torso or Skin78 deformation criterion**.

**R574 learned outcomes:** It inherits labels derived from the narrower seated criteria. A later native replay can pass this screen while the head is visibly unacceptable, as already observed. This identifies a specific **loss of evaluation coverage** between the different research tasks. It does not prove the code was literally copied and lines removed, or that an earlier stable seated build was destroyed.

**Meaning:** the false-success result was at least partly an **acceptance-contract regression**. Restore independent head/arm/skin and controller-state conditions to a *whole-body* qualification contract, while retaining seated-specific checks as subtasks. Do not conflate the R541 standing cold-start requirement with R590's supported-rest task, which legitimately begins from a physical snapshot but must be labeled differently.

## 4. Contact friction and solver sensitivity had already been investigated in the original archive

**Earlier physical experiment:** `lucid_bcr/contact_material_r536.py:1–21` (R5.36) already defines matched native MuJoCo `low_friction`, `high_friction`, `soft_contact`, `stiff_contact` and `reduced_iterations` experiments. Lines 55–88 measure effective contact friction, contact gap, normal loads and tangential contact-point slip using Jacobians. It explicitly states the friction perturbations are **not calibrated material values**.

**Energy interpretation:** `lucid_bcr/energy_dissipation_r535.py:1–6` and `:29–51` track spring storage and passive force components; contact constraint work is not automatically thermal dissipation.

**Much later R583/R584:** Near-ice/higher-grip contact sensitivity and additional no-slip solver intervention were again studied on the seated rig. They may provide **new case-specific experiments**, but the conceptual contact-material/frequency/solver methodology was clearly present earlier. **Without comparing the actual code paths, calling those later insights entirely new system fundamentals is misleading.**

**Meaning:** future work must first reuse and compare known R5.35/R5.36 contact and energy ledgers against seated R5.51+ test objects, instead of repeatedly rediscovering contact mechanics and ignoring earlier calibration infrastructure.

## 5. Full-state snapshot semantics existed before the R590 restart discovery

**Original CausalRig:** `lucid_bcr/pipeline.py:1–20` explicitly states all persistent quantities that influence later frames belong in `CausalState` and are included in `snapshot()/restore()`; debug restoring snapshots is not physical recovery.

**R590 physical restart:** the R590 branch experiments showed that restoring native qpos/qvel/act but resetting posture reference or the allocator's previous muscle action causes new transients and unwanted impacts. Restoring the reference/allocator history with native state preserved the supported-rest experiment.

**Meaning:** exact state-continuity is a pre-existing architectural invariant, but it was insufficiently mapped between the original articulation pathway and later native MuJoCo research. The meaningful work is to identify the **full set of physically causally necessary state fields across both paths**, including time, support contact, solver settings, previous action, sensor state, muscle activation and Skin78 state mapping.

## 6. Render authority degraded from original Skin78 proof to bare rig-only acceptance

**Original:** `lucid_bcr/semantic.py`, `pipeline.py`, `skinning.py` and `render.py` define the canonical character surface, pose compilation and physical/render truth separation. The frozen source records a canonical skinning output path.

**Recent:** R576–R584 frequently presented exposed MuJoCo rigs or sparse contact-frame captures as evidence of progress. The head catastrophe only became obvious after restoring the full Skin78 animation. That is a **visual QA and acceptance workflow regression**, independent of whether each experimental numeric result was reproducible.

**Meaning:** always run the full-character SKIN78 renderer on the same native state as physical metrics, and fail a visual/whole-body gate before reporting a general success. Camera/lighting changes must be marked visual-only. Never substitute generated imagery for renderer output.

## 7. User-level original objective and recent bench objective are not equivalent

The requested BioRig architecture seeks a character that autonomously enacts goals, avoids damage, uses an anatomical muscle system and automatically coordinates joint dynamics. The seated 14-scene R574 policy is explicitly bounded to `none` versus `R28` additional lateral pulses and localized postural recovery. R585–R590 repair genuine shortcomings of that physical bench. **Those repairs are worth retaining but are not a demonstration that the broader system can choose and accomplish new intentional actions.**

Do not throw away newer developments or reset to old R5xx code. Instead, document each older capability, determine whether and where it is actually instantiated in the current native runtime, and integrate only through typed, independently tested interfaces. An absent call path may mean the feature is preserved but **unwired**, rather than “regressed”.

## Immediate source-identity rules

- Original archive SHA-256 is `21e0c354023badd40485840296e09034809ae4eb055fd926eff39ac0b8700701`.
- Every claim above is anchored to an exact path/line in this archive. Full SHA-256 of individual source entries is in `COMPLETE_ARCHIVE_MANIFEST.json`.
- Actual GitHub branch source is separately fingerprinted in `GITHUB_BRANCH_TREE_INVENTORY.json`; local archive equivalence must not be assumed without matching SHA.
- Version markers in nested paths are descriptive evidence, not proof of commit chronology; compare actual Git ancestry to find a first-bad revision.
- Keep successful and unsuccessful R575–R590 experimental code distinguishable. Never erase tests or untested variants during consolidation.