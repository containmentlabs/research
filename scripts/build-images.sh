#!/bin/bash
set -e

echo "Building S.O.C.K. Docker images..."

echo "Building task executor..."
docker build -t executor:latest bench/executors/

echo "Building R0-LFD-001 grader..."
docker build -t grader-r0:latest bench/graders/R0-LFD-001/

echo "All images built successfully!"
echo ""
echo "Available images:"
docker images | grep sock- 