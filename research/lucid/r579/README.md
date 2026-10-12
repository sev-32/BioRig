# R579 — actuator-resolved hip/trunk synergy, native MuJoCo

**Status:** experiment committed to `research/lucid-r575-goal-intent`; do not promote into the frozen R574 evaluation or the established R577 baseline.

## Engineering result

R578's stronger feedback reduced lateral drift only 0.7 mm while raising sustained muscle excitation. R579 isolates which actual anatomical actuator channels supply the corrective authority instead of increasing a four-muscle group together. Source-backed group: `left_lateral` = quadratus lumborum (iliolumbar), quadratus lumborum (iliocostal), gluteus medius, external oblique; the right side mirrors this.

`r579_identify.py` saves one *R577-supported* MuJoCo state at t=8 seconds and forks ten physical 0.8-second constant-input perturbation branches from that same state. The gluteus medius alone reduced lateral displacement by 0.3209 mm relative to no extra command, compared with 0.3279 mm from the complete four-muscle lateral group. This is a **local dynamic response**, not proof of equivalent sustained behavior. The extra extension group moved the root outward and was rejected.

`r579_controller.py` uses exactly the same R577 online sensed-position trigger, muscle command ramp and contact safety gates. It changes only independently named actuator weights: `r577_full=(1,1,1,1)`, `hip_only=(0,0,1,0)`, `hip_trunk_20pct=(.2,.2,1,.2)` and `hip_trunk_50pct=(.5,.5,1,.5)`. It does not read disturbance magnitude, scene ID, future trajectory or probe results online. The frozen R574 early choice (none or R28) remains separate. **Implementation caveat:** this first test harness temporarily substitutes the R577 research-controller constructor inside a guarded `try/finally`. It restores the original afterwards, but is **not thread-safe**; run sequentially. Do not use this research harness as a production control API.

## Real 40-second outcomes, undisturbed narrow seat

| Profile | Hazard | Settled at end | Final root x | Final root tilt | Sum of *all* added muscle-channel excitation × seconds |
|---|---|---|---:|---:|---:|
| R577 all four | No | No | 0.031844 m | 12.390° | 3.8453 |
| R579 gluteus only | No | No | 0.035089 m | 12.460° | 0.9613 |
| R579 gluteus + 20%-trunk | No | No | 0.033863 m | 12.453° | 1.5381 |

**Interpretation:** 75% and 60% less summed additional excitation, respectively, without hazards in this single 40-second case, but displacement is **worse** and neither reaches the ≤0.030 m settling threshold. The reduction is in a control-effort proxy, **not measured metabolic energy or calibrated force**. The four-muscle R577 row is an earlier verified reference rather than a freshly rerun R579 branch.

Both new profiles also passed 12 seconds in scene 00 **and** the already successful pushed scene 04 with no hazard and `settledAtEnd=true`. This is not a 14-scene pass or a held-out test. Files and SHA-256 for full numerical traces are in `R579_NATIVE_AUDIT.json` and the offline checkpoint ZIP.

## Reproduction

Restore the immutable R574/R575 ZIPs using `research/lucid/tools/bootstrap.py` into repo-root `./runtime`. Python 3.13, MuJoCo 3.15.0, NumPy and scikit-learn required, plus Pillow/EGL for native rendering.

```bash
python research/lucid/r579/r579_identify.py

python research/lucid/r579/r579_controller.py \
  --scene 0 --seconds 40 --profile hip_trunk_20pct \
  --out r579_hybrid_40s.json

python research/lucid/r579/r579_controller.py \
  --scene 4 --seconds 12 --profile hip_only \
  --out r579_pushed_recovery_12s.json

python -m unittest discover -s research/lucid/r579 -p 'test_r579.py' -v
R579_NATIVE=1 python -m unittest discover -s research/lucid/r579 -p 'test_r579.py' -v
MUJOCO_GL=egl python research/lucid/r579/r579_render.py
```

The native test suite passed **6/6**, including a fresh physical 12-second replay. The renderer produced four real MuJoCo images at 0, 4, 8 and 12 seconds, with visually transparent seat and adjusted lighting only; geometry, inertia, forces and contacts stayed unchanged. The PNG is supplied separately rather than committed as a repo asset.

**Next:** replace fixed weight fractions with a measured contact-relative two-actuator allocation (hip + trunk), constrain excitation and muscle fatigue proxies, and test 40–60-second settling and all frozen scenes. The required criterion is not simply avoiding a fall; a candidate should eliminate drift **and** preserve prior pushed recovery without new hazards. Whole-loop sensory delay remains untested.
