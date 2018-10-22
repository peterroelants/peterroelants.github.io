#!/usr/bin/env bash

layout="post"
subdir="blog/neural_net_implementation"

../notebook_convert.py \
    --nbpath neural-network-implementation-part01.ipynb \
    --date "2015-06-12" \
    --layout $layout \
    --subdir ${subdir} \
    --description "How to implement, and optimize, a linear regression model from scratch using Python and NumPy. The linear regression model will be approached as a minimal regression neural network. The model will be optimized using gradient descent, for which the gradient derivations are provided." \
    --tags "Neural Networks" "Machine Learning" "NumPy" "Gradient Descent" "Linear Regression" "Notebook"

../notebook_convert.py \
    --nbpath neural-network-implementation-part02.ipynb \
    --date "2015-06-13" \
    --layout $layout \
    --subdir ${subdir} \
    --description "How to implement, and optimize, a logistic regression model from scratch using Python and NumPy. The logistic regression model will be approached as a minimal classification neural network. The model will be optimized using gradient descent, for which the gradient derivations are provided." \
    --tags "Neural Networks" "Machine Learning" "NumPy" "Classification" "Logistic Regression" "Cross-Entropy" "Gradient Descent" "Notebook"

../notebook_convert.py \
    --nbpath neural-network-implementation-part03.ipynb \
    --date "2015-06-14" \
    --layout $layout \
    --subdir ${subdir} \
    --description "Transition from single-layer linear models to a multi-layer neural network by adding a hidden layer with a nonlinearity. A minimal network is implemented using Python and NumPy. This minimal network is simple enough to visualize its parameter space. The model will be optimized on a toy problem using backpropagation and gradient descent, for which the gradient derivations are included." \
    --tags "Neural Networks" "Machine Learning" "NumPy" "Backpropagation" "Nonlinearity" "Radial Basis Function (RBF)" "Notebook"

../notebook_convert.py \
    --nbpath neural-network-implementation-part04.ipynb \
    --date "2015-06-15" \
    --layout $layout \
    --subdir ${subdir} \
    --description "Vectorization of the neural network and backpropagation algorithm for multi-dimensional data. Vectorization of operations is illustrated on a simple network implemented using Python and NumPy. The network is trained on a toy problem using gradient descent with momentum." \
    --tags "Neural Networks" "Machine Learning" "NumPy" "Vectorization" "Backpropagation" "Gradient checking" "Momentum" "Classification" "Notebook"

../notebook_convert.py \
    --nbpath neural-network-implementation-part05.ipynb \
    --date "2015-06-16" \
    --layout $layout \
    --subdir ${subdir} \
    --description "Generalization of neural networks to multiple layers. Illustrated on a simple network build from scratch using Python and NumPy. The network is trained on a digit classification toy problem using stochastic gradient descent." \
    --tags "Neural Networks" "Machine Learning" "NumPy" "Classification" "Backpropagation" "Gradient Descent" "Notebook"
