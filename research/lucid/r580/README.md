# R580 — measured-position adaptive hip/trunk recruitment

**Research branch:** `sev-32/BioRig` / `research/lucid-r575-goal-intent`  
**Promotion status:** **NOT PROMOTED**. Frozen R574 source, trained goal selector and 84-muscle MuJoCo plant remain unchanged.

## Mechanism

R579 isolated the gluteus medius as the strongest local lateral actuator; its 40-second fixed hip-only and hip+20%-trunk configurations reduced total additional muscle-channel excitation but drifted outward after 23–28 seconds. R580 is an independent, real-time, **sensed-state** adaptation: every 40 ms, it uses measured root x and outward velocity to forecast a short-horizon lateral escape proxy (|x| + lookahead × outward velocity). That proxy smoothly recruits three supporting trunk actuators alongside gluteus medius. Muscle excitation and fraction changes are individually bounded and contact hazard gates ramp the command down. No future simulation state, applied harness force metadata, externally imposed position or root locking is accessed online.

The controller **does not solve balance**. Its position threshold and gain choices were developed after examining frozen scene 00's known failure, and these experiments must not be presented as blind held-out evaluation.

## True native 40-second comparisons — same frozen scene00

| System | End x | Added muscle-channel excitation × seconds | Hazard | Settled? |
|---|---:|---:|---|---|
| Prior R577 four-muscle tonic | 0.031844 m | 3.84528 | No | No |
| Prior R579 hip+20%-trunk tonic | 0.033863 m | 1.53811 | No | No |
| R580 earlier/higher recruitment | 0.031567 m | **4.73323** | No | No |
| **R580 later/lower recruitment** | **0.031906 m** | **2.84989** | **No** | **No** |

The selected lower-effort *research comparator* uses `triggerPositionM=.0284`, `fullRecruitAtM=.0308`, `lookaheadS=1`, `hipMax=.029`; all other defaults come from `CONFIG`. It is **25.9% lower in summed additional excitation than R577** for virtually the same lateral position, but does **not** meet the legacy |x| ≤ 0.030 m criterion and is not a metabolic-energy measurement. Earlier/stronger R580 corrects x slightly better but is considerably more costly. This trade-off is preserved instead of burying unfavorable results.

At 12 seconds, the prior successful *pushed recovery scene04* was retained with the later/lower candidate: R574 selects `R28`, end root x=0.024247 m, no hazard, settled=true, peak arm-seat contact=5.811 N. All experimental controller trajectories use a new clone of the same saved plant state.

The attempted **60-second extension timed out after 180 seconds wall-clock**. It generated no complete trace, so no 60-second safety or settling claim can be made.

## Reproduce from source

Restore original immutable R574 and R575 archives to the repository-root `./runtime` with `research/lucid/tools/bootstrap.py`. Python 3.13, native MuJoCo 3.15.0, NumPy, scikit-learn. Renderer also uses EGL and Pillow.

```bash
python research/lucid/r580/r580_adaptive_synergy.py \
  --indices 0 --seconds 40 --out r580_early_strong.json

# Reproduce the stronger hip, later recruitment comparator:
python research/lucid/r580/r580_adaptive_synergy.py \
  --indices 0 --seconds 40 --hip-max .029 --full-recruit-at .0308 \
  --out r580_commandline_partial_override.json
```

**Important:** That second CLI command modifies only two parameters and therefore does NOT exactly reproduce the late/lower 40-second receipt. For exact reproduction, invoke the module interface with the full config:

```bash
python - <<'PY'
import sys,json
sys.path.insert(0,'research/lucid/r580')
import r580_adaptive_synergy as r
_,_,lock=r.r577.baseline.frozen.frozen()
scene=r.r577.baseline.frozen.scenarios(lock)[0]
config={**r.CONFIG,'triggerPositionM':.0284,'fullRecruitAtM':.0308,
        'lookaheadS':1.,'hipMax':.029}
result=r.rollout(scene,'none',40.,config)
with open('r580_late_exact.json','w') as f:
    json.dump(result,f,indent=2,allow_nan=False)
PY

R580_NATIVE=1 python -m unittest discover -s research/lucid/r580 -p 'test_r580.py' -v
MUJOCO_GL=egl python research/lucid/r580/r580_render.py
```

All **8 R580 tests passed locally** including native scene04 12-second physics. `R580_AUDIT.json` has the real numerical results, matching initial-state fingerprint, source trace SHA-256s, native renderer image checksum and stated evaluation gaps. Raw trace JSONs live in the separate compact checkpoint ZIP, not in Git.

## Next stop/go

Do not modify the R574 baseline, R577 comparator or canonical controller yet. Focus on the **physical limit of the present feedback law**: measured root x is not synonymous with COM relative to contact support and extra muscle excitation may not reverse the pelvis's reference offset. Next implement a model-based *contact-relative* hip/trunk allocator with antagonistic muscle tests, net applied joint moments and actuator saturation constraints, benchmark on cloned 40-second states, and only then consider a 14-scene full 12–40 second campaign. Full low-level sensory latency remains untested.
