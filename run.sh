#!/bin/bash
# Launch the Streamlit linear equation solver
source source_me.sh && python3 -m streamlit run linear_solver.py "$@"
