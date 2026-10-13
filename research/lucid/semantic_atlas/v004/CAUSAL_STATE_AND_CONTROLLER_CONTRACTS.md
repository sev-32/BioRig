# LUCID / BioRig — source-verified causal state and controller contracts

**Atlas V004, handwritten semantic audit of the 28 critical modules.** Verified against pinned archive-entry SHA-256 in `PINNED_RUNTIME_SOURCE_MANIFEST.json`. This document is a mechanical engineering map of **what the provided source says**; it does not certify physiological fidelity, runtime stability, or completeness of all historical source. The machine-readable `CRITICAL_RUNTIME_EVERY_LINE_SEMANTIC_TAGS.jsonl.gz` contains every one of the 4,996 literal lines of these modules, including comments and blank lines. Its first-pass tags are explicitly syntactic, not purported human interpretations.

## 1. What constitutes the actual executed system?

There are **three distinct paths** in the source; conflating them was the central historical failure.

**A. Historical task vocabulary and reference realization.** `BCR.game_intent` describes user/world intent. `BCR.planner` turns locomotion intent into candidate future COM and support contacts. `BCR.core_steering` and `BCR.core_steering_runtime` express transferable action primitives. `BCR.pipeline:CausalRig` compiles an articulated pose and its canonical SKIN78 skin. All are present as actual source, but there is no evidence in the studied **R590 restarted seated** entry point that these planner/goal objects are instantiated. The reference rig can produce attractive visuals without proving free-root native dynamics.

**B. Historical native whole-body control architecture.** `BCR.neuro:WholeBodyMuscleController` owns posture, COM, foot/contact and orientation QP tasks, moment mapping and fatigue options. At its initialization, `pb.set_state` establishes target posture and `self.R_star` captures target world orientations (`BCR.neuro:196–256`). `control()` begins at line 347 and uses native contact and muscle state. This is important preserved work; its **presence does not mean** it is the active controller in R589/R590. The later experiments directly call an inherited `posture_stabilization_r51.controller_excitation` instead.

**C. Executed R585–R590 seated physical lane.** `R585` builds a MuJoCo seated model and adds a ten-muscle, six-neck-DOF allocator; `R586` wraps that allocator with an excitation-minimizing constrained optimizer; `R589` optionally adds explicit shoulder-muscle landing commands; `R590.capture` runs R589 uninterrupted 24 s, while `R590.restart` reads the physically produced t=12s state and directly runs the inherited postural controller and R586 neck optimizer. For this last routine, no task-level `GameIntent`, `CentroidalStepPlanner`, `IntentionAgent`, or `WholeBodyMuscleController` is invoked by direct reference in the root code (`R590.restart:1–104`). This is a **root-specific source fact**, not an inference that no other scene uses those systems.

## 2. The physics authority, exact state and units

| State or operation | Authority and units | Written/read by | Failure if disconnected |
|---|---|---|---|
| `m.opt.timestep` | Integration dt in seconds; R589's declared `.002` should be cross-checked with the model's actual dt | R589:19,106–108; R590.restart:23,60–62 | commands and sampling interpreted at wrong frequency |
| `d.time` | Absolute physics clock, seconds | R590.restart:43; `mj_step` advances | replay timing and delayed controllers can diverge |
| `d.qpos` | Position manifold: root translation in metres, quaternion rotation unitless, hinge angles radians; dimension `m.nq` | R590.restart:37,40; R589:61,125 | raw subtraction invalid for quaternion; rendered root may drift |
| `d.qvel` | Generalized velocity: root linear m/s, angular rad/s, hinge rad/s; dimension `m.nv` | R590.restart:38,41,78; R589:61,126 | wrong derivative/units; `nv ≠ nq` for free joints |
| `d.act` | Physically integrated muscle activation state, likely one value per activation state, dimension `m.na` | R590.restart:39,42,48–51 | command history cannot be assumed equal to realized act |
| `d.ctrl` | Muscle actuator excitation command, clipped/unitless per muscle | R585:86–87; R589:133–138; R590.restart:83 | lower-level and specialized control can overwrite same channel |
| `d.qfrc_applied` | Direct generalized force/torque; units depend on DOF | R589:139; R590.restart:84 | passive endpoint force is **not** a muscle command: needs explicit accounting |
| `d.xfrc_applied` | Body Cartesian wrench (forces newtons, torques N·m) | R589:140–141; R590.restart:85–86 | external push must never be described as muscle-generated |
| `qref` | Frozen native generalized *posture reference*, not geometric reaching target | R589:99,125; R590.restart:33,53,77 | replacing with settled qpos changes goal; lost control identity |
| `neutral` | Head-to-hip world horizontal offset reference in metres, X/Z | R585:65; R589:100; R590.restart:35–36 | restoring pose without reference produces new transient |
| `d.contact` and `d.ncon` | Current MuJoCo contact points, normals, constraint outputs | R589:110 via R588.ledger; BCR.neuro:317–344 | contacts can appear/disappear between low-rate samples |
| `d.subtree_com` | Native body-subtree COM in world metres | R589:128; R590.restart:80 | using pelvis position alone can miss whole-body support failure |
| `d.qfrc_bias` | Native gravity / Coriolis bias generalized force at current state | R585:39 | omission can lead incorrect head holding moments |
| `d.qfrc_passive` | Native passive generalized joint forces | R585:39 | double counting passive support corrupts demand |
| `d.actuator_force` | Actual current actuator force (not expected command torque) | R585:42 | limits of instantaneous gain model need testing |
| `d.actuator_moment` | Sparse actuator moment arms, state dependent | R585:34; BCR.neuro:286–290 | fixed mapping can select wrong moment channel |
| `allocator.last` / `.last_eff` | Controller optimization history, excitation fractions | R585:30,53; R586:26–27,48,67; R590.restart:47–51 | state snapshot without command memory is not a causal rewind |
| `head_cmd` | Ten specialized neck-muscle excitation commands | R589:104,131,138; R590.restart:57,82–83 | overlap overrides global posture allocation and changes physical effort |
| `arm_cmd` | Four deltoid / pectoralis arm-muscle channel values with timed gain | R589:104,130–137 | released after movement; does not automatically maintain bilateral seat support |
| `solref`, `noslip_iterations` | Numerical contact compliance/damping and contact solver configuration | R589:92–98; R590.restart:32 | need preserve exact material/solver identity; artificial no-slip is not material calibration |
| `Renderer.render(vertices)` | Camera/appearance output from a mesh, not plant integration | R590.render_restart:33–38 | visual success does not validate force realism |

**Ownership principle.** The native MuJoCo model/data is sole authority for free-root body motion and contact. Controllers may only set bounded muscle commands and explicitly documented applied passive/external forces. Articulation and skinning transform *observed native state* into a display witness. Game/project goal and planner outputs cannot teleport the native joint/root configuration.

## 3. Exact causal time step for R589 (source lines 88–150)

The following ordering matters. Later stages may not be interchanged without rewriting test semantics:

1. **Build plant** `r585.prior.make_body('seated')`; apply left and right SCM site-offset research geometry; enable `noslip_iterations=6`. Optionally modify thumb `geom_solref` only when `thumb_solref_s` is provided (`R589:88–99`). The default verified profile does not require that optional contact-material treatment.
2. **Capture posture reference** `qref = prior.reset(pb)`; store `neutral` from current head versus hip world positions (`R589:99–100`). It is a global whole-body orientation/posture reference, not the target for active hand reach.
3. **Construct controllers**: `MomentConstrainedAllocator` for the six neck DOFs using ten muscle channels, and optionally `ArmLanding` for bilateral shoulder abduction/adduction (`R589:101–104`). There is still the inherited baseline `controller_excitation` applied to other muscles.
4. **Loop using model timestep** `k*m.opt.timestep`. At `stride` samples read real contact ledger; count `>1 N` on/off transitions, track peaks and head angle (`R589:106–123`). This measurement is observer side, not an automated visual validator; 10 ms sampling can miss faster transitions.
5. **Calculate native generalized error** via `mj_differentiatePos(m, ..., d.qpos,qref)` and form `wanted[hinges] = clip(10*difference - .8*d.qvel, -8,8)` (`R589:125–126`). This is a proportional/differential posture stabilizer's generalized demand, *not* an intention-to-hand-position allocator.
6. **Sense support** from foot contact data and current hip subtree COM, then call the inherited base muscle controller (`R589:127–129`). Direct call path goes through `R585` to `BCR.posture`, not through `BCR.neuro.WholeBodyMuscleController`.
7. **Update specialized controllers every five physics substeps** (`k%5==0`), so nominal 10 ms updates for 2 ms physics (`R589:130–132`). Neck and arms are updated on the same period, but they are separately designed and may compete for shared posture effort.
8. **Actuator command composition** first copies `base` to all muscles, then overwrites selected shoulder actuator channels with `arm_cmd`, then overwrites all ten selected neck channels with `head_cmd` (`R589:133–138`). This **order is the physical semantic of priority**: last writer has authority. There is no whole-body QP resolving those overrides in the shown loop.
9. **Apply forces** using `passive_end_for_data` to `d.qfrc_applied` and a temporary X-direction hip force to `d.xfrc_applied` during `[.8,.92)` seconds (`R589:139–141`). Every reported muscle-only behavior must distinguish inherited passive direct forces from active muscle work.
10. **Advance time and physics** via `mj.mj_step`; muscle activation dynamics and contact constraints then produce the next native state (`R589:142`). Metrics include peak contacts, control effort and head angles; they are not a general motor task success criterion (`R589:143–150`).

### R589 landing mathematics and scope

`ArmLanding.update` (`R589:46–85`) creates a predetermined **single-DOF shoulder angle trajectory**, not a general-purpose goal. The target in radians is smoothed with `s(z)=z²(3−2z)` where `z=clip(t/arrival,0,1)` (`R589:28–30,52–59`). Desired angular speed is the derivative `target*(6z−6z²)/arrival` before arrival. Required corrective shoulder moment is `kp*(desired−q)+kd*(desired_speed−v)` (`R589:60–62`): units of `kp` must be N·m/rad, `kd` N·m·s/rad if `desired_torque` is N·m. These are fitted controller parameters; source does not show physiological identification.

After `release_at` the extra torque fades according to `1−s((t−release_at)/fade_duration)` (`R589:64–69`). An actuator is selected by sign of moment request, using deltoid middle for nonnegative and pectoralis major for negative requests (`R589:72–73`). Requested extra excitation `amp = clip(desired_torque / (moment_arm*muscle_gain), 0,max_extra)` unless the instantaneous per-excitation moment is too small (`R589:74–80`). **Important sign hazard:** a muscle selected by torque sign is not by itself proof the actual product `moment_arm*gain` has matching sign. If the ratio is negative and clipped to zero, the requested moment is silently unserved. This needs a measured actuator sign/efficacy gate.

The extra command is added to `base[idx]` and clipped to `.8`; this is **not** the actual muscle activation or delivered torque. The controller's effort counter uses `amp*.01` per update (`R589:80–82`), appropriate only when controller updates at .01 s. Its verified profile specifies target angles `−28°`, left gain `kp=16`, default `kp=20`, and fade-off after 1.2–1.9 s (`R589:22–26`). These are time-scripted shoulder targets, not adaptive bilateral support, and do not solve hand contact.

## 4. R585/R586 neck: two different optimization objectives

### R585: six-DOF neck stabilization, physically bounded actuator set

`NeckAllocator.__init__` builds six named controlled hinges and ten selected neck muscles, asserting all the native actuator IDs exist (`R585:16–31`). `update()` reads actual neck angles and speeds and constructs per-axis proportional/derivative torques from current bias/passive terms (`R585:32–42`). The rest of the active body's realized muscle generalized forces are subtracted from the neck moment requirement. `moment_matrix` supplies current moment arms and `mju_muscleGain` supplies state-dependent per-excitation force, giving a six-by-ten instantaneous model `M` (`R585:43–44`). The solver chooses excitation bounded in [0,max_activation] by normalized least squares, with a penalty toward previous command (`R585:45–55`). Its solution is a candidate command, not an observed muscle force.

**Head-angle measurement:** `angle()` compares world-space Head and Spine02 rotation matrices and reports absolute three-dimensional orientation difference in degrees (`R585:19–21`). This is not a direct measurement of isolated neck-flexion DOF, cranial angle relative gravity, cervical curvature, skin stretch or anatomy-approved appearance. The head can move as part of the torso, or the neck can contort locally while changing that aggregate value modestly. Thus a low scalar angle cannot replace the skinned animation.

**Geometry intervention:** `m.site_pos[sid,2]=-.025` alters the model-local left/right SCM insertion geometry (`R585:59–63`). Although source comments call the frozen baseline untouched, this is still an **experimental runtime model parameter edit**. Experiment identity must include it; no universal physiological calibration follows.

### R586: moment-constrained activation minimization

R586 subclasses R585 and calls `super().update(d,base)` to obtain a reference excitation (`R586:20–41`). At the same physical state, it constructs a six-by-ten estimated linear moment map `A` from moment arms times muscle gains and requires optimized commands to stay within a **per-axis 0.02–0.04 N·m band of `A@reference`** (`R586:40–52`). It minimizes the sum of muscle excitation plus a small auxiliary penalty on excitation change using HiGHS `linprog`. Bounds include a per-update slew of ±0.20 excitation and [0,.8] activation-command limits (`R586:20–76`). On optimizer infeasibility it falls back to the R585 command. The tracked integrals multiply each 10ms command sum by `.01` (`R586:67–74`).

This is a valid, measurable **algebraic instantaneous torque proxy** for R585 reference commands. It is **not** direct physical verification that actual `d.actuator_force` or net realized neck torques match those target bands throughout the subsequent integration. MuJoCo muscle activation lag, nonlinear force-length-velocity and contact coupling still operate. The physical trajectory/whole-body render must independently validate it.

### Written command priority

At the final native write (`R589:133–138`), base commands are written everywhere, arm-selected commands override their muscles, and head allocator commands override its ten muscles. This is not the same decision problem as the old `WholeBodyMuscleController` which attempts to optimize many objectives jointly. It explains why localized gains can trade arm behavior against head behavior and vice versa.

## 5. R590: physically generated rest is **not** a complete deterministic state rewind

### Continuous path (`R590.capture:25–68`)

1. Runs the unchanged R589 `run(24, candidate=True, arm_params=VERIFIED_PROFILE)`; retains actual time from zero and samples late physics from t=12–24 s.
2. Samples `qpos`, `qvel`, `act` every 0.4 seconds, computes a simple digest over those three fields, and stores 31 samples (`R590.capture:25–45`).
3. Separately counts >1 N arm-contact transitions using the denser R589 `samples` after 12 seconds (`R590.capture:46–54`).
4. The observation window is physically contiguous, but a visually stable late window does **not** validate the earlier 0–12s descent which produced the settled state.

### Restart path (`R590.restart:26–97`)

1. Loads the saved native `qpos`, `qvel`, `act` arrays; rebuilds the model and experimental SCM/no-slip settings (`R590.restart:26–32`).
2. Calls `prior.reset(pb)` **before** replacing physical state and captures the inherited neutral reference at that earlier position (`R590.restart:33–36`). This is deliberate; resetting these references from the settled state changed control policy.
3. Assigns qpos/qvel/act from the saved t=12 state, sets `d.time=12`, calls `mj_forward` to recompute derived native state (`R590.restart:37–44`). `mj_forward` is not a physical settle or integration step.
4. Creates a fresh R586 allocator. It seeds the prior command history from the native activation indices if available (`R590.restart:45–51`). **Command and activation are not generally identical.** This is a plausible approximation and a source-proven dependence, not a byte-identical restoration of the original allocator's commands.
5. Directly executes the inherited native base controller and R586 neck allocation for 12 new seconds, setting forces and optionally adding the 120 N hip push (`R590.restart:55–87`). It **does not instantiate or update `ArmLanding`**. Because the R589 landing program fades after ~1.9s, a later sitting interval can remain similar; that is not equivalence of code paths.
6. Its recorded metrics cover arm load, head orientation, pelvis X and contact toggles. They do not prove foot force distribution, skin collision, grasp, end-effector task error, fatigue, or purposefulness (`R590.restart:58–97`).

### Missing from a claimed “complete causal state”

The actual serialized `R590_SETTLED_CONTINUOUS_NATIVE_QPOS.npz` contains only qpos/qvel/act/time arrays (`R590.capture:43–45`). Recreated values include the initial posture reference and inferred previous neck command. The source does **not** serialize the full controller object, `self.last` vs actual history, possible model-internal runtime state, MuJoCo warm-start quantities, solver contact constraints or RNG/external sensory state. This may be sufficient for the observed short controlled restart, but **it is not an exact generic `mj_getState` / `mj_setState` and full controller rewind contract**. That broader guarantee remains unproven. The original `BCR.pipeline:CausalRig.snapshot` (`BCR.pipeline:243–260`) similarly defines its own *reference-lane* state, not the same native solver/control state.

### Source-defined restart test classification

`R590.restart` supports a *seated steady-state continuation* classification. It **must not** be promoted as a proof of autonomous whole-body balance from arbitrary cold start, arm stabilization during new reaching movements, or learned action planning. The +120 N push applies for 120 ms at absolute native time 12.8–12.92 s, not 120 N indefinitely. The numeric result of that push may be slight and cannot substitute for wider disturbances.

## 6. Canonical SKIN78 render path and proof boundary

R590's renderer is correctly sourced: it uses the existing `CausalRig(RigConfig(realization='reference', deformation='canonical', muscles=False, demand=False, support='none'))` and checks the original skin hash (`R590.render_restart:16–20`). It reads native `qpos` via `pb.read_state(qpos=q)`, compiles anatomical joints with explicit native placement, invokes `_deform` and renders the deformed vertices via the original `Renderer` (`R590.render_restart:33–38`). The compositor labels 31 actual stored physics states for 0 and +120 N and creates a GIF without interpolated poses (`R590.render_restart:40–88`). The seat visualization derives its box dimensions from the actual `research_seat` native geom (`R590.render_restart:22–29`).

This gives strong **source identity and image pipeline provenance**. There are still two independent truth questions: (1) Does the MuJoCo plant enforce physically plausible force/contact/muscle dynamics? (2) Does the SKIN78 skin agree geometrically with all collision bodies and avoid penetration, clipping, broken twist/neck skin? No automatic vertex-to-collider distance or continuous contact deformation test appears in this renderer. Hashing the mesh and source states does not establish skin/collision clearance or visual acceptance. Native frames every .4s may also conceal high-frequency jitter, so output-review tools must be able to ask for contact-event-centered frames.

## 7. Full-body evaluation gates versus narrower bench criteria

The earlier R541 development curriculum checks loaded feet, support margin, head/hip orientation, root tilt, return and missing motor assistance, with an explicit **ownerVisualApproval=false** and **productionApproved=false** (R541:96–135). R562 `is_settled` checks root X, root velocities, seat and foot forces and impacts but no head-vs-torso or skinned deformation (`R562:38–46`). Hence “settled” is only a bounded condition for that experiment. It is unsound to infer head integrity from its Boolean return.

R574's `GoalContract` (`R574.goal:23–57`) adds explicit aversions, but its actual action set is `('none','R28')` (`R574.goal:20`). The `OutcomeMemory` trains event-specific ExtraTrees on only 36 source rows and 29 paired observations (`R574.goal:68–99`). `IntentionAgent.decide` selects between the two actions according to measured aborts, novelty and predicted risks/benefit (`R574.goal:119–140`). This is a *bounded policy evaluation*, not universal movement intelligence. Its lock/evaluation harness (`R574.evaluate:13–69`) records independent cloned counterfactual branches; it does not mean that R590's restarted loop calls the policy.

## 8. Semantics of the wider preserved modules that require reunification

- **`BCR.game_intent.GameIntent`**: coordinates are world-space velocity m/s and yaw radians (`BCR.game_intent:30–66`); projection to planner converts XZ velocity into speed and heading, choosing `atan2(v_x,-v_z)` unless near rest. Does not issue muscles.
- **`BCR.planner`**: centroidal COM/DCM and proposed footstep contacts, at planning interval with a one-second default horizon (`BCR.planner:1–9,63–125`). Planner output explicitly includes the truth label that it is *not a joint target* (`BCR.planner:88–110`). Does not physically guarantee a successful gait.
- **`BCR.core_steering`**: named primitives correspond to desired support/pose/momentum behaviors, not an actuator implementation. Runtime adapter can set controller COM/segment targets (`BCR.core_steering_runtime:17–69`); the path to native R590 is not directly established.
- **`BCR.neuro`**: has independent/affine-coupled DOF reduction (`BCR.neuro:203–212`), separate support flags and contact force caps (`BCR.neuro:231–255`), state-dependent muscle moment maps (`BCR.neuro:276–290`), ground patch sampling (`BCR.neuro:317–344`) and comprehensive control logic beyond seated stabilization (`BCR.neuro:347–580`). Existing code merits test-by-test reintegration review; simply swapping controllers would be an unjustified rollback.
- **`BCR.pipeline`**: the original causal reference lane can compile demanded intents and produce canonical skin. `CausalRig.step` can `ground_lock` the reference skin/root (`BCR.pipeline:307–324`). Such a root adjustment is not a valid replacement for native free-root physics. Source intent separates these truth classes.
- **`BCR.contact_material` and `BCR.contact_flight`**: friction solver tests and signed foot/force transforms predate R583/R584. The experiments must be compared by actual physical model, units and rig to determine whether later work was redundant or new.
- **`BCR.muscle_allocator`**: reduces antagonistic overlap in multi-task muscle demands, but is a heuristic priority allocator; the local R586 neck LP is mathematically distinct. A compatibility review is needed before combining them.

## 9. Semantic invariants for all future analysis and implementations

**Invariants that can be tested without creating a new controller:**

1. Every realized native state is finite, with `qpos.shape == (nq,)`, `qvel.shape == (nv,)`, `act.shape == (na,)`, all in the correct coordinate/units convention; never subtract quaternions as vectors.
2. Source-built experimental plant identity includes mesh SHA, SCM insertion coordinates, friction, contact geometry, solver iterations, timestep and passive priors. A match in mesh alone is insufficient.
3. All non-muscle applied forces have separately traceable channels (`qfrc_applied`, `xfrc_applied`); none may be disguised as muscle-generated balancing.
4. Record `base`, `arm`, `neck`, final `d.ctrl` and actual `d.actuator_force` at controller/physics rates. If a command is overwritten, the final command—not the hypothetical intermediate result—is what determines plant input.
5. Preserve native physical state **plus controller recurrent state and all goal/reference variables** across reproducible continuation. An approximate restart must be labeled approximate until equality of trajectories is demonstrated with tolerances.
6. Record actual actuator sign, per-muscle delivered moment, and saturation. Test the R589 sign/clip hazard rather than assuming deltoid and pectoralis recruitment was effective.
7. Do not equate R586's algebraic `A@u` with actual realized force at the next timestep. Test both with the native muscle activation delay.
8. A supported-rest test, a controlled arm landing, a unilateral reach, bilateral hand rest, grasp, standing recovery and locomotion are **different tasks** with distinct acceptance gates. A pass in one cannot silently imply others.
9. Pair each native trajectory with full SKIN78 visual output, including close-up head, arm, seat and contact-event windows at adequate framerate. Presentation must be derived from physical qpos; rendering cannot improve the physics.
10. No version is promoted or discarded on semantic similarity. Require exact archive/tree hashes, relevant task metrics, replay tests, visually inspected native render, and explicit user override authority.

## 10. What remains unknown—do not invent relationships

The pinned source proves explicit imports, call syntax and writes; it does **not** prove every historical version ever ran correctly, nor when a regression first occurred. The V003 all-pairs relation universe has 7,795,264 cells; unobserved edges remain unknown. Comprehensive architecture completion requires actual Git history and missing binaries, reflection/dynamic-call resolution, MuJoCo instrumentation, sensor timing, contact solver state, model actuator parameter inventory, and semantic review of all other 70,823 source lines beyond the 4,996 runtime-priority lines here. No hidden OpenAI deployment explanation is inferred from these project files.
