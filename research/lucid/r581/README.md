# R581 — anatomical moment mapping and contact-relative hip–oblique control

Research branch: `sev-32/BioRig`, `research/lucid-r575-goal-intent`. **Not promoted.** Frozen R574/R575, inherited MuJoCo 84-actuator physical plant, low-level stabilizer and R577–R580 reference code were not modified. The initial state of every paired scene is cloned independently. The only research commands are bounded extra muscle excitation; no pose teleportation, root constraint or artificial position stabilizer.

## Measurements before control

`r581_moment_probe.py` resumes the real R580 lower-effort controller to 8 seconds, saves one supported MuJoCo physical state, and forks ten actual 0.5-second branches with identical initial state but different named actuator activations (0.025 extra excitation per included muscle). This is **offline identification**, not information exposed to the online controller. In MuJoCo 3.15, `data.actuator_moment` uses compressed sparse row storage; the instrument explicitly expands `moment_rowadr`, `moment_rownnz`, and `moment_colind` instead of wrongly reshaping the sparse values as a full matrix.

At t=8 seconds the model reports local actuator moment arms for gluteus medius about the hip abduction/adduction axis, and for quadratus lumborum/external oblique about spine lateral-bend axes. Their physical effects are not interchangeable. Relative to the same cloned no-extra-muscle branch:

| Extra muscle | Root lateral shift after 0.5 seconds |
|---|---:|
| Left gluteus medius | −0.200 mm |
| Left external oblique | −0.023 mm |
| Left quadratus lumborum, iliolumbar | −0.015 mm |
| Right gluteus medius | +0.223 mm |

These are state-specific impulse responses. The actuator-force/moment-arm products represent the **measured current generalized joint moments** (N·m for rotational DOFs), not an estimate that a fixed percentage of activation will always produce the same torque.

## New independent fundamentals

`r581_support.py` provides a read-only mass-weighted world center of mass, a seat/ground vertical-reaction-weighted *one-dimensional* contact center, contact interval and support load in explicit metres and newtons. External geometry is found **by name** rather than assumed from numeric geom indices. This is a *contact-pressure centroid*, not a full stability polygon, zero-moment-point proof, or human-calibrated clinical stability measure. It reads `mj_contactForce` and the world vertical projection of the actual contact normal; it does not change simulator state.

`r581_controller.py` owns a separate contact-gated, two-muscle allocator. It selects the current displacement-opposing gluteus medius and external oblique, using present pelvis displacement, velocity, COM relative to contact-pressure centroid, support load, tilt and arm contact. It has independently slew-limited hip and trunk doses, hard maximum 0.04 per muscle, and fails closed to decreasing activity when external support is unavailable or contact is hazardous. R574 still selects the early `none` or `R28` goal-conditioned response at 60 ms. There is no online access to future counterfactual trajectories or to the harness disturbance.

## Native MuJoCo results (R581)

| Development run | Duration | Hazard | Settled at end | Final root lateral x | Added muscle-channel excitation × seconds |
|---|---:|---|---|---:|---:|
| Scene 00, no push | 12 s | No | Yes | 0.027744 m | 0.45367 |
| Scene 04, preserved R28 pushed recovery | 12 s | No | Yes | 0.024353 m | 0.452996 |
| Scene 00, no push | 40 s | No | **No** | **0.032166 m** | **1.953904** |

The 40-second simulation had final root tilt 12.38°, peak tilt 14.47°, no simultaneous seat/foot support-loss samples, and 0.26 N peak seat-arm force. Relative to the prior **R577 full lateral** 40-second receipt, R581 reduced total added muscle-channel excitation by approximately **49.2%**, but lateral displacement was 0.322 mm worse. Relative to the earlier R580 lower-effort result, effort was about 31.4% lower, but lateral displacement was 0.259 mm worse. These are previously verified *reference receipts*, not new paired R577/R580 runs during R581. The reported excitation integrals are **not metabolic energy**.

A more significant new diagnostic emerged: COM minus the weighted contact-pressure center grew from 0.00546 m at 12 s to 0.01015 m at 25 s and 0.03675 m at 40 s. This is a possible control concern even though the existing project hazard criteria never triggered. The contact-pressure estimate omits frictional moments and is not an independently validated full 3D stability margin. Accordingly, **R581 is not approved for canonical integration**.

All 8 local regression tests passed, including a native MuJoCo 12-second replay of the previously successful scene-04 push with matching displacement. `r581_render.py` created five genuine MuJoCo/EGL images from a continuous 40-second physics run at 0, 12, 25, 30, and 40 seconds. The renderer changes camera, lighting and seat opacity only; it does not alter the plant dynamics. The PNG is provided separately to the user, excluded from source-only Git and ZIP distributions.

## Reproduction

Restore the original immutable R574 and R575 archives with `research/lucid/tools/bootstrap.py` from repository root to `./runtime`. Requirements: Python 3.13, MuJoCo 3.15, NumPy, scikit-learn. EGL render additionally needs PyOpenGL and Pillow.

```sh
python research/lucid/r581/r581_moment_probe.py
python research/lucid/r581/r581_controller.py --indices 0 4 --seconds 12 --out r581_paired_12s.json
python research/lucid/r581/r581_controller.py --indices 0 --seconds 40 --out r581_scene00_40s.json
R581_NATIVE=1 python -m unittest discover -s research/lucid/r581 -p 'test_r581.py' -v
MUJOCO_GL=egl python research/lucid/r581/r581_render.py
```

R581 program files expect the restored runtime in repository-root `runtime`, as does the prior R576–R580 lineage. `R581_AUDIT.json` contains fingerprints of the source, trace JSONs, model baseline and renderer. Full numerical traces are included in the separate checkpoint ZIP, not the small Git source tree.

## Open gates

This is calibrated on an observed scene-00 failure, not an independent held-out test. The remaining engineering priority is **long-horizon support-relative equilibrium**, not simply avoiding tilt hazards. Next compare COM/contact-pressure discrepancy against a physics-valid contact-wrench/ZMP representation, determine whether the increasing gap can be driven down *without* introducing oscillations or arm contacts, measure true actuator work/force rather than only excitation integral, and run all fourteen frozen scenarios with per-scene execution limits. Re-test the 40–60-second horizon and full sensorimotor latency before any promotion. The unresolved support metric must not be turned into a deceptive settling classifier.
