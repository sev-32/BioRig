# R586 — bounded neck activation with actual SKIN78 visual regression

**Repository:** `sev-32/BioRig`  
**Branch:** `research/lucid-r575-goal-intent`  
**Status:** Native physical research, **not promoted**, **not visually approved**. Frozen R574 and the verified R585 repair are unchanged. **No GitHub Actions.**

## Why this experiment exists

R585 restored genuine six-joint head stabilization after discovering one-sided head.nod muscle moment authority and insufficient inherited neck recruitment. The R585 12-second native SKIN78 animation visibly preserved head pose but used high summed neck-muscle activation. R586 reduces unnecessary co-contraction without reverting to a weak neck controller.

`r586_effort.py` calls the unchanged R585 neck torque allocator as a *reference*, then solves a ten-muscle linear program for lower summed excitation. The new excitation is accepted only if predicted generalized forces on all six neck/head degrees of freedom stay within **0.02–0.04 N·m** of the R585 reference at the current MuJoCo state. Activation remains in [0, 0.8] per muscle, with a bounded per-update change and a fallback to R585 commands if the optimization is infeasible. Neither direct joint torques nor root forces are added. The original 84-muscle MuJoCo plant, corrected bilateral SCM geometry, model gravity, seat/floor geometry and no-slip solver remain identical to R585.

**Important:** the moment error is an *instantaneous, local model approximation*, not a proof that future physical trajectories must match. The candidate is therefore tested through full real physical simulation and original SKIN78 rendering.

## Verified real native runs

| Result | R585 independent reference | R586 new controller |
|---|---:|---:|
| 4-second maximum head–torso rotation | 4.099° | **2.163°** |
| 4-second summed activation × seconds | 11.3358 | **7.3481** |
| 12-second maximum head–torso rotation | 4.099° | **2.163°** |
| 12-second summed neck activation × seconds | 38.1846 | **25.1326** |
| 12-second activation reduction | — | **34.18%** |
| 12-second final pelvis x | approx. 13.6 mm | **13.34 mm** |
| 12-second maximum arm-seat contact | 25.84 N | **31.54 N** |
| 12-second maximum pelvis tilt | 13.50° | **13.91°** |

Separate fresh **120 N lateral push, 12 seconds**: R586 maximum head–torso rotation 2.311°, final x 18.31 mm, maximum arm-seat 31.54 N, no other-floor hazard, and no optimization fallback. In the no-push case, 1200/1200 neck updates met the moment envelope with **zero infeasible solves or fallbacks**. The cost metric is summed activation × seconds, **not actual muscle work, force, fatigue, or calibrated metabolic energy**.

The suite passed **8/8 local regression tests with both optional native 12-second physical replays enabled**. Repeatability is demonstrated in these tested cases only. Longer-horizon 40–60 second stability, anatomical realism, other frozen scenes, complex disturbance directions, nonlinear tendons and relaxed equilibrium **remain unverified**.

## Actual original SKIN78 renderer

`r586_render.py` captures 31 fresh native MuJoCo poses from one 12-second R586 simulation, deforms the canonical original SKIN78 mesh from `mjData.qpos`, and compares them against 31 previously recorded *real* R585 frames at exactly matching timestamps (0.4-second intervals). It includes the native seat/floor geometry. No artistic image generation, pose interpolation or replacement skin. The animated image is delivered **in conversation**, not committed into the source-only Git branch.

Source `R586_RENDER_RECEIPT.json` stores the original skin fingerprint and rendered GIF SHA256. The full image and 31 exact native frame-state hashes are distributed in the offline checkpoint.

## Reproduce on a local CPU machine, no Actions

Restore the original R574 ZIP into repository-root `./runtime` using `research/lucid/tools/bootstrap.py` (the large original R574 assets are **not** stored in this Git research branch). Requires Python 3.13, MuJoCo 3.15, NumPy, SciPy. Real renderer additionally requires VTK and Pillow with working headless VTK rendering.

```sh
# From repository root:
export BIORIG_WORKSPACE="$PWD"
export PYTHONPATH="$PWD/runtime/LUCID_R552_WORKSPACE/BIOMECH_CAUSAL_RIG:$PYTHONPATH"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python research/lucid/r586/r586_effort.py --seconds 12 --out r586_12s_native.json
python research/lucid/r586/r586_effort.py --seconds 12 --push 120 --out r586_push120_native.json

# Six fast checks plus two fresh ~12s MuJoCo replays:
R586_NATIVE=1 R586_NATIVE_PUSH=1 python -m unittest discover \
  -s research/lucid/r586 -p 'test_r586.py' -v

# Supply the original R585 native comparison GIF (from previous R585 checkpoint)
export BIORIG_R585_REFERENCE_GIF=/path/to/R585_REAL_SKIN78_NECK_REPAIR_12S.gif
python research/lucid/r586/r586_render.py
```

The Git `R586_12S.json` and `R586_RENDER_RECEIPT.json` are small, explicitly marked **summary receipts**. Complete sampled physical traces, 31 qpos-state fingerprints, local test log and source fingerprints are in the compact offline checkpoint. No model assets and no images are duplicated in that ZIP.

**Stop/go:** R586 must not replace the approved visual reference or the original model until the owner actually approves the entire skinned motion, including head, neck, arms, torso, hips, feet and contacts. The project’s earlier catastrophic failure was incorrectly declared safe by head-blind pelvis-only tests; R586 retains an explicit head-to-thorax gate so that cannot be silently repeated.


## Second actual SKIN78 animation: no push versus +120 N

A separate `R586_NATIVE_SKIN78_PUSH120_COMPARISON.gif` was rendered from 31 fresh 120 N physical frames beside the already captured real no-push R586 frames. The canonical R586 renderer was subsequently rerun with the same configuration and independently reproduced **identical SHA256**:

`c46c90d26fa63cce05f1f1b96c85e20400823ec69717cea5b48bf7d4446a47af`

No mesh, inertia, muscle-site, friction or solver parameters differ between the pushed and unpushed modes. The only physical difference is the 120 N lateral force on the Hip during 0.8–0.92 s. Full native numeric run: maximum head deviation 2.3107°, final pelvis x 0.018306 m, maximum arm-seat 31.543 N, 0 unexpected floor hazard. Neither case has owner visual acceptance.

From a local restored Git checkout, **first** generate the standard no-push R586 animation as documented above; **then** use that actual native GIF as the reference for a real pushed run:

```sh
export BIORIG_SKIN78_REFERENCE_GIF="$PWD/research/lucid/r586/R586_NATIVE_SKIN78_VS_R585_12S.gif"
BIORIG_R586_PUSH_N=120 python research/lucid/r586/r586_render.py
```

This produces the `R586_NATIVE_SKIN78_PUSH120_COMPARISON.gif` proof image and `R586_PUSH_RENDER_RECEIPT.json`; images remain excluded from the source-only Git branch and code ZIP.
