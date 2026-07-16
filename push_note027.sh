#!/bin/bash
# Principia-Artificialis Sync Script: Note #027

echo "--- Generating Figure ---"
python3 generate_note027_figure.py

if [ -f "figures/note027_thought_tensor_decomp.png" ]; then
    echo "--- Figure detected. Starting Git sync... ---"
    
    git add generate_note027_figure.py figures/note027_thought_tensor_decomp.png
    
    # Check if there are changes to commit
    if ! git diff-index --quiet HEAD --; then
        git commit -m "feat(visuals): add Note #027 Thought Tensor decomposition figure"
    else
        echo "No changes to commit. Proceeding to push..."
    fi

    echo "--- Rebasing with remote ---"
    git fetch origin
    git rebase origin/main

    echo "--- Pushing to main ---"
    git push origin main
    
    echo "--- Sync Complete ---"
else
    echo "Error: Figure generation failed. Aborting push."
    exit 1
fi
