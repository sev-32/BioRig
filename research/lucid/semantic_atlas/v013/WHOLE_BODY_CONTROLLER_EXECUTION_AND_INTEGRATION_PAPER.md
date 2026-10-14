# LUCID / BioRig Semantic Atlas V013 — whole-body controller execution, priorities, and historical integration contracts

**Status:** Forensic source-anchored analysis. The frozen R574 and R590 source is not modified. No new MuJoCo motion was simulated or visually approved by V013. All source claims below are scoped to the exact files and hashes in `SOURCE_MANIFEST_V013.json`; the executable assertions are in `WHOLE_BODY_SEMANTIC_WITNESSES.json`.

## 1. What exists, what is actually called, what is merely proposed

The project is **not** one monolithic controller with all historical features implicitly combined. The frozen R574 archive includes multiple **distinct** control lines:

- `lucid_bcr/neuro.py` — a standing, full-body constrained muscle optimizer. `lab/stance_lab.py` **instantiates, calls, assigns native `d.ctrl`, and steps MuJoCo** using this optimizer (source `stance.py:252,262,288–295`; witnesses WB029–WB034). `lab/posture.py:38–43` exercises its static effort solve. Those are actual source-connected lab entrypoints, not mere import relationships.
- `lucid_bcr/agility.py` — support-state machine over that whole-body controller. It **can** update foot support, swing targets, COM goals and contact force caps when `agility` is passed into the standing laboratory (`stance_lab.py:265–285`). This remains a *conditional* execution path.
- `lucid_bcr/planner.py` — a named 0.8–1.5 second centroidal planner based on support foot, speed, cadence, heading and capture-point prediction. It returns `CentroidalPlan`; it does not drive native actuators itself. In the complete frozen 558-Python-file archive, the *literal* `CentroidalStepPlanner(` constructor call candidates are in `tests/test_longterm.py`, not in R590 seated code. The FSM accepts an optional planner object, so this is **not** proof that planner execution is globally impossible; it is a limit of this archived source's explicit call-site evidence.
- `lucid_bcr/game_intent.py`, `game_engine.py`, `game_runtime.py`, `military_runtime.py` — intent and world-state interfaces, deterministic multi-rate tick accumulator and acceptance targets. They explicitly reject arbitrary pose-authority packets, but they **do not themselves implement one game-to-MuJoCo full-body step loop**. An acceptance matrix is a declared test goal, not demonstrated movement.
- `lucid_bcr/core_steering_runtime.py` — a translator from world/local COM and core orientation intent into fields on an *existing* whole-body controller. `apply()` writes `ctrl.com_goal`, `ctrl.com_height`, `ctrl.com_axis_scale`, and `ctrl.R_star`. It does not call `ctrl.control()` or `mj_step()` and therefore is not a standalone driven actor.
- `R546` to `R550` — a **separate real research lineage** of explicit arm-joint intent, physiological moment-arm allocation, learned proprioceptive/contact overlays and action-conditioned data collection. `R546` creates a joint-intent coordinator, calls its constrained least-squares correction, and applies the correction through the R543/R546 seated loop. Later R547–R550 runners reuse the task-waveform function. These sources do **not** establish an arbitrary 3-D hand-goal interface or automatic incorporation into R590.
- `R551` then `R574` — the seated correction/goal-conditioned R28 pulse line. Its muscle-command update follows **baseline plus correction, clamp, native physics**; R574 adds a decision between `none` and `R28`, proven by V012's archived decision replay. It is not a call to `WholeBodyMuscleController.control`.
- `R590` restart — uses `phys.controller_excitation` and ten final neck-channel overrides (R590:77–87), with **no call** in `continue_native` to `IntentionAgent`, `JointIntentCoordinator`, `CoreSteeringRuntime`, `CentroidalStepPlanner`, or `WholeBodyMuscleController`.

**Source-wide bounded search:** `FROZEN_R574_SYMBOL_REFERENCE_CROSSWALK.csv` records the exact source path and line of references to ten important symbols across *all* original Python files, plus whether each literal occurrence resembles a definition, import or candidate call. These types are **static syntax observations**, not measured runtime coverage. The R590 restart path is independently read from its separately pinned ZIP.

## 2. The original full-body optimizer: actual physical meaning

The class is `WholeBodyMuscleController` (`neuro.py:196–580`). Construction (`197–255`) requires `pb.with_muscles`, builds a reduction matrix `T` for dependent joint coordinates, selects hinges excluding hand/passive-toe targets, **sets a reference posture in the native physics body** at `:218`, captures target world rotations for Hip/Spine02/Head, and initializes mutable goal, support, fatigue and excitation state.

### 2.1 State and units

| Variable | Meaning | Source location | Ownership / continuity |
|---|---|---|---|
| `pb.data.qpos`, `qvel` | Current generalized position/velocity | `neuro.py:348`, `stance_lab.py:279–299` | MuJoCo native plant |
| `pb.data.act` | Native muscle activation state, dimensionless | `neuro.py:359`, `:561` | MuJoCo, not the optimizer's last `u` |
| `pb.data.ctrl` | Requested muscle excitation, dimensionless | `stance_lab.py:288,295` | Final program writer before native step |
| `controller.u`, `a_des` | Computed excitation and desired activation | `neuro.py:247,520–525` | Whole-body controller; *not* automatically the plant |
| `qstar`, `R_star` | Intended hinge position / world orientation references | `neuro.py:218–222` | Captured at construction, later mutable by bridge |
| `com_goal` | Optional COM (world position m, velocity m/s, acceleration m/s²) | `neuro.py:233,411–441` | Supplied externally or derived from planted feet |
| `support`, `swing`, `force_cap` | Feet selected for support, planned swing-foot trajectory, per-foot force limit | `neuro.py:232–237`, `:317–344`, `:463–470` | Set by the agility layer, if attached |
| `p`, fatigue, reflex, `last` | Solver parameters and time-dependent controller state | `neuro.py:200,242–249,525–534,536–555` | Separate from MuJoCo arrays; must be checkpointed for exact continuation |

**Coordinates:** the standing neural model uses vertical **Y**, ground horizontal **X/Z**, and orientation rotation vectors in radians. `CoreSteeringTarget` uses local displacement meters, local velocity m/s, acceleration m/s², and yaw/pitch/roll in **degrees** (`core_steering_runtime.py:17–25`); `apply()` explicitly converts those degrees to rotation matrices at `:60–64`. The planner carries heading in **radians** and velocity in m/s (`planner.py:180–261`), not the same interface or coordinate convention as R546's *joint-angle task amplitudes in degrees* (`joint_intent_r546.py:98–118`). A bridge must not silently treat these targets as interchangeable.

### 2.2 Equations of motion and optimizer control variables

The source forms reduced-space dynamics in `neuro.py:350–377` using the true MuJoCo mass matrix `M`, reduced coordinate transform `T`, measured muscle moment arms `R`, force-length-velocity gain `g`, passive actuator bias `b`, and physically applied loads. In semantic form:

`reduced generalized acceleration = inverse_reduced_mass × (muscle_activation_forces + contact_reaction_forces + bias_terms - required_inertial/gravity loads)`.

It solves for **reachable muscle activations** and nonnegative friction-pyramid coefficients for native foot-ground contacts. The latter represent *planned* ground reaction forces, **not independent forces injected into the native simulator**; the actual plant receives excitation from the controller, then resolves contact through MuJoCo. `neuro.py:520–534` returns `self.u`, records planned forces separately, and does not itself call `mj_step`.

The active contact set in `foot_contacts()` (`:317–344`) explicitly filters for `pb.ground_geom` and then for `self.foot_bodies`. Consequently, this task **does not contain seat, pelvis-seat, forearm-seat or hand-seat contacts** in its optimization contact variables. It does not follow that the MuJoCo plant has no seat collisions: it only establishes that the optimizer's own support-force/task set excludes them.

### 2.3 The task hierarchy exists, but the default is **weighted**

Source `neuro.py:389–486` constructs these candidate objectives:

| Source line | Objective | Nominal rank if hierarchical option used | Condition |
|---|---|---|---|
| 392 | foot contact acceleration / slip damping | 0 | qualifying planted-foot contact exists |
| 403 | planted foot flatness | 0 | `w_foot_flat > 0`, foot planted |
| 442 | horizontal/vertical COM balance | 1 | always produces a task row; capture-point branch is conditional |
| 446 | whole-body angular momentum damping | 1 | `w_angmom > 0` |
| 459 | head world orientation | 1 | always, with current head weight |
| 459 | pelvis / thorax world orientation | 2 | always, with weights |
| 467,469 | swing-foot position and orientation | 1 | `self.swing is not None` |
| 475–477 | joint-posture tracking | 3 | enabled by derived posture weights |
| 480–486 | muscle activation effort and contact-force regularization | 4 | current activation/force dimensions |

**Crucial configuration truth:** the default `NeuroParams` at `neuro.py:33–93` sets `solver='weighted'`, `capture_k=0.0`, `w_foot_flat=0.0`, `w_angmom=0.0`, `relaxed_arms=True`, `fatigue=True`, `control_dt=0.002`, `activation_model='step'`. Only if explicitly configured as `solver='hierarchical'` does control use `lexicographic_box_least_squares` (`:503–513`). Therefore **a source-defined rank is not a runtime rank guarantee** when using the default weighted objective. Nor are capture-point damping, foot-flat orientation or angular-momentum tasks active at their zero-weight defaults.

Under `relaxed_arms=True`, `neuro.py:225–228` excludes the defined arm-muscle mask from free optimizer variables. The code takes their current native activation as a load (`:357–361`), outputs fixed arm tone (`:521`), and does not actively coordinate a reaching arm in the normal standing configuration. That is **not equivalent** to all 84 muscles jointly solving a purposeful arm reach.

### 2.4 Activation, muscle force and fatigue

`neuro.py:488–525` clips activation to the reachable interval given native current activation (`:564–570`), optionally clamps it further by the fatigue model (`:489–490`), solves for task satisfaction, and calculates excitation to request the chosen activation (`:572–580`). `step` and `interval` are distinct activation discretization modes. The exact `u` chosen by an optimizer is not equal to the instantaneous physical force; V010/V011 measured the geometric and time-dependent relations separately.

`fast_reflex_excitation()` at `:544–555` is another optional layer and can modify the final command **after** a normal controller tick. In the standing laboratory, `d.ctrl[:] = ctrl.control()` occurs at the slow tick while `d.ctrl[:] = ctrl.fast_reflex_excitation()` can execute at every MuJoCo physics tick if a reflex was attached (`stance_lab.py:279–299`). A successful unit test of `control()` alone does not establish which excitation reaches native physics when reflexes are enabled.

## 3. Source-exercised entrypoints and program authority

| Source entrypoint | Purpose | Explicitly invoked control path | Final plant command | Physics guarantee established by this review |
|---|---|---|---|---|
| `lab/stance_lab.py::rollout` | Quiet stance / push recovery | `WholeBodyMuscleController.control`, optional `SupportFSM`, optional reflex | `d.ctrl` from controller/reflex | Source calls `mj_step`; **no new physical rollout was performed in V013** |
| `lab/posture.py::static_effort` | Search standing posture effort | `WholeBodyMuscleController.control` once with `static=True` | Static activation proposal | Does not establish successful dynamic stance by itself |
| `R546::run_task` | 3-joint arm-intent paired tests | `arm_joint_intent` → `JointIntentCoordinator.compute` → seated `do_step` | `base+delta` via research task | Earlier separate native tests, not integrated current actor |
| `R547–R550` | Learned/contact-informed arm and action-conditioned data research | Reuses authored R546 tasks through distinct runners | Their own research command composition | Existence and dependency evidenced; original reported success requires separate source receipt review |
| `R551::step_perturbed` | Seated posture with temporary muscle pulse | `controller_excitation` → `base+delta` | clipped 84-vector `d.ctrl` | Direct `mj_step` source invocation, separate solver |
| `R574::evaluate` | Safety/goal-dependent R28 pulse evaluation | `IntentionAgent.decide` → R569/R551 | `none` or bounded four-muscle supplement | V012 verifies archived decisions and 2,800 pulse updates, not new V013 physical runs |
| `R590::continue_native` | Settled restart posture/neck replay | seated posture excitation → R586 moment allocator | `d.ctrl[:]=base`, then neck override | Native replay built in R590; does not call old full-body solver in inspected loop |

### Why older functionality must be *integrated*, not merely copied

A planner output (`CentroidalPlan`), a whole-body controller COM task (`com_goal`), an R546 3-hinge trajectory (`qref`) and an R574 two-action policy (`none/R28`) are **different typed commands** with distinct coordinate frames, units, horizons and safety criteria. A piece of code existing somewhere inside R574 is not evidence that the latest seated runner inherits it, or that its default is active, or that two independent command vectors can be safely summed.

The potentially reusable abstractions are real: `GameIntent.to_locomotion_intent`, `CentroidalStepPlanner.plan`, `SupportFSM`, `CoreSteeringRuntime.apply`, `WholeBodyMuscleController.control`, the R546 native moment-arm allocator, R574 hazard vetoes, R586 neck allocation, R590 state restoration, and the original SKIN78 realization path. Their **interfaces need explicit adapters, activation conditions and common safety gates**, not an unqualified merge of source files.

## 4. Non-negotiable semantic integration contracts (no implementation yet)

1. **Goal identity and time:** every goal must carry a stable task/actor ID, timestamp, physical horizon and termination conditions. An R574 named policy switch is not a 3-D target.
2. **Frame and units:** distinguish world X/Y/Z from body-local lateral/up/forward; radians from degrees; joint-space target from hand endpoint in meters; correct gravity and orientation conventions.
3. **Measured-state freshness:** sensor observation time must precede the command; no use of future native poses or outcomes to pick a current movement.
4. **Actuator authority:** one resolved final writer per native muscle channel at each physical tick. Additive safety corrections, antagonist release and neck overrides must specify ordering, clipping, smoothing and fallback.
5. **Contact support classes:** foot-ground, pelvis-seat, forearm-seat, hand-seat, hand-object and unwanted floor impacts have different semantics. The original standing contact pyramid is *not* an arm-seat support solver.
6. **Activation and force:** optimization outputs activation/excitation; actual force depends on activation delay, geometry and native force-length-velocity. The V010/V011 physical relationships are measured for their specific states, not universal.
7. **Persistent memory:** save/restore goal and risk-state history, controller reference posture, COM offsets, support FSM phase, swing plan, fatigue, reflex history, neck allocator memory, native `qpos/qvel/act/ctrl`, simulation time, contact warm starts and all output provenance needed by the chosen runner. R590 restoration provides only a subset of this list.
8. **Safety gate and proof:** test native physical response and contact forces, head/torso integrity and full SKIN78 animation, with the owner retaining visual veto; do not replace physics with inverse-kinematics animation or declare source existence a delivered movement.

These contracts describe the **missing connection specifications**, not a new R591 controller and not permission to change a frozen version.

## 5. Verified negatives, positive connections and known limits

**Positive source-execution proofs:** standing laboratory constructs full-body controller, issues `d.ctrl` and calls `mj_step`; optional support FSM and reflex are wired; R546's coordinator is actually called in its research runner; R551's separate posture controller writes native excitation; R590 restart writes posture then neck and advances native physics.

**Specific negative source findings:** original `WholeBodyMuscleController.foot_contacts()` does **not** include seat collision contacts in optimization; default weighted solver does **not** implement strict lexicographic priorities; `relaxed_arms=True` excludes arm muscles from free optimization; `GameCommandFrame` is not a native engine execution loop; the selected R590 restart has no call to old whole-body controller or R574 goal policy.

**Still unproven:** universal absence of dynamic/reflection-based invocations outside explicitly inspected source; live successful old whole-body stepping; faithful total-model restart including memory; full body/seat integration of old solver; arbitrary world-space hand target reaching; motor-policy performance; generalized stability under contact changes; full human-level per-line semantic understanding of all R574 file instances.

## 6. Reproducibility and preservation

1. Keep `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` and `BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13.zip` in the atlas's parent directory, unchanged.
2. Run `python build_v013.py`; the script parses **21 exact source modules**, checks **70 independently authored semantic witnesses**, and produces the complete selected-module symbol index and a symbol-reference crosswalk across every Python file in the original archive.
3. Run `python verify_v013.py` for independent re-hash/source-line/AST row checks; see its structured JSON receipt.
4. Run `python package_v013.py` to build an integrity-checked ZIP containing all new code/docs plus unchanged V012 checkpoint (no model assets or images); verify the nested V012 SHA.

V013 source-line proofs are **static** and tied to archived bytes. Numeric V010/V011 measurements and V012 replay records remain preserved intact inside V012. None of the original R574–R590 executable implementations were touched; no GitHub Actions were used.
