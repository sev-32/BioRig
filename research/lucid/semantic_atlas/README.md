# BioRig Semantic Atlas — persistence and coverage

This is the GitHub checkpoint for the source semantic reconstruction. Do not merge or overwrite prior versions. No GitHub Actions.

The authoritative working inputs are the SHA-pinned full R574 archive and all available R575–R590 checkpoint ZIPs. The complete local static-source ledger is available as a separate checksum-verifiable package, including:

- Every archived file by ZIP/path, CRC32 and SHA256;
- All literal readable code lines with AST scope and first-pass semantic classification;
- Each function/class declaration and docstring;
- Static imports, call sites and explicit cross-file/duplicate-content edges;
- JSON key-path schemas;
- A manually grounded semantic ontology with typed units, frames and authority boundaries;
- Version and known-regression tables, with missing/equivocal relationships marked **unknown**.

**No number of syntax-indexed lines can establish 100% program behavior.** The source-index coverage is full for pinned inputs but human-level and runtime semantic validation is underway, not complete. A relationship not inferred by static analysis is not proven nonexistent.

Reference remote tree: [GITHUB_BRANCH_TREE_INVENTORY.json](./GITHUB_BRANCH_TREE_INVENTORY.json). Core architecture: [SEMANTIC_SYSTEM_SPECIFICATION.md](./SEMANTIC_SYSTEM_SPECIFICATION.md). This directory is documentation only; it must not change any R574–R590 executable module.

## Freeze rules

Do not modify frozen sources or silently consolidate variants. Diff by content SHA and declared units, keep every original identity, and require native physics plus actual Skin78 renderer proof before promoting behavioral changes. No GitHub Actions.