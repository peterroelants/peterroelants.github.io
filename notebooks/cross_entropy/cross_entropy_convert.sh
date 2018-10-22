#!/usr/bin/env bash

set -eu

layout="default"

../notebook_convert.py --nbpath cross-entropy-logistic.ipynb --date "2015-06-10" --layout $layout --description "How to model a binary classification problem with the logistic function and the cross-entropy loss function."

../notebook_convert.py --nbpath cross-entropy-softmax.ipynb --date "2015-06-10" --layout $layout --description "How to perform multiclass classification with the softmax function and cross-entropy loss function."
