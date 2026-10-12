# R577: sustained, proprioceptive lateral support — research checkpoint

**Status:** native physical development result; source pushed to `research/lucid-r575-goal-intent`. Frozen R574/R575 source, training records, held-out evaluation lock and lower-level MuJoCo stabilizer remain unmodified. **Not approved for promotion.**

## Mechanism

The previously tested R576 support controller emits up to four time-bounded R562 muscle pulses and fails again beyond 12 s. R577 instead overlays *tonic muscle excitation*, bounded by the inherited maximum `0.04`, using a sensed lateral-position threshold. From t≥1.4 s, when the measured root displacement exceeds 8 mm, the controller increases lateral support to `0.025` additional muscle excitation at a maximum of `0.003` per 40-ms update. It selects the opposing muscle group from the sign of the measured displacement, ramps down when contact or tilt safety gates fire (15 N seat-arm contact or 35° tilt), and retains the frozen R574 `none` or `R28` early selection.

There is **no positional teleportation, root stabilization force, external harness direction in the online controller, or rerouting of the native plant**. This is a simple bench candidate tuned on *scene 00 after the failure was discovered*. Sustained activity consumes nonzero muscle work and does not prove passive or long-term stability.

## Verified native MuJoCo results

Scene 00 (seat half-width 0.131 m, friction 0.82, zero external push, choice `none`):
- R574 frozen baseline: exceeded the 45° hazard threshold at about 11.32 s; R576 four-pulse variant avoided a hazard through 12 s but fell before 20 s.
- R577 continuous `0.025` excitation: **40 s complete, no measured hazard**, peak tilt 14.9314°, final tilt 12.3896°, final root lateral position 0.031844 m, speed −0.0001514 m/s; seat force 441.8 N, foot force 193.1 N, maximum arm-seat load 0.25 N.
- R577 `settledAtEnd = false` at 40 s because the last lateral position is beyond the 0.030 m legacy threshold. The maximum earlier contiguous settled duration was ~22.04 s. This is **long-horizon suppression of the fall, not verified equilibrium**.

12-second scene checks: scenes 01 (no hazard, settled), 02 (no hazard, not settled), 04 (no hazard, settled) and 07 (no hazard, settled). Scene 03 reached an existing arm-contact hazard by 1.02 s *before* R577 was allowed to turn on; scenes 05 and 06 also reached previously known R574-failing hazard conditions by 1.58 and 1.82 s. These failed runs were stopped at the first hazard, so they are **not complete 12-second continuations**. Scene 08 did not finish within the allotted execution window, and scenes 09–13 were not evaluated in this checkpoint. **Do not infer a full 14-scene safety regression pass.**

`R577_DEVELOPMENT_RECEIPT.json` gives numeric measurements and source/render SHA-256 fingerprints. `r577_render.py` reproduces true native EGL/MuJoCo captures at 0, 12, 20, 30 and 40 seconds (image delivered separately, not stored in Git).

## Reproduce

From the repository root, restore the original immutable R574/R575 archives using `research/lucid/tools/bootstrap.py`, with destination `./runtime`. Dependencies: Python 3.13, MuJoCo 3.15, NumPy, scikit-learn, PIL for rendering, and EGL/OpenGL.

```bash
python research/lucid/tools/bootstrap.py \
  --r574 /path/LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip \
  --r575 /path/LUCID_R575_VERIFIED_TAKEOVER_LATENCY_ADDENDUM.zip \
  --destination ./runtime

python research/lucid/r577/r577_tonic_support.py \
  --indices 0 --seconds 40 --control tonic \
  --out ./R577_SCENE00_40S.json

python -m unittest discover -s research/lucid/r577 -p 'test_r577.py' -v
R577_RUN_NATIVE=1 python -m unittest discover -s research/lucid/r577 -p 'test_r577.py' -v
MUJOCO_GL=egl python research/lucid/r577/r577_render.py
```

The six R577 native/contract tests passed locally, including the optional 40-second real-physics replay. The short regression pass takes roughly 7 seconds and the 40-second replay around 30 seconds in the tested CPU runtime. Standard tests skip the expensive replay unless the environment variable is set.

## Next stop/go gates

1. Complete the remaining wider-seat scenes with independent per-case timeouts and diagnose unresponsive scene 08. Extend all cases to 20–40 s only where safe. Compare equal cloned starts with no overlay and R576.
2. Replace the present **bang-bang tonic bias** with a measured support-relative COM and torso angular-velocity controller. Explicitly track and penalize sustained excitation, including oscillations and force-sharing between muscle groups. Evaluate at 40–60 s without false settling.
3. Preserve zero new action-induced hazards relative to unmodified R574 frozen starts, retain earlier rescue successes, and verify guard behavior under contact spikes and sign crossings.
4. Test full sensorimotor latency and perturbation-domain variation; R575 delayed only high-level observations, not the inherited reflex/stabilizer. No claims about biological equivalence.

This is a research branch, not the production simulator. The canonical R574 evaluation lock remains the nonmodified reference.
