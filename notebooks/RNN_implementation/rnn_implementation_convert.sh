#!/usr/bin/env bash

layout="default"

../notebook_convert.py --nbpath rnn-implementation-part01.ipynb --date "2015-09-27" --layout $layout --description "How to implement a simple RNN with Python, and how to train it with backpropagation through time using Rprop optimization."

../notebook_convert.py --nbpath rnn-implementation-part02.ipynb --date "2015-09-27" --layout $layout --description "How to train an RNN with input data stored as a tensor, and optimized with Rmsprop and Nesterov momentum."
