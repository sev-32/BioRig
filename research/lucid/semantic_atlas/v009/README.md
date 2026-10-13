# BioRig Semantic Atlas V009

Full named 84-muscle actuator registry derived from original R574 source, exact R589/R590 per-channel commanding authority, 84×84 writer-equivalence matrix, physics/state contracts, source hashes and reproducible scripts.

**Scope limitation:** static named-channel proofs, no native MuJoCo execution. The upstream checkpoint V008 is embedded byte-for-byte in the V009 transfer ZIP; V008 embeds V007 and the preceding versions. No BioRig simulation source changed. No rollback. No GitHub Actions.

Regenerate with `python build_v009.py`; verify with `python verify_v009.py`. Read `MUSCLE_AUTHORITY_AND_CAUSAL_MODEL_PAPER.md` first.
