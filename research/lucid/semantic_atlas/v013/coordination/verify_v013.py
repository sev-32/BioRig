#!/usr/bin/env python3
"""Fail closed on mismatched source hashes, rows, pair topology or numerical evidence."""
from pathlib import Path
import csv,hashlib,io,json,zipfile
import numpy as np
root=Path(__file__).resolve().parent
s=json.loads((root/'V013_AUDIT_RECEIPT.json').read_text())
zip_path=Path('/mnt/data')/s['sourceV010Archive']
assert hashlib.sha256(zip_path.read_bytes()).hexdigest()==s['sourceV010SHA256']
with zipfile.ZipFile(zip_path) as z:
    raw=z.read(s['sourceMomentEntry']);assert hashlib.sha256(raw).hexdigest()==s['sourceMomentBytesSHA256']
    with np.load(io.BytesIO(raw)) as n:
        J=n['momentJacobian'];mus=n['actuatorNames'].astype(str).tolist();dofs=n['dofNames'].astype(str).tolist()
with np.load(root/'ALL_84x84x102_SIGNED_MUSCLE_PAIR_STATE_COUNTS.npz') as n:
    same=n['same_sign_states'];opp=n['opposing_sign_states'];assert same.shape==opp.shape==(84,84,102)
    assert n['state_count'].tolist()==[94] and n['actuator_names'].tolist()==mus and n['dof_names'].tolist()==dofs
    assert np.array_equal(same,same.transpose((1,0,2)))
    assert np.array_equal(opp,opp.transpose((1,0,2)))
    assert not np.any(np.diagonal(opp,axis1=0,axis2=1))
    assert np.max(same.astype(int)+opp.astype(int))<=94
    for j in range(102):
        v=J[:,:,j];active=np.abs(v)>1e-6
        same_actual=sum(((np.sign(x[:,None]*x[None,:])>0)&(mask[:,None]&mask[None,:])).astype(np.uint8) for x,mask in zip(v,active))
        opp_actual=sum(((np.sign(x[:,None]*x[None,:])<0)&(mask[:,None]&mask[None,:])).astype(np.uint8) for x,mask in zip(v,active))
        assert np.array_equal(same[:,:,j],same_actual)
        assert np.array_equal(opp[:,:,j],opp_actual)
with (root/'ELBOW_EQUAL_NET_TORQUE_COACTIVATION_94_POSES.csv').open() as f:
    rows=list(csv.DictReader(f))
assert len(rows)==564
for row in rows:
    i=int(row['stateIndex']);j=dofs.index(row['elbowDof']);a=mus.index(row['flexor']);b=mus.index(row['extensor']);gain=float(row['extensorTensionNPer1NFlexor'])
    assert np.isclose(gain,-J[i,a,j]/J[i,b,j],rtol=1e-12,atol=1e-12)
    assert abs(J[i,a,j]+gain*J[i,b,j])<4e-15
    other=J[i,a,:]+gain*J[i,b,:];other[j]=0
    assert np.isclose(np.linalg.norm(other),float(row['allOtherDofLeakNmPer1NFlexor']),rtol=1e-12,atol=1e-12)
with (root/'COORDINATION_SOURCE_WITNESSES.json').open() as f:
    witnesses=json.load(f)
assert len(witnesses)==13
for w in witnesses:
    raw=(root/'source'/w['sourceFile']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==w['sourceSHA256']
    excerpt='\n'.join(raw.decode().splitlines()[w['startLine']-1:w['endLine']]);assert excerpt==w['evidenceExcerpt']
    assert hashlib.sha256(excerpt.encode()).hexdigest()==w['literalExcerptSHA256']
print('V013 PASS: all 719,712 pair/coordinate bins regenerated; 564 six-pair state rows; 13 pinned source witnesses; original V010 SHA verified')
