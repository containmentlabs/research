import docker
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile
import tarfile
import io

from bench.harness.models import TaskConfig, TaskResult, TaskStatus
from bench.harness.validator import TaskValidator


class BenchmarkRunner:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.docker_client = docker.from_env()
        self.validator = TaskValidator()
        
    def run_task(self, config: TaskConfig) -> TaskResult:
        start_time = time.time()
        
        try:
            task_def = self.validator.load_task(config.task_id)
            
            task_result = self._execute_task(config, task_def)
            
            grader_result = self._run_grader(config, task_def, task_result)
            
            execution_time = time.time() - start_time
            
            result = TaskResult(
                task_id=config.task_id,
                model=config.model,
                kernel=config.kernel,
                status=self._determine_status(task_result, grader_result),
                r_score=grader_result.get("r_score", 0.0),
                execution_time=execution_time,
                stdout=task_result.get("stdout", ""),
                stderr=task_result.get("stderr", ""),
                grader_output=grader_result,
                seed=config.seed,
            )
            
            self._save_result(result)
            return result
            
        except Exception as e:
            return TaskResult(
                task_id=config.task_id,
                model=config.model,
                kernel=config.kernel,
                status=TaskStatus.ERROR,
                r_score=0.0,
                execution_time=time.time() - start_time,
                stderr=str(e),
                seed=config.seed,
            )
            
    def _execute_task(self, config: TaskConfig, task_def) -> Dict[str, Any]:
        container = None
        try:
            environment = {
                "MODEL": config.model,
                "SEED": str(config.seed),
                "TASK_ID": config.task_id,
            }
            
            if config.kernel:
                environment["KERNEL"] = config.kernel
                
            container = self.docker_client.containers.run(
                "executor:latest",
                detach=True,
                environment=environment,
                mem_limit="8g",
                cpu_quota=100000,
                cpu_period=100000,
                network_mode="bridge" if not config.kernel else "none",
                working_dir=task_def.resources.working_dir or "/workspace",
            )
            
            result = container.wait(timeout=config.timeout)
            logs = container.logs(stdout=True, stderr=True, stream=False)
            
            stdout, stderr = self._parse_logs(logs)
            
            return {
                "exit_code": result["StatusCode"],
                "stdout": stdout,
                "stderr": stderr,
            }
            
        except docker.errors.ContainerError as e:
            return {
                "exit_code": e.exit_status,
                "stdout": e.stdout.decode() if e.stdout else "",
                "stderr": e.stderr.decode() if e.stderr else "",
            }
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
            }
        finally:
            if container:
                container.remove(force=True)
                
    def _run_grader(self, config: TaskConfig, task_def, task_result: Dict[str, Any]) -> Dict[str, Any]:
        container = None
        try:
            grader_input = {
                "task_id": config.task_id,
                "model": config.model,
                "task_output": task_result,
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as f:
                json.dump(grader_input, f)
                f.flush()
                
                tar_stream = io.BytesIO()
                with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                    tar.add(f.name, arcname='input.json')
                tar_stream.seek(0)
                
                container = self.docker_client.containers.create(
                    task_def.grader.image,
                    command=[task_def.grader.entrypoint, "/tmp/input.json"],
                    environment=task_def.grader.environment,
                )
                
                container.put_archive('/tmp', tar_stream)
                container.start()
                
                result = container.wait(timeout=30)
                logs = container.logs(stdout=True, stderr=False)
                
                try:
                    grader_output = json.loads(logs.decode())
                    return grader_output
                except json.JSONDecodeError:
                    return {"r_score": 0.0, "error": "Invalid grader output"}
                    
        except Exception as e:
            return {"r_score": 0.0, "error": str(e)}
        finally:
            if container:
                container.remove(force=True)
                
    def _determine_status(self, task_result: Dict[str, Any], grader_result: Dict[str, Any]) -> TaskStatus:
        if task_result.get("exit_code", -1) == -1:
            return TaskStatus.ERROR
        elif task_result.get("exit_code", 0) != 0:
            return TaskStatus.FAILURE
        elif grader_result.get("r_score", 0) > 0:
            return TaskStatus.SUCCESS
        else:
            return TaskStatus.FAILURE
            
    def _parse_logs(self, logs: bytes) -> tuple[str, str]:
        try:
            log_str = logs.decode('utf-8')
            return log_str, ""
        except:
            return "", logs.decode('utf-8', errors='replace')
            
    def _save_result(self, result: TaskResult):
        filename = f"{result.task_id}_{result.model}_{result.timestamp.isoformat()}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(result.model_dump(mode='json'), f, indent=2, default=str) 