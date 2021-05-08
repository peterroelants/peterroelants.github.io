#!/usr/bin/env bash

layout="post"
subdir="blog/misc"

../notebook_convert.py \
    --nbpath multi-armed-bandit-implementation.ipynb \
    --date "2018-09-26" \
    --layout $layout \
    --subdir ${subdir} \
    --description "How to implement a Bayesian multi-armed bandit model in Python, and use it to simulate an online test. The model is based on the beta distribution and Thompson sampling." \
    --tags "Multi-Armed Bandit (MAB)" "A/B-testing" "Beta Distribution" "Notebook"

../notebook_convert.py \
    --nbpath multivariate-normal-primer.ipynb \
    --date "2018-09-28" \
    --layout $layout \
    --subdir ${subdir} \
    --description "Introduction to the multivariate normal distribution (Gaussian). We'll describe how to sample from this distribution and how to compute its conditionals and marginals." \
    --tags "Gaussian Distribution" "Probability" "Sampling" "Notebook"

../notebook_convert.py \
    --nbpath linear-regression-four-ways.ipynb \
    --date "2018-10-22" \
    --layout $layout \
    --subdir ${subdir} \
    --description "Linear regression implemented in four different ways. We'll describe the model and four different ways of estimating its parameters: MLE, OLS, gradient descent, & MCMC." \
    --tags "Linear Regression" "MCMC" "Probability" "Gradient Descent" "Least Squares" "Metropolis-Hastings" "Machine Learning" "Notebook"
