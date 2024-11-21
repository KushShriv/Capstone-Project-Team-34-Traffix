#!/bin/bash

echo "Starting all scripts..."

# Run each Python script in the background
python3 image_capturing.py &
python3 orchestrator.py &

echo "All scripts have been started."

# Wait for all background processes to complete
wait

echo "All scripts have completed."
