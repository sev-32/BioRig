# BioRig / LUCID — semantic system specification, source-anchored draft 001

**Status:** Semantic reconstruction and verification map. **Not** a new movement controller, not an approved behavioral model, and not a substitute for running the full system. Statements marked *source intent* mean the code's stated purpose; they do not establish that MuJoCo actually achieves it. A function, renderer, planner or sensor can exist in source without being integrated into the active research runtime.

## A. The object of the project

The project is not a chair-balancing demonstration. The desired product is a single **continuously evolving, anatomically constrained body** capable of generating goal-directed movement through interacting bodily subsystems. Higher-level intent should select **what** to accomplish and avoid, not prescribe thousands of detailed muscle activations. Lower-level systems should derive coordinated muscle activity from physical state, task geometry, capacity, reaction forces, time and constraints. Future frames must be consequences of the actual physical transition, not edited screenshots or teleported body geometry.

A correct specification therefore must distinguish **task goal**, **selected primitive**, **predicted plan**, **support requirement**, **feedback**, **physical actuator**, **plant**, **observed result**, **rendered witness**, and **acceptance gate**. These are not synonyms. Numerical success in any single measurement is not enough to establish full-body success.

## B. The two physical/visual realization pathways must not be conflated

The historical archive contains two different causal authorities:

**Path 1 — original CausalRig/articulation and original Skin78:** `lucid_bcr/pipeline.py` explicitly distinguishes *reference realization* from *dynamic* joint realization. It sends permitted Semantic51 commands through anatomical relationships and pose realization to original skinning. In the reference profile, target joints can be committed directly; its correct skin output is a valid **appearance/rendering reference**, not proof of free-root physics. Skin deformation must preserve original weights, canonical helper rules and mesh signature.

**Path 2 — native free-root forward dynamics:** `lucid_bcr/physbody.py`, `lucid_bcr/neuro.py`, `lucid_bcr/contact_flight_r46.py`, `lucid_bcr/posture_stabilization_r51.py`, later `R551_ACTIVE_RECOVERY/run_r551.py`, and R562–R590 experimental modules operate on native MuJoCo generalized coordinates, muscle activation and contacts. They must not move the root or joints by assigning rendered poses. Only the native state drives the skin for physical proof.

**Critical boundary:** Showing the Skin78 character with correct appearance is not a physical validation, while showing a bare MuJoCo rig in a simulation is not an adequate **visual** validation of full-body behavior. The valid proof joins the two using the same stored physical `qpos` at each actual rendered frame.

## C. Full ontology of the working system

| Fundamental | What it means | Where it is defined/anchored | Inputs -> outputs | Truth boundary |
|---|---|---|---|---|
| Actor / world state | Authoritative root, velocity, support and contact identity | `lucid_bcr/game_runtime.py:WorldBodyState` | physical state -> validated world actor record | FPS offsets have no right to change world collision |
| Intent | Desired result, urgency, optional avoidance | `lucid_bcr/game_intent.py:GameIntent`, `AimIntent`, `lucid_bcr/intent.py`; R574 `GoalContract` | game/actor task -> typed goal | Goal isn't a pose or a physical force |
| Plan | Candidate temporal route through future support transitions | `lucid_bcr/planner.py:CentroidalStepPlanner` | intent + centroidal state -> proposed steps and COM/DCM path | Planner's docstring explicitly says candidate; no validated gait claim |
| Core action semantics | Hold/shift/brace/create clearance/absorb momentum/protect/settle | `lucid_bcr/core_steering.py:CorePrimitive`, `select_primitives` | current support danger + intent -> primitive sequence | Primitive isn't proof that muscles enacted it |
| Task bridge | Translate target COM/attitude to a control interface | `lucid_bcr/core_steering_runtime.py:apply` | local COM shift/velocity/acceleration + rotations -> controller task inputs | source says candidate, requiring physical proof |
| Body/articulation | Anatomical nodes, allowed DOFs, hand articulation, couplings | `lucid_bcr/semantic.py`, `anatomy.py`, `physbody.py` | legal motor/pose representation -> physical/generalized state | Semantic51 reference equivalence is separate from dynamic validity |
| Sense / proprioception | Measured joint/contact/body state | `whole_body_sense_r511.py`, `proprioception_r510.py`, `contact.py`, native `phys.sense` | plant state and contacts -> observations | current measurements must not access future outcome or harness labels |
| Reflex and stabilizer | Fast action based on current physical threats and support | `lucid_bcr/neuro.py`, `posture_stabilization_r51.py`, `contact_flight_r46.py`, `r562_settling.py` | current state + task -> desired force/activation | unvalidated posture criteria can create false passes |
| Muscle allocation | Turn competing body task forces into anatomically realizable excitation | `lucid_bcr/muscle_allocator_r58.py`; R585–R586 neck allocation | required generalized moments + actuator moment arms/gains -> bounded excitation | only physical forward dynamics proves output works |
| Plant | Masses, inertia, joints, tendons, muscle dynamics, contacts, solver, timestep | `lucid_bcr/physbody.py`, `plant.py`, native MuJoCo model builders | activation + external force + state -> next state | friction/solver/contact stiffness govern balance; never ignore |
| Skin | Convert committed skeletal state to original canonical deformed surface | `lucid_bcr/pipeline.py`, `skinning.py`, `render.py`; R585/R590 SKIN78 bridges | native qpos -> joints -> mesh positions -> image | camera and seat visuals cannot modify physics |
| Memory/prediction | Learn outcome likelihood or store safe motor histories | `motor_synergy_memory_r516.py`, `safe_motor_memory_r517.py`, R574 `OutcomeMemory` | observed samples -> trained decision data | small-sample outcome frequency ≠ guarantee |
| Safety/avoidance | Protect against collision, falling, unsupported motion and excess excitation | R562 safety and R574 `CONTRACTS`; R587 `whole_body_gate` | state + goal constraints -> permitted action | full-body visual head/arm gate was previously missing |
| Evidence/version history | Record what code and model produced each observation | immutable original ZIP, Git blob SHAs, receipts and renderer source | code, hash, scene, seed/state, trace -> falsifiable proof | a screenshot alone cannot reveal source ancestry |
| Engine presentation | FPS/third-person/NPC camera state; runtime handoff | `game_runtime.py`, `game_network.py`, `game_actions.py` | realized world-body actor -> presentation | viewpoint must not become a second physics authority |

## D. Causal cycle, explicit in semantic steps

1. **Receive intention**. The actor receives a typed desired task: velocity/facing/stance/hand reach/avoidances; validate units and domain. Example `GameIntent.desired_velocity_world_mps` is explicitly a world-space three-vector in metres/second; `desired_facing_rad` is radians.
2. **Measure reality**. Acquire present joint positions/velocities, segment orientation, COM, support contacts, skin integrity/geometry and contact loads with frame identifiers. Do not allow experiment metadata or future simulation branches into action selection.
3. **Understand affordances and constraints**. Identify which supports and routes are available, contact limits, clearance, reachable end-effectors, compatible core posture, fatigue, active goals/aversion.
4. **Select actionable intent**. A high-level primitive expresses desired result, not a detailed muscular script. `CorePrimitive.CREATE_CLEARANCE` is only a semantic selector until linked to physical tasks.
5. **Construct bounded task trajectory**. Predict time-dependent COM, capture margin, contact change and desired end-effector movement within limits, without overwriting the plant.
6. **Allocate demands**. Generate task-space or generalized force/moment demand and map it through the *current* actuator moment-arm matrix and force-length-velocity gains. Balance priorities across head, trunk, limbs, contacts and effort. Do not normalize away small but essential neck torques against stronger leg demands.
7. **Apply physical excitation**. Clamp per-actuator commands; integrate native muscle state, passive force and contact in MuJoCo at a declared timestep. Do not replace with kinematically authored joint trajectories for a physics proof.
8. **Measure actual effects**. Observe contact locations, effective friction, sign-correct wrench, actual joint motion, head-to-torso angle, arm impact transitions, skin penetration and effort. Full contact solver settings are part of the experiment identity.
9. **Decide next command**. At the next control interval, compare achieved vs desired state and adapt. Inaction is a permissible controlled action. High-level state, low-level muscle history and previous command belong to physical/recurrent state and must survive a restart.
10. **Render actual result**. Use the frozen Skin78 mesh and the same measured native qpos to render each timestamp. Authoritative visual inspection must include the full character, not only pelvis metrics. Compare with exact model/skin hashes.
11. **Accept/reject**. A meaningful milestone needs validated task accomplishment, collision and pose safety, continuity, sensory plausibility, repeatable physics, test provenance and inspected actual animation. A seated character without an intentional task is a support test, not proof of goal-directed motor intelligence.

## E. Current source-wide dependencies and interfaces

### Intent -> planning

`lucid_bcr/game_intent.py:GameIntent.to_locomotion_intent()` validates current input, derives horizontal speed and heading, constructs `planner.LocomotionIntent`. `planner.CentroidalStepPlanner.plan()` produces a proposed horizon containing step contacts, COM positions/velocities and DCM positions. Its own docstring clearly states this isn't a validated gait controller. The semantically relevant relationship is **proposes desired future support**, not **commits physical motion**.

### Core steering -> muscle tasks

`lucid_bcr/core_steering.py:select_primitives()` chooses `PROTECT`, `BRACE`, `CREATE_CLEARANCE`, `ROTATE`, `RAISE`, `SETTLE` etc. from state and intent. `core_steering_runtime.py:CoreSteeringRuntime.apply()` sets a controller's COM target and core orientation targets. Its `CoreSteeringTarget` supplies explicitly local translations (metres), velocity (m/s), acceleration (m/s²), and yaw/pitch/roll (degrees). This mechanism is **not** a complete end-to-end closed-loop arm reach and must not be reported as such.

### Whole-body muscle feedback -> plant

`lucid_bcr/neuro.py:WholeBodyMuscleController` declares a bounded least-squares control problem over anatomical muscle activation and contact-force weights. It reads MuJoCo mass/gravity/passive properties and actuators, prioritizing COM, contact slip and segment orientation. It is architecturally richer than the later narrowly targeted seated experiments, but requires its own measured verification; the existence of its equations does not mean it underlies every later R55x/R58x scene.

`lucid_bcr/posture_stabilization_r51.py:controller_excitation()` and `contact_flight_r46.py:feedback_excitation()` are related but different postural control pathways; static code relationships alone cannot certify equivalence. `lucid_bcr/muscle_allocator_r58.py:allocate_shared_muscles()` explicitly identifies contradictory simultaneous muscle demands and reduces lower-priority opposing contributions, using a heuristic normalized demand. Its docstring calls this a **bounded priority heuristic**, not an optimal solver.

### Frozen learned intention/aversion -> narrow action

`R574_INTENTION_AND_AVERSION/r574_intention.py` defines a two-action policy `ACTIONS=('none','R28')`. The `GoalContract` expresses `restore_supported_equilibrium` and `preserve_safe_posture` with explicit named avoidances and weights. `OutcomeMemory.fit()` trains separate ExtraTrees estimators on 36 source rows and 29 paired rows; it predicts hazard, settled, and severe arm-contact indicators for each of these two actions. The current policy therefore does **not** express arbitrary articulated reaching, despite the conceptual intent ontology. Importantly, a model's success criterion is only as sound as its measured labels.

### Sedentary evaluation flaw and subsequent responses

`R562_SETTLING_CONTROL/r562_settling.py:is_settled` (lines 38–46 in original archive) checks root lateral position/speed, tilt, angular speed, seat/foot load and unexpected contact force, but **does not check head/neck or complete skin**. This source-grounded missing gate explains why a real head collapse could coexist with a passing root-based settling test. It does **not** prove every earlier version was broken, and no claim about first-bad regression can be made from this isolated function.

R575 adds only a partial high-level observation latency experiment, not whole-loop delay. R576–R584 examine long-horizon support, tonic feedback, muscle synergy, contact-frame/pressure measurement, friction and no-slip. R585 corrects a demonstrated neck actuator/moment-arm deficit and builds a six-axis moment-constrained muscle allocator. R586 reduces head allocation cost while retaining physical neck control. R587 extends the SKIN78 seated proof to 24 seconds. R588 identifies arm/hand-seat collision chatter. R589 attempts actively decelerated arm landing. R590 preserves a physical seated snapshot and correctly restores both physical state **and controller memory**. These stages must remain separate: some improvements are local tests and some test fixtures, not full task milestones.

### Source/state/render continuity

`lucid_bcr/pipeline.py` explicitly requires causal state to include all quantities that affect future frames, with `snapshot()/restore()`. R590's research tests found a similar practical point in native MuJoCo: saving qpos/qvel alone, resetting original controller posture target, or zero-initializing neck controller memory can regenerate artificial motion/impact. A valid resumed state also includes native muscle `act`, reference targets, controller previous actions/history and exact contact solver/model settings.

## F. Explicit unit, frame and temporal contracts

- World vs local: `GameIntent.desired_velocity_world_mps` is world-space; `CoreSteeringTarget.shift_local_m` is local core frame. Conversions must be explicit and reversible under fixed reference.
- Angular units: `GameIntent` facing/turn rates use radians; `CoreSteeringTarget` yaw/roll/pitch uses degrees; MuJoCo hinge qpos uses radians. The bridge must make conversions explicit.
- Position/velocity/acceleration: metres, metres/second, metres/second²; the vector frame must be named for every control command.
- Force vs torque: native muscle `actuator_force` and `actuator_moment` cannot be confused. A moment-arm multiplied by actuator force yields generalized moment in Nm for rotational DOFs; 6-DOF free root uses different generalized-force dimensions.
- Contact: normal/shear forces, signed contact frame and effective friction are separately measured; friction coefficients do not imply zero slip. `R582` corrected a pressure-only support observer that discounted vertical support transmitted by friction.
- Solver: MuJoCo native no-slip iterations are part of model identity; changing them without tracking the treatment creates a mismatched experiment.
- Causal state: physical qpos/qvel/act, previous motor commands, controller targets/memory, solver settings and time must agree on restart.
- Sample rates: MuJoCo integration timestep and feedback updates may be different. R574 chooses at 60 ms, R575 delays only certain high-level observations, R562 checks updates every 40 ms. Every delayed signal must be named rather than using the unqualified label “latency validated”.
- Rendering: the original Skin78 mesh is a presentation of native dynamics, not an alternative physics truth. Joint-to-skin mapping must have a checksum + reproducibility receipt.
- Goals/safety: `hazard=false` means only that specified hazards did not trip; it does not mean complete anatomical stability or behavior-level approval.

## G. Known source-grounded failure and regression classes

1. **Missing full-body validation gates**: R562 settling ignores head/neck and skin. Validated as a source fact; actual behavioral consequences require physical replay.
2. **One-sided actuator geometry**: an R585 experiment measured no positive `head.nod` moment authority at the seated state; a model-local sternocleidomastoid attachment correction and bounded six-joint allocation improved a tested 12-second case. It must not be globally applied without anatomical calibration.
3. **Competing muscle demand**: global normalization or shared allocation can mask smaller essential moments. `muscle_allocator_r58.py` addresses interference at a general heuristic level; do not assume it is wired into the native seated loop.
4. **Friction/contact solver mistakes**: R583 friction sensitivity and R584 no-slip experiments show that contact-physics setup is a first-class dependency of balance. High friction alone is not proof of correct material.
5. **Contact support measurement error**: early COM/pressure-centroid estimates omit important tangential contact contribution; R582's signed wrench is a better diagnostic but not a complete universal stability condition.
6. **False impact reduction**: R588's joint-damping adjustment reduced initial impact peaks but did not establish muscle-driven arm descent. R589 attempted actual shoulder recruitment and still had left contact chatter.
7. **Artificial test initialization**: arms-out gravity drop creates repeated startup collisions. R590 distinguishes the landing task from the seated-rest task and restores controller reference and memory with native physical state.
8. **Visual pipeline substitution**: bare rig capture can miss unacceptable head/skin movement. Full Skin78 animation is required for routine visual QA; independent numerical physical tests remain required.
9. **Source discontinuity**: individual source-only checkpoint branches cannot be silently treated as merged product; file SHAs and original archive provenance must travel with each experiment.

## H. Stop/go conditions for real task progress

Do not report a new level of motor intelligence merely because a seated test ran longer, a contact force dropped, or a previously broken frame now looks clean. A real closed-loop capability proof must execute *a named intentional task with geometry*, observe the task error and safety constraints, apply only physical muscle control, compare action vs inaction/counterfactual, and verify the result in time-continuous native SKIN78 animation. New control modules must be measured against the strongest baseline independently, not by presenting only favorable handpicked scenes.

## I. Completeness limits (non-negotiable)

This document is manually grounded in **specific source declarations, not all runtime paths**. The companion source index contains 70,823 exact line rows and links every available code line to AST roles and symbols, but mechanical line classification does **not equal fully interpreted program semantics**. The GitHub remote manifest captures branch files that can differ from archives. Complete dynamic relationships require runtime instrumentation, the historical Git lineage, all externally linked assets/model files, and user visual judgments that cannot be inferred from code. The next review must annotate actual data writes/reads, side effects, DOF semantics and state ownership per function and file. Unknown relationships remain explicitly unresolved.