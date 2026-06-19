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
    --last_modified_at "2026-08-20" \
    --tags "A/B-testing" "Bayesian Inference" "Beta Distribution" "Bernoulli Distribution" "Binomial Distribution" "Probability" "Notebook" \
    --update "2026-08-20|Clarified Bayesian A/B testing foundations|Clarified the model assumptions, observed CTRs, simulation design, posterior comparison, and transition to online policies." \
    --externalize_media \
    --add_notebook_source_note

uv run ../notebook_convert.py \
    --nbpath post_02_multi_armed_bandits.ipynb \
    --date "${date}" \
    --layout "${layout}" \
    --subdir "${subdir}" \
    --description "Move from fixed A/B testing to online learning with Bayesian multi-armed bandits, probability matching, and Thompson sampling." \
    --image "/images/social/2026-06-15-post_02_multi_armed_bandits-preview.png" \
    --last_modified_at "2026-08-20" \
    --tags "Multi-Armed Bandit (MAB)" "Thompson Sampling" "A/B-testing" "Bayesian Inference" "Beta Distribution" "Online Learning" "Notebook" \
    --update "2026-08-20|Updated bandit and Thompson-sampling explanation|Updated the title and clarified posterior updates, policy notation, probability matching, regret, and the transition to RL." \
    --externalize_media \
    --add_notebook_source_note

uv run ../notebook_convert.py \
    --nbpath post_03_delayed_feedback_menace.ipynb \
    --date "${date}" \
    --layout "${layout}" \
    --subdir "${subdir}" \
    --description "Use MENACE and tic-tac-toe to move from one-step bandit feedback to state-dependent policies and delayed rewards." \
    --image "/images/social/2026-06-15-post_03_delayed_feedback_menace-preview.png" \
    --last_modified_at "2026-08-20" \
    --tags "Reinforcement Learning" "Policy Learning" "Delayed Rewards" "Notebook" \
    --update "2026-08-20|Updated title and expanded MENACE explanation|Added restored historical and SVG figures, clarified state-dependent policies and delayed rewards, and updated the title and series references." \
    --externalize_bokeh \
    --lazy_bokeh \
    --externalize_media \
    --add_notebook_source_note
