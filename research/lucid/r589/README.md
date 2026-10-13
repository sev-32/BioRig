# BioRig R589 — muscle-controlled arm descent and real SKIN78 contact proof

Research-only stage: `sev-32/BioRig`, branch `research/lucid-r575-goal-intent`. **No GitHub Actions. Frozen R574 and prior R585–R588 remain untouched. No canonical promotion.**

## Why this stage is different

R587 genuinely held its head stable but threw the initial outstretched arms down onto the seat edges. In 10-ms native contact measurement, thumb hulls struck the seat at 0.27 seconds (270 N right; 201 N left). R588 reduced those impacts by making shoulder/elbow/wrist passive damping **ten times** as strong; this was a non-biological proxy and could not be accepted as the control solution. R589 removes that intervention entirely.

R589 uses actual native shoulder muscle channels to **brake and guide the arms in physical time**, measuring *current* shoulder angle, speed, native actuator moment arms and muscle gain. It commands opposing anatomical muscles according to needed signed shoulder moment (primarily deltoid middle or pectoralis major), slows the abducted arms into a natural lower resting posture, and **returns control to the inherited muscles** after 1.2–1.9s. No synthetic joint torques, pose interpolation, root locks, changed friction, thumb collision coefficients, or artificially high passive damping. The original R586 moment-constrained six-DOF neck stabilization remains active and unchanged.

The first prototype did lower right impact but destabilized the head, so it was rejected. The new separately tuned, bounded left/right landing profile is locked in `VERIFIED_PROFILE` of `r589_arm_landing.py`. The same locked profile produced the 3-second and 12-second trace/reproduction.

## Native 12-second cloned result

| Native quantity | R587 original | R589 bounded muscle descent |
| --- | ---: | ---: |
| Max right arm-on-seat impulse/normal contact load | 269.99 N | **10.99 N** |
| Max left arm-on-seat load | 201.44 N | **35.90 N** |
| Right-arm >1 N contact on/off transitions | 14 | **6** |
| Left-arm >1 N contact on/off transitions | 7 | **13** (worse; open issue) |
| Maximum head–upper-torso angle | 4.154° | 4.445° |
| Final pelvis x | 13.342 mm | 12.910 mm |
| Arm additional muscle excitation ∫activation·dt | 0 | 0.348 excitation·seconds |
| Right arm load at 12 seconds | 0 N | 0 N |
| Left arm load at 12 seconds | 17.9 N | 7.0 N |

Both 12s runs use the same native model, 0N external push, same original seat and floor geometry and friction, same SKIN78, 0.002s physics step, six no-slip iterations inherited from R586. The 0 N final right-arm seat load means the right hand hangs by the side rather than remaining mechanically supported on the seat; **do not claim a newly solved supported hand-rest task**. The left contact transitions increased; do not claim complete chatter elimination. The reduced peak impacts and smoother visible arm descent are specific measured improvements.

Original source is evaluated against the corrected R585 physical neck model with R586 muscle allocator, not an obsolete R574 neck-failure scene. Skin is the actual canonical 14,164-vertex Skin78 with SHA-256 `88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10`.

## Visual evidence, not a fabricated picture

`r589_capture_native.py` saves actual qpos snapshots from 31 selected frames **while native physics runs** and hashes each physical state; it captures 0–3s every .2s and 3.6–12s every .6s. `r589_render_saved_native.py` independently renders those exact immutable qpos snapshots through the original SKIN78 deformation path and a real collision-derived seat. The paired GIF `R589_NATIVE_SKIN78_12S_COMPARE.gif` and proof panels are user-visible in chat, not committed to the source-only repository. The underlying numerical qpos snapshots and SHA receipts are in the compact checkpoint ZIP, along with source/test logs, so screenshots cannot conceal physical differences.

### Native reproduction (local only; no GitHub Actions)

Restore original immutable R574 runtime to repository-root `runtime/` using `research/lucid/tools/bootstrap.py`. Requires Python 3.13, MuJoCo 3.15, NumPy, SciPy, VTK and Pillow. If the restored runtime is outside this repo, export `BIORIG_WORKSPACE` to that root. Run from repository root:

```
python research/lucid/r589/r589_arm_landing.py --seconds 3 --out r589_native_3s.json
python research/lucid/r589/r589_arm_landing.py --seconds 12 --out r589_native_12s.json
R589_NATIVE=1 R589_NATIVE_12=1 python -m unittest discover -s research/lucid/r589 -p 'test_r589.py' -v
python research/lucid/r589/r589_capture_native.py
python research/lucid/r589/r589_render_saved_native.py
```

`r589_render.py` is the earlier rejected 3s exploratory attempt, retained in the separate checkpoint, not the accepted 12s render. `r589_render_long.py` was an unsuccessful direct-in-loop VTK renderer and remains off the Git branch. The **decoupled physical snapshot rendering** is the tested working 12s path and is the one to use.

## Gates and honest limits

8/8 tests passed locally including *fresh* 3s paired native physics and the native 12s replay. The 12s zero-push case is complete. A combined attempted 12s 120 N push run exceeded the wall-time limit; there is no verified pushed R589 endpoint. No reliable 24s R589 test yet. Do not call this fully validated whole-body equilibrium or biologically optimal muscle effort. Missing: pushed 12/24s, left contact chatter, posture/seat realism under different widths, fatigue/metabolic work, continuous high-rate visual inspection. No existing frozen baseline was modified, and no GitHub Actions were used.
