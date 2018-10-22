#!/usr/bin/env bash

set -eu

layout="post"
subdir="blog/cross_entropy"

../notebook_convert.py \
    --nbpath cross-entropy-logistic.ipynb \
    --date "2015-06-10" \
    --layout ${layout} \
    --subdir ${subdir} \
    --description "Description of the logistic function used to model binary classification problems. Contains derivations of the gradients used for optimizing any parameters with regards to the cross-entropy loss function." \
    --tags "Logistic Function" "Logistic Regression" "Machine Learning" "Cross-Entropy" "Classification" "Gradient Descent" "Neural Networks" "Notebook"

../notebook_convert.py \
    --nbpath cross-entropy-softmax.ipynb \
    --date "2015-06-11" \
    --layout ${layout} \
    --subdir ${subdir} \
    --description "Description of the softmax function used to model multiclass classification problems. Contains derivations of the gradients used for optimizing any parameters with regards to the cross-entropy loss function." \
    --tags "Softmax" "Logistic Regression" "Machine Learning" "Cross-Entropy" "Classification" "Gradient Descent" "Neural Networks" "Notebook"
