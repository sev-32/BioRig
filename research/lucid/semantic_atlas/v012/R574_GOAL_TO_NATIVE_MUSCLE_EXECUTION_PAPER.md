# BioRig / LUCID — Semantic Atlas V012: frozen goal decisions to native muscle channels

**Research paper and reproducible source-truth audit.** This is a continuation of V011, with no changes to any native physics/controller source. Its main advance is a **complete, independently replayed archived goal-decision chain** and a code-and-measurement crosswalk to the native 84-channel plant. It is not a new successful reaching or balancing demonstration.

## 1. The actual exercised R574 causal path

The frozen R574 evaluation harness (`R574_INTENTION_AND_AVERSION/r574_evaluate.py:34–68`) constructs native paired physical scenes and measures **10 sensed values** at *physical time 60 ms*, before added corrective excitation. An `IntentionAgent` (`r574_intention.py:112–143`) reads that observation and a **named goal contract**, obtains saved ExtraTrees-based predictions, applies priority-ordered safety vetoes, then emits **one of two** literal actions: `none` or `R28` (`r574_intention.py:20`). It does **not** emit a joint target, wrist reach, arbitrary hand location, 84-muscle vector, generated action sequence, or a continuous multigoal plan.

```text
user-specified named goal contract + 60 ms native observation
  -> frozen OutcomeMemory.forecast(state)  [trained on 29 paired rows]
  -> novelty and veto threshold evaluation
  -> score(R28 relative to no pulse)
  -> literal action name: none | R28
  -> R569 TimedPulse, 40 ms update cadence (R28 only)
  -> R551 pulse_for(model, 'right_lateral') [exact four muscle IDs]
  -> native baseline muscle stabilizer + additive excitation delta
  -> clamp [0,1] -> MuJoCo data.ctrl[84]
  -> delayed muscle activation and force, native dynamics and seat contact
  -> physical outcome over 8 seconds (archived R574 paired run)
```

The **source-pinned execution edge** is the R574 evaluation's `selected=agent.decide(...)`, followed by `phy.rollout(...)`, the R569 `TimedPulse` execution, R551 `step_perturbed()` command composition and `mj.mj_step()`; these are not just similarly named modules.

## 2. The exact action/muscle interface

`R569_TERMINAL_CURRICULUM/r569_temporal.py:27–38` defines `R28=((.06, 'R', .28, .04),)`—a 60 ms onset, 280 ms full-duration target, 60 ms rise and 120 ms release ramp. `r569_temporal.py:56–80` updates excitation **every 40 ms**, vetoes the pulse within its update when measured `armsSeatN>=40 N` or `rootTiltDeg>=39°`, and clips incremental muscle command at 0.04. `r569_temporal.py:98–112` advances the native plant at **2 ms** steps via R551.

The exact right-lateral actuator names come from `LUCID_R552_WORKSPACE/R551_ACTIVE_RECOVERY/run_r551.py:34–45`, with lookup by native MuJoCo actuator name at `:65–73`:

1. `m_right_quadratus_lumborum_iliolumbar`
2. `m_right_quadratus_lumborum_iliocostal`
3. `m_right_gluteus_medius`
4. `m_right_external_oblique`

R551 `run_r551.py:75–90` **adds** the pulse to recomputed base muscle excitation (`ctrl = clip(base + delta, 0,1)`), rather than replacing all base excitation with a new R574 vector. This matters: the later R589 controller instead **overwrites** four arm channels after its base update; R590 rest-restart overwrites ten neck channels and has no R574 goal selection at all. These are separate execution paths and command arbitration contracts.

**Measured pulse-history proof:** `FULL_2800_PULSE_TIMELINE_REPLAY.csv` contains every saved R574 restoration pulse command, 14 scenes × 200 updates each. A separately written source-derived waveform reproduction matched all **2,800** recorded `maxExtra` values with a maximum absolute residual of **0.0** (binary64 as read and computed here). Zero of those replayed update points crossed the pulse-internal arm/tilt veto thresholds. This validates the **logged command envelope**, not a fresh full physics replay.

## 3. Decision score and veto priority

`r574_intention.py:103–143` calculates the predicted advantage as:

```text
fallWeight * (P(hazard | none) - P(hazard | R28))
+ settleWeight * (P(settled | R28) - P(settled | none))
- armHazardWeight * P(severe arm contact | R28)
- actionEffortCost
```

The first veto encountered wins. In source order: *current measured arm contact or tilt*, *distance from prior training states*, *predicted R28 hazard or predicted severe arm contact*, then *insufficient expected advantage*. When all pass, R28 is selected. The `preserve_safe_posture` contract raises the expected-advantage threshold and effort penalty and tightens the hazard veto, so it generally selects less intervention.

`28_ORIGINAL_GOAL_DECISION_REPLAYS_AND_VETOES.csv` executes the **original frozen R574 dataclass, goal contracts, score, and decision AST**, not a reimplemented chooser, on the same archived observations and forecast values. It checks complete equality of all **28 recorded decision dictionaries**, including labels, veto reasons and probability fields. The original ExtraTrees models were **not refitted** by V012; their output probabilities are replayed from the preserved records.

## 4. The 14 held-out native physical outcomes (archived, not re-simulated)

The following is reconstructed directly from all fourteen immutable `R574_LOCKED_SCENE_XX.json` receipts. `hazard` is the original R569 native rollout criterion: arm-seat ≥50 N, unexpected floor ≥50 N, root tilt ≥45°, or sustained loss of seat/foot support. Restoration and preservation names are evaluation goal contracts, **not independent model body architectures**.

| Scene | Seat half-width (m) | External X push (N) | Restore choice | Preserve choice | Neutral hazard | Restore hazard | Rescue |
|---:|---:|---:|---|---|---:|---:|---:|
| 0 | 0.131 | +0 | none | none | 0 | 0 | 0 |
| 1 | 0.131 | -120 | R28 | none | 0 | 0 | 0 |
| 2 | 0.131 | +120 | R28 | none | 0 | 0 | 0 |
| 3 | 0.131 | -235 | none | none | 1 | 1 | 0 |
| 4 | 0.131 | +235 | R28 | R28 | 1 | 0 | 1 |
| 5 | 0.131 | -365 | none | none | 1 | 1 | 0 |
| 6 | 0.131 | +365 | none | none | 1 | 1 | 0 |
| 7 | 0.175 | +0 | none | none | 0 | 0 | 0 |
| 8 | 0.175 | -120 | none | none | 0 | 0 | 0 |
| 9 | 0.175 | +120 | R28 | none | 0 | 0 | 0 |
| 10 | 0.175 | -235 | R28 | none | 1 | 0 | 1 |
| 11 | 0.175 | +235 | R28 | R28 | 0 | 0 | 0 |
| 12 | 0.175 | -365 | none | none | 0 | 0 | 0 |
| 13 | 0.175 | +365 | none | none | 1 | 1 | 0 |

Across these 14 scenes: **six** restore-goal R28 actions, **two** preserve-goal R28 actions, **four** scenes where goals select differently, **two** neutral-to-safe-and-settled rescues with restoration, and **zero** new hazards in this small hold-out. The two rescues occur at **scene 04** (0.131 m seat half-width, +235 N) and **scene 10** (0.175 m, −235 N), showing the same right-lateral pulse is not a general signed directional response. The model's predicted action forecasts and the actual action outcomes are *different data layers*; positive predicted utility cannot be counted as observed benefit.

The frozen research summary also reports **R569** took 12 actions and rescued three hazards; R574 restoration took six actions and rescued two. This is a different selectivity/safety trade-off, not proof R574 dominates every older controller.

## 5. Coupling to the native 84 × 102 time-response atlas (V011)

`R574_R28_FOUR_MUSCLE_TO_V011_102_DOF_DYNAMIC_CROSSWALK.csv` joins each of the **four exact R28 muscle names** to the native actuator names measured in V011: 4 actuators × 102 generalized velocity coordinates × 3 time samples = **1,224 signed dynamic measurements**. The joint label, linear/angular velocity unit and native actuator numeric ID are retained in every row.

**These are not replicas of the R574 physical pulse.** V011 stimulated one muscle at a time with a +0.12 excitation perturbation from the later R590 seated state; R574 commands four muscles together at up to +0.04 excitation in its earlier held-out scenario. The V011 effects may not be added together, divided by three, or treated as a faithful R574 trajectory: contact and muscle dynamics are nonlinear, and the starting state and active posture controller differ. This is a validated *identity/measurement crosswalk*, not an inferred behavioral equivalence.

## 6. Explicit historical integration gap: R574 vs R590

`r590_rest_restart.py` in the immutable R590 archive contains no `IntentionAgent.decide` call, no goal contract access, and no `ArmLanding.update()` invocation. The **whole body is still physically actuated**: its seated controller writes base excitation, with R586 neck commands as final override; but its goal-driven pulse selection is not wired to R574's agent. R590's continuous-capture source does call R589's candidate controller, while the restart path does not. 'Available in the archive' must never be presented as 'executing in the active program'.

To establish genuine seamless intent-to-muscle execution in a future protected experiment, a new integration seam would have to define: target and frame, measured state timestamp, data freshness, action/veto type, muscle command writer priority, update cadence, controller memory, safe command composition, native physical receipt and visible SKIN78 acceptance. This document **does not implement such an integration or propose discarding the existing neck/seat fixes**.

## 7. Reliability boundary

**Independently reproduced here:** original source SHA and evaluation lock; 28 existing frozen decision dictionaries using original AST; 14 saved paired-hazard outcomes and their original summary totals; all 2,800 recorded research pulse commands to the exact source-defined envelope; four-actuator identity join against V011 native pulse measurements; confirmed no original goal-decision call in the R590 restart source.

**Not reproduced here:** refitting ExtraTrees, new 8-second native R574 physics trajectories, skin animation, subjective autonomy, closed-loop reaching, general risk calibration, out-of-distribution reachability, or a fully serialized MuJoCo-plus-controller state rewind.

### Original frozen source SHA-256 anchors

| Source alias | Frozen archive path | SHA-256 |
|---|---|---|
| `agent` | `R574_INTENTION_AND_AVERSION/r574_intention.py` | `08d06b1373901bbbccac2c60e706ad5968767ac0ff231c42dd0ffebe3dd8de8a` |
| `eval` | `R574_INTENTION_AND_AVERSION/r574_evaluate.py` | `79437f0817cebe7254b04a483fa90556b2fd06f74e3dc8bd2701e3199a8a5811` |
| `pulse` | `R569_TERMINAL_CURRICULUM/r569_temporal.py` | `734f7acb09755f704c99cd06d83dce0f49e69186597637455c5ab6559633a514` |
| `base` | `LUCID_R552_WORKSPACE/R551_ACTIVE_RECOVERY/run_r551.py` | `702fb4e7b4eecc4f6021e3857e87c9da0c5c141b1e70d79b77a30ef7abb06b57` |
| `r572` | `R572_PAIRED_FORCE_CALIBRATION/r572_paired.py` | `9fda219e514529c14d6082f378a29abc390cf2d930f147c27ac62a6a4c373003` |

The exact frozen R574 archive SHA-256 is `21e0c354023badd40485840296e09034809ae4eb055fd926eff39ac0b8700701`. V011's native time-response matrix SHA-256 is `ab73e26fa36a89dfd92b7e8a01a61b21f99d20a7f410512b8f49d85bb9700541`. The reference R590 archive SHA-256 is `42c080f6a0c78042882bd27c5309d8158709a825a3fc6399ed07a5416f4679a7`. Their bytes and identities are tracked independently; not copied into GitHub's small documentation tree.

## 8. Next complete-system audit questions

- Which earlier planner and `WholeBodyMuscleController` APIs actually run together under an original supported movement scenario, and which are only declared?
- Which controller writes (overwrite/add/skip) have well-defined global arbitration when intent, postural response, arm landing and neck stabilization act simultaneously?
- Does a snapshot include the exact intent/forecast state, base controller memory, neck allocator memory, MuJoCo derivative/cache state and native muscle excitation? If not, list the missing fields and their effect.
- Which goal targets have a defined coordinate frame, physical unit, anatomical reachability check, hazard monitor and **native target-completion criterion**?
- How does native seat contact stiffness/friction change the probability of contact chatter during a purposeful move? Only tested physics may answer this.

**Freeze:** no legacy source edited; no GitHub Actions; no rollback; no newly generated render claimed.
