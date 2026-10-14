# V014 parameter / controller feature-gate audit

This builds on the V013 whole-body-controller source audit. All 48 NeuroParams fields are exhaustively inventoried from the frozen original AST, and 95 same-attribute-name occurrences across 558 Python modules are indexed with conservative object-identity confidence.

Run `python build_v014.py` then `python verify_v014.py`. Source archive SHA-256 is pinned in `V014_MACHINE_VERIFICATION_RECEIPT.json`. No original source files or native simulation changed.

Read `NEURO_PARAMETER_AUTHORITY_AND_FEATURE_GATES.md` before any controller integration.
