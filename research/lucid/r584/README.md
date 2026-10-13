# R584 — physical contact-creep correction (MuJoCo no-slip solver)

**Development branch:** `sev-32/BioRig:research/lucid-r575-goal-intent`. **No GitHub Actions.** R574 goal-conditioned controller and R582 signed-wrench motor controller remain unmodified.

The user's rendered-motion review found an unmistakable grip problem: seat and foot contacts were visibly sliding. Earlier controller updates repeatedly compensated for this with more muscle activation without addressing the contact error. R583 confirmed measured sliding. R584 fixes the **contact-solver configuration first**, rather than arguing that nonzero material friction makes slipping acceptable.

## Engineering change

Native MuJoCo 3.15 has an optional no-slip solver pass. In the frozen plant, `model.opt.noslip_iterations == 0`. On an **independently cloned model**, R584 sets `noslip_iterations=6` and `noslip_tolerance=1e-6`. That is the only physics change in the primary A/B test. The actual seat and ground sliding-friction coefficients stay **0.82 and 1.0**, respectively, with unchanged contact stiffness, surfaces, collision geometry, body masses, initial states, muscles and control policy. No root locking, scene fakery, additional forces or muscle strengthening.

Use `r584_solver_config.py` to apply the independent physical fundamental. `r584_replay.py` replays the exact inherited R583 scene with identical warmup, control, contact-point slip instrumentation and the new solver option. It serializes the temporary test-hook injection, restoring the original even on error; it is a **research runner**, not a thread-safe production API.

## Native results

| Same frozen scene, 12 s | Original solver | No-slip 6 |
|---|---:|---:|
| Loaded seat-contact sliding | 1.218 mm/s | **0.003 mm/s** |
| Loaded foot-contact sliding | 4.866 mm/s | **0.044 mm/s** |
| Final lateral displacement | 27.718 mm | **15.822 mm** |
| Root tilt | 12.601° | 12.368° |
| Extra muscle excitation-seconds | 0.43053 | 0.40805 |
| Hazard | No | No |

On the already successful **pushed scene 04**, the original 12-s result was safe and settled at x=24.263 mm; no-slip 6 was **also safe and settled**, at x=14.304 mm. R574 still selects `R28`.

On undisturbed scene 00, a standalone **40-second no-slip 6** continuation completed without a hazard and passed the settling test at x=15.993 mm **with zero extra R582 corrective muscle excitation**. The inherited **low-level muscle stabilizer remains active**; this is not an unassisted or fully passive human-like pose. A separate 40-second run with the R582 additional controller also held near x=15.819 mm and maintained contact.

The attempt to extend to 60 seconds did not finish. A later combined test suite stalled when rerunning 40-second physics; therefore that longer result is not certified for repeatability. The independent four-test contract suite, including fresh native 12-second physical reproduction, passed **4/4**.

## Real animated visual proof

A **31-frame actual native MuJoCo EGL capture**, covering 0 to 12 seconds in 0.4-second increments, displays the unmodified versus corrected contact-solver physical runs side-by-side. These are renderer captures; no interpolation or image generation. Its SHA-256 is `4dafac0ae54029434e836a00bd27ee02a9b9b31a5af1a22342edcd7c9fe9a924`. The GIF is delivered in chat, not committed as source-code bloat.

The complete native physics runner used for the 31-frame render (`r584_contact_solver.py`), tests, corresponding numerical traces, and checksum receipt are included in the companion ZIP checkpoint. The Git branch retains the minimal physics change, reproducible 12-second native replay, contract tests and numerical audit.

## Reproduce without GitHub Actions

Restore the original R574 and R575 archives to repository-root `./runtime`, using `research/lucid/tools/bootstrap.py`. Requirements: Python 3.13, MuJoCo 3.15, NumPy, scikit-learn; EGL/Pillow only for rendering.

```sh
python research/lucid/r584/r584_replay.py --seconds 12 --iterations 0 --out r584_original.json
python research/lucid/r584/r584_replay.py --seconds 12 --iterations 6 --out r584_corrected.json

R584_NATIVE=1 python -m unittest discover \
  -s research/lucid/r584 -p 'test_r584_solver_config.py' -v
```

## Next acceptance gate

**Visual acceptance comes first.** The user is the authority on whether seat/foot movement looks physically right. Do not silently promote this setting until that review. After visual acceptance: run the full frozen fourteen-scene hazard/settling regression with isolated per-scene limits and 40–60-second continuations; check friction-cone compliance and joint torque/effort; evaluate low/high-grip materials rather than masking genuine physical slips. No GitHub Actions.
