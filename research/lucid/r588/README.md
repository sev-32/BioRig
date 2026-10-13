# R588 — reproduce and isolate the seat-edge/thumb impact defect

Research branch `sev-32/BioRig:research/lucid-r575-goal-intent`. **R587, R586, R585 and the frozen R574 model remain unchanged. No GitHub Actions. Not approved for canonical integration.**

## What actually failed

High-rate **native MuJoCo contact records at 10 ms intervals** reveal an impact hidden by R587's earlier 200 ms sampled gates. At **0.27 seconds**, both first-thumb collision hulls strike the nearly vertical sides of the hard-edged research seat at world X ≈ ±0.28 m. Native impulses reach **269.99 N on the right and 201.44 N on the left**. The right contact repeatedly appears/disappears, then loses seat support (14 contact transitions in 3 seconds). The left forearm eventually carries ~17 N. This is neither proof of a globally soft seat nor a missing friction coefficient; it is a *specific distal-collision/arm-descent problem*.

The model uses 84 native muscle actuators and the original SKIN78 skin. A prior reference seated start begins with arms outstretched; they drop rapidly toward the seat sides. The inherited R586 gate only sampled arm loads at 0.2 s, missing these brief severe collisions. Root tilt or head-stability success must NOT conceal this behavior.

## Experimental intervention and outcome

A research-only **contact compliance plus joint-viscous-damping diagnostic** modifies cloned model coefficients before native simulation: bilateral thumb-hull contact solref = `[0.05,2]` with priority 2 and shoulder, elbow and wrist viscous damping multiplied ×10. The physical seat, floor, body mass, skin, neck repair, inherited muscle controller and initial state are unchanged. No root locks, direct joint motors, after-the-fact pose corrections, image synthesis or interpolated image frames are used.

| Real 3-second measured metric | R587 unchanged | R588 diagnostic |
|---|---:|---:|
| Right arm peak seat impact | 269.99 N | **34.75 N** |
| Left arm peak seat impact | 201.44 N | **45.89 N** |
| Right seat contact on/off changes | 14 | **3** |
| Right arm load at 3 s | 0 N | **3.61 N** |
| Left arm load at 3 s | 17.33 N | **3.54 N** |
| Peak head/torso angle | 4.15° | **4.28°** |

A matching native MuJoCo/SKIN78 31-frames-per-condition **0–3 s animation** was produced with original skinned model and real seat/floor visuals: `R588_SKIN78_ARM_CONTACT_BEFORE_AFTER.gif`. The 10 ms force curves are `R588_ARM_CONTACT_MEASURED_FORCES.png`. Renders are delivered in chat separately, not committed to code-only Git.

### Important: this is not yet a realistic full balance solution

At **12 seconds**, the unpushed R588 case remains below the prior tilt and neck hazard thresholds but its pelvis shifts to **−24.90 mm**, with the **left arm no longer carrying seat load**; with a **120 N push**, pelvis ends **+14.71 mm** and the **right arm unloads**. Consequently the seat-contact balancing and symmetry are **not validated long-term**. Joint damping ×10 is an *uncalibrated, non-muscle-driven proxy for landing resistance*, not an anatomically verified stabilization law. This is an initial *impact suppression finding*, **not** a production-approved arm landing controller or relaxed equilibrium.

The alternative attempted seat-stiffness and seat-shape/width variants failed or worsened impact or body support; those results are preserved as diagnostic traces in the offline ZIP. The next correct implementation should use measured hand-to-seat clearance and contact-aware **muscle recruitment** to decelerate the arm before thumb/seat collision, with appropriately rounded/cushioned side geometry rather than arbitrary joint damping.

## Reproduction

Restore immutable R574 and R575 model archives into repository-root `./runtime` using `research/lucid/tools/bootstrap.py`. R585 and R586 source must be present in sibling research folders. Requires Python 3.13, MuJoCo 3.15, NumPy, SciPy, scikit-learn, VTK and Pillow. Provide local MuJoCo via installed package or `PYTHONPATH`.

```sh
python research/lucid/r588/r588_probe.py --seconds 3 --out r588_baseline.json
python research/lucid/r588/r588_probe.py --seconds 3 --thumb-time .05 --thumb-damping 2 --limb-damping-mult 10 --out r588_candidate.json
python research/lucid/r588/r588_probe.py --seconds 12 --thumb-time .05 --limb-damping-mult 10 --out r588_12s.json
python -m unittest discover -s research/lucid/r588 -p 'test_r588.py' -v
R588_FULL_12S=1 python -m unittest discover -s research/lucid/r588 -p 'test_r588.py' -v
python research/lucid/r588/r588_render.py
```

The ordinary suite runs both real 3-second physical cases. Its optional 12-second native replay was run separately as two command-line experiments, and an additional all-in-one 12-second suite remains optional. Each simulated condition is rebuilt from the unchanged initial model, no mutable shared state. No CI or GitHub Actions.

**Visual stage:** initial landing bounce substantially improved in the displayed 3-second actual render. **Whole-body and long-horizon visual approval: withheld.**
