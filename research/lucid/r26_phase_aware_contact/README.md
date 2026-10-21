# BioRig R26 — phase-aware contact-instability evidence audit

**Status:** experimental, read-only diagnosis; no gait-controller promotion. **Date:** 2026-10-21.

## Source provenance

This branch starts from `research/lucid-clothing-r1-clean-handoff-20261018` at `1916fb29fdf515b8a98f792797c605bd5dc7530a`. Existing R574–R590 and clothing-engine research remain intact. The R20/R22/R24/R25 working code-and-evidence ZIPs were provided separately in the conversation and are **not** contained in the BioRig GitHub repository. Do not describe a GitHub commit of this audit as a commit of the full BioRig R25 physics runtime.

SHA-256 of original conversation ZIPs:

| Archive | SHA-256 |
|---|---|
| R20 CODE_AND_EVIDENCE | `70ae3160116ad0571a51dfa9dcdcb9afc0188304016ba38c95be8c876dd86c19` |
| R22 CODE_AND_EVIDENCE | `e110d1832baadd7e2d0bde642cba94060a1d90a98ef95696475454587d9807c7` |
| R24 CODE_AND_EVIDENCE | `883ac210ac4a0fa634d121684c7fb278b83260d01e371f5f8378dede3b3d2c72` |
| R25 CODE_AND_EVIDENCE | `2453e61ebcfd1c2bf178045ec27bcbb82890ed68c2519d8f75a51fb9d5d87a73` |

The R25 ZIP passed a complete CRC traversal; R25 archived-evidence tests: **8/8 PASS**, including the expected-failure checks. The tests do not rerun native 540 Hz articulated dynamics; they evaluate saved physical telemetry and saved geometry.

## Reproduction

Requires Python 3 standard library and the exact R25 ZIP above. No unpacking necessary.

```bash
python research/lucid/r26_phase_aware_contact/r26_archive_audit.py \
  LUCID_BioRig_R25_CODE_AND_EVIDENCE_20261021.zip \
  --self-test --out r26_audit.json
```

The script verifies ZIP CRC, hashes the complete input archive and each telemetry member, then evaluates a **backward-difference**, phase-tagged, multi-signal observation gate. It does **not** add a contact force solver or predict full-body reachable support states.

## Observed result

| 1-step recorded condition | Recorded fall | First R26 joint signal | Retrospective lead |
|---|---:|---:|---:|
| Baseline, 540 Hz | None | None | — |
| R25 margin-guard, 540 Hz | 6.035185 s | 5.43333 s | 0.60186 s |
| R25 margin-guard, 270 Hz | None | None | — |

The alert requires three successive 30 Hz telemetry observations with **all** of:
- lateral hip/pelvis coordinate |X| > 0.15 m;
- lateral pelvis velocity |dX/dt| > 0.25 m/s (causal backward difference);
- logged DCM-to-support margin < -0.10 m;
- |lower lumbar lateral bend| > 15 degrees.

Thresholds were chosen by examining the very same three runs. Accordingly, this is **in-sample discrimination only**, not a calibrated viability predictor. Both baseline and failed guard cross DCM margin below -50 mm around 4.233 s; DCM margin alone is not a useful failure classifier here. The contact state (`wds`, `wss`, double support), future foot landing, force reserves, joint saturation and attainable contact wrench are still needed.

## Visual evidence and known packaging defect

The companion R26 chat checkpoint regenerates a **true Skin78 posed-vertex point-cloud projection** from stored per-frame 14,164-vertex floats and shows physical baseline versus rejected guard at 5.x and 6.333 s. This is not live browser/WebGL and is not triangulated skin. R25's surface renderer cannot be reproduced from the code-and-evidence ZIP because its referenced `08_TESTS_RESULTS/reports/skin_faces_u32.bin` topology input is missing (all four provided code ZIPs lack it). Do not quietly fabricate topology or claim that archived PNGs are newly rendered.

## Next physical experiment (not yet completed)

Export synchronized future foot landing intent, predicted touchdown time, achievable 3-D contact wrench polytope/cone, per-muscle activation and moment-arm bounds, and segmental angular momentum. Compare held-out trials at 270/540/1080 Hz, lateral disturbances 60/90 N, multiple seeds and sustained three-step walking. Train/calibrate the observation gate on separate trajectories **before** using it to modify the real controller. An R26 signal may veto a proposed action only after real plant validation.

**Explicitly not changed:** archived R24/R25 muscle controller, pad material/contact plant, original geometry, original research branch, Moto host or visual shaders. No visual acceptance is inferred.
