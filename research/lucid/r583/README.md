# R583 — contact friction comes before muscle-control tuning

The user observed that the native LUCID rig's pelvis and feet appeared to be sliding on ice. This project therefore **stops controller tuning to audit contact mechanics first**. Everything runs in `sev-32/BioRig`, branch `research/lucid-r575-goal-intent`. Frozen R574/R582 and the underlying 84-muscle MuJoCo model are never edited. **No GitHub Actions.**

## Source-grounded discovery

The native scene **does** enable friction. The actual effective sliding-contact coefficients are 0.82 on the research seat and 1.0 on the floor. Contact forces have nonzero tangential components. At 12 seconds in the undisturbed original scene, the seat transmits 105.5 N aggregate tangential contact force and the feet 105.2 N. Nevertheless, physically measured load-weighted slip remains about 1.22 mm/s at the seat and 4.87 mm/s at the feet. The stance *is not stationary at the points of contact*.

`r583_friction_probe.py` computes slip with **world-space MuJoCo contact-point velocity Jacobians** for the moving body relative to the seat/floor body, projects into each contact's tangent plane, and weights by actual normal contact loads. It obtains effective coefficients from the **generated contact pair** `contact.friction[0]`, not simply from a configured material label. Seat/ground are identified by geometry names; changing only one of two interacting surfaces does not guarantee a changed effective coefficient under MuJoCo's default friction mixing.

## Native cloned physical results (12 s, no external push)

All treatments begin from the exact same saved R574 warmup state (SHA256 `3baf94ca375e535d72bacccdee2c43141e7d2a3a156539257274de1862339c24`), with the original R582 sensed-state muscle controller and every joint/inertia/collision geometry unchanged. After restoring the initial state, only the contact sliding friction is changed. Renderer settings change only colors, lighting, camera and visible seat opacity.

| Test | Effective seat/floor sliding friction | Final pelvis x | Final tilt | Additional muscle excitation × seconds |
|---|---|---:|---:|---:|
| Near ice | 0.00001 / 0.00001 | −0.19638 m | 73.23° | 0 (safety gate aborts) |
| Frozen original | 0.82 / 1.0 | +0.02772 m | 12.60° | 0.43053 |
| Higher-grip stress test | 2.0 / 2.0 | +0.01767 m | 12.54° | 0.40931 |

The larger effective friction reduced final lateral drift by approximately **36%** and additional activation by roughly **5%** relative to the original 12-second case. This demonstrates a causal sensitivity to grip. **It does not prove 2.0 is a realistic material value** or that any controller has learned relaxed mechanical equilibrium. Near-ice loses its seat support and the R582 controller's safety interlock shuts off additional activity; do **not** interpret zero dose in that failing scene as efficient control.

The frozen original-friction 40-second replay also finished at x=0.0322755 m (not settled), confirming the previously identified drift. The attempted 40-second higher-grip extension **timed out** and has no verified endpoint. No claims are made for its 40-second outcome.

## Native animation and numerical proof

`R583_FRICTION_SIDE_BY_SIDE_NATIVE.gif` (shared separately, not stored on GitHub) contains **real** MuJoCo/EGL captures at 0, 2, 4, 6, 8, 10 and 12 seconds; every pane uses a fixed camera. The original numerical traces are distributed in a separate compact ZIP alongside the raw source, checksum audit, test log and friction/slip graph. They are not synthesized frames or artistic animations.

## Reproduction (no GitHub Actions)

Restore the original frozen R574 and R575 archives into repository root `./runtime` using `research/lucid/tools/bootstrap.py`. Requires Python 3.13, MuJoCo 3.15, NumPy, scikit-learn and Pillow; native EGL capture requires OpenGL.

```sh
python research/lucid/r583/r583_friction_probe.py --seconds 12 --render
R583_NATIVE=1 python -m unittest discover -s research/lucid/r583 -p 'test_r583_friction.py' -v
```

The optional native replay is enabled by `R583_NATIVE=1`. All **6 tests passed**, including real 12-second high-grip physical reproduction. The source and test files are stored in Git with exact blob SHA checks.

## Engineering judgment and next gate

**Do not install the 2.0 friction stress-test values as a permanent solution.** First calibrate independent shoe-to-floor and clothing-to-seat material interfaces, their tangential stiffness and permitted slip, and verify the geometric contact patches, normals, and support-force distribution. Only then re-evaluate relaxed equilibrium and muscle recruitment. Pair the same controller with material-credible low, nominal and high friction; vary perturbation and body/seat geometry; check actual *sliding*, contact hysteresis, commanded muscle work, and long-horizon 40–60-second settling. The native solver can exhibit microslip even with Coulomb friction, and a visual appearance of sliding is not proof that friction is zero.

**Status: physics diagnostic only. Frozen R574/R582 preserved. No GitHub Actions used.**
