# BioRig Semantic Atlas V009 — complete 84-muscle command-authority topology

**Status:** new exact-source derivation; **not** a claim that the whole program's runtime has been semantically resolved. R574 and R585–R590 remain untouched.

## 1. What the original physical model actually exposes

`muscles.py:85–276` declares **43 `MuscleDef` expressions**: 41 per-side definitions instantiated once each for left and right (82), plus two central trunk muscles, for **84 distinct muscle IDs**. The physical MJCF builder in `physbody.py:480–537` iterates `ms.defs`, names a tendon `t_<muscleID>` and an actuator `m_<muscleID>`, and emits bounded native muscle excitation with activation/deactivation time constants **0.010 / 0.040 seconds**. These are engineering muscle proxies with uncalibrated anatomy/strength limits, not literal subject anatomy.

We generated **all 84 channels** directly from AST nodes and checked uniqueness, side cardinalities and controller membership without loading or modifying the plant. See `ALL_84_MUSCLE_CHANNELS_AND_WINNING_COMMAND_WRITERS.csv`; every channel has a source line and version-pinned source hash.

## 2. R589 controller authority on all 84 muscles

| Last command writer before the native physics step | Actuators | Source | Cadence |
| --- | ---: | --- | --- |
| Seated-posture `controller_excitation` baseline | **70** | R589:133 | 2 ms |
| R589 `ArmLanding` transient arm channel override | **4** | R589:137 | 10 ms cached command |
| R586/R585 neck allocation override | **10** | R589:138 | 10 ms cached command |
| **Total** | **84** | R589:142 physics step | 2 ms |

**Important improvement over V008:** the 4 arm channel *names* (`m_left_deltoid_middle`, `m_left_pectoralis_major`, and right equivalents) are proven **disjoint** from the 10 neck names (`neck_extensors`, `suboccipitals`, `sternocleidomastoid`, `longus_colli`, `upper_trapezius`, bilateral). Both sets are known members of the original 84-muscle catalog. For these named channels, R589's arm and neck overrides **cannot overwrite the same actuator** if the MuJoCo actuator IDs are resolved by exact name as implemented. No numeric actuator-ID list has yet been independently executed and checked.

Also important: `ArmLanding.update` returns a full copy of the *base vector* with one selected channel per side modified; then the R589 loop overwrites **both** selected arm-family channels per side from that cached copy. It refreshes this copy every 5 × 2 ms = 10 ms, even while the baseline posture controller recomputes at 2 ms intervals. This creates **up to 8 ms of stale-baseline control for all four selected arm channels** between refreshes. The single chosen channel receives a nonnegative added excitation rather than a fully signed, constrained actuator solution. Source evidence is clear; whether this materially causes measured contact chatter requires an instrumented physical replay, not a source-only accusation.

## 3. R590 restart controller authority

| Last command writer | Actuators | Source |
| --- | ---: | --- |
| Seated posture controller | **74** | R590:83 |
| R586/R585 neck allocator | **10** | R590:83 |
| R589 arm landing controller | **0** | **not invoked by `continue_native`** |

R590 restart loads `qpos`, `qvel` and `act`; it does not restore all optimizer state or run R589's arm landing controller. Previous R589 muscle guidance was used during the **continuous capture** that generated the settled state. The restart then uses a **different set of command writers**. Any claim that R590 tests active arm landing would conflate these two paths.

## 4. Typed physical contracts and model limitations

- World coordinate system: gravity `[0,-9.81,0]`, making Y vertical and X/Z the horizontal plane. The torso head-relative correction in `posture_stabilization_r51.py` explicitly uses X/Z and zeros the 6 free-root torque channels.
- Native `data.ctrl` is a muscle-excitation request. `data.act` is activation state, `data.actuator_force` is realized actuator force, `data.qfrc_applied` external generalized force and `data.xfrc_applied` externally applied body wrench. One is not interchangeable with another.
- R589 calculates an instantaneous torque-per-excitation estimate `moment[idx,dof] * muscleGain`, and only adds bounded **positive** excitation to the selected muscle. This does not guarantee desired signed torque when the baseline has already recruited the antagonist, nor does it independently validate delivered delayed force.
- R590 initializes a neck optimizer memory by copying the actual activation into `last` and `last_eff`, an **approximate** reconstruction. It explicitly requires `mj_forward` to rebuild derived mechanical quantities after state assignment. It does not prove byte-exact solver warmstart equivalence.

The `MANUALLY_REVIEWED_PHYSICS_AND_AUTHORITY_CONTRACTS.json` file pins 14 physical and algorithmic contracts to source SHA, exact line, actual literal code and unproven limits.

## 5. What the relationship matrix really establishes

`R589_84x84_CONTROLLER_WRITER_EQUIVALENCE.txt` is an 84 × 84 ordered binary matrix: `1` iff two channels share the same **last commanding subsystem under R589 candidate mode**. It is an exhaustive channel-by-channel matrix **for that specific, exactly defined relation**. It is **not** a neural-connectivity matrix, full moment-arm coupling, unknown muscle-muscle interactions, or evidence of human-equivalent biology. The earlier 2,792² file-pair matrix remains separately preserved in V003; unknown relationships must stay unknown.

## 6. Next evidence boundaries

1. Execute actual native model and record numeric `mj_name2id` for all 84 names, actual 4/10 channel masks, post-write `data.ctrl`, and delayed `data.act` vs actuator force across a controlled replay.
2. Instrument the 2 ms / 10 ms arm loop to quantify whether stale baseline assignment causes arm contact chatter; no dynamics outcome is inferred here.
3. Join original whole-body neural solver, planner, and high-level goal paths with explicit caller/callee traces, while preserving existing modern controller milestones.
4. Expand exhaustive per-function semantic proofs across the 65k+ archive lines not yet manually interpreted.

**No physics code changed. No rollback. No generated images. No GitHub Actions.**
