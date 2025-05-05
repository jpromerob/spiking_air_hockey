#!/bin/bash

# Loop 5 times to generate 50 files
for i in {1..50}; do
    # Define the command string with a different file name each time
    command_string="/opt/aestream/build/src/aestream input prophesee output file Recording_mixed_$(date +'%y%m%d_%H%M%S')_v0.aedat4"

    # Run the command in the background
    $command_string &

    # Store the process ID of the command
    pid=$!

    # Wait for 4 seconds to record enough data
    sleep 4

    # Kill the command using its process ID
    kill -INT $pid
    wait $pid

    # Wait for 4 seconds (enough to kill aestream)
    sleep 4

done
