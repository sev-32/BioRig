# R582 — signed three-dimensional external contact wrench

**Research only** · repository `sev-32/BioRig` · branch `research/lucid-r575-goal-intent` · frozen R574/R575 baseline unchanged · **GitHub Actions not used**. The local native MuJoCo 3.15 simulation and tests are authoritative for this checkpoint, not claimed GitHub CI runs.

## Physical correction

R581's *one-dimensional contact normal-load centroid* computed each contact's vertical weight from `abs(contact.frame[1]) * mj_contactForce(...)[0]`. This silently discards upward load carried by **tangential friction on near-vertical seat/thigh contacts**. In the true 40-second R581 replay, two right thigh-side contacts individually carry ~49.7 and ~49.9 N of *upward* force, but the old estimator counts only 2.37 and 2.15 N. The old vertical support total is 630.78 N, versus 740.49 N when all actual signed world forces are included. Original COM and plant states remain unchanged.

`r582_wrench.py` is a separate, read-only, world-frame observer. It uses named external support geoms (`research_seat`, `ground`), excludes self-contacts, transforms all 6 components of `mj_contactForce` using the **transpose of MuJoCo's row-major contact frame**, and adjusts sign to return the force on the **body** rather than on the support. It integrates **three-dimensional** net reaction force (N) and moment about whole-body COM (N·m), including contact tangential forces and contact torsion. The vertical-pressure centroid is separately preserved for comparison but includes only upward forces, not contact-normal weights. The resultant wrench is projected onto virtual world plane Y=0 with `projected X = Mz about the plane origin / Fy`; it is **NOT a physical zero-moment-point or stability guarantee**, because the feet and seat are supported at different heights and because of dynamic acceleration and other body moments.

### Corrected R581 native measurements (one 40-second continuous physical replay)

| 40s measurement | Original R581 normal-weight proxy | R582 world-wrench observer |
| --- | ---: | ---: |
| Upward support | 630.775 N | 740.492 N |
| COM minus pressure centroid | 0.036752 m | 0.019589 m |
| COM minus projected resultant at Y=0 | Not available | 0.003018 m |

This explains why R581's apparent support displacement was exaggerated: near-horizontal seat normals can nonetheless sustain large world-up friction forces. It **does not** eliminate the measured 0.032-m lateral root drift or prove equilibrium; changing the measurement cannot change physical history retroactively.

## R582 controller experiment

`r582_controller.py` preserves the existing R581 hip+oblique anatomical actuator names, activation caps, controller gains, 40-ms cadence, safety gates, frozen R574 early intention selection, and scene initial states. It changes one online feature: **COM relative to the signed-wrench projection** replaces **COM relative to R581's incomplete contact-normal pressure proxy** for selecting extra oblique recruitment. The projected-reaction feature is guarded for finite/positive support; a missing valid support result aborts stimulation. The unchanged long-horizon project settling condition remains authoritative, not this new measurement.

| Native paired development result | R581 prior measured reference | R582 signed-wrench controller |
| --- | ---: | ---: |
| Scene 00 12s | Settled; no hazard | Settled; no hazard |
| Scene 04 12s pushed rescue | Settled; no hazard | Settled; no hazard |
| Scene 00 40s hazard | No | No |
| Scene 00 40s settled | **No** | **No** |
| Scene 00 40s final root x | 0.032166 m | 0.032276 m |
| Scene 00 40s added excitation-seconds (two channels) | 1.953904 | **1.742945** |
| Scene 00 40s final root tilt | 12.380° | 12.389° |

The corrected feedback consumes **10.8% less added muscle-channel excitation** while preserving tested safety at the cost of 0.11 mm more root displacement. These are **development scene** results; not a generalization claim. Extra excitation is a control-effort proxy, not physical work or metabolism.

## Verify locally — no GitHub Actions

Restore original immutable R574 and R575 archives with existing `research/lucid/tools/bootstrap.py` to repo-root `runtime`. Python 3.13, MuJoCo 3.15.0, NumPy, scikit-learn; EGL and PyOpenGL/Pillow for actual 3D captures. Tests performed **locally**:

```bash
R582_NATIVE=1 python -m unittest discover -s research/lucid/r582 -p 'test_r582_*.py' -v
python research/lucid/r582/r582_probe.py
python research/lucid/r582/r582_controller.py --indices 0 4 --seconds 12 --out R582_SCENES00_04_12S.json
python research/lucid/r582/r582_controller.py --indices 0 --seconds 40 --out R582_SCENE00_40S.json
MUJOCO_GL=egl python research/lucid/r582/r582_render.py
```

`R582_AUDIT.json` and full numerical JSONs, local test log and genuine EGL renderer checksum accompany this checkpoint. The large original runtime and PNG are not committed to the source branch. The actual PNG is displayed separately in chat.

**Stop/go:** Do not promote to R574. Need contact-wrench conservation comparison beyond quasi-static bench, physically meaningful supporting polygon on multi-height surfaces, counteracting hip muscle allocation rather than just increasing excitation, and full 14-scene/40–60-second safety regression with complete sensorimotor latency. The 40-second 0.030-m positional criterion still fails.
