# BioRig semantic atlas V013 — balanced muscle allocation and impedance

**Central document:** `MUSCLE_BALANCE_IMPEDANCE_AND_GOAL_INTENT_PAPER.md`

Inputs: immutable V010 84×102×94 native moment-arm data, V011 native one-muscle dynamical perturbations, original R574 neuromuscular controller, and R579/R586/R589 research sources.

The new **84×84** ledger includes each ordered muscle pair's pose-and-joint signed leverage, separating opposition, assistance, mixed behavior and no shared active joint within the tested states. The joint signs do not by themselves measure active joint stiffness, relaxation timing or coactivation ability.

`build_v013.py` independently verifies precise archived source lines and generates:

- `ALL_84x84_POSE_CONDITIONAL_JOINT_SIGN_RELATIONSHIPS.csv`
- `ELBOW_OPPOSING_MUSCLE_FORCE_BALANCE_94_NATIVE_POSES.csv`
- `V011_ELBOW_ISOLATED_PULSE_CAUSAL_READOUTS.csv`
- `V013_SOURCE_AND_MECHANICAL_RELATIONSHIP_RECEIPT.json`

`verify_v013.py` checks every output row against the pinned matrices with an independent implementation.

The ZIP preserves unchanged V012 as the full earlier atlas. It contains **no newly claimed simulation success** and does not replace R574–R590. No GitHub Actions.
