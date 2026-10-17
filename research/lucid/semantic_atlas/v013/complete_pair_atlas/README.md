# BioRig Semantic Atlas V013 — Joint equilibrium, reciprocal muscle control and co-contraction

Research-documentation checkpoint continuing **V012**; contains **the exact unmodified V012 ZIP**. All earlier frozen sources and simulations remain unchanged.

The core V013 result is a direct source-backed map of the user's principle: achieving a new limb posture is a coupled **load-bearing, movement, deceleration and stabilization problem**, rather than single-agonist contraction. It recovers earlier reciprocal-reflex/tone research and shows where the current seated arm controller uses only two selected shoulder actuators per side instead of a whole-body, dynamically coupled solver.

Read `V013_RECIPROCAL_MUSCLE_COORDINATION_AND_ACTUATOR_CONTRACT.md` first. Reproduce with `build_v013.py` and `verify_v013.py` (requires NumPy and the named, SHA-pinned historical archives; does not modify source or execute a new MuJoCo rollout).

New verified artifacts: 9-module 1,636-line exact source/AST ledger, 72 function/class boundaries, 26 manually described code regions, 7,056 directed native muscle-pair relationships, and 188 elbow-pose hypothetically torque-balanced coactivation rows. The 94 recorded poses are real V010 MuJoCo geometry; coactivation experiment is a *static mechanical counterfactual*, not a forward simulation. See `V013_RECEIPT.json` and `V013_VERIFY_RESULT.json`.

Full prior V003–V012 atlas is nested unchanged. No rollback, no executable BioRig code changes, no GitHub Actions, and no claims of new SKIN78 animation.
