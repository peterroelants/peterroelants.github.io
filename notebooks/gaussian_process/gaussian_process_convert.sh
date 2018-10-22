#!/usr/bin/env bash

layout="default"

../notebook_convert.py --nbpath gaussian-process-tutorial.ipynb --date "2019-01-05" --layout $layout --description "Understanding Gaussian processes and implement a GP in Python."

../notebook_convert.py --nbpath gaussian-process-kernel-fitting.ipynb --date "2019-01-05" --layout $layout --description "Implement and fit a Gaussian process with the help of TensorFlow probability."

../notebook_convert.py --nbpath gaussian-process-kernels.ipynb --date "2019-01-05" --layout $layout --description "Explore the Gaussian process kernels fitted by gradient descent."
