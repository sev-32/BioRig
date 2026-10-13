# Source-verified function and mutation boundary catalog

**Static only.** This review accounts for qualified method names and source line locations. A listed read/write is an AST occurrence, not evidence it executes on every step. Nested functions may be double counted inside their enclosing function. Missing reflection/dynamic dispatch is explicitly unknown.

## `R574.goal` — R574_INTENTION_AND_AVERSION/r574_intention.py
Pinned SHA-256 `08d06b1373901bbbccac2c60e706ad5968767ac0ff231c42dd0ffebe3dd8de8a`. 9 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `sha` | 67–67 | `path` | none found |
| `all_training` | 68–73 | `` | none found |
| `feature` | 74–75 | `obs` | none found |
| `OutcomeMemory.__init__` | 78–79 | `self` | none found |
| `OutcomeMemory.fit` | 80–99 | `self, rows` | none found |
| `OutcomeMemory.forecast` | 100–109 | `self, observation` | none found |
| `score` | 111–117 | `forecasts, contract` | none found |
| `IntentionAgent.__init__` | 120–120 | `self, model` | none found |
| `IntentionAgent.decide` | 121–140 | `self, observation, goal` | none found |

## `R574.evaluate` — R574_INTENTION_AND_AVERSION/r574_evaluate.py
Pinned SHA-256 `79437f0817cebe7254b04a483fa90556b2fd06f74e3dc8bd2701e3199a8a5811`. 3 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `frozen` | 16–25 | `` | none found |
| `scenarios` | 27–31 | `lock` | none found |
| `evaluate` | 33–69 | `i, frozen_models` | none found |

## `R562.settle` — R562_SETTLING_CONTROL/r562_settling.py
Pinned SHA-256 `cf6ef15f4374e0d8623eb7231ba3bb35ccb610360271639486b606b2abaa2df1`. 6 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `observation` | 31–36 | `pb, d` | none found |
| `is_settled` | 38–46 | `o, rule` | none found |
| `SettlingCoordinator.__init__` | 49–56 | `self, model, option, rule` | `self.active_group`, `self.active_mask`, `self.active_since` |
| `SettlingCoordinator.update` | 57–96 | `self, t, o` | `self.active_group`, `self.active_mask`, `self.active_since` |
| `SettlingCoordinator.output` | 97–97 | `self` | none found |
| `rollout` | 99–134 | `pb, saved, qref, neutral, world_push_newtons, option, seconds, traces, rule` | none found |

## `R551.run` — LUCID_R552_WORKSPACE/R551_ACTIVE_RECOVERY/run_r551.py
Pinned SHA-256 `702fb4e7b4eecc4f6021e3857e87c9da0c5c141b1e70d79b77a30ef7abb06b57`. 9 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `filehash` | 53–53 | `p` | none found |
| `new_scene` | 54–63 | `width` | none found |
| `pulse_for` | 65–73 | `model, action` | none found |
| `step_perturbed` | 75–92 | `pb, d, qref, neutral, delta, push_world` | `d.ctrl[:]`, `d.qfrc_applied[:]`, `d.xfrc_applied[:]`, `d.xfrc_applied[pb.body_id['Hip'], :3]` |
| `root_tilt_deg` | 94–96 | `pb, d` | none found |
| `decision_features` | 98–113 | `pb, initial, ref, neutral, side, force` | none found |
| `simulate` | 115–162 | `pb, initial, ref, neutral, side, force, action, store_trace` | none found |
| `run` | 164–183 | `widths, forces, sides, actions, verbose` | none found |
| `main` | 185–198 | `` | none found |

## `R541.curriculum` — LUCID_R552_WORKSPACE/R541_DEVELOPMENTAL_CURRICULUM/curriculum_r541.py
Pinned SHA-256 `03ebb3300fb660095b8579923e0300eb8fcc7347a0d4df8dd016a558d44695a0`. 5 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `verify_stage_graph` | 66–74 | `` | none found |
| `pose_at` | 76–83 | `name, t, duration, amplitude` | none found |
| `check_pose_rom` | 85–94 | `pose, joint_ranges` | none found |
| `classify_episode` | 96–135 | `episode` | none found |
| `curriculum_status` | 137–149 | `episodes` | none found |

## `BCR.game_intent` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/game_intent.py
Pinned SHA-256 `6f55bd84c465655f89842abda07ba95d9679ae8883a32892e57eb95781e2fa48`. 3 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `GameIntent.validate` | 43–51 | `self` | none found |
| `GameIntent.to_locomotion_intent` | 53–66 | `self, cadence_spm, step_length_m, step_width_m` | none found |
| `AimIntent.validate` | 85–91 | `self` | none found |

## `BCR.planner` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/planner.py
Pinned SHA-256 `71b36d9ab3588b7cde89fe3e5e30518d3ae12f102659baf43bfb0e328e67185d`. 10 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `LocomotionIntent.validate` | 30–39 | `self` | none found |
| `CentroidalState.validate` | 51–60 | `self` | none found |
| `CentroidalPlan.schema` | 85–86 | `self` | none found |
| `CentroidalPlan.to_dict` | 88–110 | `self` | none found |
| `intent_from_amass_descriptor` | 127–152 | `desc` | none found |
| `CentroidalStepPlanner.__init__` | 156–157 | `self, params` | none found |
| `CentroidalStepPlanner._axes` | 160–163 | `heading` | none found |
| `CentroidalStepPlanner._step_time` | 165–168 | `self, intent` | none found |
| `CentroidalStepPlanner._step_length` | 170–178 | `self, intent, T` | none found |
| `CentroidalStepPlanner.plan` | 180–261 | `self, state, intent` | none found |

## `BCR.core_steering` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/core_steering.py
Pinned SHA-256 `971b0596c5f75c27deb0f39a8c3b553eb8b3f9b5c2c4238ff9d7744ff1ffa602`. 1 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `select_primitives` | 45–78 | `state, intent` | none found |

## `BCR.core_steering_runtime` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/core_steering_runtime.py
Pinned SHA-256 `8d33641c2f32ed4d93f92d959955af7392e5ba1b40358aa91ef2ef219e5565e6`. 4 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `CoreSteeringRuntime.__init__` | 29–43 | `self, ctrl` | `self.ctrl`, `self.last_target` |
| `CoreSteeringRuntime.local_vec` | 45–47 | `self, xyz` | none found |
| `CoreSteeringRuntime.apply` | 49–66 | `self, target` | `self.last_target` |
| `CoreSteeringRuntime.hold` | 68–69 | `self` | none found |

## `BCR.neuro` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py
Pinned SHA-256 `49243739c69abeca38daa460b154da4a33c869fdec58e3caf2a8188bcc69da4a`. 22 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `clamp_to_polygon` | 96–118 | `pt, P, margin` | none found |
| `load_tuned_params` | 121–134 | `path` | none found |
| `orientation_task_weights` | 142–149 | `p` | none found |
| `posture_task_weights` | 152–160 | `p, hinges` | none found |
| `box_solver_backend` | 163–174 | `` | none found |
| `box_least_squares` | 177–193 | `A, b, lo, hi` | none found |
| `WholeBodyMuscleController.__init__` | 197–255 | `self, pb, target_cmds, params, target_hand, target_root` | `self.last` |
| `WholeBodyMuscleController.feet_center` | 258–260 | `self` | none found |
| `WholeBodyMuscleController.set_com_target_from_current` | 262–267 | `self` | none found |
| `WholeBodyMuscleController.current_com_target` | 269–274 | `self` | none found |
| `WholeBodyMuscleController.muscle_gain_bias` | 277–284 | `self` | none found |
| `WholeBodyMuscleController.moment_matrix` | 286–290 | `self` | none found |
| `WholeBodyMuscleController.centroidal_momentum_matrix` | 292–305 | `self, com` | none found |
| `WholeBodyMuscleController.limit_forces` | 307–315 | `self` | none found |
| `WholeBodyMuscleController.foot_contacts` | 317–344 | `self` | none found |
| `WholeBodyMuscleController.control` | 347–534 | `self` | `self.last`, `self.last_angmom`, `self.last_pstar` |
| `WholeBodyMuscleController.control.task` | 381–387 | `J, target, w, name, priority` | none found |
| `WholeBodyMuscleController.attach_reflex` | 536–542 | `self, layer` | none found |
| `WholeBodyMuscleController.fast_reflex_excitation` | 544–555 | `self` | none found |
| `WholeBodyMuscleController._taus` | 560–562 | `self` | `act` |
| `WholeBodyMuscleController.reachable_activation` | 564–570 | `self` | none found |
| `WholeBodyMuscleController.excitation` | 572–580 | `self, a_des` | none found |

## `BCR.physbody` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/physbody.py
Pinned SHA-256 `c1a8657d7d7e592aa06d5b096be5fd35558ee8674ee170e97306741bd9d6497c`. 27 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `_wxyz` | 48–50 | `R` | none found |
| `hull_mass_properties` | 53–68 | `pts, mass` | none found |
| `segment_of_cluster` | 71–96 | `name` | none found |
| `convex_parts` | 106–113 | `P, k, seed` | none found |
| `passive_prior` | 134–167 | `dof_id, joint` | none found |
| `stance_gain` | 181–188 | `joint, dof_id` | none found |
| `PhysicsBody.__init__` | 192–259 | `self, shoulder_adduction_min_deg, timestep, muscles, stance_actuators, wraps` | `self.timestep` |
| `PhysicsBody._segment_points` | 262–297 | `self` | none found |
| `PhysicsBody._mass_properties` | 299–335 | `self` | none found |
| `PhysicsBody._build` | 338–413 | `self, exclude` | none found |
| `PhysicsBody._build.add_hull` | 341–351 | `body, name, P` | none found |
| `PhysicsBody._build.body_xml` | 364–391 | `j, indent` | none found |
| `PhysicsBody._default_wrap` | 416–428 | `self, mid, k, fol_k, loc_k` | none found |
| `PhysicsBody._coupler` | 440–445 | `self, parent, carrier, frac` | none found |
| `PhysicsBody._coupler_xml` | 447–458 | `self, cname, cp, indent` | none found |
| `PhysicsBody._equality_xml` | 460–470 | `self` | none found |
| `PhysicsBody.fold_coupled` | 472–478 | `self, J` | none found |
| `PhysicsBody._prepare_muscles` | 480–524 | `self` | none found |
| `PhysicsBody._muscle_xml` | 526–537 | `self` | none found |
| `PhysicsBody._calibrate_lengthrange` | 539–573 | `self, samples, seed` | none found |
| `PhysicsBody._index` | 575–596 | `self` | `m.actuator_actearly[:]` |
| `PhysicsBody._rest_overlaps` | 598–610 | `self` | none found |
| `PhysicsBody.set_state` | 613–637 | `self, commands, hand, placement, qvel` | none found |
| `PhysicsBody.read_state` | 639–665 | `self, qpos, clamp` | `self.last_overshoot_deg` |
| `PhysicsBody.end_range_forces` | 667–676 | `self` | none found |
| `PhysicsBody.joint_positions` | 678–679 | `self` | none found |
| `PhysicsBody.collision_report` | 682–688 | `self` | none found |

## `BCR.pipeline` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/pipeline.py
Pinned SHA-256 `aa2acd4818186358ac1876e34148fad32ac3aeffe6e6c500f3af33d5a1352a55`. 16 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `_h` | 45–46 | `arr` | none found |
| `JointRealizer.__init__` | 58–73 | `self, profile, omega, amax_scale` | none found |
| `JointRealizer.reset` | 75–76 | `self, q0` | none found |
| `JointRealizer.step` | 78–103 | `self, target, dt, substeps` | `self.last_saturated` |
| `hinge_axes` | 118–131 | `pose, commands` | none found |
| `MuscleDemand.__init__` | 142–145 | `self, reserve_scale_nm, limit_cost` | none found |
| `MuscleDemand.solve` | 147–183 | `self, tau_world, moment_arms, hinges` | none found |
| `RigConfig.__post_init__` | 210–213 | `self` | none found |
| `CausalRig.__init__` | 217–229 | `self, config` | `self.act` |
| `CausalRig.reset` | 232–241 | `self, q0` | `self.act.a[:]`, `self.qpos_hist` |
| `CausalRig.snapshot` | 243–250 | `self` | none found |
| `CausalRig.restore` | 252–260 | `self, s` | `self.act.a` |
| `CausalRig.state_hash` | 262–270 | `self` | none found |
| `CausalRig._deform` | 273–280 | `self, pose` | none found |
| `CausalRig._contacts` | 283–304 | `self, V, pose` | none found |
| `CausalRig.step` | 307–389 | `self, intent, dt, root_translation, effort, record, placement` | `qpos`, `self.qpos_hist` |

## `BCR.skinning` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/skinning.py
Pinned SHA-256 `506f4faf0261df16aa34d062dc7e6c2b9bc2ed62bc805ba2380792541df55172`. 12 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `qmul` | 32–41 | `a, b` | none found |
| `quat_to_mat` | 44–51 | `q` | none found |
| `mats_to_quat` | 54–56 | `D` | none found |
| `Skinner.__init__` | 60–81 | `self, W, tag` | none found |
| `Skinner.lbs` | 84–92 | `self, D, T, points` | none found |
| `Skinner.lbs_matrices` | 94–100 | `self, D, T` | none found |
| `Skinner._blend_quat` | 103–117 | `self, qc, extra` | none found |
| `Skinner.dqs` | 120–135 | `self, D, T` | none found |
| `Skinner.cor_centers` | 138–195 | `self, sigma, force` | none found |
| `Skinner.cor` | 197–210 | `self, D, T` | none found |
| `Skinner.deform` | 212–219 | `self, D, T, method` | none found |
| `skinner` | 225–229 | `` | none found |

## `BCR.render` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/render.py
Pinned SHA-256 `4ba2c1443ffa3d718b12524413a9898d1887cb2fef7f146f4d4feaf16bbfc537`. 16 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `font` | 20–24 | `size, bold` | none found |
| `colormap` | 38–49 | `values, vmin, vmax, cmap` | none found |
| `Renderer.__init__` | 53–83 | `self, width, height, faces` | `self.actor` |
| `Renderer.set_ground` | 85–98 | `self, y, size, on, center` | `act` |
| `Renderer._clear_extras` | 100–103 | `self` | none found |
| `Renderer.add_lines` | 105–121 | `self, segments, color, width` | `act` |
| `Renderer.add_lines_colored` | 123–140 | `self, segments, colors, width` | `act` |
| `Renderer.add_arrow` | 142–156 | `self, start, vec, color, shaft, head` | `act` |
| `Renderer.add_points` | 158–164 | `self, pts, color, radius` | `act` |
| `Renderer.render` | 166–191 | `self, V, view, rgb, camera, scale, opacity, keep_extras` | none found |
| `region_camera` | 194–203 | `points, direction, pad, up_offset` | none found |
| `header` | 206–219 | `img, lines, height, sizes` | none found |
| `hstack` | 222–227 | `images, gap, bg` | none found |
| `vstack` | 230–235 | `images, gap, bg` | none found |
| `label` | 238–245 | `img, text, color, size, pos` | none found |
| `colorbar` | 248–261 | `width, vmin, vmax, unit, cmap, title` | none found |

## `BCR.contact_material` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/contact_material_r536.py
Pinned SHA-256 `bb23f035b46454d05f76735f2e3f8558ad03a69f11742d699f89e4811d73f717`. 4 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `contact_geoms` | 25–33 | `model, ground` | none found |
| `set_variant` | 35–53 | `model, ground, key` | none found |
| `ground_contact_measures` | 55–88 | `model, data, ground` | none found |
| `matched_rollout` | 90–115 | `model, ground, snap, variant` | none found |

## `BCR.muscle_allocator` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/muscle_allocator_r58.py
Pinned SHA-256 `7339bfe3b9dca45b1be9994041fb8b275192994d627f652cdddd2007ef5ca9cb`. 1 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `allocate_shared_muscles` | 10–69 | `moment, tracking, posture, com, lateral, priority, lateral_weight, amplitude, tonic` | `ctrl` |

## `BCR.posture` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/posture_stabilization_r51.py
Pinned SHA-256 `138f69009e84f0a5c7db436f2e7d4ea3b452cf74872f0576e70cff70106ec0cf`. 3 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `relative_head_hip_pd` | 14–38 | `model, data, head_body, hip_body, neutral_xz, kp, kd, max_desired_nm, direction` | none found |
| `controller_excitation` | 40–59 | `moment, desired, model, data, pb, neutral_xz, mode, target` | none found |
| `physical_acceptance` | 61–74 | `row, min_support, min_com_inside, max_head_deg, max_root_deg, max_nonfoot` | none found |

## `BCR.contact_flight` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/contact_flight_r46.py
Pinned SHA-256 `3edbc384e079cf9f6b9d7e6b506167a8c6ca3b82954b3c07940b488550223dcd`. 3 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `classify_sample` | 12–46 | `com_xyz, ground_force_n, index, fps, ballistic_residual_tolerance_mps2, support_polygon_valid` | none found |
| `muscle_moment_matrix` | 48–54 | `data, nu, nv` | none found |
| `feedback_excitation` | 56–76 | `moment, desired_torque, amplitude, tonic, reverse` | none found |

## `BCR.contact_grounded` — LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/contact_grounded_r48.py
Pinned SHA-256 `e611e8ad73977310d9dc0d84b830a709356a46e3a4758b8c7af1f4249a96ba53`. 5 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `loaded_support_target` | 13–35 | `com_xyz, contact_points, normal_force_n, min_load_n` | none found |
| `support_com_torque` | 38–61 | `jacobian_com, com_xyz, com_velocity_xyz, target, kp, kd, joint_limit_nm` | none found |
| `guarded_muscle_excitation` | 64–100 | `moment, desired_joint_torque, com_torque, support_target, amplitude, tonic, edge_margin_m, max_amplitude` | none found |
| `native_com_state` | 103–108 | `model, data, hip_body_id` | none found |
| `foot_contact_summary` | 111–138 | `body` | none found |

## `R543.run` — LUCID_R552_WORKSPACE/R543_MULTICONTACT_LEARNING/run_r543.py
Pinned SHA-256 `ccf48801484c56b66b15bdbe4b6907f5350c3f8acd2991cbbe6e6954e5cc8d54`. 14 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `sha` | 42–42 | `path` | none found |
| `dump` | 43–43 | `path, x` | none found |
| `make_body` | 44–59 | `context` | none found |
| `reset` | 61–72 | `pb` | `d.qpos[1]`, `d.qpos[cq]`, `d.qpos[pb.hinge_qadr[name]]` |
| `contacts` | 74–96 | `pb, d` | none found |
| `mode` | 98–100 | `s` | none found |
| `do_step` | 102–128 | `pb, d, qref, neutral, delta, root_spotter, anchor` | `d.ctrl[:]`, `d.qfrc_applied[:]`, `d.xfrc_applied[:]`, `d.xfrc_applied[hip, 3:]`, `d.xfrc_applied[hip, :3]` |
| `state_digest` | 130–131 | `d` | none found |
| `identify` | 133–162 | `pb` | none found |
| `identify.branch` | 143–149 | `muscle` | none found |
| `compare_maps` | 164–178 | `a, b` | none found |
| `local_map` | 180–183 | `record` | none found |
| `evaluate` | 185–242 | `pb, task, policy, maps` | none found |
| `main` | 244–315 | `output` | none found |

## `R585.neck` — R585/r585_neck_repair.py
Pinned SHA-256 `c356fd555e114360d31ff5466e15d71edf32b3cb7dcfeea7daa529e12c017c6e`. 4 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `angle` | 19–21 | `pb, d` | none found |
| `NeckAllocator.__init__` | 24–31 | `self, pb, kp, kd, regular, gain_scale, max_activation` | `self.last` |
| `NeckAllocator.update` | 32–55 | `self, d, base` | `self.last` |
| `run` | 57–94 | `cfg, secs, change_geometry, save, on_frame, baseline, push_N, push_onset_s` | `d.ctrl[:]`, `d.ctrl[ctl.ids]`, `d.qfrc_applied[:]`, `d.xfrc_applied[:]`, `d.xfrc_applied[pb.body_id['Hip'], 0]`, `m.site_pos[sid, 2]` (+1 more in JSON) |

## `R586.effort` — research/lucid/r586/r586_effort.py
Pinned SHA-256 `44ee7be8f86641cc3ce516893eaa872f0125b732c8b7dfe15adc097e8fdcd364`. 3 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `MomentConstrainedAllocator.__init__` | 21–35 | `self, pb` | `self.last_eff`, `self.last_torque_errors` |
| `MomentConstrainedAllocator.update` | 37–76 | `self, d, base` | `last`, `self.last_eff`, `self.last_torque_errors` |
| `run` | 79–128 | `cfg, secs, push_N, on_frame, collect_stride` | `d.ctrl[:]`, `d.ctrl[allocator.ids]`, `d.qfrc_applied[:]`, `d.xfrc_applied[:]`, `d.xfrc_applied[pb.body_id['Hip'], 0]`, `m.opt.noslip_iterations` (+1 more in JSON) |

## `R588.contact` — research/lucid/r588/r588_probe.py
Pinned SHA-256 `e000a713e9747de6ba5ff031951eb32523fe38065b69c7c6351f923b460c25b6`. 3 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `discover` | 9–15 | `name, legacy` | none found |
| `ledger` | 20–41 | `pb, d` | none found |
| `run` | 43–117 | `seconds, push, seat_solref, arm_solref, arm_priority, limb_damping_mult, thumb_time, thumb_damping, on_frame, damping_fade_end, seat_half_width, seat_round` | `d.ctrl[:]`, `d.ctrl[allocator.ids]`, `d.qfrc_applied[:]`, `d.xfrc_applied[:]`, `d.xfrc_applied[pb.body_id['Hip'], 0]`, `m.geom_solref[gi]` (+3 more in JSON) |

## `R589.landing` — R589/r589_arm_landing.py
Pinned SHA-256 `5a6a30f7ed93410abf56aa774c1e47ef5f8653735c64d506b799f59dfc1c336c`. 4 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `smooth` | 28–30 | `z` | none found |
| `ArmLanding.__init__` | 33–45 | `self, pb, target_deg, arrival_s, kp, kd, max_extra, release_at, fade_duration, opposing, side_profiles` | none found |
| `ArmLanding.update` | 46–85 | `self, d, base, t` | none found |
| `run` | 88–150 | `seconds, push, candidate, arm_params, on_frame, stride, save_trace, thumb_solref_s` | `d.ctrl[:]`, `d.ctrl[allocator.ids]`, `d.ctrl[idx]`, `d.qfrc_applied[:]`, `d.xfrc_applied[:]`, `d.xfrc_applied[pb.body_id['Hip'], 0]` (+4 more in JSON) |

## `R590.capture` — r590_settled_capture.py
Pinned SHA-256 `bbc5218777d174b9506df8c2e57116ddb7f2dea0e7990025141051dbb038e77d`. 1 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `on_frame` | 25–35 | `pb, d, t, arms` | none found |

## `R590.restart` — r590_rest_restart.py
Pinned SHA-256 `3ed8765c1e76b774376f9f29792a2c643070244d84a69f292356e0ad8c50af68`. 2 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `setup` | 26–53 | `` | `d.act[:]`, `d.qpos[:]`, `d.qvel[:]`, `d.time`, `m.opt.noslip_iterations`, `m.site_pos[sid, 2]` |
| `continue_native` | 55–97 | `seconds, pushN, pushAtS, save_frames` | `d.ctrl[:]`, `d.ctrl[allocator.ids]`, `d.qfrc_applied[:]`, `d.xfrc_applied[:]`, `d.xfrc_applied[pb.body_id['Hip'], 0]` |

## `R590.render_capture` — r590_render_settled.py
Pinned SHA-256 `f5221ac7d8a39b3a7e46075e59b22bbe0faa37ba586eccdc0ea172a2be6e9ce3`. 0 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|

## `R590.render_restart` — r590_render_rest_restart.py
Pinned SHA-256 `fd54bf9bcaae93681cb2175d3c55691a5e6af5204d9453f6ee240734d34b10c5`. 1 callable definitions.

| Callable | Lines | Parameters | Direct state write targets |
|---|---:|---|---|
| `render` | 33–38 | `q` | none found |

