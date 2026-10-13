# BioRig Semantic Atlas V008 — native controller provenance and physical state ownership

This is a source-verifiable, static semantic continuation of V007, V006, V005, V004 and V003. It adds **69 human-reviewed exact-line source witnesses** across **11 original/experimental modules**, **14 physical-state authority contracts**, **17 explicitly qualified directed inter-module links** and **21 regression/feature gates**. It **does not** claim to have achieved a complete human-level explanation of 70,823 archived code lines, exhaustive dynamic relationships, or execution coverage.

**Open the paper:** `CONTROL_AUTHORITY_AND_STATE_LIFECYCLE_PAPER.md`. The data are in `CONTROL_FLOW_LINE_WITNESSES.json`, `SOURCE_PINNED_MODULE_MANIFEST.json`, `STATE_FIELD_OWNERSHIP_CONTRACTS.csv`, `DIRECTED_RUNTIME_INTERFACE_EDGES.json`, and `FEATURE_INTERLOCK_AND_REGRESSION_GATES.csv`.

## Crucial source-proven relationship

- R590 continuous capture calls R589 native `run(...candidate=True)`, which invokes transient shoulder-muscle landing and neck control. It writes `data.ctrl` **base → arm → neck** before each MuJoCo step.
- R590 restart imports R589 but does not invoke its `ArmLanding`. It restores `qpos/qvel/act`, reconstructs neck allocator memory, and runs **base → neck** before each MuJoCo step.
- The separate R574 goal-veto controller and older full-body muscle controller are not called by the inspected R590 restart entrypoint. **This statement is limited to the inspected source path**, not a global assertion across all BioRig versions.

## Verification and epistemic boundary

Run `python verify_v008.py`: it re-opens each pinned source archive, checks SHA256, reparses the AST, verifies all literal witness lines, all witness references and Git semantic files, and confirms controller write order and the absent R590 arm-controller call *statically*. It **does not** run MuJoCo, replace the actual renderer, simulate a goal, or prove physical behavior. The native runtime is not bundled.

`build_v008.py` regenerates the ledger and paper, reading the pinned checkpoint archives under `/mnt/data`. `write_features.py` generates the 21-gate table. Source archives remain untouched. The previous archive V007 is preserved byte-for-byte in this checkpoint ZIP.

## Nonnegotiable continuation

Next: instrument actual native execution to connect **action → actuator ID owner → `ctrl` → `act` → moment/force → qpos/qvel/contact → SKIN78** at high temporal resolution, and bridge this causal trace with all previous versions' source-level architectural relationships. Required: channel overlap proof; muscle lag, state-warmstart consistency, and actual native visual comparison. No unverified capabilities should be marked as achieved.

No original executable BioRig code was changed. No GitHub Actions used. R574–R590 versions are preserved.
