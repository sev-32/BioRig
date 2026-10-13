# R575–R590 evidence-indexed version-by-version source atlas

**Classification:** this source-catalog chapter records what code and statements actually exist in each available archive. Source docstrings represent their authors’ stated intent and may not equal validated behavior. A filename or version marker does not prove chronological Git ancestry, runtime integration or regression.**

| Version | ZIP containers | Python instances | Distinct source SHA | Status |
|---|---:|---:|---:|---|
| R575 | 2 | 11 | 8 | ARCHIVED SOURCE VERIFIED |
| R576 | 1 | 3 | 3 | ARCHIVED SOURCE VERIFIED |
| R577 | 1 | 5 | 5 | ARCHIVED SOURCE VERIFIED |
| R578 | 1 | 6 | 6 | ARCHIVED SOURCE VERIFIED |
| R579 | 1 | 5 | 5 | ARCHIVED SOURCE VERIFIED |
| R580 | 1 | 18 | 18 | ARCHIVED SOURCE VERIFIED |
| R581 | 1 | 5 | 5 | ARCHIVED SOURCE VERIFIED |
| R582 | 2 | 12 | 6 | ARCHIVED SOURCE VERIFIED |
| R583 | 0 | 0 | 0 | REMOTE-ONLY: NOT MIRRORED |
| R584 | 1 | 5 | 5 | ARCHIVED SOURCE VERIFIED |
| R585 | 1 | 8 | 8 | ARCHIVED SOURCE VERIFIED |
| R586 | 1 | 3 | 3 | ARCHIVED SOURCE VERIFIED |
| R587 | 1 | 3 | 3 | ARCHIVED SOURCE VERIFIED |
| R588 | 1 | 3 | 3 | ARCHIVED SOURCE VERIFIED |
| R589 | 1 | 4 | 4 | ARCHIVED SOURCE VERIFIED |
| R590 | 1 | 5 | 5 | ARCHIVED SOURCE VERIFIED |

## R575

### `tools/bootstrap.py`
Source: `BioRig_LUCID_R575_GITHUB_BRANCH_CHECKPOINT_2026-10-12.zip`, SHA-256 `552e5fe83eb1962d25b709e27bd42c71a16c0c8ab6f0a7421f4fd2f0dc6a1dbd`; 80 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** Restore the exact user-supplied LUCID research archives, offline.  Does not modify either input archive. Refuses unsafe ZIP paths and unexpected primary-archive digest. The source archive is NOT silently replaced with git code.

Definitions: `digest` (L17–22), `extract_checked` (L25–51), `main` (L54–77).

### `tools/audit_latency.py`
Source: `BioRig_LUCID_R575_GITHUB_BRANCH_CHECKPOINT_2026-10-12.zip`, SHA-256 `47bb8841981798ef2eba26daeea09e48ed6d52e4620f08184b5a73dbf54a68a4`; 121 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** Strict, dependency-free replay-data audit for frozen LUCID R575 records.  Uses saved physical observations; never predicts or substitutes missing rollouts. Results are descriptive and do not constitute a new controller evaluation.

Definitions: `assert_finite_float` (L22–25), `inspect_record` (L28–73), `compare` (L76–110), `main` (L113–118).

### `tests/test_repository_tools.py`
Source: `BioRig_LUCID_R575_GITHUB_BRANCH_CHECKPOINT_2026-10-12.zip`, SHA-256 `1fdd4216617641674a71aa2c91057dd1c698a8e85839c2c7353cdc643ce60a46`; 68 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** Fast offline tests for the BioRig research import and trace checker.

Definitions: `fixture` (L16–26), `OfflineChecks` (L28–66).

### `native/r574_intention.py`
Source: `BioRig_LUCID_R575_GITHUB_BRANCH_CHECKPOINT_2026-10-12.zip`, SHA-256 `08d06b1373901bbbccac2c60e706ad5968767ac0ff231c42dd0ffebe3dd8de8a`; 140 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** LUCID R574: explicit goal/aversion contract over bounded native muscle pulses.  The body has an externally specified intention, NOT a subjective wish. The policy receives only current measured sensors at 60ms, and compares learned outcomes of neutral continuation vs one historically well-observed R28 muscle excitation. Simulator/harness metadata are evaluation-only. Risk probabilities are small-data ExtraTrees frequencies, not guarantees.

Definitions: `GoalContract` (L24–38), `sha` (L67–67), `all_training` (L68–73), `feature` (L74–75), `OutcomeMemory` (L76–109), `score` (L111–117), `IntentionAgent` (L119–140).

### `native/r574_evaluate.py`
Source: `BioRig_LUCID_R575_GITHUB_BRANCH_CHECKPOINT_2026-10-12.zip`, SHA-256 `79437f0817cebe7254b04a483fa90556b2fd06f74e3dc8bd2701e3199a8a5811`; 75 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** R574 frozen goals-vs-aversions native MuJoCo evaluation.  Goal selection at 60ms has NO access to external impulse, geometry label, or counterfactual future. All applied physics branches are cloned initial states.

Definitions: `frozen` (L16–25), `scenarios` (L27–31), `evaluate` (L33–69).

### `native/r575_latency.py`
Source: `BioRig_LUCID_R575_GITHUB_BRANCH_CHECKPOINT_2026-10-12.zip`, SHA-256 `b420dd32b336b22b2dca7f36266d201f46e2a528d72ddd503845999314e2a5bf`; 114 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** R575 research-only physical latency audit; R574 source and training frozen.  At t=60ms apply a goal-conditioned decision computed using measurements from 60/40/20ms. At each 40ms extra-muscle controller feedback update apply the same sensor delay. The MuJoCo plant and inherited native-muscle stabilizer remain unchanged and still observe privileged current simulator mechanics.  This is therefore a true 8/12s native physical rollout with delayed high-level sensing and pulse safety feedback, NOT full system-wide neuro-sensory latency. No policy refit; no use of future outcomes when selecting an action.

Definitions: `frozen_scene` (L32–33), `simulate` (L35–91), `main` (L93–113).

### `native/r575_render.py`
Source: `BioRig_LUCID_R575_GITHUB_BRANCH_CHECKPOINT_2026-10-12.zip`, SHA-256 `561936f9fbdc4b7d462ac2f8c485e34f3d39f62ac98b48a7a80f7d4a04fdcca2`; 46 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Actual MuJoCo offscreen frame capture of the frozen R574 R28 rescue (scene 4). Rendering-only seat translucency and headlight; physical model dynamics unchanged.

No top-level named function or class definitions found.

### `native/test_r575_evidence.py`
Source: `BioRig_LUCID_R575_GITHUB_BRANCH_CHECKPOINT_2026-10-12.zip`, SHA-256 `d079033f5985a97599ab72c5b4446be4cc3b6c9003b43f7ada2ce016bf34f86d`; 50 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** Fast audit of completed R575 branches against locked R574 evidence. This does NOT re-run the slow native-physics branches; see r575_latency.py.

Definitions: `R575EvidenceChecks` (L11–49).

### `R575_SENSOR_LATENCY_PHYSICS/r575_latency.py`
Source: `LUCID_R575_VERIFIED_TAKEOVER_LATENCY_ADDENDUM.zip`, SHA-256 `b420dd32b336b22b2dca7f36266d201f46e2a528d72ddd503845999314e2a5bf`; 114 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** R575 research-only physical latency audit; R574 source and training frozen.  At t=60ms apply a goal-conditioned decision computed using measurements from 60/40/20ms. At each 40ms extra-muscle controller feedback update apply the same sensor delay. The MuJoCo plant and inherited native-muscle stabilizer remain unchanged and still observe privileged current simulator mechanics.  This is therefore a true 8/12s native physical rollout with delayed high-level sensing and pulse safety feedback, NOT full system-wide neuro-sensory latency. No policy refit; no use of future outcomes when selecting an action.

Definitions: `frozen_scene` (L32–33), `simulate` (L35–91), `main` (L93–113).

### `R575_SENSOR_LATENCY_PHYSICS/r575_render.py`
Source: `LUCID_R575_VERIFIED_TAKEOVER_LATENCY_ADDENDUM.zip`, SHA-256 `561936f9fbdc4b7d462ac2f8c485e34f3d39f62ac98b48a7a80f7d4a04fdcca2`; 46 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Actual MuJoCo offscreen frame capture of the frozen R574 R28 rescue (scene 4). Rendering-only seat translucency and headlight; physical model dynamics unchanged.

No top-level named function or class definitions found.

### `R575_SENSOR_LATENCY_PHYSICS/test_r575_evidence.py`
Source: `LUCID_R575_VERIFIED_TAKEOVER_LATENCY_ADDENDUM.zip`, SHA-256 `d079033f5985a97599ab72c5b4446be4cc3b6c9003b43f7ada2ce016bf34f86d`; 50 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** Fast audit of completed R575 branches against locked R574 evidence. This does NOT re-run the slow native-physics branches; see r575_latency.py.

Definitions: `R575EvidenceChecks` (L11–49).


## R576

### `R576/r576_longhorizon.py`
Source: `BioRig_LUCID_R576_NATIVE_LONG_HORIZON_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `3fe724631994060be4d1c0b00addccba0d2fe81d9cec767388077dff06be629b`; 126 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** R576: post-lock, sensed-state late-support research on the frozen R574 plant.  FROZEN R574/R575 source, model locks, training and physics are unmodified. This experiment *adds* a separate R562-derived bounded support guard only when requested, retaining the already selected R574 early action. Harness force, scene width, future trajectories and counterfactual results are not observed by online controllers. A 12-second safety result is NOT asymptotic stability.

Definitions: `make_guard` (L31–36), `branch` (L39–91), `compare` (L94–113).

### `R576/r576_render.py`
Source: `BioRig_LUCID_R576_NATIVE_LONG_HORIZON_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `7723d3a6a722837d8e78cdd6500f1fa1668970d05219fbbb23fb44777ff7c992`; 71 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** True MuJoCo offscreen headless captures, frozen scene00 vs R576 guard. No generated art, no joint/root teleportation, no collision/inertia changes.

Definitions: `capture` (L19–54), `main` (L56–69).

### `R576/test_r576.py`
Source: `BioRig_LUCID_R576_NATIVE_LONG_HORIZON_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `e724a76857e2943eed30a61d7ebd229f06d341db253d7129438fb3e8c6debd58`; 46 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** R576 research-contract tests; set R576_RUN_NATIVE=1 for paired 12s physics.

Definitions: `TestR576` (L9–44).


## R577

### `research/lucid/r576/r576_longhorizon.py`
Source: `BioRig_LUCID_R577_NATIVE_40S_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `3fe724631994060be4d1c0b00addccba0d2fe81d9cec767388077dff06be629b`; 126 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** R576: post-lock, sensed-state late-support research on the frozen R574 plant.  FROZEN R574/R575 source, model locks, training and physics are unmodified. This experiment *adds* a separate R562-derived bounded support guard only when requested, retaining the already selected R574 early action. Harness force, scene width, future trajectories and counterfactual results are not observed by online controllers. A 12-second safety result is NOT asymptotic stability.

Definitions: `make_guard` (L31–36), `branch` (L39–91), `compare` (L94–113).

### `research/lucid/r577/r577_batch.py`
Source: `BioRig_LUCID_R577_NATIVE_40S_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `363fc24982db3ff03978ae1ddfa696a602ae561b80b81d1013cfb9a1ead2fb76`; 23 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** (no module-level docstring)

No top-level named function or class definitions found.

### `research/lucid/r577/r577_render.py`
Source: `BioRig_LUCID_R577_NATIVE_40S_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `1bca32e8bf62b9b86686a7da45ce9a5a1ff7ee31c31fa21b9ba42b8e6df4c236`; 60 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Real EGL/MuJoCo 3.15 side sequence at 0,12,20,30,40 seconds; native rig.

Definitions: `capture` (L16–41), `main` (L43–59).

### `research/lucid/r577/r577_tonic_support.py`
Source: `BioRig_LUCID_R577_NATIVE_40S_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `4c82b09dbabd621d151dfa5fbd4114c4308b0e08af0b335ddd13755a6a8fdab4`; 161 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** R577: native sensed-state bounded tonic recruitment research.  The frozen R574 predictor, R569/562 base stabilizer, MuJoCo model and initial states are never modified. The optional low-level overlay senses only current posture/contacts. R577 candidate parameters are tuned on R574 scene00 and have NOT been certified on held-out scenes. No root locking or external pose forces.

Definitions: `TonicSupport` (L25–64), `rollout` (L67–131), `main` (L134–160).

### `research/lucid/r577/test_r577.py`
Source: `BioRig_LUCID_R577_NATIVE_40S_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `598ee8a21cb93295529556e7c146d5d21b4f4c91482ceaa315242c96ac86411d`; 46 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** (no module-level docstring)

Definitions: `TestR577` (L7–45).


## R578

### `research/lucid/r576/r576_longhorizon.py`
Source: `BioRig_LUCID_R578_SUPPORT_FEEDBACK_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `3fe724631994060be4d1c0b00addccba0d2fe81d9cec767388077dff06be629b`; 126 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** R576: post-lock, sensed-state late-support research on the frozen R574 plant.  FROZEN R574/R575 source, model locks, training and physics are unmodified. This experiment *adds* a separate R562-derived bounded support guard only when requested, retaining the already selected R574 early action. Harness force, scene width, future trajectories and counterfactual results are not observed by online controllers. A 12-second safety result is NOT asymptotic stability.

Definitions: `make_guard` (L31–36), `branch` (L39–91), `compare` (L94–113).

### `research/lucid/r577/r577_tonic_support.py`
Source: `BioRig_LUCID_R578_SUPPORT_FEEDBACK_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `4c82b09dbabd621d151dfa5fbd4114c4308b0e08af0b335ddd13755a6a8fdab4`; 161 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** R577: native sensed-state bounded tonic recruitment research.  The frozen R574 predictor, R569/562 base stabilizer, MuJoCo model and initial states are never modified. The optional low-level overlay senses only current posture/contacts. R577 candidate parameters are tuned on R574 scene00 and have NOT been certified on held-out scenes. No root locking or external pose forces.

Definitions: `TonicSupport` (L25–64), `rollout` (L67–131), `main` (L134–160).

### `research/lucid/r578/r578_support.py`
Source: `BioRig_LUCID_R578_SUPPORT_FEEDBACK_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `dbb78db2a80bde03e9160a82cda871d910f80b07abbd8df2ac312ae956035d5f`; 44 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** Measured mass-centre vs active seat/floor support in world coordinates.  Independent fundamental: this module contains no policy, no muscle actuation, no knowledge of disturbance metadata, and no future state. Metres/Newtons only.

Definitions: `SupportMeasurement` (L12–18), `measure` (L21–44).

### `research/lucid/r578/r578_feedback.py`
Source: `BioRig_LUCID_R578_SUPPORT_FEEDBACK_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `8950ab78b524b065d4664ac4743a02d944960f8facab45ced4de445ed9495cfd`; 161 lines; declared topic `CONTROLLER`.

**Author statement (source docstring; not independently verified):** R578 controlled research: support-aware gradual muscle feedback vs frozen R577.  No edits to R574/R575/R576/R577. All online variables are sensed; counterfactual scene/force metadata is only applied to the test harness. No position locking. Experimental tuning on known-failing scene00 is *not heldout generalization*.

Definitions: `SupportFeedback` (L27–71), `run` (L74–133), `main` (L136–160).

### `research/lucid/r578/test_r578.py`
Source: `BioRig_LUCID_R578_SUPPORT_FEEDBACK_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `b2af5a846735116665afb9a3a36933488436c775623557a525e9caa4ee7317d6`; 50 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** R578 structural, dimensional, and native physical regression gates.

Definitions: `R578Tests` (L9–49).

### `research/lucid/r578/r578_render.py`
Source: `BioRig_LUCID_R578_SUPPORT_FEEDBACK_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `1ea2548a0ed2067f5af2d230c4f0dea5b18ab975538652c5afbd1a487d6f51d7`; 77 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Actual MuJoCo 3.15 EGL capture for R578 feedback, *no generated images*. Freeze camera and display each true physics state from one continuous run.

Definitions: `capture` (L18–57), `main` (L59–76).


## R579

### `research/lucid/r579/r579_controller.py`
Source: `BioRig_LUCID_R579_NATIVE_SYNERGY_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `78f1428bd1385f2d5f131b533cae6d1c14e726b4eaf587e4079b4ef89d3f9dd1`; 101 lines; declared topic `CONTROLLER`.

**Author statement (source docstring; not independently verified):** R579 constrained muscle synergy atop the unmodified R577 native plant.  A different weight for each independently named actuator, identical R577 proprioceptive trigger, ramp, safety gate and base R574 muscle controller. Weights were chosen after a same-state *offline* probe; the online controller never observes probe outcomes or future trajectories. Development-only.

Definitions: `Synergy` (L23–44), `rollout` (L47–76), `main` (L79–100).

### `research/lucid/r579/r579_identify.py`
Source: `BioRig_LUCID_R579_NATIVE_SYNERGY_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `a58b8ca2c35709918f4ebc8d85e3088c8450a91956ca5a816afb4333aca7034b`; 86 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** Local one-factor probe of native muscle authority at a cloned, supported state.  Only reads current MuJoCo state; probes are offline research and do not feed the active policy. All branches share an identical saved state at t=8 seconds.

Definitions: `groups` (L19–40), `run_probes` (L42–84).

### `research/lucid/r579/r579_render.py`
Source: `BioRig_LUCID_R579_NATIVE_SYNERGY_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `5070c28a40da29b40c0fa94c4e8f597c70c56f868b1f6651952b237540453525`; 66 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Actual MuJoCo/EGL fixed-camera scene, four physical times; no generated art.

Definitions: `main` (L16–65).

### `research/lucid/r579/test_r579.py`
Source: `BioRig_LUCID_R579_NATIVE_SYNERGY_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `e7700c682cc3957d24bf77ef6e1e92617a964583331643ecfc812ecc34e47272`; 49 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** Contract and optional native physics gates for experimental muscle synergy.

Definitions: `TestR579` (L10–48).

### `research/lucid/r579/r579_synergy.py`
Source: `BioRig_LUCID_R579_NATIVE_SYNERGY_CODE_EVIDENCE_2026-10-12.zip`, SHA-256 `7a9b3d74381732d27de63ce8a470c55d93ea89c74b64885cf9daec0246cd688b`; 131 lines; declared topic `CONTROLLER`.

**Author statement (source docstring; not independently verified):** R579: hip-dominant muscle synergy experiment on the unchanged R574 plant.  The plant and frozen R574 policy are immutable. Profiles redistribute the *same* R577 command amplitude over independently identified actuator channels; only current proprioceptive observations determine side, onset and dose. No probe result is read during online control; probes establish offline hypotheses.

Definitions: `MuscleSynergy` (L28–56), `rollout` (L59–108), `main` (L110–130).


## R580

### `research/lucid/r576/r576_longhorizon.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `3fe724631994060be4d1c0b00addccba0d2fe81d9cec767388077dff06be629b`; 126 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** R576: post-lock, sensed-state late-support research on the frozen R574 plant.  FROZEN R574/R575 source, model locks, training and physics are unmodified. This experiment *adds* a separate R562-derived bounded support guard only when requested, retaining the already selected R574 early action. Harness force, scene width, future trajectories and counterfactual results are not observed by online controllers. A 12-second safety result is NOT asymptotic stability.

Definitions: `make_guard` (L31–36), `branch` (L39–91), `compare` (L94–113).

### `research/lucid/r577/r577_batch.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `363fc24982db3ff03978ae1ddfa696a602ae561b80b81d1013cfb9a1ead2fb76`; 23 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** (no module-level docstring)

No top-level named function or class definitions found.

### `research/lucid/r577/r577_render.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `1bca32e8bf62b9b86686a7da45ce9a5a1ff7ee31c31fa21b9ba42b8e6df4c236`; 60 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Real EGL/MuJoCo 3.15 side sequence at 0,12,20,30,40 seconds; native rig.

Definitions: `capture` (L16–41), `main` (L43–59).

### `research/lucid/r577/r577_tonic_support.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `4c82b09dbabd621d151dfa5fbd4114c4308b0e08af0b335ddd13755a6a8fdab4`; 161 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** R577: native sensed-state bounded tonic recruitment research.  The frozen R574 predictor, R569/562 base stabilizer, MuJoCo model and initial states are never modified. The optional low-level overlay senses only current posture/contacts. R577 candidate parameters are tuned on R574 scene00 and have NOT been certified on held-out scenes. No root locking or external pose forces.

Definitions: `TonicSupport` (L25–64), `rollout` (L67–131), `main` (L134–160).

### `research/lucid/r577/test_r577.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `598ee8a21cb93295529556e7c146d5d21b4f4c91482ceaa315242c96ac86411d`; 46 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** (no module-level docstring)

Definitions: `TestR577` (L7–45).

### `research/lucid/r578/r578_feedback.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `8950ab78b524b065d4664ac4743a02d944960f8facab45ced4de445ed9495cfd`; 161 lines; declared topic `CONTROLLER`.

**Author statement (source docstring; not independently verified):** R578 controlled research: support-aware gradual muscle feedback vs frozen R577.  No edits to R574/R575/R576/R577. All online variables are sensed; counterfactual scene/force metadata is only applied to the test harness. No position locking. Experimental tuning on known-failing scene00 is *not heldout generalization*.

Definitions: `SupportFeedback` (L27–71), `run` (L74–133), `main` (L136–160).

### `research/lucid/r578/r578_render.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `1ea2548a0ed2067f5af2d230c4f0dea5b18ab975538652c5afbd1a487d6f51d7`; 77 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Actual MuJoCo 3.15 EGL capture for R578 feedback, *no generated images*. Freeze camera and display each true physics state from one continuous run.

Definitions: `capture` (L18–57), `main` (L59–76).

### `research/lucid/r578/r578_support.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `dbb78db2a80bde03e9160a82cda871d910f80b07abbd8df2ac312ae956035d5f`; 44 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** Measured mass-centre vs active seat/floor support in world coordinates.  Independent fundamental: this module contains no policy, no muscle actuation, no knowledge of disturbance metadata, and no future state. Metres/Newtons only.

Definitions: `SupportMeasurement` (L12–18), `measure` (L21–44).

### `research/lucid/r578/test_r578.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `b2af5a846735116665afb9a3a36933488436c775623557a525e9caa4ee7317d6`; 50 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** R578 structural, dimensional, and native physical regression gates.

Definitions: `R578Tests` (L9–49).

### `research/lucid/r579/r579_controller.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `78f1428bd1385f2d5f131b533cae6d1c14e726b4eaf587e4079b4ef89d3f9dd1`; 101 lines; declared topic `CONTROLLER`.

**Author statement (source docstring; not independently verified):** R579 constrained muscle synergy atop the unmodified R577 native plant.  A different weight for each independently named actuator, identical R577 proprioceptive trigger, ramp, safety gate and base R574 muscle controller. Weights were chosen after a same-state *offline* probe; the online controller never observes probe outcomes or future trajectories. Development-only.

Definitions: `Synergy` (L23–44), `rollout` (L47–76), `main` (L79–100).

### `research/lucid/r579/r579_identify.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `a58b8ca2c35709918f4ebc8d85e3088c8450a91956ca5a816afb4333aca7034b`; 86 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** Local one-factor probe of native muscle authority at a cloned, supported state.  Only reads current MuJoCo state; probes are offline research and do not feed the active policy. All branches share an identical saved state at t=8 seconds.

Definitions: `groups` (L19–40), `run_probes` (L42–84).

### `research/lucid/r579/r579_render.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `5070c28a40da29b40c0fa94c4e8f597c70c56f868b1f6651952b237540453525`; 66 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Actual MuJoCo/EGL fixed-camera scene, four physical times; no generated art.

Definitions: `main` (L16–65).

### `research/lucid/r579/r579_synergy.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `7a9b3d74381732d27de63ce8a470c55d93ea89c74b64885cf9daec0246cd688b`; 131 lines; declared topic `CONTROLLER`.

**Author statement (source docstring; not independently verified):** R579: hip-dominant muscle synergy experiment on the unchanged R574 plant.  The plant and frozen R574 policy are immutable. Profiles redistribute the *same* R577 command amplitude over independently identified actuator channels; only current proprioceptive observations determine side, onset and dose. No probe result is read during online control; probes establish offline hypotheses.

Definitions: `MuscleSynergy` (L28–56), `rollout` (L59–108), `main` (L110–130).

### `research/lucid/r579/test_r579.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `e7700c682cc3957d24bf77ef6e1e92617a964583331643ecfc812ecc34e47272`; 49 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** Contract and optional native physics gates for experimental muscle synergy.

Definitions: `TestR579` (L10–48).

### `research/lucid/r580/r580_adaptive_synergy.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `d648ad45626a4ae1fca23b8912a6ee93f8cd26bce7fcc40e719cab4dc6a8ccc5`; 189 lines; declared topic `CONTROLLER`.

**Author statement (source docstring; not independently verified):** R580: causal, bounded proprioceptive hip/trunk adaptive recruitment.  The original 84-muscle R574 MuJoCo plant, baseline stabilizer and early intention selector are never modified. Research controller only reads current sensors. Development calibration: R579 scene00 drift between 23 and 28 simulated seconds.

Definitions: `clamp` (L36–36), `smoothstep` (L38–40), `AdaptiveSynergy` (L42–105), `rollout` (L108–165), `main` (L168–188).

### `research/lucid/r580/r580_render.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `a44370f45225d55fcb4d301e69fa9aa481917d86c25bd648a1bde05ffe861001`; 68 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Native MuJoCo 3.15 EGL renderer with identical controller/scene as R580 LATE 40s. Visual-only transparent seat, fixed inspection camera; no dynamics changes.

Definitions: `main` (L18–67).

### `research/lucid/r580/test_r580.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `1e5f405ecdcb521c297591d4ccca76f0a705386064204005a38ebd7e01c80fdf`; 72 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** R580 typed motor/safety contract tests, plus optional native 12s replay.

Definitions: `TestR580` (L11–71).

### `research/lucid/tools/bootstrap.py`
Source: `BioRig_LUCID_R580_NATIVE_ADAPTIVE_SYNERGY_2026-10-12.zip`, SHA-256 `552e5fe83eb1962d25b709e27bd42c71a16c0c8ab6f0a7421f4fd2f0dc6a1dbd`; 80 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** Restore the exact user-supplied LUCID research archives, offline.  Does not modify either input archive. Refuses unsafe ZIP paths and unexpected primary-archive digest. The source archive is NOT silently replaced with git code.

Definitions: `digest` (L17–22), `extract_checked` (L25–51), `main` (L54–77).


## R581

### `research/lucid/r581/r581_support.py`
Source: `BioRig_LUCID_R581_MOMENT_CONTACT_NATIVE_EVIDENCE_2026-10-12.zip`, SHA-256 `df51cd0625d0af27b7b96937144d775ab352b53e2d9374d91f1bcbe794d3f471`; 45 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** R581 measured support geometry: contact pressure, COM and reaction loads.  Pure observer: reads MuJoCo state without modifying it. Coordinates are world X in metres; forces are N; only seat/ground normal's world-Y component counts as vertical support. The 1D contact interval is NOT a stability polygon proof.

Definitions: `SupportState` (L13–21), `sense_support` (L23–45).

### `research/lucid/r581/r581_moment_probe.py`
Source: `BioRig_LUCID_R581_MOMENT_CONTACT_NATIVE_EVIDENCE_2026-10-12.zip`, SHA-256 `91b200b8adc8881316b07ef3d29b5a82b654a2a357f202df41f0d81d901c61c9`; 118 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** R581 frozen-state anatomical actuator moment and causal response identification.  The native 84-muscle plant and R580 controller remain unmodified. Probe acts on independent clones of ONE supported t=8s state. Online controller never sees probe outcomes. Force-dependent qfrc is generalized force in SI units; rotational DOFs measure N*m and are not directly interchangeable with x motion.

Definitions: `actuator_ids` (L33–39), `moment_snapshot` (L41–61), `setup_frozen_state` (L63–76), `run` (L78–115).

### `research/lucid/r581/r581_controller.py`
Source: `BioRig_LUCID_R581_MOMENT_CONTACT_NATIVE_EVIDENCE_2026-10-12.zip`, SHA-256 `cbea7fbd2781ecac543ca46b1809461c4aec0c24870c0005e660c3f9eb9d303f`; 160 lines; declared topic `CONTROLLER`.

**Author statement (source docstring; not independently verified):** R581 contact-relative hip/oblique correction on frozen native LUCID plant.  Development experiment, NOT production or heldout evidence. A causal feedback loop uses sensed root displacement+speed, center of mass relative to measured seat/foot pressure and support load. Named muscles only, no direct root forces.

Definitions: `ContactAllocator` (L29–83), `rollout` (L85–141), `main` (L143–159).

### `research/lucid/r581/r581_render.py`
Source: `BioRig_LUCID_R581_MOMENT_CONTACT_NATIVE_EVIDENCE_2026-10-12.zip`, SHA-256 `01c60f2b47150741a326f5d830cca4f82ab379894eabbc6761e1eba345b1aa05`; 75 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Actual fixed-camera MuJoCo 3.15 EGL, transparent seat visual inspection.  Frames are sampled from same native continuous R581 40-second simulation. Only rendering rgba/lighting/camera altered; contact/dynamics unchanged.

Definitions: `main` (L20–74).

### `research/lucid/r581/test_r581.py`
Source: `BioRig_LUCID_R581_MOMENT_CONTACT_NATIVE_EVIDENCE_2026-10-12.zip`, SHA-256 `baac04440a377e00546dafaf29b38b4b7e20ef753ae618e03632a8c8f4dbb63c`; 72 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** R581 observer/allocator structural gates and optional native physical replay.

Definitions: `TestR581` (L12–71).


## R582

### `research/lucid/r582/r582_wrench.py`
Source: `BioRig_LUCID_R582_SIGNED_WRENCH_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `d15ecf5f0268dea0ab929584a408f0ec362a994bfde2d2b087fb29abdf14b86a`; 90 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** R582 | Pure observation of *signed* native external contact wrenches.  All quantities are world frame, SI metres/Newtons/Newton-metres. MuJoCo's contact frame uses rows (normal, tangent1, tangent2) and contact forces are for geom2; negate if the externally supported body is geom1. No model or data mutation. World +Y is vertical in this specific inherited seated model.  A projection of the 3D resultant on world Y=0 is a *virtual equivalent reaction*, not a dynamic-ZMP claim or a physical contact point when seat and floor have different heights. It may lie outside the actual contact envelope.

Definitions: `ContactWrench` (L20–35), `world_wrench` (L38–48), `sense_wrench` (L51–90).

### `research/lucid/r582/r582_controller.py`
Source: `BioRig_LUCID_R582_SIGNED_WRENCH_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `4fe6eb4849fe01133fcf16f820cad15333971f91932ce4a8f860bd7c57b1c6bf`; 172 lines; declared topic `CONTROLLER`.

**Author statement (source docstring; not independently verified):** R582 signed-wrench hip/oblique correction on frozen native LUCID plant.  Development experiment, NOT production or heldout evidence. A causal feedback loop uses sensed root displacement+speed, center of mass relative to measured seat/foot signed contact wrench and support load. Named muscles only, no direct root forces.

Definitions: `SignedWrenchAllocator` (L29–88), `rollout` (L90–153), `main` (L155–171).

### `research/lucid/r582/r582_probe.py`
Source: `BioRig_LUCID_R582_SIGNED_WRENCH_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `ba421374ac695f76e88c756a36afaa955a9e9c406408e95eb31e0e9d14049c78`; 57 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** Native 40s diagnostic: real R581 controller and identical cloned initial state.

Definitions: `probe` (L11–56).

### `research/lucid/r582/r582_render.py`
Source: `BioRig_LUCID_R582_SIGNED_WRENCH_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `738e77406a77d0c3cfa3d229857aa1889dce6858fc7349ee96ce27605ab53c25`; 78 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Actual fixed-camera MuJoCo 3.15 EGL, transparent seat visual inspection.  Frames are sampled from same native continuous R582 40-second simulation. Only rendering rgba/lighting/camera altered; contact/dynamics unchanged.

Definitions: `main` (L20–77).

### `research/lucid/r582/test_r582_wrench.py`
Source: `BioRig_LUCID_R582_SIGNED_WRENCH_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `0ec88e928121568efa5bac2e63e03204b8ebd0a1c42c5d5e1c87154d53d9c968`; 60 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** R582 independent real-plant and synthetic contact-frame invariance gates.

Definitions: `TestSignedWrench` (L10–59).

### `research/lucid/r582/test_r582_controller.py`
Source: `BioRig_LUCID_R582_SIGNED_WRENCH_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `a66ccddede1826429b3934c55e83a2feb8a30aaba2c7609207c3a87983c70f0e`; 68 lines; declared topic `CONTROLLER`.

**Author statement (source docstring; not independently verified):** R582 bounded online allocator and native MuJoCo regression gates; no CI needed.

Definitions: `TestR582Controller` (L10–67).

### `research/lucid/r582/r582_wrench.py`
Source: `BioRig_LUCID_R582_VERIFIED_NATIVE_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `d15ecf5f0268dea0ab929584a408f0ec362a994bfde2d2b087fb29abdf14b86a`; 90 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** R582 | Pure observation of *signed* native external contact wrenches.  All quantities are world frame, SI metres/Newtons/Newton-metres. MuJoCo's contact frame uses rows (normal, tangent1, tangent2) and contact forces are for geom2; negate if the externally supported body is geom1. No model or data mutation. World +Y is vertical in this specific inherited seated model.  A projection of the 3D resultant on world Y=0 is a *virtual equivalent reaction*, not a dynamic-ZMP claim or a physical contact point when seat and floor have different heights. It may lie outside the actual contact envelope.

Definitions: `ContactWrench` (L20–35), `world_wrench` (L38–48), `sense_wrench` (L51–90).

### `research/lucid/r582/r582_controller.py`
Source: `BioRig_LUCID_R582_VERIFIED_NATIVE_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `4fe6eb4849fe01133fcf16f820cad15333971f91932ce4a8f860bd7c57b1c6bf`; 172 lines; declared topic `CONTROLLER`.

**Author statement (source docstring; not independently verified):** R582 signed-wrench hip/oblique correction on frozen native LUCID plant.  Development experiment, NOT production or heldout evidence. A causal feedback loop uses sensed root displacement+speed, center of mass relative to measured seat/foot signed contact wrench and support load. Named muscles only, no direct root forces.

Definitions: `SignedWrenchAllocator` (L29–88), `rollout` (L90–153), `main` (L155–171).

### `research/lucid/r582/r582_probe.py`
Source: `BioRig_LUCID_R582_VERIFIED_NATIVE_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `ba421374ac695f76e88c756a36afaa955a9e9c406408e95eb31e0e9d14049c78`; 57 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** Native 40s diagnostic: real R581 controller and identical cloned initial state.

Definitions: `probe` (L11–56).

### `research/lucid/r582/r582_render.py`
Source: `BioRig_LUCID_R582_VERIFIED_NATIVE_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `738e77406a77d0c3cfa3d229857aa1889dce6858fc7349ee96ce27605ab53c25`; 78 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Actual fixed-camera MuJoCo 3.15 EGL, transparent seat visual inspection.  Frames are sampled from same native continuous R582 40-second simulation. Only rendering rgba/lighting/camera altered; contact/dynamics unchanged.

Definitions: `main` (L20–77).

### `research/lucid/r582/test_r582_wrench.py`
Source: `BioRig_LUCID_R582_VERIFIED_NATIVE_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `0ec88e928121568efa5bac2e63e03204b8ebd0a1c42c5d5e1c87154d53d9c968`; 60 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** R582 independent real-plant and synthetic contact-frame invariance gates.

Definitions: `TestSignedWrench` (L10–59).

### `research/lucid/r582/test_r582_controller.py`
Source: `BioRig_LUCID_R582_VERIFIED_NATIVE_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `a66ccddede1826429b3934c55e83a2feb8a30aaba2c7609207c3a87983c70f0e`; 68 lines; declared topic `CONTROLLER`.

**Author statement (source docstring; not independently verified):** R582 bounded online allocator and native MuJoCo regression gates; no CI needed.

Definitions: `TestR582Controller` (L10–67).


## R583

No matching local source archive was supplied. R583 GitHub research-branch blobs were fetched and pinned separately in `REMOTE_ONLY_GITHUB_EVIDENCE.json`. **This is not evidence of absence.**


## R584

### `r584_contact_solver.py`
Source: `BioRig_LUCID_R584_CONTACT_NOSLIP_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `28e43c84d37a7f1648b88bb1df48bed0a5168b528e26fe7cf89775e6b74634fc`; 170 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** R584: native no-slip contact solver A/B physical test.  No change to the source MJCF, geom/material coefficients, muscle controller, trajectory, root forces, geometry, masses, warmup or frozen R574 intent. Only MjModel.opt.noslip_iterations differs. Experimental research branch.

Definitions: `contact_material_fingerprint` (L24–27), `setup` (L29–40), `experiment` (L42–122), `animated_comparison` (L124–142), `main` (L144–169).

### `r584_solver_config.py`
Source: `BioRig_LUCID_R584_CONTACT_NOSLIP_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `b6e92b4c3cc67a7a284b624985899c20863ff731656903656961a2aa0963b087`; 35 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** R584 supported-contact no-slip correction for LUCID's native MuJoCo plant.  One solver parameter only. Does not change R574/R582, geometry, contact coefficients, muscles, initial physics, or externally apply root constraints.

Definitions: `material_digest` (L11–15), `configure` (L18–35).

### `r584_replay.py`
Source: `BioRig_LUCID_R584_CONTACT_NOSLIP_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `b5227d6d6710b7e3f228bfcdd74f126def40f4335826c346c92e05887268d88e`; 41 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** R584 exact same-scene no-slip replay using the frozen R583 measurement loop.  Test harness only. `r583_friction_probe` remains unchanged. The temporary injection is restored in finally; execute serially (not thread-safe).

Definitions: `replay` (L16–25), `main` (L28–40).

### `test_r584_solver_config.py`
Source: `BioRig_LUCID_R584_CONTACT_NOSLIP_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `de9b67ccea5ba1bca81b6f35003c3ecd1f0e8062436eaf02e780de82ff03d78c`; 42 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** Standalone R584 solver physics contract and optional native replay.

Definitions: `TestNoSlipConfiguration` (L10–41).

### `test_r584_contact_solver.py`
Source: `BioRig_LUCID_R584_CONTACT_NOSLIP_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `e35b01764b4f6a4eaf95283ae1de7e0c8c1b5a623187083ac79b14dee1fddb35`; 60 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** R584 no-slip contact physics acceptance gates; no GitHub Actions.

Definitions: `TestContactSolver` (L8–59).


## R585

### `R585/r585_neck_repair.py`
Source: `BioRig_LUCID_R585_PHYSICAL_NECK_REPAIR_CHECKPOINT_2026-10-13.zip`, SHA-256 `c356fd555e114360d31ff5466e15d71edf32b3cb7dcfeea7daa529e12c017c6e`; 105 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** R585 experimental physically bounded six-DOF muscle allocation. Frozen plant untouched. No coordinate clamp, joint/root torque injection, or externally applied hold.

Definitions: `angle` (L19–21), `NeckAllocator` (L23–55), `run` (L57–94).

### `R585/r585_skin78_render.py`
Source: `BioRig_LUCID_R585_PHYSICAL_NECK_REPAIR_CHECKPOINT_2026-10-13.zip`, SHA-256 `77445dad9b3b589996452f1220abe2d172f3b4d61b82a367e2c45f786bf4a0fc`; 79 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Real Skin78 native MuJoCo head-repair proof; 31 continuous physical captures per condition.

Definitions: `make_seat` (L22–31).

### `R585/test_r585.py`
Source: `BioRig_LUCID_R585_PHYSICAL_NECK_REPAIR_CHECKPOINT_2026-10-13.zip`, SHA-256 `3fe6406fc700a67e565fcb5f6a9637558fddb9e8c134cd1e66de44209fdb2be3`; 68 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** R585 native validation: physical muscle moment authority, neck and full skin gates.

Definitions: `R585Physical` (L11–66).

### `R585/r585_relaxed_probe.py`
Source: `BioRig_LUCID_R585_PHYSICAL_NECK_REPAIR_CHECKPOINT_2026-10-13.zip`, SHA-256 `b3a5ccf60fdbdff2db4185be4f93c4cf91bb38055ce186be18d0b3e7a086916d`; 105 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** R585 experimental physically bounded six-DOF muscle allocation. Frozen plant untouched. No coordinate clamp, joint/root torque injection, or externally applied hold.

Definitions: `angle` (L19–21), `NeckAllocator` (L23–55), `run` (L57–94).

### `R585/neck_probe.py`
Source: `BioRig_LUCID_R585_PHYSICAL_NECK_REPAIR_CHECKPOINT_2026-10-13.zip`, SHA-256 `7be45450b8822d269156275ee74766447f86cbc0712acc5bbb0b9726f52d27db`; 57 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** Local reproducible muscle-driven recovery probe, no source changes.

Definitions: `align_degrees` (L13–15), `core_step` (L17–31), `main` (L33–56).

### `R585/neck_feedback_probe.py`
Source: `BioRig_LUCID_R585_PHYSICAL_NECK_REPAIR_CHECKPOINT_2026-10-13.zip`, SHA-256 `2af562bd7a047b60659ac95caaa94c7bdfcf74c908abf00cf88363f1ac52ad62`; 71 lines; declared topic `CONTROLLER`.

**Author statement (source docstring; not independently verified):** Muscle-only feedback experiment: no model/source modifications, no root forces.

Definitions: `angle` (L15–17), `NeckControl` (L19–34), `simulate` (L36–62).

### `R585/neck_geometry_sweep.py`
Source: `BioRig_LUCID_R585_PHYSICAL_NECK_REPAIR_CHECKPOINT_2026-10-13.zip`, SHA-256 `beb1482a81a584cf49c20c0e1e6734e313d44806919f393793a0640e75ca665d`; 20 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** (no module-level docstring)

No top-level named function or class definitions found.

### `R585/scan_head_site.py`
Source: `BioRig_LUCID_R585_PHYSICAL_NECK_REPAIR_CHECKPOINT_2026-10-13.zip`, SHA-256 `6c234ead71b5b85f59a9bda078786dee33143363d4a246a7fb1898e92080e32f`; 16 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** (no module-level docstring)

No top-level named function or class definitions found.


## R586

### `research/lucid/r586/r586_effort.py`
Source: `BioRig_LUCID_R586_NATIVE_SKIN78_MUSCLE_EFFICIENCY_2026-10-13.zip`, SHA-256 `44ee7be8f86641cc3ce516893eaa872f0125b732c8b7dfe15adc097e8fdcd364`; 138 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** R586 research: cost-aware neck muscle allocation with native torque envelope.  Immutable R585 baseline and inherited MuJoCo physical assets are never edited. A candidate activation is accepted ONLY if its predicted generalized moments on all six neck/head DOFs closely reproduce the established R585 reference. This is not a claim of validated metabolic efficiency or owner acceptance.

Definitions: `MomentConstrainedAllocator` (L20–76), `run` (L79–128).

### `research/lucid/r586/r586_render.py`
Source: `BioRig_LUCID_R586_NATIVE_SKIN78_MUSCLE_EFFICIENCY_2026-10-13.zip`, SHA-256 `346a58cd99f9b623dd06d51a0e49c4a13cc57a500f0e28813ec58799ee29d58b`; 67 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Native R585 versus new R586 SKIN78 proof. Every frame is real MuJoCo physical state.

Definitions: `capture` (L22–38).

### `research/lucid/r586/test_r586.py`
Source: `BioRig_LUCID_R586_NATIVE_SKIN78_MUSCLE_EFFICIENCY_2026-10-13.zip`, SHA-256 `c0bddbdc1c66400b62abdca0e62a8efb4204c891c8919c5f1d7c14ad18b6cd0d`; 77 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** R586 source, native motion, contact, torque-envelope and SKIN78 gates. No GitHub Actions; native tests explicitly invoked with R586_NATIVE=1.

Definitions: `TestR586` (L12–76).


## R587

### `research/lucid/r587/r587_skin78_long_render.py`
Source: `BioRig_LUCID_R587_NATIVE_24S_VERIFIED_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `910c5f7d5fff234c739084dc1f698d5285313a84928c08141d9ba97d3278ff28`; 93 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** New 24-second SKIN78 VTK captures of real native MuJoCo R586 physics.  No pose interpolation or artistic reconstruction; original SKIN78 mesh SHA checked. R586 motor controller and R585 muscle geometry preserved, no root hold.

Definitions: `capture` (L37–67).

### `research/lucid/r587/r587_whole_body_gate.py`
Source: `BioRig_LUCID_R587_NATIVE_24S_VERIFIED_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `fec05147ebc9b83d35edca21eaa7159ca77cbd418fe31dd50705436331b22766`; 77 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** R587 physical and rendered-state acceptance gate.  Explicitly prevents past false positives from pelvis-only "settled" labels. Numeric pass does not imply visual, anatomical or clinical validation.

Definitions: `inspect_native` (L14–37), `check_render` (L39–61), `main` (L63–75).

### `research/lucid/r587/test_r587.py`
Source: `BioRig_LUCID_R587_NATIVE_24S_VERIFIED_CODE_EVIDENCE_2026-10-13.zip`, SHA-256 `3eb91da2d354514f3d663d5aedbb8b2b50e55bbffe3abe7c47721817e9ff82c6`; 59 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** (no module-level docstring)

Definitions: `WholeBodyGateTests` (L7–57).


## R588

### `research/lucid/r588/r588_probe.py`
Source: `BioRig_LUCID_R588_ARM_CONTACT_ACTUAL_RENDER_EVIDENCE_2026-10-13.zip`, SHA-256 `e000a713e9747de6ba5ff031951eb32523fe38065b69c7c6351f923b460c25b6`; 125 lines; declared topic `OBSERVER`.

**Author statement (source docstring; not independently verified):** R588 read-only high-frequency native contact/actuator diagnostics for R587.

Definitions: `discover` (L9–15), `ledger` (L20–41), `run` (L43–117).

### `research/lucid/r588/r588_render.py`
Source: `BioRig_LUCID_R588_ARM_CONTACT_ACTUAL_RENDER_EVIDENCE_2026-10-13.zip`, SHA-256 `7ff2dea15f8da9cd8e1cb07a757c61287873cb151cf4bb218397d0e5f1b50f4f`; 69 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Real SKIN78 native R587 against isolated R588 arm collision/passive-damping experiment. 31 captured frames per condition, 0-3 seconds, no interpolation, no pose edit.

Definitions: `build_seat` (L25–31).

### `research/lucid/r588/test_r588.py`
Source: `BioRig_LUCID_R588_ARM_CONTACT_ACTUAL_RENDER_EVIDENCE_2026-10-13.zip`, SHA-256 `05568886edcc3874c2c792bb2ab0cb578b33e7616a58a41833f84354f44bfe2d`; 57 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** Real MuJoCo arm-seat collision regression; no Actions, no pose teleportation.

Definitions: `arm_metrics` (L9–12), `ArmContactRegressions` (L14–56).


## R589

### `R589/r589_arm_landing.py`
Source: `BioRig_LUCID_R589_SKIN78_MUSCLE_LANDING_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `5a6a30f7ed93410abf56aa774c1e47ef5f8653735c64d506b799f59dfc1c336c`; 166 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** Muscle-controlled bilateral arm descent and contact: no global joint damping, no geometry, seat/contact, root locks, replayed scripted pose, or rendered edits. Cloned native R586 SKIN78/MuJoCo model; no modifications to frozen files.

Definitions: `smooth` (L28–30), `ArmLanding` (L32–85), `run` (L88–150).

### `R589/r589_capture_native.py`
Source: `BioRig_LUCID_R589_SKIN78_MUSCLE_LANDING_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `26ae9885e743c32a0afce0aef4d4d6f347c8aaa69f819f53d6a7975f6d38e60e`; 38 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** Persist reproducible *native MuJoCo qpos* for SKIN78 rendering separately. Physical states are captured during continuous simulation, not reconstructed from pose keys, not interpolated, not altered after simulation.

No top-level named function or class definitions found.

### `R589/r589_render_saved_native.py`
Source: `BioRig_LUCID_R589_SKIN78_MUSCLE_LANDING_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `4b78530d2c9dd896ebcf4c017d84329a4f22aa6cac96def803b7ab1582765f5c`; 70 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Render exactly captured continuous native MuJoCo qpos, original SKIN78. No pose interpolation, physics rerunning, animation synthesizer, or modified mesh.

No top-level named function or class definitions found.

### `R589/test_r589.py`
Source: `BioRig_LUCID_R589_SKIN78_MUSCLE_LANDING_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `5708af7ae66733da36bcf9c39c1ece9c56ba226eb984695794ca88ac378aa928`; 81 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** R589 native contact/head checks. No GitHub Actions, no skinned-image substitution.

Definitions: `R589MotorGates` (L10–79).


## R590

### `r590_settled_capture.py`
Source: `BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `bbc5218777d174b9506df8c2e57116ddb7f2dea0e7990025141051dbb038e77d`; 68 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** 24s native R589 muscle plant, 12s physical settling -> 12s steady-state camera.  No pose keyframes, no joint teleportation, no seat-geometry or material edits. The rig physically traverses the complete 24 seconds in MuJoCo; the 12-24s segment is only redefined as the next **experiment** time window. The full 0-12s warmup remains part of documented runtime and event history.

Definitions: `on_frame` (L25–35).

### `r590_rest_restart.py`
Source: `BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `3ed8765c1e76b774376f9f29792a2c643070244d84a69f292356e0ad8c50af68`; 104 lines; declared topic `OTHER`.

**Author statement (source docstring; not independently verified):** Reproducibly instantiate a *physically settled* 84-muscle state.  Source: exactly captured MuJoCo state at t=12 s from an uninterrupted R589 24-second run; no pose authoring, no root constraints, no synthetic forces. Acceptance requires independent replay to stay close to the same uninterrupted physical continuation; do not confuse an assigned qpos with a valid stable state.

Definitions: `setup` (L26–53), `continue_native` (L55–97).

### `r590_render_settled.py`
Source: `BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `f5221ac7d8a39b3a7e46075e59b22bbe0faa37ba586eccdc0ea172a2be6e9ce3`; 65 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Original Skin78 / VTK renderer using EXACT 12-24s native MuJoCo qpos. No interpolated poses, no image-generation, no physics/body modification.

No top-level named function or class definitions found.

### `r590_render_rest_restart.py`
Source: `BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `fd54bf9bcaae93681cb2175d3c55691a5e6af5204d9453f6ee240734d34b10c5`; 90 lines; declared topic `RENDER`.

**Author statement (source docstring; not independently verified):** Native SKIN78: physically settled scene under matched 0 and +120 N pushes. Frames loaded byte-for-byte from native MuJoCo qpos; no pose interpolation. Original T-pose shown separately as cause analysis, with matching camera.

Definitions: `render` (L33–38).

### `test_r590.py`
Source: `BioRig_LUCID_R590_SETTLED_RESTART_NATIVE_EVIDENCE_2026-10-13.zip`, SHA-256 `d9a4c5009c37119c616ec7d4af62bdb446aabb2ce34e84ca66a49d8626aacbee`; 84 lines; declared topic `TEST`.

**Author statement (source docstring; not independently verified):** R590 tests: full native state provenance and contact-safe settled restart. Only local execution; NEVER GitHub Actions or model source changes.

Definitions: `R590Gates` (L12–82).


## Archive reuse and source drift (SHA-evidenced)

Same basename alone does not imply identical code. Exact identities and variants are in `VERSION_SNAPSHOT_REUSE_AND_HASH_CONFLICTS.json`. Select examples:

- `r576_longhorizon.py`: 4 archived instances, **1 distinct SHA256 content variants** across R576, R577, R578, R580.
- `r577_tonic_support.py`: 3 archived instances, **1 distinct SHA256 content variants** across R577, R578, R580.
- `r578_feedback.py`: 2 archived instances, **1 distinct SHA256 content variants** across R578, R580.
- `r579_controller.py`: 2 archived instances, **1 distinct SHA256 content variants** across R579, R580.
- `r579_synergy.py`: 2 archived instances, **1 distinct SHA256 content variants** across R579, R580.
- `r582_wrench.py`: 2 archived instances, **1 distinct SHA256 content variants** across R582, R582.
- `r582_controller.py`: 2 archived instances, **1 distinct SHA256 content variants** across R582, R582.

A single content SHA across copies proves exact archived source reuse; it **does not** prove controller configuration, physical model, initial state or executed path equality. When multiple content variants appear, inspect a line-by-line diff; do not silently select the newest filename.

## Unresolved historical and runtime connections

1. R583 source bytes are remotely visible and blob-pinned but not included as local archive entries in this checkpoint; no local AST line ledger or physics replay can be claimed for them.
2. Tests and README assertions are evidence that experiments were *described* and in some cases locally logged, not a universal behavioral proof.
3. Cross-version call wiring is sometimes via `sys.path` manipulation and direct module imports. A syntactic import does not mean every sibling checkpoint is integrated.
4. Original R574 semantic/game/planner and rich whole-body QP remain distinct from R590 root execution unless specifically called in that physical lane.
5. First-bad regression requires true Git parentage and matched native SKIN78 recordings; no first-bad claim is made here.
