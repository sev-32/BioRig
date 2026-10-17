import json,os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent/'out'
names={'base':'Inherited controller','single':'Single agonist','RELEASE_PLUS':'Antagonist release + feedback'}
fig,ax=plt.subplots(figsize=(10,4))
for key,label in names.items():
 d=json.loads((root/f'R591_{key}_MEASURED.json').read_text())
 s=d['sampledTimeSeries']
 ax.plot([x['tS'] for x in s],[x['qRad']*180/np.pi for x in s],label=label)
s=json.loads((root/'R591_RELEASE_PLUS_MEASURED.json').read_text())['sampledTimeSeries']
ax.plot([x['tS'] for x in s],[x['qTargetRad']*180/np.pi for x in s],'--',label='Voluntary elbow target')
ax.axvspan(.34,.47,alpha=.10,label='2 N·m diagnostic elbow disturbance')
ax.set(xlabel='Native physics time (s)',ylabel='Right elbow angle (degrees)',title='R591 — native arm motion: disturbance rejection and muscle-driven flexion')
ax.grid(alpha=.2);ax.legend(loc='upper right',fontsize=8);fig.tight_layout();fig.savefig(root/'R591_NATIVE_ELBOW_MOTION_TELEMETRY.png',dpi=150);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,4))
for key,label in names.items():
 d=json.loads((root/f'R591_{key}_MEASURED.json').read_text());s=d['sampledTimeSeries'];ax.plot([x['tS'] for x in s],[x['headDeg'] for x in s],label=label)
ax.axvspan(.34,.47,alpha=.10,label='Diagnostic disturbance')
ax.set(xlabel='Native physics time (s)',ylabel='Head angle relative to upper torso (degrees)',title='R591 — measured whole-body cost of elbow stabilization')
ax.grid(alpha=.2);ax.legend(loc='upper right',fontsize=8);fig.tight_layout();fig.savefig(root/'R591_HEAD_STABILIZATION_COST.png',dpi=150);plt.close(fig)
print('saved physics telemetry')
