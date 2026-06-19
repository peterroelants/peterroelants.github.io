#!/usr/bin/env bash

set -eu

layout="post"
subdir="blog/diffusion_flow_matching"

uv run ../notebook_convert.py \
    --nbpath flow_matching_intro.ipynb \
    --date "2025-11-01" \
    --layout ${layout} \
    --subdir ${subdir} \
    --description "Visual introduction to flow matching. Illustrates the flow matching model, the velocity field, and the sampled paths using a simple 1D toy example." \
    --image "/images/social/2025-11-01-flow_matching_intro-preview.png" \
    --tags \
        "Flow Matching" \
        "Neural Networks" \
        "Velocity Field" \
        "Rectified Flow" \
        "Diffusion" \
        "Generative Models" \
        "Notebook"
