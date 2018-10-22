#!/usr/bin/env bash

layout="default"

../notebook_convert.py --nbpath neural-network-implementation-part01.ipynb --date "2015-06-10" --layout $layout --description "How to implement a simple neural network with Python, and train it using gradient descent."

../notebook_convert.py --nbpath neural-network-implementation-part02.ipynb --date "2015-06-10" --layout $layout --description "How to implement a logistic classification neural network in Python."

../notebook_convert.py --nbpath neural-network-implementation-part03.ipynb --date "2015-06-10" --layout $layout --description "How to implement a neural network with a hidden layer and train it using backpropagation."

../notebook_convert.py --nbpath neural-network-implementation-part04.ipynb --date "2015-06-10" --layout $layout --description "How to vectorize neural network computations using Numpy."
