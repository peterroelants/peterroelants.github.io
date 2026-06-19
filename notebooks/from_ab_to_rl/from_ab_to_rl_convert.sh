#!/usr/bin/env bash

set -eu

layout="post"
subdir="blog/from_ab_to_rl"
date="2026-06-15"

uv run ../notebook_convert.py \
    --nbpath post_01_bayesian_ab_testing.ipynb \
    --date "${date}" \
    --layout "${layout}" \
    --subdir "${subdir}" \
    --description "Connect fixed A/B testing to Bayesian posterior uncertainty over click-through rates, and use that uncertainty to make one final decision." \
    --image "/images/social/2026-06-15-post_01_bayesian_ab_testing-preview.png" \
    --tags "A/B-testing" "Bayesian Inference" "Beta Distribution" "Bernoulli Distribution" "Binomial Distribution" "Probability" "Notebook" \
    --add_notebook_source_note

uv run ../notebook_convert.py \
    --nbpath post_02_multi_armed_bandits.ipynb \
    --date "${date}" \
    --layout "${layout}" \
    --subdir "${subdir}" \
    --description "Move from fixed A/B testing to online learning with Bayesian multi-armed bandits, probability matching, and Thompson sampling." \
    --image "/images/social/2026-06-15-post_02_multi_armed_bandits-preview.png" \
    --tags "Multi-Armed Bandit (MAB)" "Thompson Sampling" "A/B-testing" "Bayesian Inference" "Beta Distribution" "Online Learning" "Notebook" \
    --add_notebook_source_note

uv run ../notebook_convert.py \
    --nbpath post_03_delayed_feedback_menace.ipynb \
    --date "${date}" \
    --layout "${layout}" \
    --subdir "${subdir}" \
    --description "Use MENACE and tic-tac-toe to move from one-step bandit feedback to state-dependent policies and delayed rewards." \
    --image "/images/social/2026-06-15-post_03_delayed_feedback_menace-preview.png" \
    --tags "Reinforcement Learning" "Policy Learning" "Delayed Rewards" "Notebook" \
    --add_notebook_source_note
