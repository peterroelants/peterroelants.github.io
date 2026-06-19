#!/usr/bin/env bash

set -eu

layout="post"
subdir="blog/gaussian_process"

uv run ../notebook_convert.py \
    --nbpath gaussian-process-tutorial.ipynb \
    --date "2019-01-05" \
    --layout $layout \
    --subdir ${subdir} \
    --description "This post explores some concepts behind Gaussian processes, such as stochastic processes and the kernel function. We will build up deeper understanding of Gaussian process regression by implementing them from scratch using Python and NumPy." \
    --image "/images/social/2019-01-05-gaussian-process-tutorial-preview.png" \
    --tags "Gaussian Process" "Gaussian Distribution" "Probability" "Kernel" "NumPy" "Machine Learning" "Notebook" \
    --update "2026-05-04|Minor clarifications and re-ran the notebook." \
    --add_notebook_source_note

uv run ../notebook_convert.py \
    --nbpath gaussian-process-kernel-fitting.ipynb \
    --date "2019-01-06" \
    --layout $layout \
    --subdir ${subdir} \
    --description "Fit a parameterized Gaussian process kernel on the Mauna Loa CO₂ dataset. We'll use JAX and Optax to implement the model and fit the kernel parameters." \
    --image "/images/social/2019-01-06-gaussian-process-kernel-fitting-preview.png" \
    --tags "Gaussian Process" "Kernel" "JAX" "Machine Learning" "Notebook" \
    --update "2026-05-04|Reimplemented with JAX|Replaced the TensorFlow Probability implementation with explicit JAX code" \
    --add_notebook_source_note

uv run ../notebook_convert.py \
    --nbpath gaussian-process-kernels.ipynb \
    --date "2019-01-07" \
    --layout $layout \
    --subdir ${subdir} \
    --description "Explore the Gaussian process kernels fitted by the previous post by using various visualizations." \
    --image "/images/social/2019-01-07-gaussian-process-kernels-preview.png" \
    --tags "Gaussian Process" "Kernel" "JAX" "Notebook" \
    --update "2026-05-04|Reimplemented with JAX|Replaced the TensorFlow-oriented kernel examples with JAX-based code while keeping the kernel explanations and visuals." \
    --add_notebook_source_note
