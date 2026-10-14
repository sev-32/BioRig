# LUCID / BioRig Semantic Atlas V013 — whole-body controller integration truth

This is a **source-only semantic-reconstruction checkpoint**. It extends V012 without editing any original controller, MuJoCo plant, renderer or frozen version.

### New coverage

- 21 source-pinned original modules (R574 embedded runtime and original R590 restart).
- 70 manually authored claims verified against exact original source lines and SHA-256 hashes.
- 179 AST-derived class/function definitions, fully enumerated for this 21-module selection.
- 94 source occurrences across all original Python files for ten named controller/planner/intent symbols, with conservative static-syntax classification.
- Native whole-body control task-row inventory, including optional priority, COM, swing and fatigue paths.
- 15 explicit compatibility contracts distinguishing integrated, conditionally invoked, disconnected and research-only subsystems.
- Original full-body optimizer's **actual default settings**, independently confirmed from AST.

### Primary findings

1. `WholeBodyMuscleController` is actually called and drives MuJoCo in the **standing** laboratory; it is **not** called by the inspected R590 seated restart.
2. Its optimized contact set is foot-ground only. Seat and arm-rest support cannot be assumed from it.
3. Default `relaxed_arms=True`, `solver='weighted'` and zero weights for capture-point, foot-flat and angular-momentum options mean the most ambitious optimization claims do **not** describe its default behavior.
4. Earlier R546–R550 joint-intent/learned-sensory research is a separate exercised research lineage, not an inherited R590 controller.
5. A proper goal-to-native-muscle execution path requires explicit authority, units/frame conversion, support semantics, memory/state continuity and forward-MuJoCo/actual-SKIN78 acceptance gates.

**Start here:** [WHOLE_BODY_CONTROLLER_EXECUTION_AND_INTEGRATION_PAPER.md](./WHOLE_BODY_CONTROLLER_EXECUTION_AND_INTEGRATION_PAPER.md)

**Verification:** With the untouched frozen R574 and R590 ZIPs in the parent directory, run `python build_v013.py && python verify_v013.py`. Reproduction requires Python standard library only, not MuJoCo. `python package_v013.py` creates the nested V012-preserving ZIP; no image/model duplication.

**Truth boundary:** this is a reproducible source audit, not a newly executed physical dynamics result or proof of general-purpose goal-driven movement. All unexamined dynamic dispatch and undiscovered integrations remain unknown. No GitHub Actions.
