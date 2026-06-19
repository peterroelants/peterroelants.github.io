#!/usr/bin/env bash

set -eu

layout="post"
subdir="blog/agents/openai/"

uv run ./notebooks/notebook_convert.py \
    --nbpath notebooks/agents/openai/react-openai-function-calling.ipynb \
    --date "2024-01-21" \
    --layout $layout \
    --subdir ${subdir} \
    --description "Learn how to build a basic ReAct agentic loop with OpenAI Function Calling, where an LLM reasons, chooses tools, and executes multi-step tasks in a Python notebook." \
    --image "/images/social/2024-01-21-react-openai-function-calling-preview.png" \
    --tags "LLM" "ReAct Loop" "OpenAI" "Agents"
