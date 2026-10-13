# BioRig / LUCID — Goal-to-Physical-Body Ontology and Source Contracts

**Semantic atlas V007.** A source-grounded explanation of what each major subsystem actually represents; which causal relationship is defined in code; which relationship is merely a potential interface; and which behaviors have never been established by source inspection alone.

**Preservation condition:** frozen R574, R575–R590 sources, native 84-muscle data, SKIN78 surface and all historic evidence remain unchanged. This is documentation, not another experimental controller branch.

## 1. The common project objective and an operational definition of progress

A fully developed BioRig character should receive a **goal**, identify desirable and unacceptable outcomes, generate a feasible body plan, coordinate its actual muscle excitation with its balance and support constraints, step its full native physical state, observe the consequences, and use those measurements to adjust control. The visible SKIN78 surface is not itself the proof of causal actuation: it is a projection of the physical state. Real progress means acquiring a *new validated closed-loop action*, not merely recording an additional interval of a known pose.

The system already contains different prototypes of parts of this chain. Their source-level existence is real. Integration, physical realization and generality are distinct claims and require separate evidence. No old branch should be deleted or swapped in on the assumption that it automatically supplies a missing link.

## 2. The eight distinct semantic objects

| Object | What it means in ordinary language | Authoritative state and what it must NOT be confused with |
|---|---|---|
| **Goal** | The future outcome to seek and the outcomes to avoid | `GoalContract` and `IntentionAgent` decision; **not** a spatial hand target or continuous motor program |
| **Forecast** | Estimate of possible consequences of each offered action | ExtraTrees predictions from a limited paired dataset; **not** the future observed physics |
| **Plan** | Desired motion/contact transitions over time | `CentroidalPlan`, foot-placement/COM targets; **not** actual joint positions or guaranteed support |
| **Joint task** | Specific error/acceleration to reduce | Jacobian and desired acceleration rows; **not** a torque already produced |
| **Muscle allocation** | Decide which available muscle actuators should contribute | Desired activation vector under moment/contact constraints; **not** actual instantaneous fiber force |
| **Native excitation/activation** | Command and the time-dependent muscular internal state | MuJoCo `data.ctrl` vs `data.act`; distinguish them from target joint angles and output images |
| **World physical state** | Location, velocity, forces and contacts resulting from integration | Native `qpos`, `qvel`, contact impulses and solver state; **not** animator-authored pose coordinates |
| **Visible skin** | Surface deformation driven by skeletal state | Canonical SKIN78 vertices / offscreen renderer; **not** independent evidence of causal physics |

The direction of the intended interface chain is **goal → forecast and veto → plan → task rows → bounded activation/excitation → native physical step → sensed consequences → revised commands → visible mesh**. This is the required architecture contract. It does **not** assert that any one historical runnable entrypoint currently performs the entire chain.

## 3. Why two genuine capabilities do not equal one integrated capability

### R574 goal selection is deliberately small and bounded

`R574_INTENTION_AND_AVERSION/r574_intention.py:20–21` fixes the complete action set to `('none', 'R28')`. `GoalContract` defines two named intentions, with explicit fall, settling, arm-hazard, effort, novelty and measured hazard constraints (lines 24–58). `OutcomeMemory` (76–109) fits outcome estimators from 29 paired examples drawn from 36 rows (68–73). It predicts outcomes *for those available actions*. `IntentionAgent.decide` (119–140) applies measured hazard veto, novelty veto, predicted hazard veto, and advantage threshold before selecting a pulse. This is a real causal choice over limited alternatives, not a general controller that learns any arbitrary human movement or body target.

`r574_evaluate.py:33–50` constructs cloned held-out scenes and evaluates selected and neutral responses. That is a protected experiment with physical rollouts, not proof that the choice policy is embedded in R590's settled-seating timestep or that it can command a novel reaching task. The R574 source's own explanatory preamble states that the goal is externally specified; anthropomorphic intent or consciousness cannot be inferred.

### The original whole-body muscle controller is broader but on a different source path

`lucid_bcr/neuro.py:196–580` defines an independent native-muscle task solver. It models **multiple competing objectives**: stance contact, foot flatness, COM capture and angular momentum, pelvis/torso/head orientation, swing foot, joint posture, muscle work and estimated ground reaction forces. In the source, an optional `relaxed_arms` mode fixes arm muscle channels instead of optimizing them (`223–229`); such a mode cannot be assumed to achieve arbitrary arm reaching. It exposes `control()` returning muscle excitation, which a driver must explicitly put into the active MuJoCo model and execute.

This original module is not automatically the active controller just because the frozen R574 archive contains the file. Conversely, the fact that R590's runtime uses narrower posture + neck modules does not prove the original QP was better: no identical native, skinned, acceptance-gated replay has been established by this documentation stage.

### A semantic planner is not an actuator

`lucid_bcr/planner.py:180–261` uses a short step horizon with COM velocity, heading, step width, LIPM divergent-motion position, support-foot placement and a bounded landing target. The planner chooses a proposed world-space COM and foot path. It does not prove that the native body executes those targets, preserves joint limits, or keeps the support foot planted. Its outputs must reach a controller that can generate feasible muscle excitation, followed by physical-state measurement. A plan that looks physically reasonable is a **proposal**, not a motion capture or a physics result.

### A skinned pose is not a muscle-generated movement

`lucid_bcr/pipeline.py:307–325` realizes an input pose through the original articulated compiler/skin path, with an optional `ground_lock` corrective translation for visual contact. In `333–369`, the optional `plant` path uses **inverse dynamics** of *already prescribed* pose history to estimate joint torque demand and allocate candidate muscle activation. That path answers “what estimated effort could support the imposed motion?” rather than “what motion did the commanded muscles actually cause in a physical interaction?” The two questions are valuable but different.

By contrast, a native `PhysicsBody`/MuJoCo forward step integrates forces and contacts over time. The face and hands can be deformed from that native posture in SKIN78, but true muscle-driven causality must be demonstrated upstream of the render. V004 and V006 trace and partially resolve those interfaces.

## 4. The original whole-body controller's actual equations and physical meaning

The following reconstruction is based on explicit code spans in `lucid_bcr/neuro.py`; exact numerical values and solver configurations are version-dependent and are not inferred where the source does not supply them.

**Generalized coordinates:** `T` maps independent reduced joint coordinates into coupled native coordinates (203–215). It preserves dependency constraints for passive/coupled joints. The code uses generalized coordinates because hip/knee/ankle angles and the free body have different degrees of freedom and must be compared through correct mappings.

**Physical inertia and non-muscle effects:** `mj_fullM` produces the native generalized mass matrix; `d.qfrc_bias`, `d.qfrc_passive`, `d.qfrc_applied` and modeled joint limits enter the reduced bias term (347–356). In everyday terms: before choosing a muscle contraction, the controller must account for inertia, gravity-like/bias terms, passive tissues, external pushes and anatomical stops. This is a *local acceleration prediction* conditional on the current model state.

**Muscle-to-joint moment map:** actuator muscle gain and native moment-arm rows form a reduced map from desired muscle activation to generalized force, named `B` in lines 353–361. Its columns are not arbitrary animation channels: they represent how each modeled actuator influences the system's degrees of freedom at the current geometry. The map changes as posture and muscle lengths change. Merely knowing the target shoulder azimuth does not itself specify which muscle to command until this map is evaluated.

**Contact support:** foot contact positions and Jacobians form `Jc`, and a friction-pyramid basis `G` estimates admissible contact reaction contributions (362–377). Contact stabilization rows (389–403) counter sliding/sinking and help keep planted feet flat. The mathematical solver can propose contact forces; the native MuJoCo environment still determines realized contact under its collision parameters and constraints. The source should never be interpreted as a perfect friction or no-slip guarantee.

**Balance:** native subtree COM, COM velocity and height define a divergent-motion estimate on **world horizontal X/Z**, while world **Y is vertical** (`404–447`). The controller adjusts the target COM acceleration and optionally angular momentum. When a body leans or receives an impulse, the target changes with both current COM location and velocity. This is more expressive than a script that simply clamps the pelvis to a chair.

**Head and torso:** separate pelvis, thorax and head rotational Jacobian tasks (448–459) express desired orientation with rotational error vectors. The original seated experiments' severe folded-head motion demonstrates why having an orientation-related symbol or test threshold somewhere in the repo does not prove the active runtime respected it. The only valid evidence is a physics execution with sufficient whole-body/skin checks.

**Movement:** swing-foot position/orientation, COM objectives and posture are mixed into a multi-priority task system (460–477), along with effort regularization and contact-force cost (478–486). Weighted and lexicographic solvers are alternatives (500–515). Higher-priority contact/balance tasks can conflict with a lower-priority aesthetic pose. This is exactly why each new motion goal requires explicit priority, safety and compromise semantics.

**Command versus physical response:** after choosing bounded activation, `control()` computes an excitation through `self.excitation(a)` and returns the command vector (`520–534`). The code's muscle activation model uses different rise/fall time constants (`557–580`); the required activation is not achieved instantly. A command satisfying an algebraic moment equation today may deliver a different realized moment over the next tens of milliseconds. R586's neck moment-constrained allocation must therefore be separately validated in forward native time, not only with predicted instantaneous moments.

## 5. Why recent version numbers are not interchangeable feature labels

R575–R590 are archived research stages. Their contribution is known more precisely from the V005 source archive audit. R585 modifies geometry and neck allocation; R586 changes predicted moment-constrained activation economy; R587 expands physics/replay/acceptance; R588 diagnoses collisions; R589 introduces transient muscle braking; R590 uses a physically settled test state. The specific R590 **continuous capture** and **seated restart** run different code paths: only the former executes the R589 landing controller. That is a source-proven distinction, not an opinion about visual quality.

The newest source version also need not be an integration of every historically existing module. A dependency declaration is not proof of runtime invocation. Nor is a successful 12-second seated animation evidence that purposeful movement planning has been solved. The new atlas therefore protects three different facts: what a module **can represent**, whether a driver **invokes** it, and what native **experiment proves**. These are not interchangeable.

## 6. Exact type contracts for future implementation and regression checks

| Interface | Input units / frame | Output | Correctness conditions | Independent acceptance evidence |
|---|---|---|---|---|
| `GoalContract` / `IntentionAgent` | Current normalized measured observations and named preference weights | One of `none` / `R28` with recorded reason | No future scene metadata leaking into policy; source-pinned training, novelty veto | Held-out matched physics scenes, forecast calibration; does not test reaching |
| `CentroidalStepPlanner.plan` | COM/feet position m, COM velocity m/s, yaw rad, time s, support side | Time-sampled COM path m and step targets m | Horizontal X/Z, vertical Y; landing reach limits and constraints checked | Planner output + forward native stepping under active contact |
| `WholeBodyMuscleController.control` | Native qpos/qvel/act, moment arms, model inertias, support contacts, tasks | Excitation per modeled native muscle | Units: generalized torque N·m or force N as appropriate; no unsupported contact wrench; bound activations | Same MuJoCo state with actual `ctrl`, `mj_step`, contact/Jacobian telemetry |
| Native actuator update | excitation per channel, timestep s, present native `act` | Updated muscle activation and realized force | Activation delay and actuator order preserved | Direct instrumentation of `data.ctrl`, `data.act`, `data.actuator_force` per timestep |
| Native support/contact | World pose m/rad, collision geometries, friction/contact coefficients | contact impulse/force, slip and support state | True seat/foot and hands measured; no unsupported infinite grip | Contact-point velocity Jacobians, impulses, high-frequency traces |
| SKIN78 native rendering | Verified native qpos + matching rig/skin asset SHA | Actual skinned vertex positions and projected frames | Original rig, original mesh; no interpolation or image substitution; timestamp match | Inline native captured animation, skin hash and physical trace receipts |

This table describes contracts. It does not claim all are currently satisfied together in R590. The point of the specification is to prevent another false “everything is integrated” statement.

## 7. Nonnegotiable cross-version relationship matrix semantics

For any pair of modules or version instances, use one of the following evidence states rather than a binary linked/unlinked guess:

1. **Same exact code** — two archived file instances have verified identical source SHA; not necessarily the same execution environment.
2. **Static import** — syntax names another module; imported object and dynamic use may remain unknown.
3. **Declared call candidate** — the call is textually bound to a uniquely identified declaration in context, with static caveats.
4. **Actual execution path** — reproduced runtime trace proves a call occurs under specific initialization/configuration.
5. **Observed physical effect** — captured native forces, contacts and state evolution connect a command to a physical consequence.
6. **Visually accepted behavior** — actual SKIN78 motion meets stated scene/action visual gates; not equivalent to validated physiology.
7. **Unknown / unresolved** — no adequate evidence of a particular relationship. **Unknown is never evidence of independence, failure, or regression.**

The full V003 2792×2792 matrix enumerates every pair, while V006 adds 1,995 aggregated **static candidate** edges. Neither can mathematically represent 100% of all possible run-time interactions from source syntax alone, because reflection, dynamic imports, external libraries, user events and solver states are environment-dependent. Actual runtime captures are the next layer of evidence, not a detail that can be assumed.

## 8. Failure and acceptance protocol embedded in this research paper

A change to one subsystem must specify its intended consequence and invariant preservation, not merely increase a revision number. For example, arm landing cannot be accepted from the maximum contact force alone: it must preserve head orientation, trunk balance, bilateral contact quality, no contact chatter, no unrealistic damping, native muscle excitation and full rendered posture simultaneously. A solution that avoids an artificial T-pose startup impact by replaying an already settled pose is a legitimate *rest-state validation tool*, **not** proof that it solved intentional arm movement or unsupported descent.

A new feature must preserve older tested capabilities by exact source/metric/scene diffs. Visual acceptance must show complete actual native motion, but not mask unproven dynamic effects. A new source checkpoint and a new native output are separate artifacts and separate grades of evidence.

## 9. Residual unknowns — explicitly open, not silently erased

- All direct callable bindings, source-level object identities, inherited methods, dynamic state mutation and solver external effects must still be validated by actual runtime traces; V006 candidates are not sufficient.
- The entire 70,823-line archive has AST and source indexing, but this paper hand-reviewed 26 critical source contracts and V004 hand-reviewed 22 runtime interface edges. There is much more source to semantically interpret; it is incorrect to claim every historical line has been hand-explained.
- No new native physical or SKIN78 render experiment was executed in the semantic-paper V004–V007 work. Prior historical native renders and numerical outputs remain as archived evidence, not freshly revalidated proof.
- R583 source presently has verified GitHub blob identities but was absent from the 19 locally pinned archive containers.
- The source does not establish a complete general-purpose intentional hand-target action end-to-end in R590. Such a claim requires a concrete full-body physics validation, with no version regression and source-pinned actions, not a wording change.

**This document is an expanding audit and research contract, not a declaration of total system completion.**
## Appendix A — manually audited byte-identical evidence anchors

Every clause below was checked against the exact original source-file bytes in its pinned ZIP. Each identity includes the input ZIP, source path, 1-based line span, exact syntax anchor, and a semantic claim with an explicit excluded inference.

### A.01 Binary choice constraint
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `R574_INTENTION_AND_AVERSION/r574_intention.py:20–21` · SHA-256 `08d06b1373901bbbccac2c60e706ad5968767ac0ff231c42dd0ffebe3dd8de8a`.
- **Exact witness:** `ACTIONS=('none','R28')`.
- **Semantic reading:** Goal selection outputs one of two pre-defined research pulse actions.
- **Boundary:** No arbitrary motion objective or continuous reaching control is shown.

### A.02 Goal/aversion weights
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `R574_INTENTION_AND_AVERSION/r574_intention.py:40–58` · SHA-256 `08d06b1373901bbbccac2c60e706ad5968767ac0ff231c42dd0ffebe3dd8de8a`.
- **Exact witness:** `'restore_supported_equilibrium':GoalContract(`.
- **Semantic reading:** Two named goal contracts have hazard, effort and novelty safety vetoes.
- **Boundary:** Externally authored reward preference is not autonomous desires.

### A.03 Evidence size
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `R574_INTENTION_AND_AVERSION/r574_intention.py:68–73` · SHA-256 `08d06b1373901bbbccac2c60e706ad5968767ac0ff231c42dd0ffebe3dd8de8a`.
- **Exact witness:** `assert len(pairs)==29`.
- **Semantic reading:** Training evidence fixes a 36-row dataset and 29 paired scenes.
- **Boundary:** Small sample; no broad generalization claim.

### A.04 Outcome-memory forecast
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `R574_INTENTION_AND_AVERSION/r574_intention.py:76–109` · SHA-256 `08d06b1373901bbbccac2c60e706ad5968767ac0ff231c42dd0ffebe3dd8de8a`.
- **Exact witness:** `ExtraTreesClassifier`.
- **Semantic reading:** Per action/event ExtraTrees or constant predictors estimate hazard/settle/severe-contact outcomes.
- **Boundary:** Frequencies are model forecasts, not calibrated physical risk guarantees.

### A.05 Action veto and scoring
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `R574_INTENTION_AND_AVERSION/r574_intention.py:119–140` · SHA-256 `08d06b1373901bbbccac2c60e706ad5968767ac0ff231c42dd0ffebe3dd8de8a`.
- **Exact witness:** `choice,why='none','current_measured_contact_or_tilt'`.
- **Semantic reading:** First current-contact/tilt, then novelty, forecast hazard and advantage veto R28.
- **Boundary:** All decisions remain within {none,R28}.

### A.06 Held-out evaluation
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `R574_INTENTION_AND_AVERSION/r574_evaluate.py:33–50` · SHA-256 `79437f0817cebe7254b04a483fa90556b2fd06f74e3dc8bd2701e3199a8a5811`.
- **Exact witness:** `selected=agent.decide(measured,'restore_supported_equilibrium')`.
- **Semantic reading:** Clone native scenes, classify goal, simulate selected/neutral branches.
- **Boundary:** A test harness, not a permanently running general motor architecture.

### A.07 Game intent schema
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/game_intent.py:31–66` · SHA-256 `6f55bd84c465655f89842abda07ba95d9679ae8883a32892e57eb95781e2fa48`.
- **Exact witness:** `class GameIntent:`.
- **Semantic reading:** Declares a typed game-level intention description.
- **Boundary:** Schema existence alone does not prove connection to current actuator loop.

### A.08 Steering choice logic
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/core_steering.py:45–78` · SHA-256 `971b0596c5f75c27deb0f39a8c3b553eb8b3f9b5c2c4238ff9d7744ff1ffa602`.
- **Exact witness:** `def select_primitives`.
- **Semantic reading:** Maps measured capture margin, collision imminence and requested motion into primitive labels.
- **Boundary:** Selecting a primitive is not executing a native MuJoCo trajectory.

### A.09 Centroidal step planner
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/planner.py:180–261` · SHA-256 `71b36d9ab3588b7cde89fe3e5e30518d3ae12f102659baf43bfb0e328e67185d`.
- **Exact witness:** `def plan(self, state:`.
- **Semantic reading:** Generates COM reference, divergent component of motion and step-placement targets over a limited horizon.
- **Boundary:** Planning desired motion does not prove muscle-level follow-through.

### A.10 Capture foot placement
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/planner.py:220–235` · SHA-256 `71b36d9ab3588b7cde89fe3e5e30518d3ae12f102659baf43bfb0e328e67185d`.
- **Exact witness:** `math.exp(w0 * touchdown)`.
- **Semantic reading:** Approximates divergent-motion capture under an inverted pendulum to adjust foot landing position.
- **Boundary:** Requires real foot contact and swing implementation downstream.

### A.11 Whole-body controller existence
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py:196–255` · SHA-256 `49243739c69abeca38daa460b154da4a33c869fdec58e3caf2a8188bcc69da4a`.
- **Exact witness:** `class WholeBodyMuscleController:`.
- **Semantic reading:** Uses native muscle model and 3D orientation/contact/COM tasks.
- **Boundary:** Not proof that R590 invokes this control path.

### A.12 Coupled-coordinate projection
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py:203–215` · SHA-256 `49243739c69abeca38daa460b154da4a33c869fdec58e3caf2a8188bcc69da4a`.
- **Exact witness:** `T = np.zeros((nv, len(self.indep)))`.
- **Semantic reading:** Builds a reduced generalized coordinate transform T to handle dependent joints.
- **Boundary:** Dependent DOF elimination assumes built-in coupling relations are correct.

### A.13 Active muscle variable selection
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py:223–229` · SHA-256 `49243739c69abeca38daa460b154da4a33c869fdec58e3caf2a8188bcc69da4a`.
- **Exact witness:** `self.free = np.nonzero(~arm)`.
- **Semantic reading:** Explicitly can fix arm muscle channels at tonic load in relaxed_arms mode.
- **Boundary:** Relaxed_arms flag may remove direct arm optimization; check actual run settings.

### A.14 Contact/muscle dynamics linearization
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py:347–377` · SHA-256 `49243739c69abeca38daa460b154da4a33c869fdec58e3caf2a8188bcc69da4a`.
- **Exact witness:** `B = (R * g[:, None]).T`.
- **Semantic reading:** Uses native inertia, passive/bias forces, muscle moment arms and contact Jacobians to predict accelerations.
- **Boundary:** Algebraic local approximation is not proof of robust full-body action.

### A.15 Highest-priority foot contact
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py:389–403` · SHA-256 `49243739c69abeca38daa460b154da4a33c869fdec58e3caf2a8188bcc69da4a`.
- **Exact witness:** `"contact", 0`.
- **Semantic reading:** Weighted/hierarchical objectives include stance point velocity stabilization and flat-foot orientation.
- **Boundary:** Constraint violation and true slip require measured contact and motion tests.

### A.16 COM capture mechanics
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py:404–447` · SHA-256 `49243739c69abeca38daa460b154da4a33c869fdec58e3caf2a8188bcc69da4a`.
- **Exact witness:** `xi = com[[0, 2]] + vcom[[0, 2]] / w0`.
- **Semantic reading:** Computes horizontal x,z divergent COM location with world y vertical, and updates target accelerations.
- **Boundary:** Capture control only applies in actual invoked controller.

### A.17 Head/pelvis/thorax orientation
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py:448–459` · SHA-256 `49243739c69abeca38daa460b154da4a33c869fdec58e3caf2a8188bcc69da4a`.
- **Exact witness:** `"ori_" + bname`.
- **Semantic reading:** Includes orientation errors for pelvis, upper torso and head as separate tasks.
- **Boundary:** Earlier head collapse proves active tested loop did not guarantee these targets.

### A.18 Swing foot and posture
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py:460–477` · SHA-256 `49243739c69abeca38daa460b154da4a33c869fdec58e3caf2a8188bcc69da4a`.
- **Exact witness:** `"swing_pos"`.
- **Semantic reading:** Converts planned swing-foot position/orientation into Jacobian tasks and weak posture target.
- **Boundary:** No direct proof seated reaching target is implemented.

### A.19 Muscle-activation optimization
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py:478–534` · SHA-256 `49243739c69abeca38daa460b154da4a33c869fdec58e3caf2a8188bcc69da4a`.
- **Exact witness:** `self.u = self.excitation(a)`.
- **Semantic reading:** Optimization over bounded activation/contact forces converts desired next activation to excitation command.
- **Boundary:** Returned excitation must actually be written into active data.ctrl and stepped.

### A.20 Native muscle time constants
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py:544–580` · SHA-256 `49243739c69abeca38daa460b154da4a33c869fdec58e3caf2a8188bcc69da4a`.
- **Exact witness:** `def reachable_activation`.
- **Semantic reading:** Accounts for activation and deactivation dynamics and interval-reachable activation bounds.
- **Boundary:** One-step prediction is not full physiologic validation.

### A.21 Original SKIN78 rendering pipeline
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/pipeline.py:216–229` · SHA-256 `aa2acd4818186358ac1876e34148fad32ac3aeffe6e6c500f3af33d5a1352a55`.
- **Exact witness:** `self.a = load_character()`.
- **Semantic reading:** Constructs articulated figure, skinner, optional muscles, tissue and inverse-demand plant.
- **Boundary:** Not a free-root forward physical simulation by itself.

### A.22 CausalRig debug snapshot
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/pipeline.py:243–260` · SHA-256 `aa2acd4818186358ac1876e34148fad32ac3aeffe6e6c500f3af33d5a1352a55`.
- **Exact witness:** `"label": "COMPLETE_CAUSAL_STATE`.
- **Semantic reading:** Copies articulated q/qd, muscle activation and optional tissue state.
- **Boundary:** Different state model from native MuJoCo qpos/qvel/act and controller memory.

### A.23 Joint-realized articulated mesh
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/pipeline.py:307–325` · SHA-256 `aa2acd4818186358ac1876e34148fad32ac3aeffe6e6c500f3af33d5a1352a55`.
- **Exact witness:** `self.real.step(target, dt)`.
- **Semantic reading:** Realizes submitted intent into pose, computes skinned vertices and optional visual ground correction.
- **Boundary:** Forward pose realization is not equivalent to muscles generating movement under contact.

### A.24 Inverse muscle demand diagnostics
- **Source:** `LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip` · `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/pipeline.py:333–369` · SHA-256 `aa2acd4818186358ac1876e34148fad32ac3aeffe6e6c500f3af33d5a1352a55`.
- **Exact witness:** `self.pl.inverse_dynamics`.
- **Semantic reading:** Uses pose history and inverse dynamics to infer joint torques then solves muscle demand.
- **Boundary:** Inverse solved from prescribed pose is not proof that those muscles would dynamically produce it.

### A.25 Native rest-state reconstruction
- **Source:** `BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13.zip` · `r590_rest_restart.py:35–53` · SHA-256 `3ed8765c1e76b774376f9f29792a2c643070244d84a69f292356e0ad8c50af68`.
- **Exact witness:** `d.qpos[:]=raw['qpos'][0]`.
- **Semantic reading:** Restores native positions, velocities and activation; initializes neck allocator memory from state.
- **Boundary:** Controller state and contact warmstarts are not fully serialized.

### A.26 Active R590 control write order
- **Source:** `BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13.zip` · `r590_rest_restart.py:60–87` · SHA-256 `3ed8765c1e76b774376f9f29792a2c643070244d84a69f292356e0ad8c50af68`.
- **Exact witness:** `d.ctrl[:]=base;d.ctrl[allocator.ids]=head_ctrl`.
- **Semantic reading:** Base posture commands are overwritten on subset by neck allocator before native step.
- **Boundary:** No active game planner, R589 ArmLanding, or original full-body controller invocation in this restart loop.

