#!/bin/bash
# Deploy to Streamlit Community Cloud
# Opens the deployment page in your browser.
# Streamlit Cloud does not have a CLI, so deployment is done through the web UI.

REPO="vosslab/streamlit-linear-equation-solver"
BRANCH="main"
MAIN_FILE="linear_solver.py"

echo "Pushing latest changes to GitHub..."
git push origin "$BRANCH"

echo ""
echo "Opening Streamlit Community Cloud deploy page..."
echo "  Repository: $REPO"
echo "  Branch:     $BRANCH"
echo "  Main file:  $MAIN_FILE"
echo ""

# Open the Streamlit Cloud new app page
open "https://share.streamlit.io/deploy?repository=${REPO}&branch=${BRANCH}&mainModule=${MAIN_FILE}"
