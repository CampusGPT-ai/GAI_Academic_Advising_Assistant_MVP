#!/bin/bash

# Find the PID of the process running on port 8000
echo $(lsof -i :5000 -t)
PID=$(lsof -i :5000 -t)


# Check if a PID was found
if [ -z "$PID" ]; then
    echo "No process found on port 5000."
else
    # Kill the process
    kill -9 $PID
    if [ $? -eq 0 ]; then
        echo "Process on port 8000 has been terminated."
    else
        echo "Failed to terminate process on port 5000."
    fi
fi
