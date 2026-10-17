# BioRig / LUCID V013 — coordinated muscle equilibrium, reciprocal release and whole-limb authority

**Status:** source-verified semantic and measured mechanical relationship atlas; **no simulation/controller change**. Frozen R574–R590 remain intact. V013 extends V012, rather than replacing it or restarting from an older controller. Date: 2026-10-17.

## Executive finding

The key control primitive is **a whole-body force-balanced pose that can move**, not a succession of isolated agonist contractions. Voluntary flexion normally involves feedforward support at proximal joints; selective agonist recruitment, antagonistic modulation (including release when warranted), stabilizing coactivation where needed, deceleration by opposing muscles, delayed muscle excitation, and contact-aware corrections. The amount of coactivation is context dependent: unconstrained free motion, holding a weight, balancing on a seat, a perturbation, and a rapid reach require different force and stiffness budgets.

This is already **partially encoded** in BioRig's preserved source, but across disconnected generations and different arbitration rules. A new controller must not be inferred to exist merely because those modules are present. This paper relates the actual source to the 94-state native mechanical atlas.

## 1. Ontology: what the system should mean

| Semantic object | Concrete representation / required units | Physical meaning and ownership |
| --- | --- | --- |
| Intent | target world/body frame and tolerance, trajectory phase, deadline, contact policy | specifies a desired *effect*, not a muscle name |
| Postural support | desired joint configuration, root pose, COM, support polygon | many muscles jointly resist gravity, contact and moving-body reactions |
| Limb task | endpoint or joint target, velocity and allowed acceleration | distributes movement over shoulder, elbow, wrist, scapula and trunk |
| Net joint moment | signed N·m for each rotational DOF | sum of moments from all musculotendon tensions, passive tissues, contact and inertia |
| Muscle tension | nonnegative magnitude N (native actuator_force is negative in MuJoCo muscle convention) | tension carries force along geometry-dependent tendon route |
| Muscle excitation | each channel in [0,1] | neural/command input, not instantaneous tension |
| Muscle activation | native activation state in [0,1] | delayed state shaped by activation/deactivation constants |
| Coordination stiffness | target *response to displacement*, e.g. N·m/rad | not determined solely by net joint moment or pair count; requires response measurement |
| Contact | actual normal/tangential forces and active constraints | changes needed joint moments and can inhibit/release muscle commands |
| Command arbitration | exclusive writer, explicit blending or constrained shared optimization | prevents competing layers silently overwriting one another |
| Safety and acceptance | head alignment, COM/seat/feet support, muscle effort, arm-seat forces, actual SKIN78 render | final quality gate, not just an optimization residual |

The joint dynamics and muscle actuation have conceptually distinct layers:

`intent -> desired limb/body acceleration and compliance -> required generalized force (including gravity, inertia and contact) -> constrained muscle-force distribution -> delayed excitation -> actual tendon force -> native MuJoCo step -> sensation -> updated intent/control`.

Locally, for the recorded MuJoCo mechanical mapping, a muscle tension vector `F>=0` produces a signed generalized moment proportional to `-J_tendon(q)^T F`. The sign convention matters. V010 stores the native tendon moment Jacobian `J_tendon` at 94 observed configurations; V011 measures *dynamic* movement from single-muscle excitation pulses. Neither one alone proves a closed-loop coordinated movement.

For a movement goal, the muscle tension allocator should satisfy both: (a) the net moment required to hold the body against its current loads; and (b) the additional moment needed to accelerate the desired joints. Among physically equivalent solutions, a constrained choice can reduce wasted effort while retaining a task-dependent margin of stabilizing coactivation. **Zero net moment does not imply zero muscle force; and positive coactivation does not automatically prove physiological stiffness.**

### Movement is redistribution of a constrained network, not a binary biceps/triceps switch

1. **Hold:** maintain enough coactivation, passive mechanical resistance and contact support to keep the pose despite gravity/external loads. Avoid unnecessary maximal antagonist excitation.
2. **Initiate:** raise moment in the intended direction, reduce only those opposing moments that can safely be released, and keep the proximal stabilization objective active.
3. **Travel:** track velocity/trajectory using continuous feedback, accounting for excitation-to-force delays; allow multi-joint compensation instead of one-muscle pulses.
4. **Brake:** recruit the opposing direction in anticipation of stopping; do not expect the joint's mechanical position to stop instantaneously when excitation falls.
5. **Settle:** redistribute force back into the holding regime, with joint stiffness and contact loads appropriate to the task. Detect and reject chattering/repeated impacts rather than hiding them behind passive damping.

These phases describe the **required semantics**. The recorded R590 seated-restart path does not implement them as one integrated controller.

## 2. Native V010 quantitative proof of actual antagonism and cross-joint leakage

Recomputed directly from `V010/NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz`, from the originally archived 94 native configurations and 84 muscle by 102 velocity-coordinate Jacobians. Threshold for declaring leverage active is `abs(moment) > 1e-6 m/rad`. This measurement records six anatomically motivated opposing flexor–triceps pairs, three per side:

| Flexor versus triceps | Opposing sign in observed states | Median needed triceps tension per 1 N flexor tension | Important residual |
| --- | ---: | ---: | --- |
| Left biceps | 94 / 94 | 0.9532 N | shoulder moment remains |
| Left brachialis | 94 / 94 | 0.7134 N | shoulder moment remains |
| Left brachioradialis | 94 / 94 | 0.8519 N | shoulder moment remains |
| Right biceps | 94 / 94 | 1.0098 N | shoulder moment remains |
| Right brachialis | 94 / 94 | 0.7493 N | shoulder moment remains |
| Right brachioradialis | 94 / 94 | 0.9282 N | shoulder moment remains |

The ratio is **tension**, not excitation, activation or relative muscle strength. It is calculated separately at each pose to cancel *only that elbow's instantaneous tendon moment*, using one Newton of flexor tension and an appropriately scaled triceps tension. The computed residual elbow moment across every such pair/state is below `4e-18 N·m`; this is an arithmetic identity against the original matrix, **not** a new 94-run equilibrium simulation.

Critically, the same counterfactual leaves nonzero moments at other joints. At recorded right-elbow configurations, a 1 N brachioradialis/triceps elbow-balanced pair can still yield as much as **0.0208 N·m of combined other-DOF moment**. At 100 N of flexor tension, the linear geometry-only projection of that coupling would be 100 times larger at the *same pose*; actual nonlinear force and motion cannot be predicted by simply scaling this calculation. The exact per-state off-target moment appears in `ELBOW_EQUAL_NET_TORQUE_COACTIVATION_94_POSES.csv`.

This refutes the proposed architecture of independent isolated joint commands at the **mechanical mapping level**: even an elbow-equilibrating muscle pair can disturb the shoulder. It does not refute existing controllers, and it does not prove that any particular past render's arm chatter was caused by this coupling.

`ALL_84x84x102_SIGNED_MUSCLE_PAIR_STATE_COUNTS.npz` carries the exhaustive signed pair-role classification: 84×84×102 entries (719,712) with counts over all 94 V010 states. Each pair/DOF stores **same-sign** and **opposing-sign** tendon-leverage observations. A zero count means *not observed with both channels above the stated threshold in these 94 states*, never global independence. Signs may vary by pose, and this classification does not substitute for actual force/power or contact evidence.

## 3. Existing sources: proven mechanics, but distinct control paths

Exact SHA-256 hashes, line ranges, and literal quotations are in `COORDINATION_SOURCE_WITNESSES.json`.

| Frozen source | Existing concept | Important limitation |
| --- | --- | --- |
| `lucid_bcr/neuro.py:347–535` | WholeBodyMuscleController solves weighted or hierarchical concurrent tasks, including contact/COM/head/posture and effort, through native muscle moment arms and gains. `:564–580` maps desired activation to excitation under delay. | Its active integration into R590 is **not demonstrated**; it optimizes activation/task tracking, not an externally validated stiffness target. |
| `lucid_bcr/muscle_allocator_r58.py:10–66` | Explicit shared-muscle task/COM/posture conflicts; attenuates tracking demand opposing safety. | Bounded heuristic, not a global contact-aware motor optimizer; excludes some negative relaxations by clipping. |
| `lucid_bcr/muscle_impedance_r518.py:31–94` | Delayed muscle-length/stretch/load afferents and gradual recruitment/release with optional brace. | Adds nonnegative corrections on top of baseline; does not implement signed reciprocal antagonist release in the task allocator. |
| `lucid_bcr/adaptive_muscle_tone_r522.py:50–96` | Sensed load distribution and signed excitations to load-bearing channels. | Focuses calf/hip and plantar state; does not itself coordinate shoulder–elbow–wrist movement. |
| `R546.../joint_intent_r546.py:44–96` | **Most direct partial answer** to the user's point: current joint error/rate -> torque target -> signed bounded excitation changes across *all mechanically relevant muscles*, allowing negative antagonist corrections and penalizing moments leaked into protected joints. | Experimental local instantaneous allocator; fixed target/guard joint selection and no demonstrated complete R590 integration; it does not optimize full limb stiffness or model future activation delay. |
| `R547.../learned_muscle_r547.py`, `R548.../sensory_contact_r548.py` | Learned proprioceptive allocation and contact/force supervision. | Research variants; source available but not proven to be composed into the latest seated controller. |
| `r579_synergy.py`, `r580_adaptive_synergy.py` | Multiple trunk/hip muscle channels coordinated through sensed lateral displacement and load, with bounded recruitment. | Separate lateral recovery task, not general multi-joint limb coordination. |
| `r589_arm_landing.py:46–83` | Uses real shoulder moment arms and muscle gains to select an agonist and add positive excitation in order to guide arm descent. | **Only one selected shoulder muscle per side receives additional command in the active update**; it does not perform multi-muscle signed reciprocal release or a full shoulder/elbow/wrist stiffness optimization. |
| `r590_rest_restart.py:55–87` | Recomputes the base 84-muscle posture excitation every physics step; overrides selected neck channels via R586 allocator; physically steps with the actual contact model. | **No call to R5.46's coordinator, original WholeBodyMuscleController, or R589 ArmLanding.update()** in this restart loop. The original wider source exists, but is not active here. |

These differences are not evidence that older behavior should replace later validated geometry, stabilization or contact repairs. The task is to **conserve all existing useful constraints, then define a single explicit arbitration interface** rather than overwrite one experimental controller with another.

## 4. What needs to be interconnected, without discarding versions

A future implementation proposal (not yet executable or simulated):

**Typed request:** `Goal(target_frame, xyz_m, tolerance_m, end_effector, permitted_contacts, urgency, expected_load_N)`.

**Unified sensed state:** `NativeState(time_s, qpos, qvel, activation84, tendon_length, tendon_velocity, tendon_force, contacts, pelvis/head COM, estimated support, external loads)` with explicit ownership and sensory timestamp. No controller may receive oracle future values.

**Common output:** a **full 84-channel excitation candidate** with provenance per channel (`source_module`, `base_excitation`, `increment`, `actual_clamped_output`, and why it changed). Layered overwrites should be replaced by a constrained arbitration step that knows which channels have competing demands. Never reuse a stale arm buffer without reporting its timestamp.

**Mechanical optimization:** find a realizable muscle-force/activation vector constrained by (a) the full generalized-force target including passive gravity/inertia/contact, (b) available excitation/activation dynamics, (c) allowed contact forces, (d) joint/pose stiffness objective, (e) energy/effort budget and rate smoothness, (f) stable head and COM. Avoid treating an isolated joint torque target as enough to maintain the whole body. Positive excitation on a muscle and negative correction on its antagonist are both available **relative to the current safe baseline**, not as hardcoded reflex on/off rules.

**Safety:** source-pinned gating for no illicit ground contacts, arm impacts/chatter, head/spine angle, COM/seat/foot contact, velocity overshoot and fall. Full SKIN78 3D animations plus per-time telemetry required before any visual or physics acceptance. Restore the documented previous controller and state on any failed gate; never modify frozen versions.

### Quantitative acceptance tests for the *future* controller

1. **Hold while loaded:** same target in empty/free, hand-held object and seat-supported contexts; only claim stability after actual 12/24/40-second native runs, not a static moment-nullspace calculation.
2. **Reciprocal recruitment:** a signed target at the elbow changes flexor/extensor activation in mechanically consistent directions, while preserving shoulder/torso/head constraints; record all 84 channels and native moments.
3. **Release not collapse:** relaxing an opposing muscle must not lose the ability to support external load or trigger joint overshoot. Measure posture error and recovery.
4. **Braking under delayed activation:** settle at destination without endpoint ringing, repeated contact toggles or nonphysical passive damping.
5. **Cross-joint protection:** monitor full 102-DOF momentum/force; do not accept zero elbow torque while shoulder or root is silently destabilized.
6. **Contact-aware tests:** arm touches and leaves an object/seat smoothly; measure contact transitions at physics-step rate, not just a 0.4-second animation sample.
7. **Energy and stiffness:** distinguish muscle excitation, activation and actual force; measure mechanical response to bounded known perturbations before claiming effective limb stiffness.
8. **Control hierarchy:** exact restart serializes goal state, controller memory, native activation, timestamps and pending commands. Test against uninterrupted reference.

The gate is both numerical **and visual**. These are future regression requirements, not present-tense successes.

## 5. Source identity, reproducibility and gaps

The V010 archive SHA256 is `4e45e895ba51088134c95ab4b8065db193d4277e5fa18801c48c62915d88db68`. Its saved moment-matrix NPZ entry SHA256 is `34c1945fa977f2e262ea8ec62b241919b43bea0e9487cf73c2808ee27b708c07`. `build_v013.py` reconstructs pair-sign coverage and 564 elbow coactivation entries, verifies 13 exact source/line witnesses, and refuses to proceed on missing anchors.

**Verified here:** signed mechanical antagonism across 94 original native states; off-axis tendon moment coupling; static source conditions for R5.46's antagonist-capable signed update, R589's agonist-only additive update and R590's absence of that coordination path. All derived data from already recorded states.

**Not yet verified here:** a newly integrated reciprocal controller; realistic joint stiffness, task-force equilibrium under simultaneous contact and motion, measured human motor physiology, effective stateful activation control, and any new native SKIN78 animation. None of those may be reported as completed.

## 6. Next atlas layer (V014)

Expand from the elbow-pair mechanical sign matrix to **full-system feasible equilibrium allocation**: extract calibrated force/activation susceptibility and passive force at multiple poses, match projected 102-DOF generalized moments against inverse-dynamics requirements, and investigate the source-defined QP's contact/COM coupling. Execute matched native tests only after baseline/source and controller-memory snapshots are confirmed; audit the original R5.46 tests and rendered outcomes rather than silently reimplementing them.

No GitHub Actions. No changes to main or frozen R574–R590. This document is documentation and experimental analysis only.
