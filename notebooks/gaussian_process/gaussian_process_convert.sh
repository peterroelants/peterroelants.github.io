#!/usr/bin/env bash

layout="post"
subdir="blog/gaussian_process"

../notebook_convert.py \
    --nbpath gaussian-process-tutorial.ipynb \
    --date "2019-01-05" \
    --layout $layout \
    --subdir ${subdir} \
    --description "This post explores some concepts behind Gaussian processes, such as stochastic processes and the kernel function. We will build up deeper understanding of Gaussian process regression by implementing them from scratch using Python and NumPy." \
    --tags "Gaussian Process" "Gaussian Distribution" "Probability" "Kernel" "NumPy" "Machine Learning" "Notebook"

../notebook_convert.py \
    --nbpath gaussian-process-kernel-fitting.ipynb \
    --date "2019-01-06" \
    --layout $layout \
    --subdir ${subdir} \
    --description "Fit a parameterized Gaussian process kernel on the Mauna Loa CO₂ dataset. We'll use TensorFlow probability to implement the model and fit the kernel parameters. Updated to use TensorFlow 2." \
    --tags "Gaussian Process" "Kernel" "TensorFlow" "Machine Learning" "Notebook"

../notebook_convert.py \
    --nbpath gaussian-process-kernels.ipynb \
    --date "2019-01-07" \
    --layout $layout \
    --subdir ${subdir} \
    --description "Explore the Gaussian process kernels fitted by the previous post by using various visualizations." \
    --tags "Gaussian Process" "Kernel" "Notebook"
