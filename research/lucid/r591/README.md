# BioRig R591 — native reciprocal muscle stabilization experiment

Status: **research candidate, not merged into production, not general human movement solved**.

This experiment builds directly on R590's authentic 12-second seated-state snapshot, R589/R586/R585 controllers, and the original 84-muscle MuJoCo 3.15.0 plant. It tests the user's hypothesis that physical movement often requires **balanced muscle recruitment to hold posture, followed by selective antagonist relaxation** to permit controlled movement. There is no frozen-source edit, no hard-coded skinned animation, and no GitHub Actions.

## Biological hypotheses tested separately

1. **Tonic coactivation**: can equal and opposite biceps/triceps commands, balanced using native instantaneous muscle torque sensitivities, increase resistance to an outside elbow disturbance?
2. **Reciprocal arm actuation**: for a voluntary ~11.46° elbow-flexion task, is reducing the triceps command more efficient than adding biceps alone?
3. **Feedback stabilization**: is corrective antagonistic allocation based on actual elbow angle and angular velocity more effective than fixed co-contraction?
4. **Whole-body coupling**: what disturbance propagates to head and body even while elbow stabilization improves?

## Physical method and limits

All trials are independent forward MuJoCo integrations from **byte-identical 103-qpos/102-qvel/84-activation seated-state snapshots**, original collision material and seat, 0.002-second physics updates and native muscle activation dynamics. The inherited 82+ channels of whole-body posture/neck control are preserved. The **only experimental control channels** are right biceps and right triceps. During motion, no `qfrc_applied` or `xfrc_applied` is used to drive the elbow; joint motion is muscle-produced. During a short separate *diagnostic disturbance* (.34–.47 seconds), a known **+2 or −2 N·m external joint torque** is injected to measure response; this is **not** a production physics interaction or a hand/object collision.

The target starts at .78s, increases by .20 radians (11.46°) until 1.55s, holds through 1.95s and returns to initial angle by 2.65s. The existing neural posture controller independently opposes some of the commanded elbow movement; the target is not perfectly reached.

Muscle control operates through the actual `mju_muscleGain × tendon Jacobian` at the current native state. The tonic-coactivation candidate offsets flexor and extensor commands by equal predicted *instantaneous* elbow torque, but real muscle force remains activation- and velocity-dependent. Instantaneous cancellation **does not** imply constant torque balance after motion begins.

## Results: candidate selection, *not physiological calibration*

At +2 N·m for 130 milliseconds:

| Controller | Max elbow deviation | Mean movement target error | Max head–torso angle | Added positive command integral |
|---|---:|---:|---:|---:|
| Inherited R590 baseline | 24.39° | 7.15° | 1.11° | 0 |
| Agonist-only voluntary motor | 24.39° | 3.67° | 1.21° | 0.0589 |
| Fixed balanced high co-contraction | **30.22° (worse)** | 7.41° | 0.76° | 0.5691 |
| Fixed balanced reciprocal control | **30.22° (worse)** | 3.18° | 1.21° | 0.5447 |
| Position/velocity feedback, no tonic preload | 6.09° | 3.54° | 2.82° | 0.0809 |
| Feedback + small tonic coactivation | 6.01° | 3.56° | 2.83° | 0.1127 |
| **Feedback + relaxation of inherited antagonist command** | **5.92°** | 3.98° | 2.75° | **0.0113** |

For −2 N·m the inherited controller deflects 11.43°, while the antagonist-release variant deflects **6.02°**, at the cost of head motion up to **3.31°**, from 0.75° inherited. Both perturbation signs and a zero-disturbance control were executed. In the zero-disturbance goal task, the true-antagonist-release candidate used **zero extra positive biceps/triceps activation beyond the inherited controller** while recording .0423 excitation·seconds of antagonist-command relaxation; it still missed the commanded final flexion target. Hence **reducing opposing recruitment can produce movement** in the present model, but its tracking quality requires improvement.

This experiment rejects the idea that simply raising simultaneous antagonistic muscle activation necessarily makes the joint more stable. **State-feedback and reciprocal inhibition** dominate the tested result. The whole-body head response worsens under elbow perturbations, signaling a missing coupled, multi-joint stabilization law. The tests cannot establish human muscle physiology, electromyography validation, real energy expenditure or universal stiffness without model calibration.

## Files / reproduction

- `r591_balanced_muscle_experiment.py`: independently run baseline, single-agonist, fixed coactive, adaptive, and genuine existing-antagonist-relaxation alternatives.
- `test_r591_native.py`: seven local regression tests, including fresh native replay and original SKIN78 render-state hash checks.
- `r591_render_native.py`: original CausalRig/VTK SKIN78 renderer, true captured qpos, actual seat/floor, no image synthesis/interpolation.
- `r591_plot_telemetry.py`: measured joint/head time histories.
- `out/*.json`: numerical traces, full measured muscle activation/commands, precise units and timing.
- `out/*QPOS.npz`: real physical qpos snapshots; no binary mesh assets duplicated.
- `out/R591_RENDER_RECEIPT.json`: exact source-state and rendered GIF digests.

Unzip the frozen R574 original archive to `runtime/`, restore R585/586/588/589/590 source from their pinned code ZIPs to sibling directories, restore MuJoCo 3.15.0 from R574's offline vendor wheel, and set `BIORIG_WORKSPACE` to the experiment root. Run the script for each policy. Reproducing local VTK renders requires `vtk`, `Pillow` and the frozen original Skin78 assets. No GitHub Actions.

**Next experiments:** distribute joint-impedance demands across biceps, brachialis, triceps, scapular and shoulder groups; optimize antagonism under desired hand position, elbow/shoulder loads, head balance and metabolic effort; test object-applied force instead of a directly injected diagnostic joint torque; calibrate against anatomical strength and measured force–length/velocity curves; retain current research-only status until a whole-body SKIN78 movement and contact acceptance suite passes.
