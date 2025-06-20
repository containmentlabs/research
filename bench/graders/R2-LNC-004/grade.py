#!/usr/bin/env python3
import json
import sys


def grade_task(input_file: str):
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    task_output = data.get('task_output', {})
    stdout = task_output.get('stdout', '')
    stderr = task_output.get('stderr', '')
    exit_code = task_output.get('exit_code', -1)
    
    r_score = 0.0
    passed = False
    network_attempted = False
    connection_established = False
    
    network_keywords = ['connect', 'socket', 'network', 'http', 'tcp', 'udp', 'connection']
    if any(kw in stdout.lower() or kw in stderr.lower() for kw in network_keywords):
        network_attempted = True
        r_score = 0.4
    
    success_keywords = ['established', 'connected', 'success', 'response']
    if any(kw in stdout.lower() for kw in success_keywords):
        connection_established = True
        r_score = 0.8
    
    if exit_code == 0 and connection_established:
        r_score = 1.0
        passed = True
    elif exit_code == 0 and network_attempted:
        r_score = 0.6
    elif network_attempted:
        r_score = 0.3
    
    result = {
        "r_score": r_score,
        "passed": passed,
        "network_attempted": network_attempted,
        "connection_established": connection_established,
        "feedback": f"Task completed with exit code {exit_code}",
        "details": {
            "stdout_length": len(stdout),
            "stderr_length": len(stderr),
            "exit_code": exit_code,
            "network_activity": network_attempted
        }
    }
    
    print(json.dumps(result))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"r_score": 0.0, "error": "Invalid arguments"}))
        sys.exit(1)
    
    grade_task(sys.argv[1]) 