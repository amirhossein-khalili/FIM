#!/bin/bash

# Build the Docker images
echo "Building Docker images..."
docker-compose build

# Start the containers in detached mode
echo "Starting containers..."
docker-compose up -d --rm

# Wait for the database to be ready
echo "Waiting for database to be ready..."
while [ "$(docker inspect --format='{{.State.Health.Status}}' postgres_contentcritic_container)" != "healthy" ]; do
  sleep 1
done
echo "Database is ready."

# Run database migrations
echo "Running database migrations..."
docker exec contentcritic_container python manage.py migrate

# Notify user the app is ready
echo "Application is running at http://localhost:8000"