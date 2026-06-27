# Demo Preference Can404 Preflight

This preflight tests Candidate 5 from `triage_bc_sota_candidate_plan.md`.
It initializes from the positive-only policy, keeps BC on the positive-NN support, and adds a demo-level preference term over labeled positives versus labeled negatives.

## Selected Recipe

- Positive-NN BC support train demos: `50`.
- Added labeled negative preference demos: `10`.
- Labeled positive preference demos: `10`.
- Train demos in mask: `60`.
- Labeled positive / negative preference transitions: `1118` / `848`.
- Init checkpoint: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/train/can_paired_pos40_bad80_split404_positive_only_nn_policy0_official_bc_rnn/20260625141435/models/model_epoch_200.pth`.

## Training Command Template

```bash
conda run -n tri-piql python scripts/train_robomimic_official_transition_weighted.py \
  --config results/sota_candidate/demo_pref_can404_lpos_lneg_preflight/config.json \
  --transition-weights results/sota_candidate/demo_pref_can404_lpos_lneg_preflight/demo_preference_weights.hdf5 \
  --init-checkpoint results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/train/can_paired_pos40_bad80_split404_positive_only_nn_policy0_official_bc_rnn/20260625141435/models/model_epoch_200.pth \
  --demo-preference-weight 0.2 \
  --demo-preference-temperature 1.0 \
  --demo-preference-margin 1.0 \
  --anchor-logprob-weight 10.0 \
  --anchor-logprob-min-weight 0.999 \
  --num-epochs 20 --epoch-steps 100 --save-every-epochs 5 --device cuda
```

## Outputs

- Config: `results/sota_candidate/demo_pref_can404_lpos_lneg_preflight/config.json`.
- Transition weights: `results/sota_candidate/demo_pref_can404_lpos_lneg_preflight/demo_preference_weights.hdf5`.
- Diagnostics: `results/sota_candidate/demo_pref_can404_lpos_lneg_preflight/diagnostics.json`.
- Support audit: `results/sota_candidate/demo_pref_can404_lpos_lneg_preflight/demo_preference_support_audit.csv`.
