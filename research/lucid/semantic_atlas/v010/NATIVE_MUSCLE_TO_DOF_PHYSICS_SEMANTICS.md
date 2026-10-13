# V010 — measured MuJoCo muscle-to-joint mechanical relationship matrix

**Reproduction state:** the **original pinned Skin78 physical assets** pass all 13 SHA-256 identity checks. The native R543 `make_body('seated')` factory constructs the same 84-muscle model family inherited by R590. We apply the exact R585/R590 model-local SCM insertion at site z = -0.025 m and R590 `noslip_iterations = 6` to the local test instance. No archived source or numerical snapshot has been edited.

## Verified native model

- Physics solver: native **MuJoCo 3.15.0** from the original offline wheel.
- Physical state: **nq=103**, **nv=102**, **na=84**; **nu=84** independently named muscle actuators, **117** collision geoms including the seat.
- The research seat is a **rigid box** with half extents [0.28, 0.08, 0.23] metres and friction coefficients [0.9, 0.005, 0.0001]. This is not a deformable cushion; visual arm bouncing cannot be attributed to an explicitly simulated squishy seat. Contact compliance and controller oscillation remain possible causes.
- World gravity is [0.0, -9.81, 0.0] m/s²: **Y is vertical**, and X/Z horizontal.
- Native `mj_id2name` confirms every catalog channel in the original exact **84-index order**. `actuator_actadr` maps all 84 actuators one-to-one to 84 activation states.
- At all **31** fully recorded continuous states, the native identity `momentJacobian.T @ actuator_force == qfrc_actuator` holds with maximum absolute residual **4.441e-15** in native generalized-force units. The largest reconstructed native actuator force magnitude is **180.23 N**. This validates the implemented instantaneous generalized-force projection, not the historical time integration nor biological calibration.

## New source-to-physics relationship data

For each observed generalized coordinate, MuJoCo stores sparse tendon Jacobians (`moment_rowadr`, `moment_rownnz`, `moment_colind`, `actuator_moment`). The original `lucid_bcr.contact_flight_r46.muscle_moment_matrix` expands them into an **84×102 numeric matrix** at an actual physical configuration. It describes how instantaneous actuator tendon length changes under generalized motion; magnitude has dimension metres/radian for rotating DOFs and metres/metre for translational DOFs. **It is geometry, not an observed muscle torque, strength, or excitation.**

We derived **94 native geometric Jacobians × 84 muscles × 102 velocity DOFs = 805,392 numeric cells** from saved authentic MuJoCo poses, with exact channel IDs and exact native joint IDs:

| Source pose sequence | Captures | Above 10⁻⁶ in first pose | Ever above 10⁻⁶ in sequence | Maximum magnitude |
| --- | ---: | ---: | ---: | ---: |
| `cold_seated_reset` | 1 | 330 | 330 | 0.126555 |
| `continuous_12to24` | 31 | 334 | 334 | 0.121955 |
| `restart_no_push` | 31 | 334 | 334 | 0.121971 |
| `restart_plus120N` | 31 | 334 | 334 | 0.122015 |

Across all 94 samples, **334 of 8,568 possible muscle–DOF ordered pairs** exceed 10⁻⁶ in at least one state. Every pair, including zeros, is included in `ALL_8568_MUSCLE_TO_DOF_MECHANICAL_EDGES.csv.gz` with its exact unit, minimum/maximum measured value, mean absolute value, observed nonzero count, and sign flips. The full dense values and source time labels are in `NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz`.

**All six unactuated root DOFs are near machine-zero** for all 84 muscles across all 94 poses. This validates the intended root unactuation within the tested geometry. Muscle-induced whole-body movement occurs through relative internal joint forces and external contacts, not by adding an artificial root actuator.

## Important epistemic limits

1. The `continuous_12to24` input records real `qpos`, `qvel` and muscle `act`. `restart_no_push` and `restart_plus120N` record **qpos only**: their velocity and activation arrays were not serialized in those files. We use zero velocities/activation **only** when recomputing geometric moment Jacobians from the recorded poses. We do **not** call these reconstructed state tuples a faithful replay of their muscle forces or controller history.
2. This is a full relationship matrix **for muscle-to-generalized-coordinate geometry over these 94 states**. It does not establish all possible muscle interactions under all postures, contact mechanics, neural motor competence, or complete semantic understanding of the 70,823 archived code lines.
3. A signed actuator moment coefficient multiplied by actual actuator force yields a generalized-force contribution. `data.ctrl` alone is not delivered muscle force; the archived activation delay and force–length–velocity dynamics intervene.
4. The `>10⁻⁶` edge threshold is a reporting convention; the full raw numerical matrices retain floating point values without thresholding.
5. The 31 poses for each R590 variant were genuine MuJoCo-generated snapshots, **not newly integrated physical trajectories in V010**. This test loads the source physical model and applies native forward calculations to those poses.

## Preservation / next step

V009 and all older documented versions remain unchanged. We should next compare the signed force direction, actual antagonist recruitment, and observed delayed activation under true MuJoCo replays. Then trace general goal/planner output to the correct 84-channel command owner without making the existing historical versions disappear. No GitHub Actions.
