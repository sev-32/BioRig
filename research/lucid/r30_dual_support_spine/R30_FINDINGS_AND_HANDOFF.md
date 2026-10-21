# BioRig R30 — double-support spinal task continuity (experimental)

**2026-10-21 — research only; neither physical gait repair nor visually approved.**

## Confirmed source issue

The archived R29 whole-body-controller candidate contains a spinal S-mode task that requires exactly one supported foot. In the original `wds` double-support transition, `stance=null`, so the corrective row gets zero contact confidence even if both feet bear substantial verified vertical load.

The independent opt-in R30 candidate introduces `r30_dual_support_spine_brace:false`. When enabled together with `r29_spine_priority:true`, it computes actual supporting-foot pad forces separately and uses their sum during double support, with existing single-support gating unchanged. Existing task dead band 5 degrees, relative spinal lateral-bend row, maximum weight 0.12, and maximum desired relative acceleration ±35 rad/s² remain. Axial rotation is not directly constrained. Existing constrained muscle/ground-contact QP is not replaced; no extra physical torque or kinematic pose is added.

## Test and evidence receipt

- **11/11** source-extracted block integration tests PASS, including support transition, no fabricated loads, original R29 off behaviour, independently preserved axial yaw, requested-weight and acceleration bounds.
- Full R30 candidate **Node syntax check PASS**.
- Deterministically regenerated candidate from an exact archive copy of R29, compared by SHA-256.
- Archived trace replay used full measured R15/R22 lumbar and thoracic joints plus actual foot-pad ground reaction, under explicit proxy assumptions. 3.5–6.2 s window, number of samples with requested spinal task weight > 0:
  - R15 surviving 540 Hz: R29 43, R30 76.
  - R22 surviving 540 Hz: R29 41, R30 75.
  - R22 falling 1080 Hz: R29 47, R30 78.
  - R22 older falling 540 Hz: R29 52, R30 77.
- These are **retrospective hypothetical task requests** calculated without advancing the full BioRig body or the muscle optimization. They are **not** successful new simulations or demonstrations of reduced lumbar tilt. They activate in both surviving and falling historical trajectories.
- The native R25 Moto runner was re-executed unmodified and remains blocked at `assets/character/lucid_muscles_r1_5.json` with ENOENT before physics startup. Moto GitHub tree contains the muscle, body and rider-surface assets, but their bytes were not restored into the sandbox.
- Fresh R30 plot/animation presents true archived data. Original R22 Skin78 image is retained as clearly labeled, **separate 270-Hz archived reference**, not a newly computed R30 body.

## Provenance / full archive

The complete portable R30 local package contains both untouched archived R25/R29 source files, independently regenerable *full* R30 controller candidate, executable Node tests, evidence traces, the annotated skin/telemetry render, trace-animation GIF, reports and raw logs. Parent R29 SHA-256:

`26c8e07fa4fef973eb8be91cb2f255d9dd6dbd3fcd4c0430f9ed428caafe5fbe`

Generated full R30 source SHA-256:

`0a2b62e6da491d16f058e0eeaf8ff78ba8dd4eba0b02315100fb4fb394c3673c`

Package: `BIORIG_R30_DUAL_SUPPORT_SOURCE_AND_EVIDENCE_20261021.zip`, SHA-256:

`9e47498e79c538b514615df8c7c2d744a6337c7717cab2908d2ddf6648372f94`

A clean unpack of the portable ZIP re-executed **11/11 controller block tests**, archived replay, and deterministic source generation successfully.

**Important:** This GitHub research branch is a documentation checkpoint; it does **not** yet contain the full 146 KB integrated R30 candidate and must never be substituted for the portable archive. Existing GitHub branches and original controller files are unchanged.

## Native promotion gates

Restore original verified character assets; run baseline unmodified with WebGL2 screenshots and errors; A/B compare R25/R29/R30 at 270, 540, 1080 Hz with matched initial conditions. Instrument actual spinal torques, activation/force saturation, independent lumbar/thoracic lateral bend and axial yaw, measured L/R contact COP and muscle task residuals, cervical/head excursion, joint energy and multi-step falls. Reject posture improvement without improved physical support. Require user approval of actual native renders before any integration.
