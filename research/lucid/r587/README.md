# R587 — longer native SKIN78 inspection and whole-body regression gates

**Repo:** `sev-32/BioRig`, **branch:** `research/lucid-r575-goal-intent`. Research-only continuation, no changes to original R574 source/assets, canonical Skin78 mesh, R585 controller or R586 learned muscle allocator. No GitHub Actions.

This stage deliberately **does not retune neck muscles**. It tests the previously validated R586 control over **24 actual simulated seconds**, instead of making new controller claims from short, numerically green trials. The experiment addresses the earlier systemic failure to inspect the full skinned character and detect catastrophic head behavior despite passing pelvis-only tests.

## Native MuJoCo results (both fully completed)

| 24-second experiment | No push | +120 N hip push at 0.80–0.92 s |
|---|---:|---:|
| Maximum measured head relative to upper thorax | 2.16272° | 2.31073° |
| Head relative to thorax at end | 0.11590° | 0.11654° |
| Final pelvis lateral x | +0.013341 m | +0.018309 m |
| Largest root/pelvis tilt | 13.908° | 13.867° |
| Peak arm contact with seat | 31.543 N | 31.543 N |
| Unintended floor contact | 0 N | 0 N |
| Added neck activation integral (excitation × s) | 51.8175 | 55.8957 |
| Optimizer fallbacks/infeasible updates | 0/0 | 0/0 |

Between seconds 4 and 24, the measured pelvis x changes by less than approximately 0.01 mm in these **specific scenarios**. This is not a calibrated friction-slip measurement nor a guarantee of passive equilibrium. Low-level base stabilizer and actively controlled neck muscles remain engaged.

The genuine SKIN78 surface was rendered in **61 distinct MuJoCo states per case**, sampled every 0.4 simulated seconds without interpolation, using original `skinSHA256=88b6cacd2f7ad7fad0c5c9d9c731afcbc1388e09c5f0e817d181a62f11844a10`. Camera/lighting and seat visualization affect visual presentation only. The separate GIFs and four-time proof panels at 0, 8, 16 and 24 s have been displayed to the user **in chat**. Assistant visual judgment: no obvious head collapse, loss of contact, or gross skin penetration in the tested views; **visually approved for this 24s seated milestone only**. The user can overrule this judgment.

## Hard regression gate, not another pelvis-only pass

`r587_whole_body_gate.py` rejects physical runs missing a full 24 s trace, head-to-thorax angle ≥5°, root tilt ≥45°, arm-seat impact ≥50 N, unexpected floor contact ≥50 N, |pelvis x| ≥0.030 m, or optimizer fallbacks. It also verifies **all 61 time-stamped native frame hashes** and exact GIF SHA-256. This prevents the earlier gross 84° head collapse from slipping through a numerically “settled” state.

`test_r587.py`: **9/9 local tests passed**, including injected catastrophic head fold, off-center pelvis, impact, incomplete traces, both actual 24 s physical evidence receipts, both generated native animations, independent physics-to-render pose matching. No GitHub Actions were run.

## Reproduce offline from Git source

1. Restore the original locked R574 ZIP and R575 addendum into repository-root `runtime/` with `research/lucid/tools/bootstrap.py`; the archives remain unchanged. Python 3.13, MuJoCo 3.15, NumPy, SciPy, VTK and Pillow are needed.
2. Run on Linux with native VTK software rendering and the original `lucid_bcr` source. The renderer discovers `runtime/` and sibling R585/R586 research modules relative to the checkout.

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python research/lucid/r587/r587_skin78_long_render.py
R587_PUSH_N=120 python research/lucid/r587/r587_skin78_long_render.py
python -m unittest discover -s research/lucid/r587 -p 'test_r587.py' -v
```

The full 24 s native physics receipts and 61-frame hash records are stored in this research directory, allowing source-level tests without GitHub Actions. The actual GIFs and PNGs are provided separately rather than inflating the code/documentation Git branch or ZIP. `R587_VERIFIED_AUDIT.json` pins all hashes.

## Open engineering gates

**Not a production balance certificate.** Further tests need actual contact-point slip/foot shear and anatomical supports, 40–60 s continuous physical and visual observations, multiple anthropometries, stronger asymmetric disturbances, and calibrated muscle effort. The current controller's 24 s performance does not prove asymptotic balance, human neuromuscular realism, or anatomical injury safety. R585 and R586 remain protected source references.
