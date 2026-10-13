# BioRig / LUCID semantic atlas — V006 full-source call and direct-state candidate graph

This checkpoint makes the earlier line-indexed 70,823-line atlas meaningfully navigable at the *function-call interface* layer. It is a static code-evidence product, not a claim to have executed every path or semantically understood every physics equation.

**Verified new coverage:** 45,243 / 45,243 indexed Python call-site rows; 6,217 single internal static-binding candidates; 1,995 unique directed file-edge categories; 4,774 candidate callee records linked to source-declared function-body reads, direct writes, return and throw syntax. All 45,243 unresolved and resolved call sites remain in the complete lossless catalog.

The complete V005 ZIP is embedded byte-for-byte; V005 embeds V004, which embeds V003. This preserves the historical R575–R590 source archive identities, 28 core runtime-module causal contracts, original R574 lineage, 2,792 archived file hashes and the full 2792² file relationship matrix.

## Where to start

- `SOURCE_WIDE_CALL_AND_STATE_EFFECT_SEMANTICS.md`: handwritten explanation of what is known, what isn't, the source-to-runtime gap, actual controller ownership and the honest status of a goal→movement chain.
- `MODULE_CALL_BINDING_COVERAGE.md`: high-volume source modules ranked by call-site quantity and unresolved binding category.
- `SOURCE_WIDE_CALLSITE_BINDINGS.jsonl.gz`: *exactly one record for each of the 45,243 indexed source call sites*; includes source ID, line, expression, classification, binding candidates or explicit uncertainty.
- `SOURCE_WIDE_INTERNAL_CANDIDATE_EDGES.csv.gz`: 1,995 directionally pinned file-edge groups, explicitly marked static candidates.
- `DIRECT_CALLEE_EFFECTS.jsonl.gz`: a distinct row for each callsite with matched candidate callee's **direct** syntax reads/writes, returns and raises; qualified state field writes distinguished from local variables.
- `CALL_RESOLUTION_AUDIT_SUMMARY.json`, `DIRECT_EFFECT_AUDIT_SUMMARY.json`: full metrics, categories, hashes, samples.
- `build_source_wide_calls.py`, `build_direct_callee_effects.py`, `write_v006_semantics.py`, `verify_v006.py`: independent read-only regeneration and integrity checks.
- `VERIFICATION_RESULT.json`: V006 completeness and fidelity check output.

## Preservation

This V006 checkpoint does not modify any executable BioRig module. It does not change the original seat, SKIN78 mesh, actuator gains, R574 model, recent R590 baseline or controller wiring. No GitHub Actions. V003/V004/V005 archives are retained unmodified and are hashed and CRC checked. The GitHub branch is for documentation only.

## Semantic limits

Static candidate != observed runtime call; token `ctrl` != native `data.ctrl`; file import != active motor-control pipeline; identical filename != identical behavior or Git lineage. The authoritative unresolved category is **unknown**, never **independent**.

## Reproduction

Restore the original V003 directory into `/mnt/data/BioRig_SEMANTIC_ATLAS_001` and V005 ZIP into `/mnt/data`, then in this directory run:

```
python build_source_wide_calls.py
python build_direct_callee_effects.py
python write_v006_semantics.py
python verify_v006.py
```

These scripts do not import the BioRig physics runtime or execute a simulation. Their dependencies are Python standard library modules only.
