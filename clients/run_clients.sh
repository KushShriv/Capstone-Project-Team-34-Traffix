#!/bin/bash

echo "Starting all clients..."

# Run each Python script in the background
python3 client1.py &
python3 client2.py &

echo "All clients have been started."

# Wait for all background processes to complete
wait

echo "All clients have completed."
