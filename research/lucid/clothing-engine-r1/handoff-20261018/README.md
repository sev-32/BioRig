# LUCID Clothing Engine R1 — verified compact handoff (2026-10-18)

This folder registers the 2026-10-18 transfer-optimized Clothing Engine R1 snapshot against the existing BioRig research history. **This is a separate archive provenance lane, not a promotion or merger into the biomechanical controller.**

## Current branch and ancestry

- Repository: `sev-32/BioRig`
- Branch: `research/lucid-clothing-r1-clean-handoff-20261018`
- Created from: `research/lucid-r575-goal-intent` (retains existing LUCID/BioRig research history, does not modify that branch).
- Canonical transfer archive: `LUCID_CLOTHING_ENGINE_CLEAN_HANDOFF_20261018.zip` (24,913,142 bytes; SHA-256 in `PACKAGE_RECEIPT.json`).
- Previous archive: `LUCID_CLOTHING_ENGINE_FINAL_HANDOFF_20260927.zip` (73,952,564 bytes).
- **Important:** the 24.9 MB ZIP is distributed separately, not stored as a Git blob on this branch. Do not mistake the Git metadata for an independently runnable checkout.

## Import

1. Obtain the separately supplied clean ZIP exactly matching the recorded SHA-256.
2. From this directory run: `python3 verify_and_import.py /path/to/LUCID_CLOTHING_ENGINE_CLEAN_HANDOFF_20261018.zip --extract /tmp/lucid-clothing-r1`.
3. Inspect extracted `START_HERE.md`, `CURRENT_STATE.md`, `SOURCE_PERSISTENCE_NOTE.md`, and `docs/FINAL_PROMOTION_MATRIX.md`.
4. The last complete source is `project/labs/human-engine/clothing-engine/r1/src/`, with qualification tools in `.../r1/qualification/`. The upstream dependency is `project/labs/human-engine/clothing-safe/m26/source/`.
5. Run the extraction's `VERIFY_PACKAGE.py`, then JS syntax tests, then reproduce selected qualification clips. Do not conflate packaging integrity with cloth-physics acceptance.

## Why 24.9 MB

The archive removes duplicated raw qualification F32/U32 buffers and redundant captures, retaining the complete *last persisted* Clothing Engine R1 source, 103 JSON qualification reports, M26 source and assets, 11 selected original renderer contact sheets, saved offline recenter evidence, a per-file SHA-256 manifest and a file removal ledger. No solver code was rewritten during repackaging.

## Hard unresolved gate

Deep knee kneel/crawl cloth tube enclosure remains unresolved. Before implementing or promoting the proposed collective phase/manifold controller, compare the saved worst kneel state's dense tube oracle (a) with rest-axial triangle prefilter and (b) allowing all live denim triangles, preserving left/right garment identity. The prefilter may misreport deeply migrated cloth; this remains a hypothesis needing measurement.

## Truth boundaries

- Some late manifold research is evidence-only: not every late experiment exists as executable source in the recovered checkpoint.
- Single-frame harness execution produced reports but did *not* pass all physics gates; transfer verification is not a physics certification.
- The rendered PNGs in the package are preserved original engine captures, not new or reviewed renders.
- This branch is a provenance handoff, not a visual approval or a production promotion.
