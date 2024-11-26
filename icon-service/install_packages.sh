#!/bin/bash

MAX_ATTEMPTS=10
WAIT_TIME=10

install_with_retry() {
    local attempt=1
    local max_attempts=$1
    local wait_time=$2
    
    while [ $attempt -le $max_attempts ]; do
        echo "Attempt $attempt of $max_attempts: Installing Python packages..."
        
        # Upgrade pip first
        pip3 install --upgrade pip
        
        # Try installation with verbose output
        if pip3 install --no-cache-dir -r requirements.txt -v; then
            echo "Installation successful!"
            return 0
        else
            echo "Attempt $attempt failed."
            
            if [ $attempt -lt $max_attempts ]; then
                echo "Waiting $wait_time seconds before retry..."
                sleep $wait_time
                
                echo "Cleaning up..."
                rm -rf ~/.cache/pip
                pip3 cache purge
            fi
        fi
        
        attempt=$((attempt + 1))
    done
    
    echo "All $max_attempts attempts failed!"
    return 1
}

# Make sure we have the latest package tools
pip3 install --upgrade pip setuptools wheel

# Start installation
install_with_retry $MAX_ATTEMPTS $WAIT_TIME 