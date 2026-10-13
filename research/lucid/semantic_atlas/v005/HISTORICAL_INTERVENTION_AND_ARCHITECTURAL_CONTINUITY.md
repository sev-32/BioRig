# BioRig / LUCID — historical interventions and semantic continuity

**Direct source examination of R575–R590.** Entries below distinguish source-proven mathematical interventions from experiments reported in prose, code retained but not invoked, and unknown runtime performance. Every local Python source used by this version catalog has its original ZIP name, member path, SHA-256 and AST definition line spans in `VERSION_PINNED_SOURCE_DECLARATIONS.json`. The source-only GitHub R583 evidence is SHA-1 blob pinned separately. The older R574 archive is frozen and separately preserved in V003.

## What the experimental research actually changed

### R575 — two delayed channels; one important undelayed lower-level controller

`native/r575_latency.py` in `BioRig_LUCID_R575_GITHUB_BRANCH_CHECKPOINT_2026-10-12.zip` tests 0, 20 and 40 milliseconds sensor delay. The action decision at physical 60 ms uses a prior 20-ms-grid observation from 60/40/20 ms (`:25–29,35–43,65–69`). The added timed-pulse safety controller also updates every 40 ms using delayed observations (`:70–75`). However the inherited native muscle stabilizer in `phys.plant.step_perturbed` still uses immediate privileged simulator state (`:72–78`). **Therefore this is not just high-level delay, but neither is it full neural latency.** Earlier descriptions that called it high-level-only are incomplete. The source itself makes the boundary explicit (`:4–11`). No original physics/body/collision model was altered by this audit.

### R576 — bounded post-pulse guard; not a new general motor primitive

`R576/r576_longhorizon.py` declares a separate guard for late supported recovery; `make_guard` spans lines 31–36 and `branch` 39–91. It extends the experiment's horizon and applies a bounded muscle correction after early frozen action selection. Evidence labels are still seated root/contact hazards, not a full-body anatomical validator. Scope: one stabilization research treatment, not task-level locomotion or reach.

### R577 — sustained proprioceptive muscle recruitment

`research/lucid/r577/r577_tonic_support.py` defines an additional late/tonic recruitment candidate; the physical rollout is `:67–131`, using cloned scene warmups and online current observations; the extra command includes contact/tilt hard-stop conditions (`:46–62`). This directly targets late drift that a brief original pulse did not correct. It is not necessarily a universal solution: it is still referenced to the original seated posture, and success can be limited by contact and validity gates.

### R578 — separate support *observer* and adaptive feedback *controller*

`r578_support.py:21–44` computes a world-X centre-of-pressure proxy by weighting contact X locations with effective normal-support load, then divides by total load. It is a diagnostic observer, not an applied muscle force; its output is undefined without sufficient support. `r578_feedback.py` defines an independent online feedback controller (`run:74–133`) that combines measured body drift and COM-to-support error. Code has a position gate (0.008 metres) and a slew-per-40ms limit of 0.003 (`:20–25`), and contains contact/tilt abort checks (`:40–55`). These are two different mathematical concerns: **measurement** and **actuation**. Neither can be replaced by a prettier stability plot.

### R579 — muscle synergy distribution and independent offline authority probe

The `r579_controller.py`, `r579_synergy.py`, and `r579_identify.py` source files separate actual run-time candidate recruitment, muscle-weight redistribution, and one-factor cloned-state probe. `r579_identify.py` explicitly says offline cloned probes cannot feed the online policy. The main intervention is **distribution of a bounded extra muscle action across identified actuator channels**, not a new sensory observation or a general whole-body optimization. The `r579_controller.py` entry point is `rollout:47–76`. New source identity does not establish the target weights were transferable to new postures.

### R580 — adaptive hip/trunk recruitment

`research/lucid/r580/r580_adaptive_synergy.py` builds a state-responsive hip and trunk recruitment rule; `rollout:108–165`. It retains the frozen 84-muscle plant, baseline stabilizer and early intention selector, while attempting to alter later online muscle recruitment. Its code keeps an arm-contact abort gate and reports max arm/other impacts (`:81,116–134`). Its adaptive mechanism remains a bounded feedback overlay, not arbitrary goal-conditioned motion.

### R581 — contact geometry and moment-arm authority

Two distinct research themes appear in the same checkpoint: `r581_support.py` measures pressure/support geometry **using only vertical normal reaction components** and explicitly states a 1D support interval is not a stability proof; `r581_moment_probe.py` measures native muscle moment authority from cloned supported physical states. The controller `r581_controller.py` adds contact-relative hip/oblique correction (`rollout:85–141`), including COM-vs-pressure alignment tests (`:55–69`). Contact measurement, mechanical actuator authority and actual muscle policy must be treated as separate modules with independent units and validation.

### R582 — signed world-space contact wrench, not merely normal-pressure support

`r582_wrench.py` exposes `world_wrench:38–48` and `sense_wrench:51–90`. The source explicitly handles MuJoCo contact-frame sign conventions and the body-on-geom1 versus body-on-geom2 distinction. Its output can include tangential friction contributions to support, and moments around physical reference points. The R581 vertical-normal-only proxy **was incomplete** for general support interpretation; the R582 observer is semantically broader. `r582_controller.py` then runs a separate corrected policy. A signed wrench measures reaction forces; it does not by itself make the character more stable.

### R583 — friction and slip were being measured (GitHub-only source evidence)

The local checkpoint selection does not contain an R583 source ZIP. The actual branch blob `research/lucid/r583/r583_friction_probe.py` was independently fetched (Git SHA-1 `cff0ac0e4785c0fbfb10f255ff6eb21178dd2aa7`). It sets cloned friction treatments including `ice`, `original`, and `high_grip`; it measures real contact grip/slip rather than treating a friction coefficient as a guarantee of stationary seat or feet. The README blob `af62a57d94b151155f846104885b99bdb04e9656` reports source-measured effective original seat friction 0.82 and floor friction 1.0. **This is remote source testimony**, not locally replayed physics or a complete locally indexed R583 source tree.

### R584 — no-slip solver intervention on the same R583 friction benchmark

`r584_solver_config.py:18–35` changes only native `model.opt.noslip_iterations` after checking treatment validity and material identity. `r584_replay.py` imports the R583 friction probe and temporarily monkeypatches its `set_friction` function while the replay runs, restoring it in a `finally` block. The experiment intentionally holds model/actuator scene inputs constant and varies solver handling of contact slip. **Caution:** a global monkeypatch is not thread-safe; copied or parallel test orchestration could silently mix contexts. A physical grip/slip finding is not evidence that the increased no-slip treatment is anatomically or materially calibrated.

### R585 — experimental SCM geometry and independent six-axis neck-muscle controller

`r585_neck_repair.py` modifies native left/right sternocleidomastoid attachment site coordinates at runtime and adds six-head/neck-DOF feedback using ten chosen muscle actuators. Its optimizer is a bounded least-squares problem over instantaneous native actuator moment arms and muscle force gains. A scalar head-versus-Spine02 orientation metric helps quantify the dramatic neck failure but is not full shape/skin verification. The intervention must be identified as an experimental geometry variation and specialized muscle controller, **not** a frozen canonical anatomical amendment.

### R586 — constrained reduction of neck excitation

`r586_effort.py` inherits the R585 allocator and solves a linear program: reduce summed commands while constraining a **local algebraic six-axis moment proxy** close to R585 output at the same state and bounding command slew. The zero- or low-error moment *proxy* is not the delayed actual actuator force. The earlier paper documents the exact matrices and source lines. The R586 source does not claim generalized reaching or bilateral hand support.

### R587 — longer trajectory and an additional whole-body numerical gate

`r587_whole_body_gate.py` adds tests for maximum head/torso rotation, pelvis tilt, arm-seat contact and floor impact (`LIMITS` at lines 11–13; `inspect_native:14–37`, `check_render:39–61`). `r587_skin78_long_render.py` adds a new long-horizon native SKIN78 render. This changes **measurement and review coverage**; it need not change the native muscle policy. Later user visual observation of arm-seat chatter shows the gate still lacked a direct high-frequency contact-transition and natural resting-arm criterion.

### R588 — high-frequency contact diagnostics and passive damping sensitivity

`r588_probe.py:20–41` is a separate native arm/seat contact ledger; `run:43–117` tests contact parameters and joint damping variants while continuing the R586 head control. The isolated ×10 joint damping and thumb-contact treatments were useful fault-isolation probes but not calibrated biological muscle behavior. Source code distinguishes an observer from a tested intervention; collapsing the two loses provenance.

### R589 — physically simulated, but time-programmed shoulder landing

`r589_arm_landing.py:32–85` introduces `ArmLanding` with a smooth predetermined shoulder target, a PD moment request and state-dependent actuator gain/lever arm conversion to bounded extra muscle excitation. Its action is applied during native MuJoCo stepping (`run:88–150`), not by pose teleportation; the added command fades after arrival. It improved the local impact test but was **not** an intelligent hand target/reach planner; the right arm can remain unsupported and the left contact can still chatter.

### R590 — two distinct continuation/test routes

`r590_settled_capture.py` runs actual R589 native physics uninterrupted for 24 s and records late t=12–24 state. `r590_rest_restart.py` constructs an independent native state from qpos/qvel/act and reconstructs the original postural target and R586 allocator command memory. Critically, the restarted path does not instantiate the earlier R589 arm-landing controller; it is an *after-landing supported-rest* test. The observed seated posture does not prove a new motor capability or complete deterministic memory rewind.

## The three non-equivalent meanings of “new version”

1. **New physical actuator policy:** R576–580 research overlays, R581/582 controllers, R585/586 allocator, R589 landing. A command change can produce actual new movements, but each is specialized.
2. **New observer or acceptance contract:** R578 support geometry, R581 pressure/moment probes, R582 world contact wrench, R583 slip observer, R587 whole-body gate, R588 high-frequency arm ledger. These may expose real flaws without adding a motor skill.
3. **New experiment harness/initial state/render:** R575 latency, R577 duration, R584 no-slip solver, R587 render, R590 physical state continuation. These change which evidence is available or conditions of the same system; they do not necessarily extend the learned movement vocabulary.

A release may combine categories. A checkpoint number is not a measure of motor intelligence. **All three categories can be valuable, but must be independently labeled** or the development narrative will imply capabilities the actual model cannot demonstrate.

## Verified source-copy continuity and the limits of inference

The archive SHA crosswalk confirms `r576_longhorizon.py`, `r577_tonic_support.py`, `r578_feedback.py`, and `r579_controller.py` were carried byte-identically into later bundled ZIPs; similarly the R582 signed wrench controller and observer are byte-identical between two R582 archives. This proves **file reuse**, not a guaranteed matching executable environment. `VERSION_SNAPSHOT_REUSE_AND_HASH_CONFLICTS.json` contains the per-file exact content variants and their archive origin.

A definitive **first-bad regression** has not been established. Version folders can represent independently explored solutions, not a linear Git parent sequence. The correct comparison unit is an immutable model/config/scene with a specific physical source and a complete SKIN78 replay. Historical source existence, bench regression test success and user acceptance must not be collapsed.

## Immediate semantic closure work still needed

A full reconciliation must integrate the original `WholeBodyMuscleController`, goal/planner/steering source, and the newer R5xx physical research without silently replacing either. It must identify the exact executable path for each benchmark, the full MuJoCo state and actuator model, all source/changelist SHAs, the temporal call/mutation log and model-to-SKIN78 collision clearance. The current source map is a checkpoint, not a completed ontology. Dynamic physical behavior cannot be proved by source description alone.
