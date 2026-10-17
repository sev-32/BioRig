#!/usr/bin/env python3
"""Verify V013 geometry-driven opposing/assisting muscle relationships, not stiffness.
Usage: python verify_pairs.py /path/to/V010.zip /path/to/V013_pairs.csv
"""
from pathlib import Path
import sys, zipfile, io, csv
import numpy as np

def verify(v010, register):
    with zipfile.ZipFile(v010) as z:
        d=np.load(io.BytesIO(z.read("V010/NATIVE_MOMENT_GEOMETRY_94_STATES_84x102.npz")))
        jac=d["momentJacobian"]
        names=list(map(str,d["actuatorNames"]))
        coords=list(map(str,d["dofNames"]))
    assert jac.shape==(94,84,102)
    with open(register,newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==84*84
    tol=1e-6
    for row in rows:
        i=int(row["actuatorA_ID"]); j=int(row["actuatorB_ID"])
        assert names[i]==row["actuatorA"] and names[j]==row["actuatorB"]
        a,b=jac[:,i,:],jac[:,j,:]
        assisting=opposing=0
        if i!=j:
            assisting=int(np.count_nonzero(((a>tol)&(b>tol))|((a<-tol)&(b<-tol))))
            opposing=int(np.count_nonzero(((a>tol)&(b<-tol))|((a<-tol)&(b>tol))))
        assert assisting==int(row["sameSignJointPoseCount"]), (i,j,"assist")
        assert opposing==int(row["opposingSignJointPoseCount"]), (i,j,"oppose")
    for side in ("left","right"):
        joint=coords.index(side+"Elbow.flexionExtension")
        triceps=jac[:,names.index("m_"+side+"_triceps"),joint]
        for flexor in ("biceps","brachialis","brachioradialis"):
            arm=jac[:,names.index("m_"+side+"_"+flexor),joint]
            assert np.all(arm*triceps<0)
            ratio=np.abs(arm/triceps)
            assert np.allclose(arm+ratio*triceps,0,atol=1e-12)
    return len(rows)
if __name__=="__main__":
    assert len(sys.argv)==3, "V010.zip V013_pairs.csv"
    print("Verified",verify(Path(sys.argv[1]),Path(sys.argv[2])),"ordered native pair rows")
