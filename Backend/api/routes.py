from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List
import uuid

from api.models import (
    InstructionRequest, 
    PipelineResponse, 
    JobStatus, 
    ErrorResponse
)
from api.pipeline_service import pipeline_service

router = APIRouter()

@router.post("/run-pipeline", response_model=dict)
async def run_pipeline(instruction: InstructionRequest):
    """
    Start a new pipeline run with the given instruction.
    Returns a job ID that can be used to check status and get results.
    """
    try:
        job_id = await pipeline_service.run_pipeline_async(instruction)
        return {
            "job_id": job_id,
            "message": "Pipeline started successfully",
            "status": "pending"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start pipeline: {str(e)}"
        )

@router.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get the status of a pipeline job.
    Returns the exact same format as metadata.json with combinations array.
    """
    # Get job status from file (which merges with in-memory status)
    job = pipeline_service.get_job_status_from_file(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    # Convert combinations from dict to CombinationResult objects
    combinations = []
    if job.get("combinations") is not None:
        from api.models import CombinationResult
        combinations = [CombinationResult(**combo) for combo in job.get("combinations", [])]
    
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress"),
        message=job.get("message"),
        created_at=job["created_at"],
        completed_at=job.get("completed_at"),
        error=job.get("error"),
        # Include metadata.json fields
        episode_name=job.get("episode_name"),
        task=job.get("task"),
        url=job.get("url"),
        steps=job.get("steps"),
        expected_behavior=job.get("expected_behavior"),
        combinations=combinations
    )

@router.get("/results/{job_id}", response_model=PipelineResponse)
async def get_job_results(job_id: str):
    """
    Get the results of a completed pipeline job.
    """
    job = pipeline_service.get_job_status(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed yet. Current status: {job['status']}"
        )
    
    if not job.get("result"):
        raise HTTPException(
            status_code=500,
            detail="Job completed but no results available"
        )
    
    return job["result"]

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and its data.
    """
    job = pipeline_service.get_job_status(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    # Remove job from service
    del pipeline_service.jobs[job_id]
    
    return {"message": "Job deleted successfully"}

@router.get("/jobs", response_model=List[JobStatus])
async def list_jobs():
    """
    List all jobs with their status.
    """
    jobs = []
    for job_id, job_data in pipeline_service.jobs.items():
        # Get job status from file to get latest combinations
        job = pipeline_service.get_job_status_from_file(job_id)
        if not job:
            continue
            
        # Convert combinations from dict to CombinationResult objects
        combinations = []
        if job.get("combinations") is not None:
            from api.models import CombinationResult
            combinations = [CombinationResult(**combo) for combo in job.get("combinations", [])]
        
        jobs.append(JobStatus(
            job_id=job_id,
            status=job["status"],
            progress=job.get("progress"),
            message=job.get("message"),
            created_at=job["created_at"],
            completed_at=job.get("completed_at"),
            error=job.get("error"),
            episode_name=job.get("episode_name"),
            task=job.get("task"),
            url=job.get("url"),
            steps=job.get("steps"),
            expected_behavior=job.get("expected_behavior"),
            combinations=combinations
        ))
    
    return jobs

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "active_jobs": len(pipeline_service.jobs)
    }
