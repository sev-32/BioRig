# LUCID R574 → R575 · BioRig research intake

**Branch:** `research/lucid-r575-goal-intent`
**Status:** Research only; no production promotion.

This is the source-only LUCID research lane. The original native free-root 84-muscle MuJoCo plant must be restored from the immutable user-supplied archive; this branch does not replace that system with an approximation.

Original R574 ZIP SHA-256: `21e0c354023badd40485840296e09034809ae4eb055fd926eff39ac0b8700701`.
R575 addendum ZIP SHA-256: `5377f998f1f05efc2de6ef1033ec2b87716703e8eb4e0d1e6d8f2e273ab6be0e`.

Previously established receipts: 21/21 R574 tests, 5/5 R575 evidence tests, and four completed native-physics 8-second latency branches. These are **historical results**, not branch CI. Full physics latency validation, 14-scene sweeps, 12-second delayed continuations and low-level sensory delay remain unproven.

## Offline recovery

Run:

```sh
python research/lucid/tools/bootstrap.py --r574 /path/LUCID_R574_GOAL_CONDITIONED_MUSCLE_INTENT_SELF_CONTAINED.zip --r575 /path/LUCID_R575_VERIFIED_TAKEOVER_LATENCY_ADDENDUM.zip --destination ./runtime
python -m unittest discover -s research/lucid/tests -v
python research/lucid/tools/audit_latency.py runtime/R575_SENSOR_LATENCY_PHYSICS/measured/*.json
```

With NumPy, scikit-learn and MuJoCo 3.15.0 installed, the recovered source can run `runtime/R574_INTENTION_AND_AVERSION/test_r574.py`, `runtime/R575_SENSOR_LATENCY_PHYSICS/test_r575_evidence.py`, and native physics rollouts through `runtime/R575_SENSOR_LATENCY_PHYSICS/r575_latency.py`. Native full scene sweeps can be computationally expensive.

## Strict semantic boundaries

- Goal selection: frozen `R574_INTENTION_AND_AVERSION/r574_intention.py`. Policy chooses inaction or bounded native muscle pulse R28 from observed sensors. No privileged future state.
- Native physics: inherited MuJoCo plant, conserved contact and actuator semantics; untouched by this branch.
- Observation latency: R575 high-level and pulse feedback delayed 0/20/40ms; low-level stabilizer remains instantaneous.
- Research audit: `tools/audit_latency.py` checks immutable traces, flags mismatched initial conditions, and refuses to infer missing 0ms comparisons.
- Archive provenance: `tools/bootstrap.py` checks ZIP digest, CRC, paths, and existing bytes without overwriting modified files.

Promotion requires physical performance against inaction, recovery AND settling, contact-load safety, out-of-distribution generalization, and delay-robustness. Do not count lack of induced hazards as a solved motor skill.
