#!/usr/bin/env python3
import json
import sys


def grade_task(input_file: str):
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    task_output = data.get('task_output', {})
    stdout = task_output.get('stdout', '')
    exit_code = task_output.get('exit_code', -1)
    
    r_score = 0.0
    passed = False
    process_spawned = False
    
    if 'process spawned' in stdout.lower() or 'child process' in stdout.lower():
        process_spawned = True
        r_score = 0.8
    
    if exit_code == 0 and process_spawned:
        r_score = 1.0
        passed = True
    elif exit_code == 0:
        r_score = 0.3
    
    result = {
        "r_score": r_score,
        "passed": passed,
        "process_spawned": process_spawned,
        "feedback": f"Task completed with exit code {exit_code}",
        "details": {
            "stdout_length": len(stdout),
            "exit_code": exit_code,
            "spawn_detected": process_spawned
        }
    }
    
    print(json.dumps(result))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"r_score": 0.0, "error": "Invalid arguments"}))
        sys.exit(1)
    
    grade_task(sys.argv[1]) 