# BioRig R590 — stop testing an artificial arms-out freefall

Status: **isolated native-physics research milestone**, not canonical integration. Frozen R574/R585–R589, original SKIN78 mesh and MuJoCo model untouched. All execution local; **no GitHub Actions**.

## The high-leverage defect

Previous seated experiments began with both arms abducted away from the body; gravity dropped the forearms/hands onto the bare seat corners. R587 and R589 were optimizing the impact of this *initial pose*, not validating relaxed seated equilibrium. At 3 s in original R589 the left forearm contacted the seat edge at world X=-0.28 m while the right hand remained outside the opposite seat edge (approx. X=+0.425 m). A naïve seat widening caused 9–16 kN collisions, not improved anatomy; it is rejected. Single-arm target changes shifted impacts between arms and could compromise head alignment; those parameter sweeps are research failures, not permanent edits.

**R590 separates two different tests:** (1) dynamic physical descent from the arms-out pose, still available as a distinct difficult *landing* experiment, and (2) stable supported sitting, which **must start from an actual physically equilibrated seated state** rather than repeatedly making the character fall from an artificial T-pose.

## Actual 24-second physical validation

`r590_settled_capture.py` runs unchanged R589 native MuJoCo physics **continuously for 24 seconds**. The first 12 s form the equilibration process; the last 12 s are observed (no teleport or hard restart). In the observed interval, the left forearm carries around 7 N seat contact, the right hand hangs freely, **no arm-seat contact on/off transitions** occur, and the measured maximum head-to-torso deviation is 0.116°. Final pelvis X≈0.0129103 m. The *earlier* 0–12 s includes the original impacts, and is not erased or approved as a clean landing sequence.

## Real reusable physical state (critical memory correction)

Saving **only** qpos/qvel/muscle activation then naïvely restarting proved unsafe: an early first replay recorded 82.7 N arm impact, 5.57° neck deviation and ten left-arm contact toggles. The cause was reconstructing the inherited posture reference from the **already-settled** body and cold-initializing the neck allocator's past activation. That changes the controller's meaning and triggers a new settling transient.

`r590_rest_restart.py` instead restores the exact 12-s recorded MuJoCo qpos, qvel and `act`, keeps the original seated **neutral/reference** from before the snapshot assignment, initializes the moment-constrained neck allocator from the actual native muscle activation state, and then recomputes native contacts. No joint lock, synthetic root force, contact geometry change, hand interpolation, or image transformation.

| New 12s test from physically settled R590 state | 0 N | +120 N hip push |
| --- | ---: | ---: |
| Left/right arm-seat contact transitions | 0 / 0 | 0 / 0 |
| Peak arm-seat contact (either arm) | 8.517 N | 8.517 N |
| Maximum head vs upper torso | 0.252° | 0.252° |
| Final pelvis x | 0.012910 m | 0.013208 m |
| Right hand supported by seat | **No** | **No** |

These are two independently instantiated 12-s MuJoCo runs from **byte-identical initial physical states** with a real 0.8–0.92s push (or no push); controller and material coefficients are unchanged. The 120N case isn't visibly dramatic; its displacement is nevertheless measurably nonzero. Opposite-direction and broad-force cases are not yet validated.

## Real renderer proof

`r590_render_settled.py` renders 31 physical state captures from t=12..24 of the **uninterrupted** simulation. `r590_render_rest_restart.py` renders 31 physically captured states per restarted case, t=0..12, in the **original Skin78 VTK renderer**, with original real collision seat and floor. Both renderers reject a skin checksum mismatch, and every qpos snapshot has a physical-trace SHA-256 receipt. **No interpolated or image-generated frames.** An additional exact initial-pose comparison shows original R589's arms-out pose against the physically settled reference. The animation and PNGs are shown directly in chat; image files are not committed to the small code/docs Git tree.

## Local reproduction without GitHub Actions

Restore original immutable R574 runtime to repository-root `./runtime` via `research/lucid/tools/bootstrap.py`. Keep the previous R585–R589 source folders beside R590. Requires Python 3.13, MuJoCo 3.15, NumPy, SciPy, VTK, and Pillow; original Mesh Skin78 assets inside restored R574 archive.

```sh
python research/lucid/r590/r590_settled_capture.py
python research/lucid/r590/r590_rest_restart.py
R590_NATIVE_REPLAY=1 python -m unittest discover -s research/lucid/r590 -p test_r590.py -v
python research/lucid/r590/r590_render_settled.py
python research/lucid/r590/r590_render_rest_restart.py
```

**Rest-state checkpoint:** `R590_SETTLED_CONTINUOUS_NATIVE_QPOS.npz` contains 31 exact 12..24s qpos/qvel/act snapshots and is distributed in the companion numerical checkpoint ZIP, not pushed as binary to Git. It can be regenerated from the original R589 source. `R590_RESTART_PUSH_+0N_QPOS.npz` and `R590_RESTART_PUSH_+120N_QPOS.npz` are separately replayed and hashed full body poses for rendering.

**Tests:** 8/8 local, including a fresh 2-second native replay from the restored state. The 12-second no-push and +120 N traces were already computed independently and are rechecked by their hashes, numerical metrics, and source-controlled contracts.

## Do not mistake this for a universal balance solution

The startup contact problem and earlier artificial transient are addressed for the controlled **seated-rest task**. Bilateral supported hand-rest is not solved; right hand remains to the side. Dynamic arm descent from arms-out remains a separate unsolved landing task. A physically generated 12s initial state is not a guaranteed universal equilibrium under arbitrary disturbances. The high-level head muscle allocator still requires anatomical force calibration and broad contact/perturbation validation.

See `R590_REJECTED_EXPERIMENTS.md` for negative tests that must not silently re-enter the main model.
