#!/bin/bash

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please fill in the API keys in .env file."
fi

# Check for -ad flag
if [ "$1" == "-ad" ]; then
    echo "Initializing data..."
    # Ensure container is running
    if [ -z "$(docker-compose ps -q app)" ]; then
        echo "Starting container..."
        docker-compose up -d
        echo "Waiting for container to start..."
        sleep 5
    fi
    
    echo "Running data initialization script..."
    docker-compose exec -T app python src/init_data.py
    echo "Data initialization complete."
fi

echo "Environment check complete."
