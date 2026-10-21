# BioRig R27 — contact-lag diagnosis (not a controller release)

**Sources:** Original user-provided R20, R22, R24 and R25 CODE_AND_EVIDENCE archives. Their upload snapshots are authoritative, regardless of the relative age of BioRig or Moto GitHub branches. The script in this directory executes directly against the **original R25 ZIP**, not against a reconstructed default branch.

Archive reconciliation identified **982 unique file paths, zero byte-level conflicts for shared files, and 79 R25-omitted paths recoverable from the older snapshots**. No original R25 source was overwritten. Recovered evidence tests pass: R20 26/26, R22 21/21, R24 6/6, R25 8/8. R27 new offline tests: 8/8. These are archived-evidence tests, not fresh native dynamics.

## R27 recorded observation

| Archived case | Result | R27 detection |
|---|---|---|
| R25 baseline, 540 Hz | No recorded fall | None |
| R25 guard, 540 Hz | Falls at 6.035185 s | 5.13333 s |
| R25 guard, 270 Hz | No recorded fall | None |

The R27 read-only signal combines loaded-right-foot force (>450 N), unloaded-left-foot force (<65 N), lateral pelvis X (>0.105 m), **causally backward-differenced** outward pelvis speed (>0.10 m/s), and DCM-minus-COP lateral separation (>0.06 m), over three successive 30 Hz observations. The failure precedes the recorded fall by 0.902 s. All **81** nearby tested threshold combinations distinguished these same three archived runs; alarm times ranged 5.067–5.200 s. **This is in-sample retrospective discrimination, not predictive validation.**

At about 5.3 s, the standing baseline has lateral hip position X ≈0.052 m, the failing 540 Hz guard ≈0.179 m, and surviving 270 Hz guard ≈0.097 m. It is the unarrested outward motion relative to the stance foot's measured COP, not simply a negative instantaneous support margin, that deserves the next physical experiment.

**Units warning:** the archived `q.spine01.lateralBend` values are **degrees**, not radians; do not convert them again. Archived GIF/MP4 visual comparisons are real saved Skin78 renders, not new physics executions.

## Reproduction

```sh
python3 r27_portable_archive_check.py LUCID_BioRig_R25_CODE_AND_EVIDENCE_20261021.zip
```

Stdlib only. It verifies R25 ZIP integrity, prints a SHA-256 and reproduces the three outcomes plus threshold sensitivity.

## What is still untested / missing

- The original native R25 trace currently fails on an absent Moto **`assets/character/lucid_muscles_r1_5.json`** in the supplied code snapshot. Both that muscle file and `lucid_female_v4_2.json` are present as GitHub repository files in `sev-32/moto` at tree `2c260713`, but have not been materialized into this sandbox. The original `skin_faces_u32.bin` topology required by R25's triangulated skin renderer is absent from the four code ZIPs.
- No **new** 270/540/1080 Hz native physics trial or multi-step evaluation was conducted in R27. In particular, the observational gate has not been wired to a controller and must not be used as a replacement for a physically constrained stance/load planner.
- Next: restore the exact asset versions, rerun unchanged R25, inspect COP/ground-wrench/muscle-reserve and touchdown feasibility, test 3-step episodes, 60/90 N impulses, rate convergence, and visibly review fresh native 3D motion.

**Repository scope:** analysis-only descendant of R26 diagnostic branch; no saved controller, render shader, or previous research source was changed. Companion full offline analysis, tests, renders and provenance are packaged separately in the user conversation as the R27 evidence delta.