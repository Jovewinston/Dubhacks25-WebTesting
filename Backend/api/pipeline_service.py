import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os

# Add the Backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.pipeline_runner import pipeline_runner
from api.models import InstructionRequest, PipelineResponse, CombinationResult, TaskStep, BrowserContext

class PipelineService:
    """Service for running the web testing pipeline"""
    
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
    
    async def run_pipeline_async(self, instruction: InstructionRequest) -> str:
        """Run pipeline asynchronously and return job ID"""
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        self.jobs[job_id] = {
            "status": "pending",
            "progress": 0,
            "message": "Starting pipeline...",
            "created_at": datetime.now(),
            "instruction": instruction,
            "result": None,
            "error": None
        }
        
        # Start pipeline in background
        asyncio.create_task(self._execute_pipeline(job_id, instruction))
        
        return job_id
    
    async def _execute_pipeline(self, job_id: str, instruction: InstructionRequest):
        """Execute the pipeline in background with incremental updates"""
        try:
            # Update status to running
            self.jobs[job_id].update({
                "status": "running",
                "progress": 10,
                "message": "Initializing pipeline...",
                "completed_combinations": [],
                "total_combinations": len(instruction.devices) * len(instruction.browsers)
            })
            
            # Run the pipeline with incremental updates
            loop = asyncio.get_event_loop()
            pipeline_response = await loop.run_in_executor(
                None, 
                self._run_pipeline_with_updates,
                job_id,
                instruction
            )
            
            # Update job with final result
            self.jobs[job_id].update({
                "status": "completed",
                "progress": 100,
                "message": "Pipeline completed successfully",
                "completed_at": datetime.now(),
                "result": pipeline_response
            })
            
        except Exception as e:
            # Update job with error
            self.jobs[job_id].update({
                "status": "failed",
                "progress": 0,
                "message": f"Pipeline failed: {str(e)}",
                "completed_at": datetime.now(),
                "error": str(e)
            })
    
    def _run_pipeline_with_updates(self, job_id: str, instruction: InstructionRequest):
        """Run pipeline and read from existing metadata.json files"""
        from api.pipeline_runner import pipeline_runner
        
        # Use job_id as the folder name instead of episode_name
        import os
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_episode_dir = os.path.join(backend_dir, "data", "results", job_id)
        os.makedirs(base_episode_dir, exist_ok=True)
        
        # Generate episode name for internal use
        episode_name = f"{instruction.task.lower().replace(' ', '_')}"
        
        # Store episode info for easy retrieval (no need for separate job_status.json)
        self.jobs[job_id]["episode_name"] = episode_name
        self.jobs[job_id]["base_episode_dir"] = base_episode_dir
        self.jobs[job_id]["task"] = instruction.task
        self.jobs[job_id]["url"] = instruction.url
        self.jobs[job_id]["steps"] = instruction.steps
        self.jobs[job_id]["expected_behavior"] = instruction.expected_behavior
        self.jobs[job_id]["devices"] = instruction.devices
        self.jobs[job_id]["browsers"] = instruction.browsers
        
        # Run the pipeline - it will create metadata.json for each combination
        response = pipeline_runner.run_pipeline(
            instruction, 
            episode_name, 
            base_episode_dir
        )
        
        return response
    
    def _initialize_job_status_file(self, filepath: str, job_id: str, instruction: InstructionRequest, episode_name: str):
        """Initialize the shared job status JSON file - matches metadata.json format"""
        import json
        from datetime import datetime
        
        # Use the exact same format as metadata.json
        initial_status = {
            "episode_name": episode_name,
            "task": instruction.task,
            "url": instruction.url,
            "steps": instruction.steps,
            "expected_behavior": instruction.expected_behavior,
            "combinations": []  # Will be populated as each combination completes
        }
        
        with open(filepath, 'w') as f:
            json.dump(initial_status, f, indent=2)
    
    def get_job_status_from_file(self, job_id: str):
        """Read job status from the shared metadata.json file at the base episode folder"""
        import json
        import os
        
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        base_episode_dir = job.get("base_episode_dir")
        if not base_episode_dir or not os.path.exists(base_episode_dir):
            # Return basic job info if directory doesn't exist yet
            return job
        
        # Path to the shared metadata.json file
        shared_metadata_path = os.path.join(base_episode_dir, "metadata.json")
        
        if not os.path.exists(shared_metadata_path):
            # File doesn't exist yet, return empty combinations
            job["combinations"] = []
            return job
        
        try:
            # Read the shared metadata.json file
            with open(shared_metadata_path, 'r', encoding='utf-8') as f:
                shared_metadata = json.load(f)
            
            # Extract combinations array
            combinations = shared_metadata.get("combinations", [])
            job["combinations"] = combinations
            
            # Calculate progress based on completed combinations
            total_combinations = len(job.get("devices", [])) * len(job.get("browsers", []))
            completed = len(combinations)
            
            if job["status"] == "running" and completed > 0:
                progress = int((completed / total_combinations) * 90) + 10  # 10-100%
                job["progress"] = progress
                job["message"] = f"Completed {completed}/{total_combinations} combinations"
            
            return job
        except Exception as e:
            print(f"Error reading shared metadata file: {str(e)}")
            job["combinations"] = []
            return job
    
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status by ID - checks memory first, then filesystem"""
        # First check if job is in memory
        job = self.jobs.get(job_id)
        if job:
            return job
        
        # If not in memory, try to load from filesystem
        return self._load_job_from_filesystem(job_id)
    
    def _load_job_from_filesystem(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Load a completed job from the filesystem by job_id"""
        import os
        import json
        
        # Check if job directory exists
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        job_dir = os.path.join(backend_dir, "data", "results", job_id)
        
        if not os.path.exists(job_dir):
            return None
        
        # Check if metadata.json exists
        metadata_path = os.path.join(job_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            return None
        
        try:
            # Read metadata.json
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Reconstruct job status from metadata
            job = {
                "job_id": job_id,
                "status": "completed",
                "progress": 100,
                "message": "Job completed (loaded from filesystem)",
                "created_at": datetime.now(),  # We don't have the original time
                "completed_at": datetime.now(),
                "error": None,
                "episode_name": metadata.get("episode_name", job_id),
                "task": metadata.get("task", ""),
                "url": metadata.get("url", ""),
                "steps": metadata.get("steps", ""),
                "expected_behavior": metadata.get("expected_behavior", ""),
                "combinations": metadata.get("combinations", []),
                "base_episode_dir": job_dir
            }
            
            return job
        except Exception as e:
            print(f"Error loading job from filesystem: {str(e)}")
            return None
    
    def get_job_result(self, job_id: str) -> Optional[PipelineResponse]:
        """Get job result by ID"""
        job = self.jobs.get(job_id)
        if job and job["status"] == "completed":
            return job["result"]
        return None

# Global service instance
pipeline_service = PipelineService()
