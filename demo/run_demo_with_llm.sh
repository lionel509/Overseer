#!/bin/bash

# This script runs the Overseer CLI demo and records the session,
# including the simulated LLM output.

# Start recording the session to demo/output/demo_with_llm_session.log
# The -q flag runs in quiet mode
# The -c flag allows running a command
script -q demo/output/demo_with_llm_session.log python3 demo/demo_with_llm_output.py
