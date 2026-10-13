# R574–R590 verified static execution architecture and reachability

**Source provenance:** Each module below was read directly from an original, SHA-256 pinned archive entry. This paper describes explicit calls, reads and assignments. It does not claim whole-program dynamic reachability or actual physics acceptance. See the machine relationship ledger and source-path manifest.

## 1. Executed entry point versus preserved historical source

The R590 *restarted* seated run (`R590.restart:continue_native`) enters native MuJoCo at an equilibrated state. It does **not** begin in the goal-policy object and does **not** invoke the historical whole-body QP or centroidal planner. The latter systems exist in the archive and are important, but their presence in the repository is not evidence of integration into this specific experiment.

The R590 continuous-capture path is different: it really calls `R589.run` for 24 seconds, and so includes the time-limited R589 muscle arm controller for the initial descent. The restart is **not** an identical code path: it reproduces an after-landing condition using stabilization without reexecuting that landing controller. Claims about "R590 includes R589" must identify which of these distinct pathways is meant.

## 2. Typed source-grounded edges

| From | To | Relationship | Evidence |
|---|---|---|---|
| `R590.capture` | `R589.landing` | IMPORTS AND CALLS RUN | `R590.capture:21,38–39` |
| `R590.restart` | `R589.landing` | IMPORTS MODEL HELPERS ONLY | `R590.restart:21–22,63` |
| `R590.restart` | `R586.effort` | INSTANTIATES AND UPDATES | `R590.restart:45–51,82` |
| `R590.restart` | `R585.neck` | USES ANGLE AND PHYSICAL SETUP | `R590.restart:22,28–36,64,77–87` |
| `R589.landing` | `R588.contact` | IMPORTS DIAGNOSTIC | `R589.landing:16,110–123` |
| `R589.landing` | `R586.effort` | INSTANTIATES AND UPDATES | `R589.landing:17,101,131,138` |
| `R589.landing` | `R585.neck` | USES OLDER STABILIZER | `R589.landing:89–103,125–142` |
| `R586.effort` | `R585.neck` | EXTENDS NECK ALLOCATOR | `R586.effort:17,20,37–76` |
| `R585.neck` | `R551.run` | IMPORTS CONTACT AND FORCE HELPERS | `R585.neck:12,78–91` |
| `R585.neck` | `R543.run` | IMPORTS PHYSICAL PLANT SETUP | `R585.neck:12,58,64` |
| `R585.neck` | `BCR.contact_flight` | IMPORTS MOMENT MATRIX | `R585.neck:13,34,42–44` |
| `R585.neck` | `BCR.posture` | IMPORTS BASE COMMAND | `R585.neck:14,82` |
| `R585.neck` | `BCR.contact_grounded` | IMPORTS SUPPORT TARGET | `R585.neck:15,81` |
| `R551.run` | `BCR.posture` | CALLS BASE COMMAND | `R551.run:21–25,75–92` |
| `BCR.game_intent` | `BCR.planner` | IMPORTS TYPED GOAL | `BCR.game_intent:14,53–66` |
| `BCR.core_steering_runtime` | `BCR.core_steering` | USES CORE TASK CONTRACT | `BCR.core_steering_runtime:1–69` |
| `BCR.pipeline` | `BCR.skinning` | DEFORMATION REALIZATION | `BCR.pipeline:272–280` |
| `R574.evaluate` | `R574.goal` | IMPORTS AND EVALUATES GOAL POLICY | `R574.evaluate:13,22–25,33–69;R574.goal:20–21,68–109,119–140` |
| `R562.settle` | `R541.curriculum` | GATE NARROWER THAN EARLIER RESEARCH | `R562.settle:38–46;R541.curriculum:96–135` |
| `R590.restart` | `BCR.neuro` | NOT DIRECTLY INVOKED IN STUDIED ENTRYPOINT | `R590.restart:1–104` |
| `R590.restart` | `BCR.planner` | NOT DIRECTLY INVOKED IN STUDIED ENTRYPOINT | `R590.restart:1–104` |
| `R590.restart` | `R574.goal` | NOT DIRECTLY INVOKED IN STUDIED ENTRYPOINT | `R590.restart:1–104` |

## 3. Semantics and provenance of each relationship

### 1. `R590.capture` → `R589.landing`
**IMPORTS_AND_CALLS_RUN** — R590.capture calls R589.run continuously for 24s, including active first-stage arm descent; saves its actual qpos/qvel/act states.
Evidence: `R590.capture:21,38–39`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 2. `R590.restart` → `R589.landing`
**IMPORTS_MODEL_HELPERS_ONLY** — The restarted seated loop imports R589 but uses only its exported R586/R585 lineage and the R588 contact ledger. It does NOT call R589.run or ArmLanding.update.
Evidence: `R590.restart:21–22,63`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 3. `R590.restart` → `R586.effort`
**INSTANTIATES_AND_UPDATES** — Instantiates R586 moment-constrained head allocator and seeds its previous commands from the native actuator activation state.
Evidence: `R590.restart:45–51,82`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 4. `R590.restart` → `R585.neck`
**USES_ANGLE_AND_PHYSICAL_SETUP** — Recreates a seated 84-muscle MuJoCo plant with R585 SCM adjustment; restores qpos/qvel/act and runs the inherited R551 stabilizer.
Evidence: `R590.restart:22,28–36,64,77–87`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 5. `R589.landing` → `R588.contact`
**IMPORTS_DIAGNOSTIC** — Uses R588.ledger to measure left/right contact loads. Does not require the R588 ×10 joint damping experiment.
Evidence: `R589.landing:16,110–123`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 6. `R589.landing` → `R586.effort`
**INSTANTIATES_AND_UPDATES** — Active R586 neck optimizer overrides only its ten chosen actuator commands.
Evidence: `R589.landing:17,101,131,138`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 7. `R589.landing` → `R585.neck`
**USES_OLDER_STABILIZER** — Calls imported older physical scene builder and proprioceptive/postural controllers through R586.r585.
Evidence: `R589.landing:89–103,125–142`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 8. `R586.effort` → `R585.neck`
**EXTENDS_NECK_ALLOCATOR** — R586 LP minimizes excitation while remaining within algebraic neck moment tolerance of R585 bounded-least-squares reference.
Evidence: `R586.effort:17,20,37–76`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 9. `R585.neck` → `R551.run`
**IMPORTS_CONTACT_AND_FORCE_HELPERS** — R585 imports R551 as core, using foot contact, root tilt and passive endpoint force helpers.
Evidence: `R585.neck:12,78–91`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 10. `R585.neck` → `R543.run`
**IMPORTS_PHYSICAL_PLANT_SETUP** — Scene builder and initial seated native state are inherited from R543 experimental module.
Evidence: `R585.neck:12,58,64`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 11. `R585.neck` → `BCR.contact_flight`
**IMPORTS_MOMENT_MATRIX** — Reads the MuJoCo actuator moment-arm mapping at the current physical state.
Evidence: `R585.neck:13,34,42–44`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 12. `R585.neck` → `BCR.posture`
**IMPORTS_BASE_COMMAND** — Invokes inherited global posture-to-muscle excitation routine.
Evidence: `R585.neck:14,82`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 13. `R585.neck` → `BCR.contact_grounded`
**IMPORTS_SUPPORT_TARGET** — Creates a loaded support target from actual feet-contact samples and COM.
Evidence: `R585.neck:15,81`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 14. `R551.run` → `BCR.posture`
**CALLS_BASE_COMMAND** — Uses the narrower posture stabilizer and optional additive muscle pulse; does not directly instantiate WholeBodyMuscleController.
Evidence: `R551.run:21–25,75–92`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 15. `BCR.game_intent` → `BCR.planner`
**IMPORTS_TYPED_GOAL** — GameIntent converts world velocity and facing into typed LocomotionIntent, a plan request rather than muscles.
Evidence: `BCR.game_intent:14,53–66`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 16. `BCR.core_steering_runtime` → `BCR.core_steering`
**USES_CORE_TASK_CONTRACT** — Maps core steering targets to controller task fields, not joint-command authority.
Evidence: `BCR.core_steering_runtime:1–69`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 17. `BCR.pipeline` → `BCR.skinning`
**DEFORMATION_REALIZATION** — Computes canonical or experimental Skin78 surface from skeletal pose; no claim of native free-root physics.
Evidence: `BCR.pipeline:272–280`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 18. `R574.evaluate` → `R574.goal`
**IMPORTS_AND_EVALUATES_GOAL_POLICY** — Frozen offline trial imports and fits the two-action none vs R28 intention agent; policy training uses 36 source rows and 29 pairs, not general reach.
Evidence: `R574.evaluate:13,22–25,33–69;R574.goal:20–21,68–109,119–140`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 19. `R562.settle` → `R541.curriculum`
**GATE_NARROWER_THAN_EARLIER_RESEARCH** — R562 seated gate omits R541 head-to-hip and cold-start checks: scope mismatch, not proof of direct literal version regression.
Evidence: `R562.settle:38–46;R541.curriculum:96–135`. Status: `STATIC_SOURCE_VERIFIED_RUNTIME_NOT_PROVEN`.

### 20. `R590.restart` → `BCR.neuro`
**NOT_DIRECTLY_INVOKED_IN_STUDIED_ENTRYPOINT** — No direct call or instantiation of WholeBodyMuscleController in this root module. This negative claim is root-specific, not repository-wide.
Evidence: `R590.restart:1–104`. Status: `MODULE_SPECIFIC_STATIC_NONINVOCATION`.

### 21. `R590.restart` → `BCR.planner`
**NOT_DIRECTLY_INVOKED_IN_STUDIED_ENTRYPOINT** — No direct locomotion planning call in the recorded 12s post-settling routine.
Evidence: `R590.restart:1–104`. Status: `MODULE_SPECIFIC_STATIC_NONINVOCATION`.

### 22. `R590.restart` → `R574.goal`
**NOT_DIRECTLY_INVOKED_IN_STUDIED_ENTRYPOINT** — R590 research loop does not call the R574 outcome-prediction agent.
Evidence: `R590.restart:1–104`. Status: `MODULE_SPECIFIC_STATIC_NONINVOCATION`.

## 4. Source verification

Analyzed 28 source modules; 224 function/class declarations; 4169 AST statement instances; 3048 syntactically present call sites; 793 conservative field-name candidates. These numbers describe **selected runtime-critical source**, not the full 70,823-line frozen global index.

The full source line and file-pair ledgers in V003 remain intact. This chapter adds source-resolved modules and separates actually called procedures from imported historical facilities.

**There is no semantic guarantee that a function without a syntactic call site cannot be invoked by reflection, dispatch, callbacks or another entry point.**
