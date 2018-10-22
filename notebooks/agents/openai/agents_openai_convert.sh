#!/usr/bin/env bash

layout="post"
subdir="blog/agents/openai/"

./notebooks/notebook_convert.py \
    --nbpath notebooks/agents/openai/react-openai-function-calling.ipynb \
    --date "2024-01-21" \
    --layout $layout \
    --subdir ${subdir} \
    --description "Simple example of using OpenAI Function Calling in a ReAct Loop to execute simple multistep tasks." \
    --tags "LLM" "ReAct Loop" "OpenAI" "Agents"
