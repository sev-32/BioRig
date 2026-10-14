# BioRig / LUCID — Atlas V011: measured control-to-contact causal dynamics

**Scope:** Source-pinned *native physical measurement* connecting the existing V009 84-channel command ownership matrix and V010 84×102 instantaneous mechanical geometry to actual simulated muscle excitation, delayed activation, force generation, body motion and contact interaction. **This is documentation and empirical identification, not a new motor controller or a simulation improvement.** All historical R574–R590 executable sources are untouched.

## A. What exists, and what is missing

The original R543 seated body has 84 muscle actuators (`nu=84`), 84 activation states (`na=84`), 103 position coordinates (`nq=103`), 102 velocity coordinates (`nv=102`), and 117 collision geometries. Gravity is Y-down, with a rigid research seat. `PhysicsBody._muscle_xml` constructs spatial tendon actuators with command limits [0,1] and `timeconst="0.01 0.04"` (`lucid_bcr/physbody.py:526–536`). `PhysicsBody._index` configures `actuator_actearly=1` for the muscle actuators (`physbody.py:585–604`), so the muscle force used in a step can depend on activation advanced during that step; do not mistakenly treat this as an entire extra frame of output delay. The native model declares `mjtDyn.mjDYN_MUSCLE` on these channels and exposes activation and force through `MjData.act`, `MjData.act_dot`, `MjData.actuator_force`.

The R574 goal agent and original planners exist in archived Python source. **None was executed in these V011 assays.** This experiment measures downstream physical response to a specifically authored excitation, not demonstrated thought, wanting, or goal completion.

## B. The explicitly different relationships

| Layer | Physical meaning and native observer | Physical units | Authority / critical caveat |
| --- | --- | --- | --- |
| 1. Goal and task choice | Desired action/target, if an actual goal agent executes | semantic intent, task frame | Not connected in this V011 experiment |
| 2. Controller | `MjData.ctrl[84]`: muscle excitation command, clamped to [0,1] | fraction | `data.ctrl` is NOT delivered muscle force |
| 3. Activation memory | `MjData.act[84]`: MuJoCo muscle state after time-dependent excitation response | fraction | Source XML `timeconst="0.01 0.04"` and native `mjDYN_MUSCLE`; `actearly=1` |
| 4. Contractile force | `MjData.actuator_force[84]` after native force–length–velocity dynamics | N (signed tendon-force convention) | Not an anatomically validated in-vivo measurement |
| 5. Instantaneous mechanical geometry | V010 `momentJacobian[84,102]`: actuator length derivative with respect to generalized velocity | m/rad on rotational DOFs; m/m on translation DOFs | Depends on posture and tendon routing; not itself force |
| 6. Generalized actuator force | `MjData.qfrc_actuator[102] = momentJacobian.T @ actuator_force` | joint N·m / translation N | Independently verified at every sampled native state |
| 7. Accelerations and motion | `MjData.qvel[102]`, `qpos[103]`, native integrator, inertia and constraints | rad/s or m/s, rad/m/quaternion | Dynamics nonlinear; no single global fixed 84×102 transfer matrix |
| 8. Physical contact | native collision impulses; sampled seat normal load | N | Depends on material, contact solver and full body state |
| 9. SKIN78 | Render source maps actual body poses to skin | world geometry | Not executed here; no claim of visual quality or goal achievement |

### Two important signed identities

For the native `muscle_moment_matrix()` expansion of MuJoCo's sparse tendon Jacobian, the predicted generalized effort is `J.T @ f`, with signed muscle force vector `f`. This was verified within floating-point tolerance. Native generalized actuator power `qfrc_actuator @ qvel` matched native tendon actuator power `actuator_force @ actuator_velocity` in the same physical states. These are accounting identities, **not proofs of movement competence**.

The source's `feedback_excitation()` (contact_flight_r46.py) assumes negative tendon tension for recruitment direction. Applying an arbitrary positive torque sign to actuator force or adding joint torque without the tendon model would silently change physical meaning.

## C. Experiment inputs and reproducibility

**Exact input state:** the first recorded frame at **physical time t=12s** of the uninterrupted R590 24s trace. Unlike the V010 restart-only pose files, this original continuous snapshot contains **qpos[103], qvel[102] and act[84]**, all pinned by archive SHA-256. We reconstructed the original R543 MuJoCo seated model, applied the already documented R585 SCM insertion (`site_pos.z=-0.025m` on left/right SCM) and existing six-iteration no-slip option **only to this in-memory test instance**. No geometry, source files, solver coefficients or muscle capacities were changed.

**Important missing state:** R590 did **not** serialize the originally running controller's private memory or its `data.ctrl` at this snapshot. The experiment intentionally sets an open-loop reference `data.ctrl=clip(recorded act,0,1)`. That is a **test proxy**, not a faithful continuation of the original R590 controller. No posture, neck, arm or goal controller executes during these assays. No synthetic root constraints or externally applied stabilization are present. We therefore **do not score the run as successful seated balance**; seat loads in an unregulated 0.2s trial are not usable as seated-performance benchmarks.

We ran **85 independent real MuJoCo forward-dynamics branches** from exactly the same recorded physical state: one reference and one +0.12 excitation pulse on each of the 84 native actuator IDs in turn, from t=0.020 to 0.100s after the initial frame, at native `dt=0.002s`. Each branch advances for 0.200s with actual gravity, muscle activation, tendon dynamics, joint mass, collisions, and the original research seat. Samples at t=0.060, 0.120 and 0.200s retain original `qpos`, `qvel`, `act`, `actuator_force`, `qfrc_actuator` and command vector, plus seat normal-contact measurements. For quaternion/free-joint positions, displacement is computed using **native `mj_differentiatePos`** to produce the correct 102-dimensional generalized-coordinate tangent, rather than subtracting 103 raw position components and mislabeling them as angles.

Four shoulder channels have an additional **0.28s, every-2ms** high-resolution physical trace (left/right deltoid middle and pectoralis major) with a +0.14 excitation pulse t=0.030–0.160s. This tracks force and activation throughout onset and release. It likewise operates without the posture controller; do not compare its seat force to an approved R590 physical response.

## D. The new complete conditional dynamic matrix

`ALL_84x102_NATIVE_CONTROL_TO_DOF_TIME_RESPONSE.npz` stores:

- `delta_velocity_84x3x102`: actual velocity differences between each single-muscle pulse and the identical uncontrolled baseline;
- `delta_position_tangent_84x3x102`: native rotation-aware generalized-coordinate differences, same time samples;
- `delta_generalized_actuator_force_84x3x102`: differences in generalized muscle effort at those instants;
- `delta_muscle_force_84x3x84` and `delta_muscle_activation_84x3x84`: cross-actuator changes, including changes from altered geometry and velocity;
- full immutable *per-branch* source state, activation, force, command and contact arrays for every time sample (85 branches × 3 samples).

This is an **input perturbation-to-motion relation**, not the same object as the V010 *instantaneous tendon Jacobian*. Input dose, initial state, solver, pulse duration, control ownership and time horizon are part of the matrix definition. Do not invert it as a universal muscle-control law.

## E. Mechanical-direct vs dynamically propagated influences

Both are calculated at the **same R590 physical state**. At initial t=12s, V010 reports **334/8,568** muscle/DOF pairs with direct tendon moment coefficient greater than 10⁻⁶. At 0.200s after a separate muscle pulse, the new conditional *velocity response* magnitude is greater than 0.01 in **3,172/8,568** pairs; **2,932** of these have **no direct geometric coefficient above 10⁻⁶ at the initial posture**. The full signed, unthresholded values are stored in `V010_V011_8568_DIRECT_VS_DYNAMICAL_COUPLING.csv.gz`.

**Interpretation:** A muscle influences some joints via tendon geometry; acceleration, inertia, passive tissue, contact and other joints transmit motion to additional coordinates. The lack of an initial direct Jacobian coefficient does not mean the downstream coordinate is unaffected. However, the 0.01 reporting threshold combines DOFs in different physical units (m/s vs rad/s), so it is **not a cross-coordinate measure of biological importance**. A downstream response may also arise after moment arms change as the body moves. No unique physical pathway can be assigned merely from a pairwise pulse response.

## F. Numerical audit, independently replayed

`verify_v011.py` separately instantiated and reintegrated all **85** MuJoCo cases (100 native 2ms steps per case) and regenerated **255 saved physical states**, comparing **1,530 state/force field arrays**. The independent comparison attained **0.0 maximum absolute native state discrepancy** on this environment. Generalized-force projection discrepancy stayed below 8.0×10⁻¹⁵, and actuator power discrepancy stayed below 4.3×10⁻¹⁴. It also recalculated quaternion-aware delta positions and V010/V011 direct-versus-downstream edge counts.

This exact numerical re-run is good evidence of **local, deterministic software reproduction**, not external or clinical validation. The baseline has no stabilization controller and loses the naturalness of the accepted R590 full loop. These data cannot be represented as a newly learned reach or an improvement in character animation.

## G. Failure conditions and next dependency

1. Need full serialized **controller state** alongside `qpos/qvel/act/ctrl` to distinguish genuine restart continuity from reconstructed intent/memory.
2. Need goal/target coordinate frames and explicit outcome tests to demonstrate true task-to-muscle control rather than pulse choice.
3. Need repeatable **closed-loop** comparative perturbation tests on the same physically supported model, with head, hand-seat, foot, and skin-render gates.
4. Need measure force and spatial coupling at more diverse postures; the 94 V010 poses are mostly one seated family.
5. Need actual anatomical calibration before equating MuJoCo proxy muscle force with human biomechanics.
6. Need investigate R589's 10ms arm command override vs the 2ms base update, without conflating the refresh rate with the muscle time constant or 2ms physics step.
7. Need compare interaction effects for simultaneous muscle commands, since per-channel pulses don't prove their sum is valid in nonlinear contact mechanics.

**Version freeze:** V010 and all earlier verified source packages are preserved. V011 has created only offline audit scripts, measurements, tests and explanatory documents. No GitHub Actions. No executable BioRig source modified.
