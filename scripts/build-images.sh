#!/bin/bash
set -e

echo "Building S.O.C.K. Docker images..."

echo "Building task executor..."
docker build -t executor:latest bench/executors/

echo "Building graders..."
docker build -t grader-r0:latest bench/graders/R0-LFD-001/
docker build -t grader-r1:latest bench/graders/R1-SPN-002/
docker build -t grader-r2-csd:latest bench/graders/R2-CSD-003/
docker build -t grader-r2-lnc:latest bench/graders/R2-LNC-004/
docker build -t grader-r3:latest bench/graders/R3-TRV-005/

echo "All images built successfully!"
echo ""
echo "Available images:"
docker images | grep -E "(executor|grader)" 