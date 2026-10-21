# BioRig R29 — spine-last support allocation (experimental)

2026-10-21 | NON-PROMOTED | NO NATIVE BIORIG RE-RUN

Source parent: the user-supplied LUCID_BioRig_R25_CODE_AND_EVIDENCE_20261021.zip, file LUCID_BioRig_Development/35_R25_CONTACT_FEASIBILITY/candidate/46_rider_wbc_r25.js. SHA-256 4f0c05f7da87831d6fee3293de84b75437fe93499d10ceda2a8a830ad30f63a5.

Full local experiment: BIORIG_R29_SPINE_LAST_CANDIDATE_AND_VISUAL_EVIDENCE_20261021.zip. Contains the complete 145 KB self-contained generated candidate, generator, 14 passing JS/Python policy and reduced-order tests, synthetic 3-second simulation animation, real R25 archived Skin78 visual reference, engineering report and SHA-256 receipt.

The standalone GitHub policy here is not the integrated runtime. The full generated controller candidate remains in the packaged artifact, not in this GitHub branch; please do not mistake this GitHub branch for the full newest R25/R29 runtime.

Candidate is opt-in OFF by default. For single-stance walking it proposes: cap overly strong world-pelvis orientation task <=0.6, apply only low-authority loaded-foot-gated relative lumbar/thoracic lateral S-mode damping beyond a five-degree free band; preserve intentional axial turning; use the existing muscle-contact QP only, without external joint torque or pose override.

Reduced-order lateral inverted-pendulum experiment: spine-only local stabilization reduced side-bend while no-step balance still failed at 1.478 seconds. With time-appropriate corrective stepping the model survived 3 seconds with lower lumbar movement. These are demonstrative synthetic physical runs, not full native BioRig results.

Native run blocked: extracted Moto source lacks assets/character/lucid_muscles_r1_5.json; archived source assets are incomplete. First recover exact assets and rerun unmodified baseline. Then test R29 270/540/1080 Hz, left/right steps, multi-step gait, push/turn and measured muscle/contact feasibility. Visual approval pending; do not promote.

Biomechanical references: Bruijn & van Dieen (2018), DOI 10.1098/rsif.2017.0816; MacKinnon & Winter (1993); PMID 38070294; PMID 29395226.
