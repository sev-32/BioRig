# BioRig/LUCID R585 — physical head/neck stabilization checkpoint

**Disposition:** research-only physical neck repair; original R574 archives untouched; not approved as a whole-body equilibrium controller; no GitHub Actions.

## Actual defect measured and repaired

The original 84-muscle MuJoCo model had **zero actuators capable of delivering positive head.nod torque** at its canonical seated state, because every muscle spanning the cranial nod DOF had a moment arm with the same sign. The inherited R551 posture reflex also projected all 84 muscle demands through a **single global normalization**, instead of allocating independent corrective torque at each neck DOF. This is a concrete *present source* flaw, not proof of the historical moment at which this model regressed. Earlier stable video renders must be audited before attributing a first-bad version.

R585 changes a **test-local physical muscle attachment**, moving each original sternocleidomastoid skull insertion to Head-local Z = −0.025 m, turning that existing 200-N/channel musculotendon into a head-nod antagonist while preserving its primary cervical-flexor moment direction. This modifies neither the skin, skeleton/DOF count, body mass, collision geometry, external support, nor 84-actuator count. Research config also uses the already measured R584 six-iteration native contact no-slip solver; both compared versions share that solver and the cold-start seated pose. Anatomical location is an engineering hypothesis requiring further validation.

The six-axis R585 controller reads current MuJoCo muscle-length/velocity gain, sparse actuator moment arms, gravity/Coriolis and passive joint torque, and estimates desired neck/head joint moments from the six anatomical joint angles and velocities. It solves a bounded **nonnegative muscle-activation allocation**, ≤0.8 per neck actuator; all non-neck baseline muscle excitations remain from original R551 stabilization. No joint/root torque injection, hard pose clamp, teleported state, IK, fake animation, or external spotter force is used in the no-push experiments. New controller acts only through the existing 10 neck-related muscle channels.

## Native matched SKIN78 visual proof

`R585_REAL_SKIN78_NECK_REPAIR_12S.gif` is 31 original SKIN78 mesh renders **per condition**, from separate continuous 12s native MuJoCo simulations at 0.4s spacing. Same original physical initial pose, seat/floor and muscle-stabilizer base; original has unmodified SCM geometry and original neck control; fixed variant has corrected physical SCM muscle sites and a new six-joint activation controller. The mesh SHA256 is `88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10`. GIF SHA256 `6e46d699cebf934b64924a8647e0df752ac4a5fab709a3757731ecb28aa25cf4`. Actual image is delivered separately, not packaged with code/docs.

Native 12s outcome:

| Measurement | Inherited neck | R585 repaired |
| --- | ---: | ---: |
| Max head-vs-thorax orientation | 86.97° | **4.10°** |
| Head-vs-thorax at 12s | 84.12° | **0.0017°** |
| Final pelvis x | ~19.8 mm | **13.6 mm** |
| R585 max arm/seat force | — | 25.84 N |
| R585 max other-floor force | — | 0 N |
| R585 max pelvis tilt | — | 13.50° |

**Repeatability:** Original 7/7 local regression suite completed successfully once, including new 12s native scene and +120 N pushed replay. A later repeat of the whole suite **timed out**, and the 40s extension did not complete; those are not validation passes. The isolated 12s no-push case and skinned paired animation have both been executed several times to completion with the same result. Separate −120 N and +120 N 12s experiments passed head and support hazard thresholds. A higher-push instrumented repetition did not complete. Full 14-scene baseline regression, 40–60s stability, and repeated stochastic/contact sensitivity remain open.

**Important limitation:** mean summed neck-muscle excitation ≈3.16 across ten channels during the 12s run, with peak individual command ≈0.58. This is a large and **not human-calibrated** muscle effort. The head is positionally stabilized here; **relaxed equilibrium is not proven**. Do not replace the canonical rig without anatomical calibration, broader contact/load tests, and owner visual acceptance.

## Reproduction (no GitHub Actions)

Restore the frozen original R574 ZIP into repo-root `./runtime` (use the existing bootstrap tool and original archive hash). Python3.13, MuJoCo3.15, NumPy, SciPy, VTK/EGL, Pillow and scikit-learn needed. If runtime is not at repo root set `BIORIG_WORKSPACE=/path/to/workspace`. From repo root:

```
BIORIG_WORKSPACE=$PWD R585_NATIVE_12S=1 R585_NATIVE_PUSH=1 \
 python -m unittest discover -s research/lucid/r585 -p test_r585.py -v
BIORIG_WORKSPACE=$PWD python research/lucid/r585/r585_skin78_render.py
```

Always inspect the real skinned GIF, the contact telemetry and frozen original before claiming visual correctness. The user's visual judgment is the acceptance criterion. Not merged or promoted. The preceding `FORENSIC_CANCELLATION_R584_2026-10-13.md` overgeneralized from one seated R574 replay to earlier historical renders, and that historical regression claim remains unverified.