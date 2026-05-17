#!/usr/bin/env bash

set -eu

layout="post"
subdir="blog/ab_to_rl"

uv run ../notebook_convert.py \
    --nbpath beta-distribution-probabilities.ipynb \
    --date "2026-05-14" \
    --layout $layout \
    --subdir ${subdir} \
    --description "Understand the Beta distribution as a model for unknown success probabilities, and derive the Beta-Bernoulli update for binary data." \
    --image "/images/ab_to_rl/beta-distribution-probabilities-preview.png" \
    --tags "Beta Distribution" "Bernoulli Distribution" "Binomial Distribution" "Bayesian Inference" "A/B-testing" "Probability" "Notebook" \
    --add_notebook_source_note

uv run ../notebook_convert.py \
    --nbpath beta-prior-sequential-binary-decisions.ipynb \
    --date "2026-05-17" \
    --layout $layout \
    --subdir ${subdir} \
    --description "See how Beta-Bernoulli updates work one observation at a time in A/B tests and bandits, and how the Pólya urn explains self-reinforcing feedback." \
    --image "/images/ab_to_rl/beta-prior-sequential-binary-decisions-preview.png" \
    --tags "Beta Distribution" "Bernoulli Distribution" "Beta-Binomial Distribution" "Bayesian Inference" "A/B-testing" "Multi-Armed Bandit (MAB)" "Sequential Data" "Notebook" \
    --add_notebook_source_note
