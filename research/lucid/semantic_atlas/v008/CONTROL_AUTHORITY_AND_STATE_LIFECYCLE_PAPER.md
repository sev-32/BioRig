# BioRig / LUCID V008 — executable path, state ownership, and controller authority

**Status:** source-exact static evidence, not instrumented MuJoCo runtime. No BioRig executable file was changed.

This audit pins **69 reviewed semantic claims** to exact raw archive bytes and AST scopes in **11 distinct modules**, with **14 state contracts** and **17 directed, explicitly qualified cross-module links**.

## 1. The two R590 entrypoints are different experiments

### Continuous 24-second capture (`cap590`)

The 24-second capture explicitly calls `reference.run(T_FINAL,candidate=True,...)` (C590A). In R589 that branch constructs `ArmLanding` (A589F), computes a shoulder-moment correction (A589C–E), refreshes it at the discrete controller cadence (A589G), and writes **base → arm → neck** muscle commands (A589H–J) before `mj_step` (A589L). The 12–24 second observation period is after an actual physical 0–12 second initial descent; later visual stability does not erase the early contact events.

### Restored 12-second evaluation (`replay590`)

The restart imports R589 (R590A), but the active loop restores `qpos`, `qvel` and `act` (R590D–F), computes the inherited base controller directly (R590I), periodically updates R586 neck allocation (R590J), writes **base → neck** (R590K) and advances the native solver (R590O). **It does not construct or call `ArmLanding` in the inspected `continue_native` loop.** The import does not imply that transient arm control is active. This is a critical version-integration distinction.

## 2. What owns the actuator channel?

The physical actuator command is `MjData.ctrl` (dimensionless excitation for these muscle actuators), not the desired joint angle, generalized torque, optimizer reference activation, or cached controller command. Within R589, individual arm channels can override the base posture controller; the neck vector writes last. Within R590 restart, there are no arm overwrites. These are *ordered program assignments*, not inferred runtime efficacy.

A controller computing a correct `u` is not necessarily the controller whose `u` reaches the plant: the last write to each overlapping actuator channel before `mj_step` wins. The channel-overlap question is left open until actuator IDs and runtime indexing are inspected. The V008 matrix makes that missing check explicit instead of assuming disjoint arm/neck sets.

## 3. State is a typed causal boundary, not a single pose

MuJoCo `qpos` (position), `qvel` (generalized velocity), `act` (internal muscle activation), and `ctrl` (excitation request) are different. `qfrc_applied` and `xfrc_applied` are separately supplied force channels. The restore copies position, velocity and activation but reconstructs some controller memory; it does not serialize all solver warmstarts, integrator internals or every stateful high-level component. `mj_forward` recomputes derived mechanical values. V004 established the concern; V008 pins the exact mutation sites and ownership in a queryable CSV.

## 4. The goal-to-motion pipeline is not joined in the inspected loop

R574 `IntentionAgent.decide` can choose only `none` or `R28` (G001, G008) in a dedicated evaluation harness (G009). The original `WholeBodyMuscleController` is a richer full-body solver (N001–N005), and the original planner produces desired trajectories (P001). **None of these is invoked in the inspected R590 restart loop**; this is a negative finding scoped to that entrypoint, not a claim that the methods are unused everywhere or that old systems were better.

## 5. Activation is not force; a frame is not proof of forward causality

The R589 arm correction measures current shoulder qpos/qvel (A589C), uses posture-dependent actuator gain (A589D), and writes bounded extra excitation (A589E). That is a limited physical local controller—not general intent. The original skin pipeline can realize prescribed joint targets and estimate inverse muscle demand (K001–K002), while actual R590 qpos snapshots come from native physics (R590P). Any generated animation must retain provenance to know which path produced it.

## 6. Source-pinned relationship map

| Upstream | Downstream | Relationship | Source evidence | Boundary |
|---|---|---|---|---|
| R574 policy | R574 experiment | choice none/R28 | G008 / G009 | connected in evaluation only |
| R574 policy | R590 restart | decision -> ctrl | G009 / R590I | NOT CONNECTED BY THE INSPECTED ENTRYPOINT |
| WholeBodyMuscleController | R590 restart | excitation output | N005 / R590I | ALTERNATIVE CONTROLLER, NOT USED BY THIS ENTRYPOINT |
| Original planner | R590 restart | foot/COM plan -> task rows | P001 / R590I | NOT CONNECTED BY THE INSPECTED ENTRYPOINT |
| R551 base posture | R585 base posture | excitation | S001 / N585B | analogous module, code lineage via imports |
| R585 posture | R586 posture | base excitation | N585B / N586C | same inherited module, neck override different |
| R586 neck allocator | R589 neck update | head excitation | N586B / A589J | R589 imports/executes allocator |
| R589 shoulder muscle | R589 d.ctrl override | arm excitation | A589G / A589I | only candidate and only selected channels |
| R589 base command | R589 arm command | actuator channel priority | A589H / A589I | arm overwrites base |
| R589 arm command | R589 neck command | actuator channel priority | A589I / A589J | neck final override, intersections must be tested |
| R589 native loop | R590 continuous capture | physical state/time | A589L / C590A | continuous 24s includes R589 landing |
| R590 settled snapshot | R590 replay setup | qpos/qvel/act | C590C / R590D | sampled state restore |
| R590 replay posture | R590 replay neck | actuator command priority | R590I / R590K | base overwritten on neck indices |
| R590 restart | R590 arm landing | optional muscle braking | R590A / A589G | NOT EXECUTED by inspected restart loop despite import |
| R590 ctrl | MuJoCo step | excitation -> updated state | R590K / R590O | native plant feedback |
| R590 step | R590 SKIN78 input | native qpos -> pose | R590O / R590P | qpos sampled, renderer separately invoked |
| Original skin pipeline | R590 native model | pose and deformation | K001 / R590P | DIFFERENT rendering path; shared canonical skin is not model-state identity |

## 7. Manually reviewed code witnesses

Each witness below is checked against the **exact source archive SHA**, exact text and line number in `CONTROL_FLOW_LINE_WITNESSES.json`. These statements do not claim branch coverage outside the evidence.

| ID | Module:line | Scope | Physical / program meaning | Unproven boundary |
|---|---|---|---|---|
| G001 | goal:20 | <module> | Decision action universe comprises exactly two research options | Cannot express arbitrary hand target |
| G002 | goal:41 | <module> | Desired seated recovery outcome is declarative | Policy desire is authored, not innate |
| G003 | goal:36 | GoalContract | Measured arm contact can veto action | Threshold does not imply calibrated injury risk |
| G004 | goal:82 | OutcomeMemory.fit | Outcome learner uses observed sensor features | No additional features inferred |
| G005 | goal:92 | OutcomeMemory.fit | Forecast uses small-data tree ensemble | Prediction not physics guarantee |
| G006 | goal:123 | IntentionAgent.decide | Decision queries forecast and novelty | Forecast is not action execution |
| G007 | goal:132 | IntentionAgent.decide | Novelty above threshold suppresses action | Source typo preserved; no undocumented branch |
| G008 | goal:138 | IntentionAgent.decide | Positive selected choice is R28 only | No more general action generation |
| G009 | eval:43 | evaluate | Held-out harness explicitly invokes agent decision | Not evidence seated R590 invokes it |
| S001 | seat551:24 | <module> | R551 uses narrower posture controller | Import alone is not execution |
| S002 | seat551:86 | step_perturbed | R551 applies a corrective pulse over all native actuator commands | Exact contact behavior only from runtime |
| S003 | seat551:89 | step_perturbed | R551 sets external world-space hip force | No synthetic root lock implied |
| S004 | seat551:90 | step_perturbed | R551 integrates real native physics | Not proof of stable motion |
| N001 | plant:196 | WholeBodyMuscleController | Separate full-body muscle controller exists in original code | Not automatically used by research seat loop |
| N002 | plant:227 | WholeBodyMuscleController.__init__ | Relaxed-arm mode can remove arm excitation variables | Conditional; not universal behavior |
| N003 | plant:355 | WholeBodyMuscleController.control | Actuator gains and moment arms map muscle activation to generalized force | Instantaneous approximation, not measured delivery |
| N004 | plant:421 | WholeBodyMuscleController.control | COM capture uses x,z world horizontal axes | Requires correct frame/unit interpretation |
| N005 | plant:525 | WholeBodyMuscleController.control | Whole-body controller converts desired activation into excitation output | Caller must write returned vector to active plant |
| P001 | planner:180 | CentroidalStepPlanner.plan | Original planner computes motion references from state | Plan output is not native execution |
| K001 | skin:311 | CausalRig.step | Pipeline can realize pose without a forward native muscle step | Render-only realization is not causal locomotion |
| K002 | skin:339 | CausalRig.step | Inverse muscle estimation starts from provided pose history | Not proof inferred muscles caused motion |
| K003 | skin:249 | CausalRig.snapshot | Original rig stores its own articulated snapshot contract | Not equivalent to full MuJoCo solver memory |
| N585A | neck585:62 | run | R585 modifies model-local SCM attachment geometry in test model | Geometry change must be audited separately from control |
| N585B | neck585:86 | run | R585 first writes posture excitation | Later overwrite changes winner |
| N585C | neck585:87 | run | R585 conditionally overwrites neck channels | Baseline switch matters |
| N585D | neck585:91 | run | R585 physics runs after control assignment | No guarantee head stable without evidence |
| N586A | neck586:20 | MomentConstrainedAllocator | R586 has a distinct moment-constrained neck allocator | Reference moment is predicted not measured |
| N586B | neck586:112 | run | Neck allocation refreshes every five physics steps | Command persists between refreshes |
| N586C | neck586:113 | run | R586 neck channels override base on each physics step | No joint whole-body multiobjective optimum |
| N586D | neck586:114 | run | Passive applied generalized joint forces have separate writer | Not muscle excitation |
| N586E | neck586:115 | run | Optional lateral hip push acts as external force | No proof robustness beyond tested force |
| N586F | neck586:116 | run | Native physical response follows writes | Rendered pose still requires native qpos |
| A589A | arm589:22 | <module> | R589 arm-descent parameters are a fixed experiment-specific profile | Not general target-language interface |
| A589B | arm589:32 | ArmLanding | R589 introduces an optional transient arm controller | Exists only when candidate truthy |
| A589C | arm589:62 | ArmLanding.update | Arm command compares desired and measured shoulder angle/speed | Single-joint PD proxy is not a whole-body intention solver |
| A589D | arm589:74 | ArmLanding.update | Uses native muscle gain at current actuator state | Cannot assume constant force |
| A589E | arm589:80 | ArmLanding.update | Shoulder excitation supplement is bounded | Only selected muscle channels |
| A589F | arm589:102 | run | R589 arm controller constructed only for candidate mode | Mode dependent |
| A589G | arm589:132 | run | R589 calls arm controller only if constructed | At update cadence, not every physics step |
| A589H | arm589:133 | run | R589 base writes all muscle channels first | Later writes may supersede |
| A589I | arm589:137 | run | R589 arm channels conditionally overwrite base | Neck channels override afterward |
| A589J | arm589:138 | run | R589 neck correction has final muscle-command priority | Potential overlapping channels must be checked |
| A589K | arm589:141 | run | R589 push has bounded active interval | No broad push generalization |
| A589L | arm589:142 | run | R589 commands feed forward physics | Skin render must be evaluated separately |
| C590A | cap590:38 | <module> | R590 continuous capture calls R589 run in candidate mode | Native measured contact must be checked |
| C590B | cap590:29 | on_frame | R590 capture explicitly copies native state | Snapshot not full solver state |
| C590C | cap590:44 | <module> | R590 stores sampled positions velocity and activation | qacc, warmstart, controller caches not included |
| C590D | cap590:48 | <module> | R590 contact-transition measurement reads sampled R589 trace | Sampling not continuous contact proof |
| R590A | replay590:21 | <module> | Restart imports R589 module | Not an execution of ArmLanding |
| R590B | replay590:22 | <module> | Restart accesses R585 through R589 -> R586 symbol chain | Symbols can be imported without running control |
| R590C | replay590:33 | setup | Neutral seated reference captured before loading settled state | Source-specific reference not new optimization |
| R590D | replay590:40 | setup | Copies saved positions into native plant | Position alone is not complete state |
| R590E | replay590:41 | setup | Copies saved generalized velocities | Does not copy full integrator state |
| R590F | replay590:42 | setup | Copies muscle activation state | Not same as excitation control inputs |
| R590G | replay590:44 | setup | Recomputes derived native quantities after state assignment | Warmstart identity not assured |
| R590H | replay590:50 | setup | Reconstructs optimization memory from current activation | Approximate memory restoration, not exact historical history |
| R590I | replay590:81 | continue_native | Restart invokes inherited seat posture controller directly | Does not call original WholeBodyMuscleController |
| R590J | replay590:82 | continue_native | Restart invokes R586 allocator through R589 symbolic chain | No `ArmLanding.update()` in this loop |
| R590K | replay590:83 | continue_native | Restart only uses base and neck writes on native ctrl | ArmLanding absent from this path |
| R590L | replay590:84 | continue_native | Native applied generalized forces set from passive model | Not equal to muscle command |
| R590M | replay590:85 | continue_native | Clears external force per simulation step | Later conditional push overrides zero |
| R590N | replay590:86 | continue_native | Push applied at hip for 120 ms | Does not validate arbitrary disturbances |
| R590O | replay590:87 | continue_native | Plant advances from actual native muscle/controller outputs | Source presence not physics accuracy proof |
| R590P | replay590:72 | continue_native | Render samples derive from native qpos | Sparse qpos samples can miss transient dynamics |
| R590Q | replay590:80 | continue_native | COM based support target reads native derived subtree_com | Only local posture controller uses this target |
| R590R | replay590:77 | continue_native | Reference qref used for posture error | Desired joint error is not a movement goal |
| R590S | replay590:36 | setup | Original neutral horizontal head-hip displacement from reset pose | World horizontal position reference, not posture quaternion |
| N585E | neck585:42 | NeckAllocator.update | R585 reads measured other-actuator force for demand | Native actuator force does not prove anatomical calibration |
| A589M | arm589:110 | run | Arm contact metrics derive from contact ledger function | Not identical to raw data.contact field |

## 8. Remaining executable verification

1. Run instrumented MuJoCo traces from identical initial conditions to verify actual `data.ctrl` writer identity, muscle-channel intersections, and the post-step effect of activation delays.
2. Materialize the complete native runtime (not just code) and compare exact checkpoint physics with the source trace; no such replay is asserted by this V008 artifact.
3. Expand semantic reviews from the current source-pinned critical modules to every historical version and every archived line; the complete static line index already exists but full causal interpretation does not.
4. Investigate optional native forward control of the original whole-body solver with protected modern regression gates; it must not silently replace later verified improvements.

**Version invariants:** original R574 frozen; R585–R590 unchanged; no actions; no generated renders; no claim of universal controller competence.
