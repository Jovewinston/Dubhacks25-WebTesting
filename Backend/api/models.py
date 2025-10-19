from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class InstructionRequest(BaseModel):
    """Request model for pipeline instruction"""
    url: str = Field(..., description="Target URL for testing")
    task: str = Field(..., description="Task description")
    steps: str = Field(..., description="Step-by-step instructions")
    expected_behavior: str = Field(..., description="Expected behavior description")
    devices: List[str] = Field(default=["desktop"], description="List of devices to test")
    browsers: List[str] = Field(default=["chrome"], description="List of browsers to test")

class BrowserContext(BaseModel):
    """Browser context information"""
    os: str
    viewport: str
    cookies_enabled: bool

class TaskStep(BaseModel):
    """Individual task step"""
    steps: List[str]

class CombinationResult(BaseModel):
    """Result for a single device-browser combination"""
    goal: str
    eps_name: str
    task: TaskStep
    start_url: str
    browser_context: BrowserContext
    success: bool
    total_steps: int
    runtime_sec: float
    total_tokens: int
    gpt_output: Optional[str] = None
    wrong_behavior: Optional[bool] = False  # Make optional with default
    explanation: Optional[str] = None
    expected_behavior: Optional[str] = None  # Make optional
    device: str
    browser: str
    
    class Config:
        # Allow extra fields from metadata that we don't need
        extra = "allow"

class PipelineResponse(BaseModel):
    """Response model for pipeline results"""
    episode_name: str
    task: str
    url: str
    steps: str
    expected_behavior: str
    combinations: List[CombinationResult]
    total_combinations: int
    successful_combinations: int
    failed_combinations: int
    total_runtime_sec: float
    created_at: datetime

class JobStatus(BaseModel):
    """Job status for async processing"""
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: Optional[int] = None  # 0-100
    message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    # Include the full metadata-like structure
    episode_name: Optional[str] = None
    task: Optional[str] = None
    url: Optional[str] = None
    steps: Optional[str] = None
    expected_behavior: Optional[str] = None
    combinations: Optional[List[CombinationResult]] = None
    
    class Config:
        # Configure JSON encoding for datetime
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime
