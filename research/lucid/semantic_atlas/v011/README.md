# BioRig Semantic Atlas V011 — conditional causal physics

This is an **audited source-to-native-physics relationship expansion** to the already verified V010 mechanical geometry atlas. It is not an accepted character-controller release.

**Read first:** `ACTIVATION_TO_CONTACT_CAUSAL_PAPER.md`.

**Measurements:** `NATIVE_84_MUSCLE_CAUSAL_TIME_TRACES.npz`, `ALL_84x102_NATIVE_CONTROL_TO_DOF_TIME_RESPONSE.npz`, `PULSED_ACTUATOR_NATIVE_DIFFERENTIAL_EFFECTS.csv`, `ALL_84_CHANNEL_NATIVE_DYNAMIC_EFFECTS.csv`, `V010_V011_8568_DIRECT_VS_DYNAMICAL_COUPLING.csv.gz`.

**Proofs and locks:** `V011_NATIVE_DYNAMIC_VERIFICATION.json`, `V011_FULL84_RESPONSE_RECEIPT.json`, `V010_V011_MECHANICAL_DYNAMIC_BRIDGE_RECEIPT.json`, `V011_INDEPENDENT_VERIFICATION.json`.

**Reproduction:** Restore the SHA-pinned original R574 source+assets to `runtime/LUCID_R552_WORKSPACE/` and local native MuJoCo 3.15.0 to `.pydeps` (not redistributed). Run `build_v011.py`, `scan_all84_v011.py`, `build_mechanical_dynamic_bridge.py`, and `verify_v011.py`, in order. Their input archives are pinned as V011 receipt hashes. All generated source and results are this `V011/` folder. V010 is nested *unchanged* in the checkpoint ZIP.

**Scope:** 84 independent native actuator perturbations (plus baseline) at three sampled times, and detailed four-shoulder-muscle dynamics. All from a saved R590 state, with feedback controllers explicitly turned OFF. The 84×102 matrices are conditional motion responses, **not** muscle moment-arm geometry, general-purpose intention, autonomous reaching, or steady-state balance.

No historical executable file edited. No GitHub Actions.
