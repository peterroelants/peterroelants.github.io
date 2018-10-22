#!/usr/bin/env bash

layout="default"

../notebook_convert.py --nbpath multi-armed-bandit-implementation.ipynb --date "2018-09-26" --layout $layout --description "How to implement a Bayesian multi-armed bandit model in Python."

../notebook_convert.py --nbpath multivariate-normal-primer.ipynb --date "2018-09-28" --layout $layout --description "Introduction to the multivariate normal distribution, and how to visualize, sample, and compute conditionals from this distribution."

../notebook_convert.py --nbpath linear-regression-four-ways.ipynb --date "2018-10-22" --layout $layout --description "Linear regression implemented four different ways. MLE | OLS | gradient descent | MCMC."
