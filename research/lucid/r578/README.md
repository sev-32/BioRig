# R578 — measured support-pressure feedback (research only)

R578 is an isolated experiment on the immutable R574 84-muscle MuJoCo free-root plant. Earlier R574–R577 controls, evaluation locks and low-level dynamics are not modified. The two executable modules are separated by semantics: `r578_support.py` measures a mass-weighted center of mass and a normal-contact-load weighted seat/floor pressure center (metres and newtons); `r578_feedback.py` uses current sensed pelvis displacement, lateral velocity and optionally COM-to-pressure displacement to regulate bounded lateral muscle excitation every 40 ms. The normal-force centroid is *not* a complete stability polygon or ZMP estimator; the tested bench has vertical support normals.

All results are **development tests after observing a failure in scene 00**, not independent held-out validation.

## Native 40-second scene 00 results

| Controller | Hazard | Settled at 40s | Final pelvis x | Final tilt | Cumulative dose (excitation·seconds) |
| --- | --- | --- | --- | --- | --- |
| R577 original tonic | No | No | 0.0318444 m | 12.390° | 0.96132 |
| R578 standard: position gain 0.4, COM gain 0 | No | No | 0.0317005 m | 12.381° | 1.01319 |
| R578 stronger: position gain 1.2, COM gain 0.3, x target 0.023 m | No | No | 0.0311359 m | 12.354° | 1.22397 |

The stronger candidate's peak tilt was 13.12°, peak arm-seat contact 0.078 N, and neither support was simultaneously lost. However, it reduced the persistent lateral offset by only 0.708 mm compared to R577, while consuming ~27% more cumulative excitation. Therefore **it is not approved for promotion**. Excitation integral is a control-effort proxy, not biological energy.

The previously safe pushed scene 04 was also tested under stronger R578: 12 s complete, hazard=false, settled=true, final x=0.024794 m, peak arm-seat=5.811 N. Other R578 scenes remain unverified. The complete 14-scene and 20–60-second regression gates remain open; sensorimotor whole-loop latency remains untested.

## Reproduce

Restore the original frozen R574 and R575 archives to `./runtime` with `research/lucid/tools/bootstrap.py`. Dependencies: Python 3.13, MuJoCo 3.15, NumPy, scikit-learn. EGL rendering also requires PyOpenGL and Pillow.

```sh
python research/lucid/r578/r578_feedback.py --indices 0 --seconds 40 --mode pd --out r578_default.json
python research/lucid/r578/r578_feedback.py --indices 0 --seconds 40 --mode pd --root-target .023 --kp-root 1.2 --kp-com .3 --out r578_strong.json
python research/lucid/r578/r578_feedback.py --indices 4 --seconds 12 --mode pd --root-target .023 --kp-root 1.2 --kp-com .3 --out r578_scene04.json
python -m unittest discover -s research/lucid/r578 -p 'test_r578.py' -v
R578_NATIVE=1 python -m unittest discover -s research/lucid/r578 -p 'test_r578.py' -v
MUJOCO_GL=egl python research/lucid/r578/r578_render.py
```

`R578_NUMERICAL_AUDIT.json` records parameter sets, horizon, comparator metrics, cloned physical-state hash and full-trace SHA-256. Original numerical trace JSON files are included in the separate local checkpoint, not the source-only Git branch. Native EGL renderer captures are provided separately.

**Next:** identify independent pelvis/hip/foot muscle actuation authority and test a bounded low-effort muscle synergy; retain zero new hazards and the existing scene-04 rescue. Do not replace the baseline or claim human-grade motor intelligence from these single-scene results.
