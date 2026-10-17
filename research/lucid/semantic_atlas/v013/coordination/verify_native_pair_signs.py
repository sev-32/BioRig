#!/usr/bin/env python3
"""V013: independently recompute antagonistic moment signs from native V010 states.

Usage: python verify_native_pair_signs.py /path/to/V010.zip
No simulator/model changes, no new physical trajectory and no claims of measured stiffness.
"""
import io
import sys
import zipfile
import numpy as np

assert len(sys.argv) == 2, "Pass original V010 checkpoint zip"
with zipfile.ZipFile(sys.argv[1]) as z:
    data = z.read("V010/NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz")
with np.load(io.BytesIO(data)) as measurements:
    J = measurements["momentJacobian"]
    muscles = list(map(str, measurements["actuatorNames"]))
    dofs = list(map(str, measurements["dofNames"]))
assert J.shape == (94, 84, 102) and np.isfinite(J).all()
# 84*84*102 bins; state threshold = 1e-6 metres per radian.
opposing = np.zeros((84, 84, 102), dtype=np.uint8)
assisting = np.zeros((84, 84, 102), dtype=np.uint8)
for j in range(102):
    for state in range(94):
        lever = J[state, :, j]
        active = abs(lever) > 1e-6
        mask = active[:, None] & active[None, :]
        sign = lever[:, None] * lever[None, :]
        opposing[:, :, j] += (mask & (sign < 0)).astype(np.uint8)
        assisting[:, :, j] += (mask & (sign > 0)).astype(np.uint8)
assert np.array_equal(opposing, opposing.transpose(1, 0, 2))
assert np.array_equal(assisting, assisting.transpose(1, 0, 2))
assert not np.any(np.diagonal(opposing, axis1=0, axis2=1))
assert np.all((opposing.astype(int) + assisting.astype(int)) <= 94)
pairs = 0
worst_off_joint = 0.0
for side in ("left", "right"):
    elbow = dofs.index(side+"Elbow.flexionExtension")
    ext = muscles.index("m_"+side+"_triceps")
    for muscle in ("biceps", "brachialis", "brachioradialis"):
        flex = muscles.index("m_"+side+"_"+muscle)
        f = J[:, flex, elbow]
        t = J[:, ext, elbow]
        assert np.all(f * t < 0)
        assert opposing[flex, ext, elbow] == 94
        ratio = -f/t  # N extensor tension per 1 N flexor tension
        canceled = J[:, flex, :] + ratio[:, None] * J[:, ext, :]
        assert np.max(abs(canceled[:, elbow])) < 1e-14
        canceled[:, elbow] = 0
        worst_off_joint = max(worst_off_joint, float(np.linalg.norm(canceled, axis=1).max()))
        pairs += 1
assert pairs == 6 and worst_off_joint > 0.02
print("V013 VERIFIED: 719712 pair/DOF bins, 94 native states, six opposing elbow pairs")
print("Maximum cross-joint moment from elbow-balanced 1 N test:", worst_off_joint, "Nm")
