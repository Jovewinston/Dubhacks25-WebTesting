import json
import os
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the Backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.generate_trajectory import run_single_trajectory
from api.models import InstructionRequest, PipelineResponse, CombinationResult, TaskStep, BrowserContext

class PipelineRunner:
    """Modified pipeline runner that returns results instead of saving them"""
    
    def __init__(self):
        self.results = {}
    
    def run_pipeline(
        self, 
        instruction: InstructionRequest,
        episode_name: str = None,
        base_episode_dir: str = None
    ) -> PipelineResponse:
        """
        Run the pipeline for a single instruction and return results
        The pipeline creates metadata.json for each device-browser combination
        
        Args:
            instruction: The instruction to execute
            episode_name: Pre-generated episode name (if None, generates new one)
            base_episode_dir: Base episode directory path (if None, creates new one)
        """
        # Use provided episode name or generate new one
        if not episode_name:
            episode_name = f"{instruction.task.lower().replace(' ', '_')}_{str(uuid.uuid4())[:8]}"
        
        # Use provided base directory or create new one
        if not base_episode_dir:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            base_episode_dir = os.path.join(backend_dir, "data", "results", episode_name)
            os.makedirs(base_episode_dir, exist_ok=True)
        
        # Create shared metadata path and lock for thread-safe updates
        import concurrent.futures
        import threading
        
        shared_metadata_path = os.path.join(base_episode_dir, "metadata.json")
        metadata_lock = threading.Lock()
        
        # Initialize the shared metadata.json file immediately
        initial_metadata = {
            "episode_name": episode_name,
            "task": instruction.task,
            "url": instruction.url,
            "steps": instruction.steps,
            "expected_behavior": instruction.expected_behavior,
            "combinations": []
        }
        with open(shared_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(initial_metadata, f, indent=2, ensure_ascii=False)
        
        combinations = []
        total_runtime = 0.0
        successful_combinations = 0
        failed_combinations = 0
        
        # Create list of all device-browser combinations
        combinations_to_run = []
        for device in instruction.devices:
            for browser in instruction.browsers:
                combinations_to_run.append((device, browser))
        
        # Run all combinations in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(combinations_to_run)) as executor:
            # Submit all tasks
            future_to_combo = {
                executor.submit(
                    self._run_single_combination,
                    instruction, device, browser, episode_name, base_episode_dir,
                    shared_metadata_path, metadata_lock
                ): (device, browser) 
                for device, browser in combinations_to_run
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_combo):
                device, browser = future_to_combo[future]
                try:
                    result = future.result()
                    if result:
                        # Convert result to our format
                        combination_result = self._convert_combination_result(result, device, browser)
                        combinations.append(combination_result)
                        total_runtime += result.get("runtime_sec", 0.0)
                        if result.get("success", False):
                            successful_combinations += 1
                        else:
                            failed_combinations += 1
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
    
    def _run_single_combination(
        self, 
        instruction: InstructionRequest, 
        device: str, 
        browser: str, 
        episode_name: str,
        base_episode_dir: str,
        shared_metadata_path: str,
        metadata_lock
    ) -> Optional[Dict[str, Any]]:
        """Run a single device-browser combination - updates shared metadata.json"""
        try:
            # Create subdirectory for this combination
            combination_dir = os.path.join(base_episode_dir, f"{device}_{browser}")
            os.makedirs(combination_dir, exist_ok=True)
            
            # Set up directories structure
            dirs = {
                "trajectory_dir": combination_dir,
                "screenshot_dir": os.path.join(combination_dir, "screenshots"),
                "axtree_dir": os.path.join(combination_dir, "axtrees"),
                "gpt_summaries_dir": os.path.join(combination_dir, "gpt_summaries")
            }
            
            for dir_path in dirs.values():
                os.makedirs(dir_path, exist_ok=True)
            
            # Convert browser name to playwright format
            browser_mapping = {
                "chrome": "chromium",
                "firefox": "firefox", 
                "safari": "webkit"
            }
            playwright_browser = browser_mapping.get(browser, "chromium")
            
            # Run the trajectory - this returns the final_metadata for this combination
            # It will also update the shared metadata.json file automatically
            result = run_single_trajectory(
                instruction.url,
                instruction.task,
                instruction.steps,
                instruction.expected_behavior,
                device,
                playwright_browser,
                episode_name,
                0,  # idx (integer)
                1,  # total (integer)
                shared_metadata_path,  # shared_metadata_path - will be updated by pipeline
                metadata_lock,  # metadata_lock - for thread-safe updates
                None   # progress_tracker
            )
            
            # The result is the final_metadata for this single combination
            # The pipeline already created metadata.json in the combination folder
            if result:
                # Add device and browser info to the result
                result["device"] = device
                result["browser"] = browser
                result["eps_name"] = f"{episode_name}/{device}_{browser}"
            
            return result
            
        except Exception as e:
            print(f"Error in combination {device}_{browser}: {str(e)}")
            return None
    
    def _convert_combination_result(self, result: Dict[str, Any], device: str, browser: str) -> CombinationResult:
        """Convert pipeline result to our API format"""
        # The result is the final_metadata for this single combination
        # It should already have device and browser info added
        
        return CombinationResult(
            goal=result.get("goal", result.get("task", "")),
            eps_name=result.get("eps_name", f"{result.get('episode_name', '')}/{device}_{browser}"),
            task=TaskStep(steps=result.get("task", {}).get("steps", []) if isinstance(result.get("task"), dict) else []),
            start_url=result.get("start_url", result.get("url", "")),
            browser_context=BrowserContext(
                os=result.get("browser_context", {}).get("os", "unknown"),
                viewport=result.get("browser_context", {}).get("viewport", "unknown"),
                cookies_enabled=result.get("browser_context", {}).get("cookies_enabled", True)
            ),
            success=result.get("success", False),
            total_steps=result.get("total_steps", 0),
            runtime_sec=result.get("runtime_sec", 0.0),
            total_tokens=result.get("total_tokens", 0),
            gpt_output=result.get("gpt_output"),
            wrong_behavior=result.get("wrong_behavior", False),
            explanation=result.get("explanation"),
            expected_behavior=result.get("expected_behavior", ""),
            device=device,
            browser=browser
        )

# Global runner instance
pipeline_runner = PipelineRunner()
