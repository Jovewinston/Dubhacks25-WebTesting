from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import List
import uuid

from api.models import (
    InstructionRequest, 
    PipelineResponse, 
    JobStatus, 
    ErrorResponse,
    PerformanceData,
    PerformanceEvent
)
from api.pipeline_service import pipeline_service
from api.statsig_api_client import statsig_api_client
import logging

logger = logging.getLogger(__name__)

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
    Get the results of a completed pipeline job, including StatSig performance data.
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
    
    # Construct the result from job data if no result field exists
    if not job.get("result"):
        # Create PipelineResponse from job data
        from api.models import PipelineResponse, CombinationResult
        
        combinations = []
        if job.get("combinations"):
            for combo_data in job["combinations"]:
                combination = CombinationResult(
                    goal=combo_data.get("goal", ""),
                    eps_name=combo_data.get("eps_name", ""),
                    task={"steps": combo_data.get("task", {}).get("steps", [])},
                    start_url=combo_data.get("start_url", ""),
                    browser_context={
                        "os": combo_data.get("browser_context", {}).get("os", ""),
                        "viewport": combo_data.get("browser_context", {}).get("viewport", ""),
                        "cookies_enabled": combo_data.get("browser_context", {}).get("cookies_enabled", True)
                    },
                    success=combo_data.get("success", False),
                    total_steps=combo_data.get("total_steps", 0),
                    runtime_sec=combo_data.get("runtime_sec", 0.0),
                    total_tokens=combo_data.get("total_tokens", 0),
                    gpt_output=combo_data.get("gpt_output"),
                    wrong_behavior=combo_data.get("wrong_behavior", False),
                    explanation=combo_data.get("explanation"),
                    expected_behavior=combo_data.get("expected_behavior"),
                    device=combo_data.get("device", ""),
                    browser=combo_data.get("browser", "")
                )
                combinations.append(combination)
        
        result = PipelineResponse(
            episode_name=job.get("episode_name", ""),
            task=job.get("task", ""),
            url=job.get("url", ""),
            steps=job.get("steps", ""),
            expected_behavior=job.get("expected_behavior", ""),
            combinations=combinations,
            total_combinations=len(combinations),
            successful_combinations=len([c for c in combinations if c.success]),
            failed_combinations=len([c for c in combinations if not c.success]),
            total_runtime_sec=sum(c.runtime_sec for c in combinations),
            created_at=job.get("created_at", datetime.now())
        )
    else:
        # Use existing result
        result = job["result"]
    
    # Fetch StatSig performance data
    performance_data = None
    try:
        if statsig_api_client.is_configured():
            logger.info(f"Fetching StatSig performance data for job {job_id}")
            
            # Calculate time range based on job creation time
            job_created_at = job.get("created_at")
            if job_created_at:
                if isinstance(job_created_at, str):
                    job_created_at = datetime.fromisoformat(job_created_at.replace('Z', '+00:00'))
                
                # Fetch events from 1 hour before job start to now
                start_time = job_created_at - timedelta(hours=1)
                end_time = datetime.now()
                
                # Get detailed information from the most recent performance and web vitals events
                detailed_performance_data = statsig_api_client.get_most_recent_performance_details()
                
                # Extract performance metrics and add them directly to the result
                performance_metrics = {}
                
                # Get performance metrics from the most recent performance event
                if detailed_performance_data.get("performance_event") and detailed_performance_data["performance_event"].get("performance_metrics"):
                    perf_metrics = detailed_performance_data["performance_event"]["performance_metrics"]
                    
                    # Map to the exact field names requested
                    performance_metrics = {
                        "load_time_ms": perf_metrics.get("load_time_ms", ""),
                        "dom_interactive_time_ms": perf_metrics.get("dom_interactive_time_ms", ""),
                        "redirect_count": perf_metrics.get("redirect_count", ""),
                        "transfer_bytes": perf_metrics.get("transfer_bytes", ""),
                        "first_contentful_paint_time_ms": perf_metrics.get("first_contentful_paint_time_ms", ""),
                        "effective_connection_type": perf_metrics.get("effective_connection_type", ""),
                        "downlink_mbps": perf_metrics.get("downlink_mbps", ""),
                        "downlink_kbps": perf_metrics.get("downlink_kbps", ""),
                        "city": perf_metrics.get("city", ""),
                        "state": perf_metrics.get("state", ""),
                        "country": perf_metrics.get("country", "")
                    }
                
                # Add performance metrics directly to the result
                if isinstance(result, dict):
                    result.update(performance_metrics)
                else:
                    # If result is a PipelineResponse object, add as attributes
                    for key, value in performance_metrics.items():
                        setattr(result, key, value)
                
                logger.info(f"Successfully added performance metrics to result: {list(performance_metrics.keys())}")
            else:
                logger.warning(f"No created_at timestamp found for job {job_id}")
                performance_data = PerformanceData(
                    fetch_timestamp=datetime.now(),
                    fetch_successful=False,
                    error_message="No job timestamp available"
                )
        else:
            logger.warning("StatSig API client not configured, skipping performance data fetch")
            performance_data = PerformanceData(
                fetch_timestamp=datetime.now(),
                fetch_successful=False,
                error_message="StatSig API not configured"
            )
    except Exception as e:
        logger.error(f"Error fetching StatSig performance data: {str(e)}")
        performance_data = PerformanceData(
            fetch_timestamp=datetime.now(),
            fetch_successful=False,
            error_message=f"Error fetching performance data: {str(e)}"
        )
    
    # Add performance data to result
    if isinstance(result, dict):
        result["performance_data"] = performance_data
    else:
        # If result is a PipelineResponse object, update it
        result.performance_data = performance_data
    
    return result

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
