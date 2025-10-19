import json
import os
import sys
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the Backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models import InstructionRequest, PipelineResponse, CombinationResult, TaskStep, BrowserContext

class SimplePipelineRunner:
    """Simplified pipeline runner that creates mock results for testing"""
    
    def __init__(self):
        self.results = {}
    
    def run_pipeline(self, instruction: InstructionRequest) -> PipelineResponse:
        """
        Run the pipeline for a single instruction and return results
        """
        # Generate episode name
        episode_name = f"{instruction.task.lower().replace(' ', '_')}_{str(uuid.uuid4())[:8]}"
        
        # Create base episode directory
        base_episode_dir = f"data/results/{episode_name}"
        os.makedirs(base_episode_dir, exist_ok=True)
        
        # Run pipeline for each device-browser combination
        combinations = []
        total_runtime = 0.0
        successful_combinations = 0
        failed_combinations = 0
        
        for device in instruction.devices:
            for browser in instruction.browsers:
                try:
                    # Create mock result for testing
                    result = self._create_mock_result(instruction, device, browser, episode_name)
                    combinations.append(result)
                    total_runtime += result.runtime_sec
                    if result.success:
                        successful_combinations += 1
                    else:
                        failed_combinations += 1
                    
                except Exception as e:
                    print(f"Error running {device}_{browser}: {str(e)}")
                    failed_combinations += 1
        
        # Create response
        response = PipelineResponse(
            episode_name=episode_name,
            task=instruction.task,
            url=instruction.url,
            steps=instruction.steps,
            expected_behavior=instruction.expected_behavior,
            combinations=combinations,
            total_combinations=len(instruction.devices) * len(instruction.browsers),
            successful_combinations=successful_combinations,
            failed_combinations=failed_combinations,
            total_runtime_sec=total_runtime,
            created_at=datetime.now()
        )
        
        return response
    
    def _create_mock_result(self, instruction: InstructionRequest, device: str, browser: str, episode_name: str) -> CombinationResult:
        """Create a mock result for testing purposes"""
        
        # Mock steps
        mock_steps = [
            f"Navigate to {instruction.url}",
            f"Execute task: {instruction.task}",
            f"Verify expected behavior: {instruction.expected_behavior}"
        ]
        
        # Mock browser context
        viewport = "375x667" if device == "mobile" else "1280x720"
        
        # Mock success (randomly fail some combinations for testing)
        import random
        success = random.choice([True, True, True, False])  # 75% success rate
        
        return CombinationResult(
            goal=instruction.task,
            eps_name=f"{episode_name}/{device}_{browser}",
            task=TaskStep(steps=mock_steps),
            start_url=instruction.url,
            browser_context=BrowserContext(
                os="darwin",
                viewport=viewport,
                cookies_enabled=True
            ),
            success=success,
            total_steps=len(mock_steps),
            runtime_sec=random.uniform(30.0, 120.0),
            total_tokens=random.randint(10000, 50000),
            gpt_output=f"Mock execution completed for {device} {browser}",
            wrong_behavior=not success,
            explanation=f"Mock explanation for {device} {browser} execution",
            expected_behavior=instruction.expected_behavior,
            device=device,
            browser=browser
        )

# Global runner instance
simple_pipeline_runner = SimplePipelineRunner()
