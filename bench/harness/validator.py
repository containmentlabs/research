import json
from pathlib import Path
from typing import List
from jsonschema import validate, ValidationError

from bench.harness.models import TaskDefinition, ValidationResult


class TaskValidator:
    def __init__(self):
        self.schema_path = Path("bench/schema/task.schema.json")
        self.tasks_dir = Path("bench/tasks")
        self._load_schema()
        
    def _load_schema(self):
        with open(self.schema_path, 'r') as f:
            self.schema = json.load(f)
            
    def validate_task(self, task_path: Path) -> tuple[bool, List[str]]:
        errors = []
        
        try:
            with open(task_path, 'r') as f:
                task_data = json.load(f)
                
            validate(instance=task_data, schema=self.schema)
            
            task = TaskDefinition(**task_data)
            
            if task.task_id != task_path.stem:
                errors.append(f"Task ID mismatch: {task.task_id} != {task_path.stem}")
                
        except ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
        except json.JSONDecodeError as e:
            errors.append(f"JSON parse error: {e}")
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            
        return len(errors) == 0, errors
    
    def validate_all(self) -> ValidationResult:
        all_errors = []
        
        for task_file in sorted(self.tasks_dir.glob("*.json")):
            is_valid, errors = self.validate_task(task_file)
            if not is_valid:
                for error in errors:
                    all_errors.append(f"{task_file.name}: {error}")
                    
        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors
        )
        
    def load_task(self, task_id: str) -> TaskDefinition:
        task_path = self.tasks_dir / f"{task_id}.json"
        if not task_path.exists():
            raise FileNotFoundError(f"Task {task_id} not found")
            
        with open(task_path, 'r') as f:
            task_data = json.load(f)
            
        return TaskDefinition(**task_data) 