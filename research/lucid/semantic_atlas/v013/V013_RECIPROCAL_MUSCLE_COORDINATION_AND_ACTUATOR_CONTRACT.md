# LUCID/BioRig — V013: reciprocal muscle coordination, pose holding, release and movement

**Scope:** Source-anchored biomechanical architecture analysis of original R574-archive `lucid_bcr` modules and R579, R580, R589, cross-checked with the independently verified V010 native 84 × 102 tendon-moment Jacobians at 94 configurations. The frozen simulation versions have not been modified. This is a **mechanical and source audit**, not a new balancing, reaching or animation result.

## 1. Fundamental operational distinction: motion versus mechanical readiness

An elbow does not bend because the software names a biceps and sends it a positive command. In the physical model, numerous tension-only actuators share the mechanical load. A held posture requires enough **net generalized moment** to counter gravity and external load, while often maintaining some co-contraction to resist small disturbances. A desired movement requires a **controlled change in the signed resultant joint moment**, usually assisted by movement-specific reduction of unnecessary opposing excitation. The rest of the arm, shoulder, scapula, trunk and global support must remain within dynamically feasible balance and contact constraints.

Important qualifications:

* **Relaxing antagonists is conditional, not universal.** Both flexors and extensors can remain active during fast or precise motion to increase impedance, damp disturbances, brake approaching a target or distribute load. Removing all antagonist recruitment sacrifices stability.
* **Co-contraction is not the same as net torque.** Opposing muscle moments can cancel while muscle tension and muscle energy expenditure remain high. Stability and joint stiffness depend on force-length-velocity, tendon and passive tissue properties, not just simultaneous excitation.
* **A muscle may span multiple joints.** The native biceps and triceps affect both elbow and shoulder. Balanced elbow torque can still create a shoulder torque. The whole body must satisfy coupled equations; each joint does not have an isolated two-muscle motor.
* **Tension is not activation.** A ratio of required tensile forces is not a ratio of excitation commands: native muscle gain, passive bias, activation delay and length/velocity must be measured at that instant.

## 2. Source-established prior work: existing systems, not capabilities to recreate

| Earlier source | Exact source anchors | What it really defines | Critical limit |
|---|---|---|---|
| Original whole-body optimizer | `lucid_bcr/neuro.py:32–94,196–256,347–387,389–535,557–580` | **One coupled** bounded solver for generalized muscle activation and contact reactions, with priorities for stance contact, COM, head, pelvis, swing leg, joint posture and effort; converts desired activation to delayed excitation | `NeuroParams.relaxed_arms=True` at line 77; arm muscle indices are excluded from the free optimization at lines 225–228. Thus the default path does **not** actively optimize coordinated reaches. Do not mistake the broader matrix formulation for proven active arm-control use. |
| R5.18 stretch/load impedance | `muscle_impedance_r518.py:13–29,31–96` | 18-ms delayed actuator-length/velocity/tension proxy, dynamic recruitment and first-order release; optional arm mask | Optional additive bounded reflex. Does not solve intended elbow torque, whole-body muscle competition or calibrated human neural control. |
| R5.20 reciprocal load synergies | `load_bearing_synergy_r520.py:20–37,39–137` | Checks **native moment-arm sign** against delayed joint velocity, recruits muscles resisting unwanted movement and can reduce excitation in movement-driving antagonists above a tonic floor | Applied to **loaded ankles, knees and hips**, not a full arm reaching controller. Velocity sign is a reactive criterion, not a goal error or predicted safe movement profile. |
| R5.21 and R5.22 tone adaptation | `R521_MUSCLE_EQUILIBRIUM_CALIBRATION_CHECKPOINT.md`; `adaptive_muscle_tone_r522.py:33–101` | Calf tone reduction; measured plantar load and tendon tension redistribute lower-body tone, bounded by support state | The original R5.21 3-second standing holdout failed sustained support even though 1.2-second containment improved; not a proven globally stable solution. |
| R579 static lateral synergy | `r579_synergy.py:20–75` | Redistributes same R577 lateral pulse dose between hip and trunk muscle group | Four preselected lateral-muscle channels, not broad reciprocal task-specific muscle coordination. |
| R580 adaptive lateral synergy | `r580_adaptive_synergy.py:42–105,108–165` | Uses position/velocity urgency to vary lateral hip/trunk recruitment; combines two corrective doses with base controller | Still operates on a small predetermined lateral subset, at ~40-ms changes; does not control upper-limb reciprocal elbow support. |
| R589 arm landing | `r589_arm_landing.py:19–26,32–85,88–150` | Controls shoulder abduction with actual native muscle leverage; per-side **deltoid middle or pectoralis major** chosen by desired torque sign, then restores base command | Exactly **one additional shoulder muscle per side per update**, not an optimized set of elbow flexors, extensors, cuff, scapular and trunk muscles. It does not compute joint impedance, antagonist floor or coordinated multi-DOF hand reach. |

**Highest-priority source truth:** `neuro.py:225–228` establishes the original whole-body solver's relaxed-arm default; `r589_arm_landing.py:72–80` establishes the single-muscle choice for each shoulder at a time. Neither statement is a runtime performance verdict. They are precisely located architectural boundaries.

## 3. Native model: what the signed 84 × 102 measurements establish

The frozen V010 measurement contains 94 full original MuJoCo tendon-moment Jacobians, each shape `(84 actuators, 102 velocity coordinates)`. `NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz` is hashed in `V013_RECEIPT.json`. For a positive tensile force **T** in a named muscle, the generalized torque under the model's sign convention is `- (d tendon_length / d joint_coordinate) * T`.

The exhaustive source-derived ordered **84 × 84** pair register has 7,056 cells (including the diagonal). A pair is compared at each of the 94 poses at all 102 coordinates where both have a native Jacobian magnitude greater than `1e-8` in the native derivative's coordinate units. Every cell records the number of shared, opposing-sign and same-sign coordinate/pose observations. In this sampled collection, **876 ordered cells** have at least one jointly influenced nonzero coordinate, **726 ordered cells** have at least one mechanically opposing influence, and **642 ordered cells** exhibit both signs across coordinates or states. These categories overlap; they must not be added. Zero shared observations means **not seen in these 94 poses**, not proof of global anatomical independence. The raw counts and coordinate definitions are in the CSV and builder.

### A tangible elbow example — one held torque, two opposing tensile muscles

For either elbow, the frozen MuJoCo geometry places biceps/brachialis/brachioradialis on one signed side of elbow flexion and triceps on the opposing side. If the biceps tension is hypothetically **100 N**, a position-specific triceps tension can cancel its elbow moment exactly in the geometric model:

`T_triceps = -T_biceps * (elbow moment_per_newton_biceps / elbow moment_per_newton_triceps)`.

The **triceps/biceps tensile-force ratio** required for this simple cancellation ranges from **0.7523 to 1.0102** across the recorded 94 poses and both arms. The residual computed **elbow** moment is numerically near zero (≤`3.5e-16 N·m` from double-precision arithmetic). Yet the two muscles also cross the **shoulder**, where the same balanced-elbow tension pair leaves a nonzero modeled moment: **0.035–0.241 N·m** across these poses, using a hypothetical 100-N biceps tension. Thus *same elbow pose* does not imply *same shoulder load*.

This is a carefully bounded **geometric thought experiment on real native values**. The model has not been run forward under that exact set of tension values, and the tension ratios are not control-activation ratios. The measured joint stiffness, intrinsic damping, reflex sensitivity, tendon slack, human physiological realism, and admissible force capacities are not established by the cancellation equation.

## 4. The missing coordination contract: do not force arm behavior through two shoulder channels

The interface should express one *coupled muscle-allocation task*, not independently prescribe each muscle or treat an elbow as a two-direction servo. Required inputs and outputs are typed:

| Contract item | Unit/frame | Authoritative owner | Audit gate |
|---|---|---|---|
| Desired hand position/orientation, acceptable task error, movement phase | metres in named body/world frame; quaternion; seconds | goal/planner | reachable target, body-relative vs world frame explicitly recorded |
| Desired joint posture / angular velocities and expected disturbance | radians; radians/s; body generalized coordinates | trajectory / state estimator | measured state timestamp and stale-data veto |
| Native joint coupling, tendon lengths/velocities and muscle moment arms | metres; m/s; m/rad or dimensionless for translations | original MuJoCo `MjModel`, `MjData` | 84-channel catalog equality; V010 moment-geometry consistency |
| Global wrench and contact support | N, N·m, metres; world/body frames | contact+COM state estimator | full-body balance, seat/feet/hand contact and slip, no-support fallback |
| Whole-body muscle activation target **and impedance budget** | activation fractions [0,1], finite effort and moment residual | centralized task allocator | maintain required hold torque while allowing goal-directed net torque; report desired vs realized effect |
| Differential antagonist **release** | bounded excitation delta; zero minimum floor only if safe | reciprocal controller below planner, above native plant | never remove demand needed for pose hold, landing braking, neck or contact safety |
| Physical actuator command | native excitation [0,1] each 2 ms | single final authority over `data.ctrl[84]` | no silent stale overwrite by 10-ms 2-channel arm buffer; explicit composition order |
| Muscle activation and force | activation [0,1], signed tendon force N, dynamical latency seconds | native MuJoCo `mj_step` | compare command, activation, force, moment, qvel and contact physically |
| Outcome | target error, joint error, speed, head tilt, seat/foot contact, muscle effort, stop/abort | independent test harness + original SKIN78 renderer | target reached AND held without chatter/bounce, unsafe contact, drift or head-fold regression |

**Principal design principle:** A pose-holding state and a movement-producing state need not activate disjoint muscles. They differ by their *desired net moments and allowed compliance*. Solve a feasible whole-body moment/contact allocation at each control step, then use safe reciprocal release in the directions where opposing excitation is unnecessary. Preserve co-contraction where joint/environment stiffness requires it. No new architecture is being inserted into R590 by this paper.

A useful local conceptual decomposition at the desired pose (not a completed current feature):

`activation demand = load-support requirement + intent-dependent signed moment change + physically necessary stiffness/co-contraction reserve - safe reciprocal release`.

These terms are coupled constraints; they must not be implemented as blindly additive channel-wise vectors. When a muscle crosses multiple joints, only a whole-body constrained solver can check that releasing it does not invalidate a different joint or support condition. `neuro.py` provides an existing mass/contact-aware solver skeleton; extending the arm task inside it is more consistent with source lineage than creating an entirely separate world of shoulder motor commands. Its existing safety and CPU/runtime costs require actual tests before integration.

## 5. Why today's seated tests are not the final goal and must not be discarded

R585–R590 established important conditions for a physical plant (neck, muscle effort, no-slip, arm collisions, settled seated state). They remain valid recorded findings within their tested conditions. The problem is **task closure**: none of the archived seated rest examples executes a general elbow task against full-body impedance and balance constraints. R574's goal action selection is a different narrow task. No source justifies calling all earlier work regression, and no old branch should replace a newer branch merely because its controller contains more functionality.

The unification target is *interface and evidence*, not merging all historical controllers indiscriminately. Freeze the existing snapshots; stage a new integrated controller behind task-scoped tests and exact native-state receipts. Failure must leave the frozen versions intact.

## 6. Explicit evaluation program — no unrendered acceptance

1. **Equilibrium before movement:** Start from recorded stable seated pose, quantify native joint moments, muscle excitation/activation/force, contact impulses, and passive support. Do not present sitting still as a newly learned goal.
2. **Intended elbow motion:** Ask for a reachable left/right hand target with a named frame. A native controller must recruit a *group* that includes available elbow flexors and extensors, stabilizes shoulder and head, and naturally transitions to a held final pose without invoking joint motors or keyframed qpos.
3. **Controlled release vs coactivation:** Paired physical trajectories should compare (a) no release, (b) bounded release of unnecessary opposing muscle, (c) state-dependent coactivation for hold/landing. Record net elbow and shoulder moments, activation delay, contact and effort; reject any difference obtained by modifying seat/contact physics asymmetrically.
4. **Perturbation and landing:** Unpushed and signed lateral pushes, arm-seat impacts, and forearm contact conditions. Measure bounce counts at native 2-ms cadence, not only 0.2–0.4-s visual samples. A successful reach that folds the head or violates seat support fails.
5. **Visuals:** Render actual full SKIN78 with the original seat and floor, several camera angles, coherent timing and synchronized contact plots. No generated mockups, interpolation disguised as physics, or screenshots from another model/branch. Only evidence-supported behavior can be promoted.
6. **No rollback and no GitHub Actions:** all experiments stay in the research branch; record exact code/data SHA-256 and independent verification, with failed trials preserved.

## 7. Precisely what V013 covers and does not cover

This checkpoint **indexes every literal line** of nine selected historical and recent modules (**1,636 line records**), with the enclosing AST function/class and human-written meaning for 26 critical source ranges. It creates a **7,056-cell complete ordered mechanical pair register**, and 188 elbow-pose/side cancellation rows. It does **not** claim independent manual semantic explanation of all 1,636 lines, let alone the complete 70,823-line multi-version program. Per-line text outside a reviewed region is explicitly marked *not manually established*. It also does not demonstrate dynamic joint stiffness, physiologic reciprocal inhibition, a new skinned movement, or integrated modern reaching. Those must be measured.

**Reproduction:** `python build_v013.py` with pinned R574/V010 and R579/R580/R589 archives beside it; `python verify_v013.py` performs an independent source and geometry recheck. The current research branch and native production controllers remain unchanged.
