#!/usr/bin/env bash

layout="post"
subdir="blog/rnn_implementation"

../notebook_convert.py \
    --nbpath rnn-implementation-part01.ipynb \
    --date "2015-09-27" \
    --layout $layout \
    --subdir ${subdir} \
    --description "How to implement a minimal recurrent neural network (RNN) from scratch with Python and NumPy. The RNN is simple enough to visualize the loss surface and explore why vanishing and exploding gradients can occur during optimization. For stability, the RNN will be trained with backpropagation through time using the RProp optimization algorithm." \
    --tags "Neural Networks" "Recurrent Neural Network (RNN)" "Machine Learning" "NumPy" "Backpropagation" "RProp" "Sequential Data" "Notebook"

../notebook_convert.py \
    --nbpath rnn-implementation-part02.ipynb \
    --date "2015-09-27" \
    --layout $layout \
    --subdir ${subdir} \
    --description "How to implement and train a simple recurrent neural network (RNN) with input data stored as a tensor. The RNN will be learning how to perform binary addition as a toy problem. RMSProp and Nesterov momentum are used as a gradient-based optimization algorithm during training." \
    --tags "Neural Networks" "Recurrent Neural Network (RNN)" "Machine Learning" "NumPy" "RMSProp" "Nonlinearity" "Nesterov momentum" "Sequential Data" "Notebook"
