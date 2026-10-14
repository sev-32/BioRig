# Semantic Atlas V012 — archived goal-to-native-muscle execution verification

Source-pinned original R574 decision replay, pulse timeline, native actuator identity crosswalk and R590 integration gap.

- `R574_GOAL_TO_NATIVE_MUSCLE_EXECUTION_PAPER.md` — human-reviewed causal specification with 14-scene evidence
- `28_ORIGINAL_GOAL_DECISION_REPLAYS_AND_VETOES.csv` — original AST, two goals × 14 scenes
- `FROZEN_14_SCENE_GOAL_COUNTERFACTUAL_LEDGER.csv` — original paired native trial receipts, not a new simulation
- `FULL_2800_PULSE_TIMELINE_REPLAY.csv` — exact logged command waveform and independently calculated values
- `R574_R28_FOUR_MUSCLE_TO_V011_102_DOF_DYNAMIC_CROSSWALK.csv` — exact shared native muscle identity at distinct experimental conditions
- `build_v012.py`, `verify_temporal_path_v012.py`, `write_v012_paper.py` — offline reproducibility tools
- two SHA-256 receipts — archive anchors and methodological limitations

Run the two verification Python scripts with the original frozen R574 archive, V010 source ZIP, V011 native NPZ and frozen R590 checkpoint in `/mnt/data`; this does not change simulation or invoke GitHub Actions. V011 is preserved unchanged in the nested full checkpoint.
