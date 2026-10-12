#!/usr/bin/env python3
"""Strict, dependency-free audit of frozen LUCID R575 physical traces.

No learned predictions and no substitution for missing native rollouts.
"""
from __future__ import annotations
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

SCHEMA = 'lucid.r575.latency-physical-branch.v1'
DT_S = .02
ARM_ABORT_N = 50.0
FLOOR_ABORT_N = 50.0
TILT_ABORT_DEG = 45.0
LOSS_SAMPLE_THRESHOLD = 3

def assert_finite_float(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name}: non-finite / invalid number')
    return float(value)

def inspect_record(record):
    if record.get('schema') != SCHEMA:
        raise ValueError('unexpected R575 schema')
    if not record.get('researchOnly') or record.get('productionModified') is not False:
        raise ValueError('record is not an immutable research evaluation')
    delay = record['delayMs']
    if delay not in (0, 20, 40) or record['observedAtMs'] != 60 - delay:
        raise ValueError('invalid decision latency contract')
    if record.get('chosenAction') not in ('none', 'R28'):
        raise ValueError('unrecognized native pulse')
    duration = assert_finite_float(record['seconds'], 'seconds')
    rows = record.get('trace')
    expected_count = round(duration / DT_S) + 1
    if not isinstance(rows, list) or len(rows) != expected_count:
        raise ValueError('missing/incomplete native physical trace')
    keys = ('rootTiltDeg', 'armsSeatN', 'otherFloorN', 'pelvisSeatN', 'feetFloorN')
    for i, row in enumerate(rows):
        if not math.isclose(assert_finite_float(row['timeS'], 'timeS'), i*DT_S, abs_tol=1e-7):
            raise ValueError(f'broken trace clock at sample {i}')
        for field in keys:
            assert_finite_float(row[field], field)
        if not isinstance(row['settledNow'], bool):
            raise ValueError('settledNow not boolean')
    tilt = max(r['rootTiltDeg'] for r in rows)
    arm = max(r['armsSeatN'] for r in rows)
    floor = max(r['otherFloorN'] for r in rows)
    loss = sum(r['pelvisSeatN'] < 5 and r['feetFloorN'] < 5 for r in rows)
    hazard = arm >= ARM_ABORT_N or floor >= FLOOR_ABORT_N or tilt >= TILT_ABORT_DEG or loss >= LOSS_SAMPLE_THRESHOLD
    settled_tail = len(rows) >= 50 and all(r['settledNow'] for r in rows[-50:])
    for key, computed in [('peakRootTiltDeg', tilt), ('peakArmSeatN', arm),
                          ('peakOtherFloorN', floor)]:
        if not math.isclose(assert_finite_float(record[key], key), computed, abs_tol=1e-8):
            raise ValueError(f'{key} differs from trace')
    if int(record['bothSupportLossSamples']) != loss:
        raise ValueError('support-loss count differs from trace')
    if record['hazard'] is not hazard or record['settledAtEnd'] is not settled_tail:
        raise ValueError('hazard or terminal settling differs from observations')
    return {
        'index': int(record['index']), 'delayMs': delay,
        'action': record['chosenAction'], 'hazard': hazard,
        'settled': settled_tail, 'peakTiltDeg': tilt,
        'peakArmN': arm, 'peakOtherFloorN': floor, 'supportLossSamples': loss,
        'initialSHA256': record['initialSHA256'], 'scene': record['scene'],
        'r574ControllerSHA256': record['r574ControllerSHA256'],
        'r575SourceSHA256': record['r575SourceSHA256'],
    }

def compare(records):
    """Only compare physically matched cases; absent conditions stay absent."""
    checked = [inspect_record(r) for r in records]
    by_index = defaultdict(dict)
    for r in checked:
        k = (r['index'], r['delayMs'])
        if r['delayMs'] in by_index[r['index']]:
            raise ValueError(f'duplicate scene/latency: {k}')
        by_index[r['index']][r['delayMs']] = r
    contrasts = []
    for index, latencies in sorted(by_index.items()):
        if 0 not in latencies:
            continue
        reference = latencies[0]
        for delay, result in sorted(latencies.items()):
            if delay == 0:
                continue
            if (result['initialSHA256'] != reference['initialSHA256']
                or result['scene'] != reference['scene']
                or result['r574ControllerSHA256'] != reference['r574ControllerSHA256']):
                raise ValueError(f'unmatched initial state / policy: scene {index}')
            contrasts.append({
                'index': index, 'lagMs': delay,
                'actionChanged': result['action'] != reference['action'],
                'newHazard': result['hazard'] and not reference['hazard'],
                'avoidedHazard': reference['hazard'] and not result['hazard'],
                'settlingChanged': result['settled'] != reference['settled'],
                'deltaPeakArmN': round(result['peakArmN'] - reference['peakArmN'], 8),
                'deltaPeakTiltDeg': round(result['peakTiltDeg'] - reference['peakTiltDeg'], 8),
            })
    return {'schema': 'biorig.lucid.latency-contrast.v1', 'completedCases': len(checked),
            'sceneIndices': sorted(by_index), 'matchedDelayContrasts': contrasts,
            'missingZeroDelayScenes': [i for i, x in sorted(by_index.items()) if 0 not in x],
            'claim': 'archived physical traces only; missing pairs are not inferred',
            'researchOnly': True}

def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('records', type=Path, nargs='+')
    args = cli.parse_args()
    records = [json.loads(p.read_text()) for p in args.records]
    print(json.dumps(compare(records), indent=2, allow_nan=False))

if __name__ == '__main__':
    main()
