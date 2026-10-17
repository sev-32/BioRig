# BioRig Semantic Atlas V013 — Controlled muscle balance, joint impedance and intentional movement

**Status:** Source-grounded mechanistic audit and executable specification. **Not a controller release; no claim of improved native motion.** All preceding R574–R590 programs and V003–V012 atlas archives remain immutable.

## Executive finding

The project's available anatomy already contains flexor/extensor pairs. Its native musculotendon Jacobians show the pairs exert opposing generalized moments in all 94 recorded seated-state postures. The missing subsystem is therefore not the *existence* of antagonistic muscles. It is an integrated **state-dependent muscle allocation policy** that maintains support, adjusts joint impedance, deliberately unloads antagonists when appropriate, and transfers load across cooperating joints when moving.

Two separate problems have been conflated:

1. The original `lucid_bcr/neuro.py` defines a **coupled** whole-body muscle optimization over forward dynamics, contact forces, COM, head posture, and joint posture. But its default `NeuroParams.relaxed_arms=True` puts the arm-muscle group **outside its muscle optimization** (`self.free` excludes all arm-name matches), fixing its desired arm activation at `arm_tone=0.01`; this is not coordinated arm load-bearing. A configuration allowing optimized arms (`relaxed_arms=False`) exists; neither its quality nor its runtime integration in R590 is thereby established. Merely toggling the flag is **not an approved fix**.
2. The recent R589 arm descent directly picks **one** shoulder muscle: `deltoid_middle` for one torque sign, `pectoralis_major` for the opposite. It adds excitation to that channel without optimizing its opponent's excitation, passive tissue load, shoulder-girdle support, elbow/wrist stiffness, or future contact wrench. R586 independently favors minimizing neck activation at fixed predicted six-coordinate neck moment; that can remove excess co-contraction without proving that appropriate stiffness was preserved. The term `synergy` in R579 refers to a chosen set of four weighted lateral corrective channels, **not** a whole-limb motor synergy or antagonistic impedance controller.

**The failure is architectural, not merely a missing muscle name, a rendering problem, or a contact stiffness parameter.** No existing subsystem is demonstrated to solve all the coupled tasks with a single owner of final commands.

## Semantic clarification: the user's balance-of-contraction insight

A muscle generates tension; it does not intrinsically issue a joint-angle command. Multiple muscles can produce the same net joint moment through very different internal force distributions. Consequently, a desired movement needs **two partly independent decisions**:

- **Net movement effort**: the difference of agonist and antagonist contributions that changes joint acceleration, corrects errors, or balances gravity;
- **Internal stabilizing tension**: recruitment distributed across muscles to influence resistance to small disturbances, with posture-dependent force-length-velocity dynamics, passive tissues, tendon elasticity and delayed activation.

A crucial qualification: continuous simultaneous co-contraction is **not always** physiologically optimal or even necessary. Under a predictable load, a relatively quiet antagonist and a load-bearing agonist can maintain posture. Reciprocal reduction of antagonist activity can make a movement smoother and less costly. When a joint must resist uncertain loading, timed co-contraction can increase short-range resistance to disturbances; excessive co-contraction wastes energy and may produce rigid movement. Some antagonists are active **eccentrically** to brake motion while lengthening. A muscle can also stabilize one coordinate while moving another, and scapular, trunk and wrist stabilizers matter during elbow movement.

Thus BioRig should allocate **a continuum from reciprocal relaxation through load-bearing activation to deliberate co-contraction**, based on task uncertainty, current support, target movement and perturbation risk. Avoid an unconditional rule that both muscle groups must always contract.

## Native anatomical evidence from V010, not invented pairings

V010's verified native MuJoCo tensor is 94 physical configurations × 84 muscle moment-arm rows × 102 generalized velocity coordinates. This analysis checks all 67,652,928 possible *actuator-pair × coordinate × state* sign comparisons. Every ordered pair appears in `ALL_84x84_POSE_CONDITIONAL_JOINT_SIGN_RELATIONSHIPS.csv` (7,056 rows, including the diagonal). A sign relationship is a **mechanical-geometric relation at a sampled pose**, not a strength, control or activation guarantee.

Across the 3,486 unordered distinct muscle pairs, the measured sign analysis finds **363** pairs that oppose on at least one coordinate/posture, **350** assisting pairs and **317** that have *both* opposing and assisting relationships across the sampled coordinates/postures. The overlap is crucial: a muscle pair can oppose at the elbow but assist at another coordinate, or change leverage with configuration. It is incorrect to give every pair one fixed global tag of `synergy` versus `antagonist`.

At the native elbow flexion/extension coordinate, left and right biceps, brachialis and brachioradialis each oppose triceps for **all 94** measured postures, with signed local moment arms (metres):

| Pair | Initial flexor lever (m) | Initial triceps lever (m) | Triceps force needed to offset 1 N of flexor force, range over 94 poses |
|---|---:|---:|---:|
| Left biceps/triceps | -0.013091 | +0.017401 | 0.752–0.954 N |
| Right biceps/triceps | -0.013052 | +0.017270 | 0.756–1.010 N |

These are **muscle-force ratios for canceling only the selected elbow DOF**, not excitation ratios. Real excitation-to-force gains, recruitment capacity, muscle path dynamics, tendon compliance, co-produced shoulder moments and other supporting loads must be accounted for. The complete CSV includes all six studied elbow flexor–extensor pairs and exact unrounded values.

V011 independently perturbed six corresponding muscles one at a time and measured generalized force and angular-velocity responses after activation. Their signed force responses were consistent with the opposing elbow action, but the later velocities can share a direction because body inertia, posture, and contact couple the movement. **Do not add isolated response curves and declare a two-muscle co-contraction outcome:** combined excitation was not physically run in V011.

## Required physical control relationships

Let `q, v` denote native joint states, `a` measured muscle activation and `u` neural excitation command. The complete model must honor:

- **Actuation:** `τ_m(q,v,a) = R(q)^T F_m(q,v,a)` where `R` is the muscle-to-coordinate leverage and `F_m` is signed native muscle force. Units: `R` in metres for rotational coordinates, `F` in newtons, `τ` in newton-metres. The correct native signs are those of MuJoCo's actuator-force model, not anatomical labels.
- **Activation history:** `a[k+1] = Actuate(a[k], u[k], Δt)` with asymmetric activation and deactivation times. An instruction to relax the triceps does **not** instantaneously cancel its tension. Stale commands and delays must be modeled, not hidden by servo damping.
- **Body mechanics and support:** `M(q) qdd + h(q,v) = τ_m + J_contact^T λ + τ_passive + τ_external`, subject to foot/seat contact and valid friction constraints. An elbow command can change seat and trunk contact through the kinematic chain.
- **Task-level net moment:** select physically feasible `τ_req` from support and movement goals, with acceptable speed/acceleration/jerk constraints.
- **Internal force / impedance policy:** among commands producing sufficiently similar required moments and contact behavior, choose a recruitment pattern that yields an intentional, measured small-perturbation response. A torque-equivalent activation null-space does not automatically mean identical stiffness; effective stiffness is a *derivative and dynamical property*, not the sum of excitations.

The **physically measured** effective stiffness and damping should be identified by perturbing a held pose: evaluate displacement and velocity following small positive/negative joint perturbations and small external wrenches at known activation, load and contact. The actuation model is compliant, nonlinear, finite-bandwidth and subject to fatigue; formal instantaneous torque equivalence is at best a local linearization.

## Contract for a single integrated, goal-conditioned allocator (design, not deployed)

The optimizer must consume the full state `S` (q, v, a, tendon states, contact constraints, support-polygon condition, prior u, reference pose) and a task `G` (pose/movement goal, allowed contact, target speed, disturbance expectation and posture constraints). It returns **one** authoritative 84-channel `u`, plus measurable diagnostics:

1. **Support reserve (continuous):** maintain pelvis/torso/head, support contacts, gravity compensation and proximal stabilization; distinguish predictable static load from disturbances.
2. **Movement distribution:** redistribute effort over all muscles that materially affect the active task, commanding controlled antagonist unloading when safe; include eccentric braking when needed.
3. **Variable joint impedance:** target experimentally meaningful resistance near critical joints, not a fixed co-contraction percentage. Recover from disturbance without high-frequency chatter; reduce stiffness where compliant contact or free motion is desired.
4. **Activation-aware allocation:** respect current `a`, separate activation/deactivation time constants, 84 channel bounds, force/velocity/length gains, recruitment capacity, fatigue and time-step rates. Do not mistake command `u` for delivered force.
5. **Contact and intention constraint:** predict onset/offset of hand/seat contact, preserve valid arm support if requested, avoid spurious collision, enforce whole-body safety and no high-impact penetration.
6. **One final control authority:** no R589 arm override after base control, followed by an independent R586 neck override. Integrate objectives into the existing whole-body task-allocation pathway with typed owners and explicit composition; the anatomy stays untouched and no old stage is deleted.
7. **Diagnostic output:** per-muscle u/a/force; per-joint total agonist/extensor moments; residual movement moment; modeled short-range stiffness/damping; contact impulse/slip; muscle-effort and co-contraction indices; safety vetoes; provenance to exact model pose and source SHA.

**Do not simply turn on `relaxed_arms=False` as a supposed fix.** First produce a paired cold-start and settled-state native test confirming that the optimization admits bilateral arm support without destabilizing the head, trunk or seat contacts. The historical flags and source routines must be integrated and tested, not resurrected as assumed-successful versions.

## Acceptance evidence that discriminates real motor coordination from a visual trick

The minimum experimental sequence after this source/documentation checkpoint should be:

- **A. Joint hold:** hold a bent elbow at a prescribed posture under a gentle external perturbation. Compare equivalent net-moment patterns with low and higher antagonist recruitment, measuring effective stiffness/settling and cost. Both conditions must begin from the *same native physical state*, with muscle activation history preserved.
- **B. Intentional bend and return:** accelerate into the bend, permit appropriate antagonist unloading, then brake and hold. Plot *both* excitation and native activation/force for biceps, brachialis, triceps, shoulder girdle, scapular and trunk muscles. Measure timing, jerk, antagonist braking, oscillation and controller saturation.
- **C. Different loads:** repeat while elbow is unloaded versus carrying a hand load and while shoulder/seat contact differs. The support baseline should change; a hardcoded single-muscle pulse should not suffice.
- **D. Whole-character SKIN78 proof:** show uninterrupted renderer captures with all contact geometry, and side-by-side plots of the same native trace. Reject bizarre limb chatter, high impact, head fold or hidden external stabilization even if a numeric task gate passes.
- **E. Version compatibility:** retain unchanged R574–R590 evidence; compare an integrated experimental allocator against R589/R590 under identical seeds, poses, materials and disturbance parameters before promotion.

This V013 paper provides architecture, source-verified defects and signed mechanical evidence; **A–E remain proposed physics experiments**. It contains no falsely claimed new movement renders, stiffness measurements, or simulated coactivation tests.

## Data provenance and exact source anchors

The attached `V013_SOURCE_AND_MECHANICAL_RELATIONSHIP_RECEIPT.json` pins input archive SHA256 and byte-specific source files. The principal literal anchors are:

- R574 frozen `LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG/lucid_bcr/neuro.py`: `NeuroParams.relaxed_arms` at L77, arm-optimizer inclusion at L225–228, dynamic task force coefficients at L347–377, effort regularization L478–486 and selection L520–525; activation reachability L560–580.
- R589 frozen `R589/r589_arm_landing.py`: sign-selected shoulder muscle L63–80; sequential command composition L129–138.
- R586 frozen `research/lucid/r586/r586_effort.py`: optimized moment-equivalent excitation L37–76 (especially minimizing total excitation L54).
- R579 frozen `research/lucid/r579/r579_synergy.py`: hard-coded four-channel lateral profile L20–54.
- V010 native matrix: `V010/NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz`; V011 native data: `V011/ALL_84x102_NATIVE_CONTROL_TO_DOF_TIME_RESPONSE.npz`.

The static 84×84 matrix is complete **for observed joint-sign relationships across 94 sampled poses**; it is not the promised 100% dynamic, semantic, physiological or temporal relationship matrix. A raw zero in its count columns means only that no joint-sign correlation was found at the specified numerical threshold in these samples.

No source, model geometry, solver setting or simulation executable has been changed here. No GitHub Actions.
