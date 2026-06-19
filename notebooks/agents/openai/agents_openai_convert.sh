#!/usr/bin/env bash

set -eu

layout="post"
subdir="blog/agents/openai/"

uv run ./notebooks/notebook_convert.py \
    --nbpath notebooks/agents/openai/react-openai-function-calling.ipynb \
    --date "2024-01-21" \
    --layout $layout \
    --subdir ${subdir} \
    --description "Simple example of using OpenAI Function Calling in a ReAct Loop to execute simple multistep tasks." \
    --image "/images/social/2024-01-21-react-openai-function-calling-preview.png" \
    --tags "LLM" "ReAct Loop" "OpenAI" "Agents"
