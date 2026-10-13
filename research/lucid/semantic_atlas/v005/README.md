# LUCID/BioRig semantic atlas — V005 checkpoint: R575–R590 complete archive identity

**Documented scope:** R575–R590, including source-verified code/version distinctions, version-specific physics/control/observer meaning, exact source hashes and reuse/conflict map; the missing local R583 source is separately pinned to real GitHub blobs. This does **not** mean the project has been semantically understood to 100% or that any untested code was executed in this audit.

The checkpoint embeds the prior **entire byte-identical V004 archive** (which itself embeds V003). All 70,823 globally indexed source lines from V003 and the detailed 28-module runtime/source analysis from V004 remain intact.

Primary human-readable documents:

- `HISTORICAL_INTERVENTION_AND_ARCHITECTURAL_CONTINUITY.md` — manual analysis of R575–R590 scientific content and its relation to native physique, sensing, control, rendering, and acceptance.
- `VERSION_BY_VERSION_SOURCE_ATLAS.md` — every 96 Python file instances present in available checkpoint archives, their container, SHA-256, first-pass declaration and top-level symbols.
- `VERSION_PINNED_SOURCE_DECLARATIONS.json` — exact machine archive/member/code mapping.
- `VERSION_SNAPSHOT_REUSE_AND_HASH_CONFLICTS.json` — exact content reuse vs drift under identical basenames.
- `REMOTE_ONLY_GITHUB_EVIDENCE.json` — two independently fetched and Git-SHA pinned R583 source/docs blobs, marked remote-only.
- `build_version_semantics.py` and `verify_v005.py` — read-only source regeneration and integrity test.

`verify_v005.py` checks every archived source member hash, exact line count, AST parse, shared-name SHA variants and nested V004 checkpoint integrity. All executable LUCID source remains untouched; no MuJoCo physical simulation, native render or GitHub Actions were run in this documentation phase.

**Critical correction:** R575 delays BOTH the high-level action selection's observations and the additional pulse's 40ms sensor updates. It does **not** delay the inherited physical postural stabilizer, which retains privileged current mechanics. The fine distinction is important to any claim about neural/sensory delay or regression.

**Next:** combine these proven historical code identities with Git commit ancestry and native direct-state/actuator instrumentation, then expand the handwritten semantics from identified high-risk modules to all remaining 65,000+ archived source lines. Do not interpret the numeric filename R590 as a complete pipeline or discard earlier capability implementations.
