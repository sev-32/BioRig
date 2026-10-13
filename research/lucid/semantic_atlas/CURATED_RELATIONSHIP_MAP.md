# Source-anchored curated causal/interface relationship matrix



These explicit source/target relationships extend automatic AST edges with semantic meaning. **Status** distinguishes a direct source contract from intended, unverified architecture. No source-only citation proves the behavior is validated.



| From | To | Relationship | Source basis / epistemic status |

| --- | --- | --- | --- |

| `game_intent.py` | `planner.py` | defines-input-to | direct import + data conversion |

| `game_intent.py` | `game_runtime.py` | cross-layer-contract | architecture intent; not validated end-to-end |

| `planner.py` | `neuro.py` | plan-to-physical-control | candidate intended integration |

| `core_steering.py` | `core_steering_runtime.py` | primitive-to-core-task | candidate intended integration |

| `core_steering_runtime.py` | `neuro.py` | writes-task-inputs | source interface |

| `neuro.py` | `physbody.py` | controls-physical-plant | architectural physical pathway |

| `physbody.py` | `semantic.py` | bridges-body-coordinate-semantic | distinct realization authorities |

| `physbody.py` | `pipeline.py` | state-to-render-geometry | cross-representation candidate |

| `pipeline.py` | `skinning.py` | deforms-surface | direct import |

| `pipeline.py` | `render.py` | presents-actual-pose | runtime consumer candidate |

| `semantic.py` | `anatomy.py` | semantic-joint-constraints | direct design family |

| `neuro.py` | `priority.py` | optimizes-priorities | direct import |

| `muscle_allocator_r58.py` | `neuro.py` | allocates-competing-task-demands | candidate parallel approach |

| `whole_body_sense_r511.py` | `neuro.py` | sensor-to-feedback | semantic subsystem relationship |

| `proprioception_r510.py` | `whole_body_sense_r511.py` | sensory-development | source historical continuity candidate |

| `motor_synergy_memory_r516.py` | `safe_motor_memory_r517.py` | memory-safety-extension | source historical continuity candidate |

| `contact_flight_r46.py` | `posture_stabilization_r51.py` | feedback-family | source temporal relationship |

| `posture_stabilization_r51.py` | `run_r551.py` | restabilization-ancestor | needs dynamic proof |

| `physbody.py` | `run_r551.py` | instantiates-native-rig | source calls and conceptual mapping |

| `r562_settling.py` | `r574_intention.py` | label-defines-training-objective | evaluation semantic dependence |

| `r572_paired.py` | `r574_intention.py` | training-source-evidence | direct import |

| `r574_intention.py` | `r575_latency.py` | high-level-latency-overlay | experimental continuation |

| `r574_evaluate.py` | `r576_longhorizon.py` | frozen-benchmark-reference | source import |

| `r562_settling.py` | `r576_longhorizon.py` | reuses-pulse-coordinator | source import |

| `r577_tonic_support.py` | `r578_feedback.py` | changes-support-estimator | source import |

| `r578_support.py` | `r578_feedback.py` | read-only-contact-observer | direct import |

| `r577_tonic_support.py` | `r579_synergy.py` | redistributes-muscle-channels | source import |

| `r579_synergy.py` | `r580_adaptive_synergy.py` | adaptive-channel-recruitment | source import |

| `r580_adaptive_synergy.py` | `r581_controller.py` | adds-hip-oblique-support-controller | source import |

| `r581_support.py` | `r581_controller.py` | contact-centroid-observer | direct import |

| `r581_controller.py` | `r582_controller.py` | changes-contact-observer | source-version continuity |

| `r582_wrench.py` | `r582_controller.py` | wrench-to-motor-allocation | direct import |

| `r584_solver_config.py` | `r584_replay.py` | model-solver-option | direct import |

| `r585_neck_repair.py` | `r586_effort.py` | neck-optimizer-efficiency | source import |

| `r586_effort.py` | `r587_whole_body_gate.py` | extends-full-body-gates | source/orchestration relation |

| `r587_whole_body_gate.py` | `r588_probe.py` | test-contact-impacts | test descendant conceptual |

| `r588_probe.py` | `r589_arm_landing.py` | replaces-passive-damping-proxy | experimental response |

| `r589_arm_landing.py` | `r590_settled_capture.py` | separate-landing-from-rest | test task decomposition |

| `r590_settled_capture.py` | `r590_rest_restart.py` | physical-snapshot-restart | tested state dependence |

| `r590_rest_restart.py` | `r590_render_rest_restart.py` | render-stored-native-state | renderer input |

| `game_runtime.py` | `render.py` | physics-vs-presentation-separation | architectural contract |



## Full explanations



**1. defines-input-to.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/game_intent.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/planner.py`. GameIntent.to_locomotion_intent validates world velocity and constructs LocomotionIntent; speed and heading become planning inputs. **Status:** direct import + data conversion.

**2. cross-layer-contract.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/game_intent.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/game_runtime.py`. Game-facing intent and engine-neutral WorldBodyState are different contract types; intent must never replace authoritative world-body state. **Status:** architecture intent; not validated end-to-end.

**3. plan-to-physical-control.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/planner.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py`. CentroidalPlan proposes COM/DCM support path to muscle controller, but planner explicitly disclaims validated gait. **Status:** candidate intended integration.

**4. primitive-to-core-task.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/core_steering.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/core_steering_runtime.py`. Core primitives represent semantic action; runtime bridge translates core COM/orientation target to controller task fields; exact primitive dispatcher must be checked. **Status:** candidate intended integration.

**5. writes-task-inputs.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/core_steering_runtime.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py`. CoreSteeringRuntime.apply writes ctrl.com_goal, ctrl.com_axis_scale and ctrl.R_star; link to ctrl implementation must be confirmed at runtime. **Status:** source interface.

**6. controls-physical-plant.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/physbody.py`. WholeBodyMuscleController requests muscle excitation using sensed MuJoCo body state and actual actuator/mass/contact properties. **Status:** architectural physical pathway.

**7. bridges-body-coordinate-semantic.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/physbody.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/semantic.py`. Native generalized state maps to semantic joint state; authoritative physics cannot be silently replaced by Semantic51 reference pose. **Status:** distinct realization authorities.

**8. state-to-render-geometry.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/physbody.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/pipeline.py`. Physical qpos to original CausalRig pose is required for real skinned native renderer; demands explicit correspondence and checksum. **Status:** cross-representation candidate.

**9. deforms-surface.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/pipeline.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/skinning.py`. Original canonical Skin78 character deformation, not a replacement mesh. **Status:** direct import.

**10. presents-actual-pose.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/pipeline.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/render.py`. Renderer may show committed canonical mesh; visual frames must carry native qpos provenance. **Status:** runtime consumer candidate.

**11. semantic-joint-constraints.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/semantic.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/anatomy.py`. Semantic51 DOF conventions and anatomical constraints are separate from muscle-generated forward dynamics. **Status:** direct design family.

**12. optimizes-priorities.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/priority.py`. Priority solver resolves task weights over anatomical muscle and contact force variables. **Status:** direct import.

**13. allocates-competing-task-demands.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/muscle_allocator_r58.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py`. R58 allocator reduces conflicting muscle demands; code does not prove it is wired into every neural controller iteration. **Status:** candidate parallel approach.

**14. sensor-to-feedback.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/whole_body_sense_r511.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py`. Proprioceptive tactile/body observations should feed motor feedback; runtime wiring must be established. **Status:** semantic subsystem relationship.

**15. sensory-development.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/proprioception_r510.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/whole_body_sense_r511.py`. R510 plantar/proprioception and R511 whole-body tactile sensing concern related sensory fields. **Status:** source historical continuity candidate.

**16. memory-safety-extension.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/motor_synergy_memory_r516.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/safe_motor_memory_r517.py`. Learned synergy histories and safeguarded residual memory are related but distinct systems. **Status:** source historical continuity candidate.

**17. feedback-family.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/contact_flight_r46.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/posture_stabilization_r51.py`. Muscle moment/feedback helpers provide an earlier contact-aware postural controller family. **Status:** source temporal relationship.

**18. restabilization-ancestor.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/posture_stabilization_r51.py` → `LUCID_R552_WORKSPACE/R551_ACTIVE_RECOVERY/run_r551.py`. Seated native research inherits motor stabilization/feedback pathways; verify call graph before claiming equivalence. **Status:** needs dynamic proof.

**19. instantiates-native-rig.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/physbody.py` → `LUCID_R552_WORKSPACE/R551_ACTIVE_RECOVERY/run_r551.py`. Native seated rig consumes MuJoCo mass/inertia/muscle body; exact model source and solver settings are part of proof. **Status:** source calls and conceptual mapping.

**20. label-defines-training-objective.** `R562_SETTLING_CONTROL/r562_settling.py` → `native/r574_intention.py`. R562 is_settled excludes head/skin; R574 hazard/settle learned labels cannot establish full-body stability. **Status:** evaluation semantic dependence.

**21. training-source-evidence.** `R572_PAIRED_FORCE_CALIBRATION/r572_paired.py` → `native/r574_intention.py`. R574 fits separate treatment outcomes from paired records, not arbitrary multi-goal movement. **Status:** direct import.

**22. high-level-latency-overlay.** `native/r574_intention.py` → `R575_SENSOR_LATENCY_PHYSICS/r575_latency.py`. R575 delays selected high-level signals but does not delay inherited low-level muscle feedback. **Status:** experimental continuation.

**23. frozen-benchmark-reference.** `native/r574_evaluate.py` → `R576/r576_longhorizon.py`. R576 augments post-lock support while keeping R574 choice fixed. **Status:** source import.

**24. reuses-pulse-coordinator.** `R562_SETTLING_CONTROL/r562_settling.py` → `R576/r576_longhorizon.py`. R576 reuse of bounded settling pulses did not prove indefinite equilibrium. **Status:** source import.

**25. changes-support-estimator.** `research/lucid/r577/r577_tonic_support.py` → `research/lucid/r578/r578_feedback.py`. R578 adds COM/contact-pressure diagnostics to original tonic muscle overlay. **Status:** source import.

**26. read-only-contact-observer.** `research/lucid/r578/r578_support.py` → `research/lucid/r578/r578_feedback.py`. COM/contact-pressure measured and used by feedback; original pressure heuristic incomplete. **Status:** direct import.

**27. redistributes-muscle-channels.** `research/lucid/r577/r577_tonic_support.py` → `research/lucid/r579/r579_synergy.py`. R579 decomposes 4-muscle lateral group into individually named hip/trunk channels. **Status:** source import.

**28. adaptive-channel-recruitment.** `research/lucid/r579/r579_synergy.py` → `research/lucid/r580/r580_adaptive_synergy.py`. R580 changes fixed profile into sensed lateral displacement+velocity adaptive recruitment. **Status:** source import.

**29. adds-hip-oblique-support-controller.** `research/lucid/r580/r580_adaptive_synergy.py` → `research/lucid/r581/r581_controller.py`. R581 builds a two-channel controller measuring physical COM vs support pressure centroid. **Status:** source import.

**30. contact-centroid-observer.** `research/lucid/r581/r581_support.py` → `research/lucid/r581/r581_controller.py`. R581 contact-pressure estimator discounts tangential vertical friction support at thigh/seat. **Status:** direct import.

**31. changes-contact-observer.** `research/lucid/r581/r581_controller.py` → `research/lucid/r582/r582_controller.py`. R582 replaces one-dimensional pressure approximation with signed 3D contact wrench; numerical estimates differ. **Status:** source-version continuity.

**32. wrench-to-motor-allocation.** `research/lucid/r582/r582_wrench.py` → `research/lucid/r582/r582_controller.py`. R582 supplies corrected contact force and moment measurements. **Status:** direct import.

**33. model-solver-option.** `r584_solver_config.py` → `r584_replay.py`. R584 no-slip iterations configure solver, not muscle strength or kinematic pose constraints. **Status:** direct import.

**34. neck-optimizer-efficiency.** `R585/r585_neck_repair.py` → `research/lucid/r586/r586_effort.py`. R586 improves neck muscle excitation allocation while retaining corrected antagonistic geometry. **Status:** source import.

**35. extends-full-body-gates.** `research/lucid/r586/r586_effort.py` → `research/lucid/r587/r587_whole_body_gate.py`. R587 extends valid 12s head stabilization to 24s and adds explicit whole-body/head checks; verify renderer lineage. **Status:** source/orchestration relation.

**36. test-contact-impacts.** `research/lucid/r587/r587_whole_body_gate.py` → `research/lucid/r588/r588_probe.py`. R588 measures arm-seat chatter missed by coarser whole-body gates. **Status:** test descendant conceptual.

**37. replaces-passive-damping-proxy.** `research/lucid/r588/r588_probe.py` → `R589/r589_arm_landing.py`. R589 attempts active shoulder muscle braking rather than 10x joint damping. **Status:** experimental response.

**38. separate-landing-from-rest.** `R589/r589_arm_landing.py` → `r590_settled_capture.py`. R590 uses R589 native physical continuation to generate a physically settled seated state. **Status:** test task decomposition.

**39. physical-snapshot-restart.** `r590_settled_capture.py` → `r590_rest_restart.py`. R590 restores qpos/qvel/act and correct posture target/controller previous state; naive reset caused fresh impact. **Status:** tested state dependence.

**40. render-stored-native-state.** `r590_rest_restart.py` → `r590_render_rest_restart.py`. Original SKIN78 render follows saved native qpos states and collision seat, never interpolated synthetic poses. **Status:** renderer input.

**41. physics-vs-presentation-separation.** `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/game_runtime.py` → `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/render.py`. Camera presentation cannot alter WorldBodyState root/collision; complete-character renderer reads physical reality. **Status:** architectural contract.


## Not found in current pinned local inputs

- `r582_controller.py` → `r583_friction_probe.py`: `R583 perturbs only seat/floor friction while keeping controller and body state fixed.` (may exist remotely on GitHub, but not in available archive inputs).

- `r583_friction_probe.py` → `r584_replay.py`: `R584 preserves friction values and changes additional MuJoCo no-slip solver iterations in a cloned model.` (may exist remotely on GitHub, but not in available archive inputs).