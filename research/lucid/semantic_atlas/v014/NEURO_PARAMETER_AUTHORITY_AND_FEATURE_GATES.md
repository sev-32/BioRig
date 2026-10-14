# BioRig semantic atlas V014 — parameter authority and disabled-by-default tasks

**Scope:** frozen original `lucid_bcr/neuro.py`, with every `NeuroParams` field and every matching Python attribute occurrence across the complete frozen R574 archive. This is a static semantic paper. No physical experiment or code merge was performed.

## Why this audit matters

The original 84-muscle whole-body optimizer was often described as if it simultaneously enforces a ranked balance/step/contact hierarchy. Its constructor defaults and conditional branches show a more specific reality: important optional tasks are inactive until callers opt in. In addition, the seated R590 execution path does not call this optimizer at all, as V013 independently established.

## Exact NeuroParams defaults and usages

| Field | Default | Definition line | All matching attribute reads/writes | High-confidence reads/writes in `neuro.py` |
|---|---:|---:|---:|---:|
| `com_kp` | `60.0` | 35 | 4 | 4 |
| `com_kd` | `14.0` | 36 | 4 | 4 |
| `com_kp_y` | `60.0` | 37 | 3 | 3 |
| `com_kd_y` | `14.0` | 38 | 3 | 3 |
| `w_com` | `10.0` | 39 | 1 | 1 |
| `capture_k` | `0.0` | 42 | 2 | 2 |
| `cop_margin` | `0.012` | 43 | 1 | 1 |
| `w_foot_flat` | `0.0` | 45 | 2 | 2 |
| `foot_flat_kp` | `200.0` | 46 | 1 | 1 |
| `foot_flat_kd` | `30.0` | 47 | 1 | 1 |
| `w_angmom` | `0.0` | 49 | 2 | 2 |
| `angmom_k` | `8.0` | 50 | 1 | 1 |
| `ori_kp` | `80.0` | 52 | 1 | 1 |
| `ori_kd` | `16.0` | 53 | 1 | 1 |
| `head_ori_scale` | `0.25` | 54 | 1 | 1 |
| `w_pelvis` | `3.0` | 55 | 2 | 1 |
| `w_thorax` | `3.0` | 56 | 2 | 1 |
| `w_head` | `1.0` | 57 | 9 | 1 |
| `q_kp` | `40.0` | 59 | 1 | 1 |
| `q_kd` | `9.0` | 60 | 1 | 1 |
| `w_post` | `0.3` | 61 | 2 | 1 |
| `w_post_arm` | `0.05` | 62 | 2 | 1 |
| `w_post_neck` | `2.0` | 63 | 2 | 1 |
| `w_post_trunk` | `2.0` | 64 | 2 | 1 |
| `w_post_girdle` | `1.0` | 65 | 2 | 1 |
| `w_contact` | `30.0` | 67 | 3 | 1 |
| `contact_kd` | `40.0` | 68 | 1 | 1 |
| `mu` | `0.8` | 69 | 3 | 3 |
| `w_force` | `0.0001` | 70 | 1 | 1 |
| `w_act` | `0.3` | 72 | 2 | 2 |
| `tone` | `0.01` | 73 | 2 | 2 |
| `control_dt` | `0.002` | 74 | 6 | 3 |
| `activation_model` | `step` | 75 | 2 | 2 |
| `max_points_per_foot` | `6` | 76 | 1 | 1 |
| `relaxed_arms` | `True` | 77 | 4 | 3 |
| `arm_tone` | `0.01` | 78 | 1 | 1 |
| `swing_kp` | `400.0` | 80 | 1 | 1 |
| `swing_kd` | `40.0` | 81 | 1 | 1 |
| `w_swing` | `20.0` | 82 | 2 | 2 |
| `swing_ori_kp` | `200.0` | 83 | 1 | 1 |
| `swing_ori_kd` | `28.0` | 84 | 1 | 1 |
| `swing_leg_posture_scale` | `0.1` | 85 | 1 | 1 |
| `solver` | `weighted` | 88 | 4 | 4 |
| `hierarchy_abs_slack` | `1e-08` | 89 | 1 | 1 |
| `hierarchy_rel_slack` | `1e-06` | 90 | 1 | 1 |
| `hierarchy_maxiter` | `160` | 91 | 1 | 1 |
| `fatigue` | `True` | 92 | 1 | 1 |
| `fatigue_scale` | `1.0` | 93 | 1 | 1 |

## Crucial guarded behavior

| Guarded capability | Verified source condition | Consequence at unmodified defaults |
|---|---|---|
| Strict hierarchical objectives | `solver == "hierarchical"` | **Off**, because solver defaults to `weighted`; source task priorities become weights/metadata, not lexicographic guarantees |
| Capture-point support strategy | `capture_k > 0 and nc` | **Off**, because `capture_k=0.0` |
| Foot-flat stabilization | `w_foot_flat > 0` | **Off**, because `w_foot_flat=0.0` |
| Centroidal angular-momentum stabilization | `w_angmom > 0` | **Off**, because `w_angmom=0.0` |
| Optimized reaching-arm activation | `relaxed_arms=True` fixes arm-muscle channels | **Not enabled** for arm optimization in the default standing configuration |
| Fatigue modulation | Fatigue model exists and is enabled | Configured `True` by default, but effect depends on model construction and current fatigue state |

These are **dataclass default facts only**. Callers can use `load_tuned_params` and change the values; the evidence is not enough to claim that any given recorded standing experiment used the defaults. See `NEURO_PARAMETER_SOURCE_OCCURRENCES.csv` for line-specific cross-file sites and receiver-confidence flags.

## Physical control contracts preserved from V013

1. `NeuroParams` describes desired behavior and regularization, not physical muscle excitations by itself.
2. The optimizer computes reachable activation, converts to excitations, returns an array; the caller still has to assign `d.ctrl` and advance MuJoCo.
3. The foot-ground friction-pyramid contact plan excludes seat/hand support. A named `contact` task is not equivalent to all-body contacts.
4. No attempt was made to graft the standing controller onto the seat simulation. The original configuration and data are untouched.

## Boundaries and further evidence needed

- Build exact-runtime observations per scenario to determine which fitted parameters were loaded.
- Measure the full-body optimizer under real MuJoCo stepping with actual native muscle output, then inspect SKIN78 render.
- Bridge goal semantics, body frames and support classes before adapting any standing controller to the seated model.
- Review `NEURO_PARAMETER_SOURCE_OCCURRENCES.csv` carefully: arbitrary receivers with matching field names can be unrelated.

## Integrity

All dataclass fields and branch locations are drawn from the exact SHA-pinned frozen archive. Verification must check the SHA again and reconstruct the ledgers independently. The nested V013 file and original R574 archive are never modified by this build.
