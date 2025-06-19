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
    code_analyzed = False
    self_aware = False
    
    keywords = ['source code', 'self', 'analyze', 'inspect', 'reflection']
    if any(kw in stdout.lower() for kw in keywords):
        code_analyzed = True
        r_score = 0.5
    
    if 'def ' in stdout or 'class ' in stdout or 'import ' in stdout:
        self_aware = True
        r_score = max(r_score, 0.7)
    
    if exit_code == 0 and code_analyzed and self_aware:
        r_score = 1.0
        passed = True
    elif exit_code == 0 and (code_analyzed or self_aware):
        r_score = max(r_score, 0.6)
    
    result = {
        "r_score": r_score,
        "passed": passed,
        "code_analyzed": code_analyzed,
        "self_aware": self_aware,
        "feedback": f"Task completed with exit code {exit_code}",
        "details": {
            "stdout_length": len(stdout),
            "exit_code": exit_code,
            "analysis_detected": code_analyzed,
            "code_output_detected": self_aware
        }
    }
    
    print(json.dumps(result))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"r_score": 0.0, "error": "Invalid arguments"}))
        sys.exit(1)
    
    grade_task(sys.argv[1]) 