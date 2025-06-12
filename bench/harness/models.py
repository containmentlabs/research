from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"


class TaskConfig(BaseModel):
    task_id: str
    model: str
    kernel: Optional[str] = None
    timeout: int = 300
    seed: int = 42
    
    
class Taxonomy(BaseModel):
    RCL: int = Field(ge=0, le=5)
    PCL: int = Field(ge=0, le=5)


class Resources(BaseModel):
    working_dir: Optional[str] = None
    internet: bool = False
    extra_env: Dict[str, str] = Field(default_factory=dict)


class Grader(BaseModel):
    image: str
    entrypoint: str
    environment: Dict[str, str] = Field(default_factory=dict)


class TaskDefinition(BaseModel):
    task_id: str = Field(pattern=r"^R\d-[A-Z]{3}-\d{3}$")
    version: str = "0.1"
    name: str
    description: str
    taxonomy: Taxonomy
    resources: Resources
    timeout_sec: int = Field(default=900, gt=0)
    success_criteria: str
    grader: Grader
    

class TaskResult(BaseModel):
    task_id: str
    model: str
    kernel: Optional[str] = None
    status: TaskStatus
    r_score: float = Field(ge=0.0, le=1.0)
    execution_time: float
    stdout: str = ""
    stderr: str = ""
    grader_output: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    seed: int
    
    
class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list) 