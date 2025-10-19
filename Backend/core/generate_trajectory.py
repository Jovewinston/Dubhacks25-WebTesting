import json
from playwright.sync_api import sync_playwright, TimeoutError
import os
import sys
import uuid
import time
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import threading
from dotenv import load_dotenv
from urllib.parse import urlparse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.new_generate_trajectory import chat_ai_playwright_code
from config import RESULTS_DIR, ACCOUNTS, BROWSER_SESSIONS_DIR, TOTAL_PERSONAS, PHASE1_INSTRUCTIONS_PER_PERSONA, PHASE2_INSTRUCTIONS_PER_PERSONA, ENABLE_CONFIDENCE_VALIDATION, ENABLE_POST_ACTION_VALIDATION, PASS_IMAGES_TO_GPT, CREATE_ANNOTATED_IMAGES
from utils.google_auth import ensure_google_login
from utils.trajectory_file_utils import (
    create_episode_directory, create_trajectory_file, create_error_log_file,
    update_playwright_error_log, update_trajectory, create_metadata,
    write_user_message, generate_trajectory_html, get_site_name_from_url
)
from utils.progress_tracker import ProgressTracker
from utils.element_utils import (
    get_comprehensive_element_data, create_simplified_element_summary,
    try_alternative_selectors, annotate_screenshot_with_bounding_boxes,
    get_all_open_tabs, check_for_new_tabs, switch_to_new_tab
)

# Knowledge base client for trajectory context
from utils.knowledge_base_client import get_trajectory_context

# Confidence validation utilities
from utils.confidence_validation import process_confidence_validation

# Post-action validation utilities
from utils.post_action_validation import process_post_action_validation

# StatSig integration utilities
from utils.statsig_injector import inject_statsig_sdk, log_custom_event, wait_for_statsig_ready, check_statsig_status

# Load environment variables from .env file
load_dotenv()




# ========== CONFIGURABLE PARAMETERS ==========
# These parameters are set by the end_to_end_pipeline.py file
PHASE = 1
MAX_RETRIES = 2
MAX_STEPS = 40  # Maximum number of steps before failing
ACTION_TIMEOUT = 10000  # 10 seconds timeout for actions
# Execution Modes:
# 0 - Automatic Mode: Processes all instructions without manual intervention
# 1 - Interactive Mode: Requires Enter press after each instruction for manual review
MODE = 0

# Knowledge base configuration
MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", "3000"))  # Maximum context length in characters
KNOWLEDGE_BASE_TYPE = os.getenv("KNOWLEDGE_BASE_TYPE", "graphrag")  # Type of knowledge base to use
SEARCH_CONTEXT = False  # Whether to search for relevant past trajectories for context

# StatSig configuration
STATSIG_CLIENT_KEY = os.getenv("STATSIG_CLIENT_KEY")  # StatSig client key from environment
ENABLE_STATSIG = bool(STATSIG_CLIENT_KEY)  # Enable StatSig if client key is provided
ENABLE_STATSIG_SESSION_REPLAY = True  # Enable session replay
ENABLE_STATSIG_AUTO_CAPTURE = True  # Enable auto-capture

# Directory to store all browser sessions
os.makedirs(BROWSER_SESSIONS_DIR, exist_ok=True)


def generate_episode_name(url: str) -> str:
    """Generate a meaningful episode name based on URL and UUID."""
    site_name = get_site_name_from_url(url)
    return f"{site_name}_{uuid.uuid4()}"


def fetch_trajectory_nodes(
    instruction: str,
    max_results: int = 3,
    max_context_length: int = 3000
) -> str:
    """
    Fetch relevant past trajectory nodes from vector database and extract steps/codes for LLM context.
    Uses modular vector database client that supports multiple database types.
    """
    return get_trajectory_context(
        query=instruction,
        max_results=max_results,
        max_context_length=max_context_length,
        kb_type=KNOWLEDGE_BASE_TYPE
    )
    
def save_metadata_with_device_browser(metadata, device, browser_type):
    """Helper to add device and browser info to metadata."""
    metadata["device"] = device
    metadata["browser"] = browser_type
    return metadata

def update_shared_metadata(shared_metadata_path, metadata_lock, new_metadata, task, url, steps, expected_behavior):
    """Update the shared metadata.json file with a new device-browser result."""
    with metadata_lock:
        # Load existing shared metadata or create new
        if os.path.exists(shared_metadata_path):
            with open(shared_metadata_path, 'r', encoding='utf-8') as f:
                shared_data = json.load(f)
        else:
            shared_data = {
                "episode_name": new_metadata.get("eps_name", "").split("/")[0] if "/" in new_metadata.get("eps_name", "") else new_metadata.get("eps_name", ""),
                "task": task,
                "url": url,
                "steps": steps,
                "expected_behavior": expected_behavior,
                "combinations": []
            }
        
        # Add the new combination metadata
        shared_data["combinations"].append(new_metadata)
        
        # Save updated shared metadata
        with open(shared_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(shared_data, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Updated shared metadata: {len(shared_data['combinations'])} combination(s) completed")

def run_single_trajectory(url, task, steps, expected_behavior, device, browser_type, base_eps_name, idx, total, shared_metadata_path, metadata_lock, progress_tracker=None):
    """Run trajectory for a single device-browser combination and update shared metadata."""
    
    print(f"\n{'='*80}")
    print(f"🚀 Running: {device.upper()} - {browser_type.upper()}")
    print(f"📝 Task {idx + 1}/{total}: {task}")
    print(f"{'='*80}\n")
    
    # Will store metadata to return
    final_metadata = None
    
    # Configure viewport based on device
    if device == 'mobile':
        viewport = {"width": 375, "height": 667}  # iPhone SE size
    else:  # desktop
        viewport = {"width": 1280, "height": 720}
    
    with sync_playwright() as p:
        # Launch browser based on browser type
        if browser_type == 'chrome' or browser_type == 'chromium':
            browser = p.chromium.launch(headless=False)
        elif browser_type == 'firefox':
            browser = p.firefox.launch(
                headless=False,
                firefox_user_prefs={
                    "dom.webdriver.enabled": False,
                    "useAutomationExtension": False
                }
            )
        elif browser_type == 'safari':
            browser = p.webkit.launch(headless=False)
        else:
            print(f"⚠️ Unknown browser type: {browser_type}, defaulting to Chromium")
            browser = p.chromium.launch(headless=False)
        
        context = browser.new_context(viewport=viewport)
        
        try:
            # Create page for this device-browser combo
            page = context.new_page()
            page.set_default_timeout(ACTION_TIMEOUT)
            
            # Steps is already a string, no need to format
            full_task_description = f"{task}\n\nSteps:\n{steps}\n\nExpected Behavior:\n{expected_behavior}"
            
            # Create episode name with device-browser subfolder
            device_browser_folder = f"{device}_{browser_type}"
            eps_name = f"{base_eps_name}/{device_browser_folder}"
            
            dirs = create_episode_directory(RESULTS_DIR, eps_name)
            create_trajectory_file(dirs)  # Create empty trajectory.json
            create_error_log_file(dirs)   # Create empty error_log.json

            print(f"🌐 {url}")
            print(f"📝 Task: {task}")
            print(f"📋 Steps:\n{steps}")
            print(f"✅ Expected: {expected_behavior}")
            print(f"📁 Saving to: {eps_name}")
            
            # Start tracking this instruction
            if progress_tracker:
                progress_tracker.start_instruction(None, idx, f"{task} ({device}/{browser_type})", eps_name)

            # Fetch relevant past trajectories for context (if enabled)
            trajectory_context = ""
            if SEARCH_CONTEXT:
                print("🔍 Fetching relevant past trajectories...")
                trajectory_context = fetch_trajectory_nodes(task, max_results=3, max_context_length=MAX_CONTEXT_LENGTH)
                if trajectory_context:
                    print("✅ Found relevant past trajectories")
                    print("📄 Full trajectory context:")
                    print("=" * 50)
                    print(trajectory_context)
                    print("=" * 50)
                else:
                    print("ℹ️ No relevant past trajectories found")

            # Navigate to URL for this instruction
            page.goto(url)
            
            # Inject StatSig SDK if enabled
            if ENABLE_STATSIG and STATSIG_CLIENT_KEY:
                print("📊 Injecting StatSig SDK...")
                
                # Create unique user ID for this test session
                test_user_id = f"test_{device}_{browser_type}_{uuid.uuid4().hex[:8]}"
                
                # Custom properties for this test session
                custom_properties = {
                    "app": "web_testing",
                    "version": "1.0.0",
                    "device": device,
                    "browser": browser_type,
                    "task": task,
                    "url": url,
                    "episode": eps_name
                }
                
                # Inject StatSig SDK
                injection_success = inject_statsig_sdk(
                    page=page,
                    client_key=STATSIG_CLIENT_KEY,
                    user_id=test_user_id,
                    custom_properties=custom_properties,
                    enable_session_replay=ENABLE_STATSIG_SESSION_REPLAY,
                    enable_auto_capture=ENABLE_STATSIG_AUTO_CAPTURE
                )
                
                if injection_success:
                    print(f"✅ StatSig SDK injected successfully for user: {test_user_id}")
                    
                    # Wait for StatSig to be ready
                    if wait_for_statsig_ready(page, timeout=10000):
                        # Log test session start event
                        log_custom_event(page, "test_session_started", {
                            "task": task,
                            "url": url,
                            "device": device,
                            "browser": browser_type,
                            "episode": eps_name
                        })
                        print("📊 StatSig test session started")
                    else:
                        print("⚠️ StatSig not ready, continuing without it")
                else:
                    print("❌ StatSig injection failed, continuing without it")
            else:
                if not ENABLE_STATSIG:
                    print("ℹ️ StatSig disabled (no client key provided)")
                else:
                    print("ℹ️ StatSig not configured")
            
            # Handle login using the new module (if needed)
            # ensure_google_login(page, email, password, url)

            execution_history = []
            task_summarizer = []
            current_goal = full_task_description
            should_continue = True
            start_time = time.time()
            total_tokens = 0  # Initialize token counter
            
            # Track initial URL for reference
            initial_url = page.url
            print(f"📍 Starting URL: {initial_url}")
            
            # Initialize tab tracking
            initial_tabs = get_all_open_tabs(context)
            previous_tab_count = len(initial_tabs)
            previous_tab_urls = {tab['url'] for tab in initial_tabs}
            print(f"📑 Initial tabs: {previous_tab_count}")

            while should_continue:
                step_idx = len(task_summarizer)
                
                # Update progress tracker with current step
                if progress_tracker:
                    progress_tracker.update_step(None, step_idx)
                if step_idx >= MAX_STEPS:
                    print(f"❌ Maximum number of steps ({MAX_STEPS}) exceeded.")
                    runtime = time.time() - start_time
                    metadata = create_metadata(
                        "", url, task, full_task_description, None,  # Pass None for final_instruction
                        [step['step'] for step in task_summarizer],
                        False, step_idx, runtime, total_tokens, page, eps_name
                    )
                    if gpt_resp and "output" in gpt_resp:
                        metadata["gpt_output"] = gpt_resp["output"]
                    final_metadata = save_metadata_with_device_browser(metadata, device, browser_type)
                    update_shared_metadata(shared_metadata_path, metadata_lock, final_metadata, task, url, steps, expected_behavior)
                    generate_trajectory_html(dirs, metadata)
                    
                    # Mark instruction as failed in progress tracker
                    if progress_tracker:
                        progress_tracker.complete_instruction(None, idx, task, eps_name, success=False, error_message=f"Maximum steps ({MAX_STEPS}) exceeded")
                    should_continue = False
                    break

                screenshot = os.path.join(dirs['images'], f"screenshot_{step_idx+1:03d}.png")
                annotated_screenshot = os.path.join(dirs['annotated_images'], f"annotated_screenshot_{step_idx+1:03d}.png")
                axtree_file = os.path.join(dirs['axtree'], f"axtree_{step_idx+1:03d}.txt")
                targeting_data_file = os.path.join(dirs['targeting_data'], f"targeting_data_{step_idx+1:03d}.json")
                try:
                    page.screenshot(path=screenshot)
                    
                    # Get comprehensive element data instead of just accessibility tree
                    print(f"🔍 Collecting comprehensive element data for step {step_idx+1}...")
                    comprehensive_data = get_comprehensive_element_data(page, url)
                    
                    # Create simplified element data for axtree file and GPT
                    elements_data = create_simplified_element_summary(comprehensive_data['targeting_data'])
                    
                    # Use simplified data as the "tree"
                    tree = elements_data
                    
                    # Save simplified element data to axtree file (just annotation_id, role, name)
                    with open(axtree_file, 'w', encoding='utf-8') as f:
                        json.dump(elements_data, f, indent=2, ensure_ascii=False)
                    
                    # Save only the targeting data (not the entire comprehensive_data)
                    with open(targeting_data_file, 'w', encoding='utf-8') as f:
                        json.dump(comprehensive_data['targeting_data'], f, indent=2, ensure_ascii=False)
                    
                    # Create annotated screenshot with bounding boxes (only if enabled)
                    if CREATE_ANNOTATED_IMAGES:
                        print(f"🎨 Creating annotated screenshot with bounding boxes...")
                        annotated_path = annotate_screenshot_with_bounding_boxes(
                            screenshot, 
                            comprehensive_data['targeting_data'], 
                            annotated_screenshot
                        )
                    else:
                        print(f"⏭️ Skipping annotated screenshot creation (CREATE_ANNOTATED_IMAGES = False)")
                    
                    print(f"✅ Saved comprehensive data: {len(comprehensive_data['interactive_elements'])} interactive elements, {len(comprehensive_data['targeting_data'])} targeting strategies")
                    
                except Exception as e:
                    if "TargetClosedError" in str(e):
                        print("❌ Page was closed unexpectedly. Attempting to recover...")
                        # Try to create a new page
                        try:
                            page = context.new_page()
                            page.set_default_timeout(ACTION_TIMEOUT)
                            page.goto(url)
                            # Handle login again (if needed)
                            # ensure_google_login(page, email, password, url)
                            # Retry the screenshot and tree capture
                            page.screenshot(path=screenshot)
                            tree = page.accessibility.snapshot()
                            with open(axtree_file, 'w', encoding='utf-8') as f:
                                json.dump(tree, f, indent=2, ensure_ascii=False)
                        except Exception as recovery_error:
                            print(f"❌ Recovery failed: {str(recovery_error)}")
                            runtime = time.time() - start_time
                            metadata = create_metadata(
                                "", url, task, full_task_description, None,
                                [step['step'] for step in task_summarizer],
                                False, step_idx, runtime, total_tokens, page, eps_name
                            )
                            # Add GPT response output to metadata if available
                            if gpt_resp and "output" in gpt_resp:
                                metadata["gpt_output"] = gpt_resp["output"]
                            final_metadata = save_metadata_with_device_browser(metadata, device, browser_type)
                            update_shared_metadata(shared_metadata_path, metadata_lock, final_metadata, task, url, steps, expected_behavior)
                            generate_trajectory_html(dirs, metadata)
                            should_continue = False
                            break
                    else:
                        print(f"❌ Error capturing page state: {str(e)}")
                        runtime = time.time() - start_time
                        metadata = create_metadata(
                            "", url, task, full_task_description, None,
                            [step['step'] for step in task_summarizer],
                            False, step_idx, runtime, total_tokens, page, eps_name
                        )
                        if gpt_resp and "output" in gpt_resp:
                            metadata["gpt_output"] = gpt_resp["output"]
                        final_metadata = save_metadata_with_device_browser(metadata, device, browser_type)
                        update_shared_metadata(shared_metadata_path, metadata_lock, final_metadata, task, url, steps, expected_behavior)
                        generate_trajectory_html(dirs, metadata)
                        should_continue = False
                        break
                is_del = 'delete' in current_goal.lower()

                # Use the targeting data as the tree (no filtering needed)
                filtered_tree = tree
                

                # Prepare context with past trajectories
                enhanced_context = ""
                if trajectory_context:
                    enhanced_context = f"\n\n{trajectory_context}\n\n"
                
                # Create structured JSON element summary for GPT
                element_summary = ""
                if comprehensive_data and 'targeting_data' in comprehensive_data:
                    # Use the function to create simplified element data
                    elements_data = create_simplified_element_summary(comprehensive_data['targeting_data'])
                    
                    # Convert to JSON string
                    element_summary = f"\n\nAvailable Interactive Elements:\n{json.dumps(elements_data, indent=2)}\n\n"
                
                # Save the minimal summary that gets sent to GPT for debugging
                gpt_summary_file = os.path.join(dirs['gpt_summaries'], f'gpt_summary_step_{step_idx}.txt')
                with open(gpt_summary_file, 'w', encoding='utf-8') as f:
                    f.write(f"Step: {step_idx}\n")
                    f.write(f"Current Goal: {current_goal}\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"Task Goal: {full_task_description}\n")
                    f.write(f"Trajectory Context: {enhanced_context}\n")
                    f.write(f"Element Summary Sent to GPT:\n{element_summary}")
                print(f"📝 Saved GPT summary for debugging: {gpt_summary_file}")
                
                gpt_resp = chat_ai_playwright_code(
                    previous_steps=execution_history,
                    task=task,
                    steps=steps,
                    expected_behavior=expected_behavior,
                    taskPlan=current_goal,
                    image_path=screenshot if PASS_IMAGES_TO_GPT else None,  # Pass screenshot only if enabled
                    failed_codes=[],
                    is_deletion_task=is_del,
                    url=url,
                    trajectory_context=enhanced_context,
                    targeting_data=element_summary
                )

                # Print GPT response
                print(f"\n🤖 GPT Response:")
                print(f"Description: {gpt_resp.get('description', 'No description') if gpt_resp else 'No response'}")
                print(f"Code: {gpt_resp.get('code', 'No code') if gpt_resp else 'No response'}")
                if gpt_resp and 'selected_annotation_id' in gpt_resp:
                    print(f"Selected Element ID: {gpt_resp['selected_annotation_id']}")
                if gpt_resp and 'thought' in gpt_resp:
                    print(f"Thought: {gpt_resp['thought']}")
                if gpt_resp and 'wrong_behavior' in gpt_resp:
                    print(f"Wrong Behavior: {gpt_resp['wrong_behavior']}")
                print(f"Full Response: {json.dumps(gpt_resp, indent=2) if gpt_resp else 'No response'}")
                # Confidence validation (if enabled)
                validation_result = None
                if ENABLE_CONFIDENCE_VALIDATION and gpt_resp:
                    print("\n🔍 Running confidence validation...")
                    # Load targeting data from the saved file
                    targeting_data = []
                    try:
                        with open(targeting_data_file, 'r', encoding='utf-8') as f:
                            targeting_data = json.load(f)
                        print(f"✅ Loaded {len(targeting_data)} targeting data entries for validation")
                    except Exception as e:
                        print(f"⚠️ Could not load targeting data for validation: {e}")
                    
                    validation_result = process_confidence_validation(
                        gpt_resp,
                        screenshot,
                        targeting_data,
                        dirs['root'],
                        step_idx
                    )
                    if validation_result and not validation_result.get('validation_skipped'):
                        print(f"📊 Validation Results:")
                        print(f"   Overall Confidence: {validation_result.get('overall_confidence', 'N/A')}")
                        print(f"   Correct Target: {validation_result.get('is_correct_target', 'N/A')}")
                        print(f"   Code Matches Description: {validation_result.get('code_matches_description', 'N/A')}")
                        print(f"   Action Appropriate: {validation_result.get('action_appropriate', 'N/A')}")
                        if validation_result.get('suggestions'):
                            print(f"   Suggestions: {validation_result.get('suggestions')}")
                    else:
                        print("⚠️ Validation skipped or failed")

                # Handle case where GPT response is None
                if gpt_resp is None:
                    print("❌ GPT returned no response")
                    runtime = time.time() - start_time
                    metadata = create_metadata(
                        "", url, task, full_task_description, None,  # Pass None for final_instruction
                        [step['step'] for step in task_summarizer],
                        False, step_idx, runtime, total_tokens, page, eps_name
                    )
                    if gpt_resp and "output" in gpt_resp:
                        metadata["gpt_output"] = gpt_resp["output"]
                    final_metadata = save_metadata_with_device_browser(metadata, device, browser_type)
                    update_shared_metadata(shared_metadata_path, metadata_lock, final_metadata, task, url, steps, expected_behavior)
                    generate_trajectory_html(dirs, metadata)
                    should_continue = False
                    break

                # Update total tokens from GPT response
                if "total_tokens" in gpt_resp:
                    total_tokens += gpt_resp["total_tokens"]
                    print(f"📊 Current total tokens: {total_tokens}")

                if "summary_instruction" in gpt_resp:
                    runtime = time.time() - start_time
                    
                    # Check if wrong_behavior is True to determine success
                    wrong_behavior = gpt_resp.get('wrong_behavior', False)
                    task_success = not wrong_behavior  # Success is True only if wrong_behavior is False
                    
                    metadata = create_metadata(
                        "", url, task, full_task_description, gpt_resp['summary_instruction'],
                        [step['step'] for step in task_summarizer],
                        task_success, step_idx, runtime, total_tokens, page, eps_name
                    )
                    if gpt_resp and "output" in gpt_resp:
                        metadata["gpt_output"] = gpt_resp["output"]
                    metadata["wrong_behavior"] = wrong_behavior
                    if gpt_resp and "explanation" in gpt_resp:
                        metadata["explanation"] = gpt_resp["explanation"]
                    metadata["expected_behavior"] = expected_behavior
                    final_metadata = save_metadata_with_device_browser(metadata, device, browser_type)
                    update_shared_metadata(shared_metadata_path, metadata_lock, final_metadata, task, url, steps, expected_behavior)
                    
                    # Generate HTML after metadata is created
                    generate_trajectory_html(dirs, metadata)
                    
                    if wrong_behavior:
                        print("⚠️ Task completed but wrong behavior detected!")
                    else:
                        print("✅ Task completed successfully, metadata saved.")
                    
                    # Log StatSig event for task completion
                    if ENABLE_STATSIG and STATSIG_CLIENT_KEY:
                        log_custom_event(page, "test_session_completed", {
                            "task": task,
                            "url": url,
                            "device": device,
                            "browser": browser_type,
                            "episode": eps_name,
                            "success": task_success,
                            "wrong_behavior": wrong_behavior,
                            "total_steps": step_idx + 1,
                            "runtime_seconds": runtime
                        })
                        print("📊 StatSig test session completed")
                    
                    # Mark instruction as completed in progress tracker
                    if progress_tracker:
                        error_msg = "Wrong behavior detected" if wrong_behavior else None
                        progress_tracker.complete_instruction(None, idx, task, eps_name, success=task_success, error_message=error_msg)
                    break

                if "updated_goal" in gpt_resp:
                    current_goal = gpt_resp["updated_goal"]

                failed_codes = []
                failed_attempts_details = []  # Track detailed info about each failed attempt
                retry = 0
                description = gpt_resp["description"] if gpt_resp else ""
                code = gpt_resp.get("code", "") if gpt_resp else ""
                success = False

                while retry < MAX_RETRIES and not success:
                    try:
                        print(f"🤖 {description}")
                        print(f"🔄 Code: {code}")
                        print(f"🔄 Failed Codes: {failed_codes}")
                        
                        # Execute the Playwright code directly
                        if "page." in code:
                            # Execute Playwright code directly (sync version)
                            exec(code)
                        else:
                            # For non-Playwright code, execute normally
                            exec(code)
                        
                        # Post-action validation (if enabled and action executed successfully)
                        if ENABLE_POST_ACTION_VALIDATION:
                            print("\n🔍 Running post-action validation...")
                            # Take screenshot after action
                            after_screenshot = os.path.join(dirs['images'], f"after_action_step_{step_idx+1:03d}.png")
                            page.screenshot(path=after_screenshot)
                            
                            # Run post-action validation
                            post_validation_result = process_post_action_validation(
                                before_screenshot_path=screenshot,
                                after_screenshot_path=after_screenshot,
                                action_description=description,
                                output_dir=dirs['root'],
                                step_idx=step_idx
                            )
                            
                            if post_validation_result:
                                print(f"📊 Post-Action Validation Results:")
                                print(f"   Action Successful: {post_validation_result.get('action_successful', 'N/A')}")
                                print(f"   Page State Changed: {post_validation_result.get('page_state_changed', 'N/A')}")
                                print(f"   Overall Confidence: {post_validation_result.get('overall_confidence', 'N/A')}")
                            else:
                                print("⚠️ Post-action validation failed")
                        
                        # ALWAYS record the successful step first (regardless of new tabs)
                        execution_history.append({
                            'step': description, 
                            'code': code, 
                        })
                        task_summarizer.append({
                            'step': description, 
                            'code': code, 
                            'axtree': tree,
                        })
                        
                        # Log StatSig event for successful action
                        if ENABLE_STATSIG and STATSIG_CLIENT_KEY:
                            log_custom_event(page, "test_step_executed", {
                                "step_number": step_idx + 1,
                                "description": description,
                                "action_type": gpt_resp.get('action_type', 'unknown') if gpt_resp else 'unknown',
                                "selected_element_id": gpt_resp.get('selected_annotation_id') if gpt_resp else None,
                                "task": task,
                                "url": url,
                                "device": device,
                                "browser": browser_type
                            })
                        # Save axtree to file only after successful execution
                        with open(axtree_file, 'w', encoding='utf-8') as f:
                            json.dump(tree, f, indent=2, ensure_ascii=False)
                        # Update trajectory.json with the successful step
                        update_trajectory(
                            dirs=dirs,
                            step_idx=step_idx,
                            screenshot=screenshot,
                            axtree=axtree_file,
                            action_code=code,
                            action_description=description,
                            page=page,
                            user_message_file=os.path.join(dirs['user_message'], f"user_message_{step_idx+1:03d}.txt"),
                            llm_output=gpt_resp,
                            targeting_data_file=targeting_data_file,
                            annotation_id=gpt_resp.get('selected_annotation_id') if gpt_resp else None
                        )
                        
                        # Simple tab switching: after successful execution, check for new tabs
                        print("🔍 Checking for new tabs after successful action execution...")
                        print(f"   Previous tab count: {previous_tab_count}")
                        print(f"   Previous tab URLs: {list(previous_tab_urls)[:3]}...")  # Show first 3 URLs
                        
                        has_new_tabs, new_tabs, current_tab_count = check_for_new_tabs(
                            context, previous_tab_count, previous_tab_urls
                        )
                        
                        if has_new_tabs:
                            # NEW CODE - End trajectory when new tabs detected
                            print(f"🆕 New tabs detected! Ending trajectory as requested...")
                            print(f"   New tabs: {[tab['domain'] for tab in new_tabs]}")
                            print(f"   Current tab count: {current_tab_count}")
                            
                            # End the trajectory when new tabs are detected
                            runtime = time.time() - start_time
                            metadata = create_metadata(
                                "", url, task, full_task_description, "Task completed - new tab opened",
                                [step['step'] for step in task_summarizer],
                                True, step_idx, runtime, total_tokens, page, eps_name
                            )
                            if gpt_resp and "output" in gpt_resp:
                                metadata["gpt_output"] = gpt_resp["output"]
                            final_metadata = save_metadata_with_device_browser(metadata, device, browser_type)
                            update_shared_metadata(shared_metadata_path, metadata_lock, final_metadata, task, url, steps, expected_behavior)
                            # Generate HTML after metadata is created
                            generate_trajectory_html(dirs, metadata)
                            print("✅ Task completed - new tab opened, trajectory ended.")
                            
                            # Mark instruction as completed in progress tracker
                            if progress_tracker:
                                progress_tracker.complete_instruction(None, idx, task, eps_name, success=True)
                            
                            # Mark as successful to exit retry loop and main loop
                            success = True
                            should_continue = False
                            break
                        else:
                            print("✅ No new tabs detected, continuing with current page")
                            # Only record the step if we didn't switch to a new tab
                            # Log successful solution with all failed attempts history
                            if retry > 0:
                                update_playwright_error_log(
                                    dirs=dirs,
                                    step_idx=step_idx,
                                    description=description,
                                    attempted_code="",  # Not needed for successful solution
                                    error_message="Previous attempts failed",
                                    successful_code=code,
                                    thought=gpt_resp.get('thought', '') if gpt_resp else '',
                                    current_goal=current_goal,
                                    all_failed_attempts=failed_attempts_details,
                                )
                            success = True
                    except Exception as e:
                        print(f"⚠️ Attempt {retry + 1} failed: {e}")
                        

                        
                        # Try alternative selectors from targeting data if this is a click action that failed
                        if "page." in code and retry == 0 and gpt_resp.get('action_type') == 'click':
                            print("🔄 Trying alternative Playwright selectors...")
                            success, failed_alternatives, successful_fallback_code = try_alternative_selectors(
                                page, code, comprehensive_data, gpt_resp
                            )
                            
                            if success:
                                print("✅ Alternative selector succeeded!")
                                print(f"🔄 Fallback code that worked: {successful_fallback_code}")
                                # Use the successful fallback code instead of the original GPT code
                                working_code = successful_fallback_code
                                

                                
                                # Simple tab switching: after successful alternative execution, check for new tabs
                                print("🔍 Checking for new tabs after successful alternative action execution...")
                                print(f"   Previous tab count: {previous_tab_count}")
                                print(f"   Previous tab URLs: {list(previous_tab_urls)[:3]}...")  # Show first 3 URLs
                                
                                has_new_tabs, new_tabs, current_tab_count = check_for_new_tabs(
                                    context, previous_tab_count, previous_tab_urls
                                )
                                
                                if has_new_tabs:
                                    # NEW CODE - End trajectory when new tabs detected
                                    print(f"🆕 New tabs detected! Ending trajectory as requested...")
                                    print(f"   New tabs: {[tab['domain'] for tab in new_tabs]}")
                                    print(f"   Current tab count: {current_tab_count}")
                                    
                                    # End the trajectory when new tabs are detected
                                    runtime = time.time() - start_time
                                    metadata = create_metadata(
                                        "", url, task, full_task_description, "Task completed - new tab opened",
                                        [step['step'] for step in task_summarizer],
                                        True, step_idx, runtime, total_tokens, page, eps_name
                                    )
                                    if gpt_resp and "output" in gpt_resp:
                                        metadata["gpt_output"] = gpt_resp["output"]
                                    final_metadata = save_metadata_with_device_browser(metadata, device, browser_type)
                                    update_shared_metadata(shared_metadata_path, metadata_lock, final_metadata, task, url, steps, expected_behavior)
                                    generate_trajectory_html(dirs, metadata)
                                    print("✅ Task completed - new tab opened, trajectory ended.")
                                    
                                    # Mark instruction as completed in progress tracker
                                    if progress_tracker:
                                        progress_tracker.complete_instruction(None, idx, task, eps_name, success=True)
                                    
                                    # Mark as successful to exit retry loop and main loop
                                    success = True
                                    should_continue = False
                                    break
                                else:
                                    # Only record the step if we didn't switch to a new tab
                                    execution_history.append({
                                        'step': description, 
                                        'code': working_code, 
                                        'note': 'fallback_selector_used',
                                    })
                                    task_summarizer.append({
                                        'step': description, 
                                        'code': working_code, 
                                        'axtree': tree,
                                    })
                                    # Save axtree to file after successful alternative execution
                                    with open(axtree_file, 'w', encoding='utf-8') as f:
                                        json.dump(tree, f, indent=2, ensure_ascii=False)
                                    # Update trajectory.json with the successful alternative step
                                    update_trajectory(
                                        dirs=dirs,
                                        step_idx=step_idx,
                                        screenshot=screenshot,
                                        axtree=axtree_file,
                                        action_code=working_code,
                                        action_description=description,
                                        page=page,
                                        user_message_file=os.path.join(dirs['user_message'], f"user_message_{step_idx+1:03d}.txt"),
                                        llm_output=gpt_resp,
                                        targeting_data_file=targeting_data_file,
                                        annotation_id=gpt_resp.get('selected_annotation_id') if gpt_resp else None
                                    )
                                    success = True
                                    break
                            else:
                                # Add all failed alternatives to failed_codes so GPT knows not to try them
                                print(f"📝 Adding {len(failed_alternatives)} failed alternatives to failed_codes")
                                for alt_code in failed_alternatives:
                                    if alt_code not in failed_codes:
                                        failed_codes.append(alt_code)
                        
                        retry += 1
                        if code not in failed_codes:
                            failed_codes.append(code)
                        
                        # Track detailed info about this failed attempt
                        failed_attempt_details = {
                            "attempt_number": retry,
                            "code": code,
                            "error_message": str(e),
                            "thought": gpt_resp.get('thought', '') if gpt_resp else '',
                            "description": description,
                        }
                        failed_attempts_details.append(failed_attempt_details)
                        
                        # Log the individual Playwright execution error
                        update_playwright_error_log(
                            dirs=dirs,
                            step_idx=step_idx,
                            description=description,
                            attempted_code=code,
                            error_message=str(e),
                            thought=gpt_resp.get('thought', '') if gpt_resp else '',
                            current_goal=current_goal,
                        )
                        
                        if retry < MAX_RETRIES:
                            print("🔄 Retrying GPT for new code...")
                            page.screenshot(path=screenshot)
                            
                            # Get comprehensive element data for retry
                            print(f"🔍 Collecting comprehensive element data for retry {retry + 1}...")
                            comprehensive_data = get_comprehensive_element_data(page, url)
                            
                            # Create simplified element data for axtree file and GPT
                            elements_data = create_simplified_element_summary(comprehensive_data['targeting_data'])
                            
                            # Use simplified data as the "tree"
                            tree = elements_data
                            
                            # Save simplified element data to axtree file for retry
                            with open(axtree_file, 'w', encoding='utf-8') as f:
                                json.dump(elements_data, f, indent=2, ensure_ascii=False)
                            
                            # Save the comprehensive targeting data
                            with open(targeting_data_file, 'w', encoding='utf-8') as f:
                                json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
                            
                            # Create annotated screenshot for retry (only if enabled)
                            if CREATE_ANNOTATED_IMAGES:
                                print(f"🎨 Creating annotated screenshot for retry {retry + 1}...")
                                annotated_path = annotate_screenshot_with_bounding_boxes(
                                    screenshot, 
                                    comprehensive_data['targeting_data'], 
                                    annotated_screenshot
                                )
                            else:
                                print(f"⏭️ Skipping annotated screenshot creation for retry {retry + 1} (CREATE_ANNOTATED_IMAGES = False)")
                            
                            error_log = str(e)
                            print(f"📝 Error log: {error_log}")
                            
                            # Use the targeting data as the tree (no filtering needed)
                            filtered_tree = tree
                            
                            # Prepare context with past trajectories for retry
                            enhanced_context = ""
                            if trajectory_context:
                                enhanced_context = f"\n\n{trajectory_context}\n\n"
                            
                            # Create element summary for GPT retry using the same function
                            element_summary = ""
                            if comprehensive_data and 'targeting_data' in comprehensive_data:
                                # Use the function to create simplified element data
                                elements_data = create_simplified_element_summary(comprehensive_data['targeting_data'])
                                
                                # Convert to JSON string (same format as first call)
                                element_summary = f"\n\nAvailable Interactive Elements:\n{json.dumps(elements_data, indent=2)}\n\n"
                            
                            gpt_resp = chat_ai_playwright_code(
                                    previous_steps=execution_history,
                                    task=task,
                                    steps=steps,
                                    expected_behavior=expected_behavior,
                                    taskPlan=current_goal,
                                    image_path=screenshot if PASS_IMAGES_TO_GPT else None,  # Pass screenshot only if enabled
                                    failed_codes=failed_codes,
                                    is_deletion_task=is_del,
                                    url=url,
                                    error_log=error_log,
                                    trajectory_context=enhanced_context,
                                    targeting_data=element_summary
                            )
                            # Update total tokens from retry response
                            if gpt_resp and "total_tokens" in gpt_resp:
                                total_tokens += gpt_resp["total_tokens"]
                                print(f"📊 Current total tokens: {total_tokens}")

                            if gpt_resp and "summary_instruction" in gpt_resp:
                                runtime = time.time() - start_time
                                
                                # Check if wrong_behavior is True to determine success
                                wrong_behavior = gpt_resp.get('wrong_behavior', False)
                                task_success = not wrong_behavior
                                
                                metadata = create_metadata(
                                    "", url, task, full_task_description, gpt_resp['summary_instruction'],
                                    [step['step'] for step in task_summarizer],
                                    task_success, step_idx, runtime, total_tokens, page, eps_name
                                )
                                if gpt_resp and "output" in gpt_resp:
                                    metadata["gpt_output"] = gpt_resp["output"]
                                metadata["wrong_behavior"] = wrong_behavior
                                if gpt_resp and "explanation" in gpt_resp:
                                    metadata["explanation"] = gpt_resp["explanation"]
                                metadata["expected_behavior"] = expected_behavior
                                final_metadata = save_metadata_with_device_browser(metadata, device, browser_type)
                                update_shared_metadata(shared_metadata_path, metadata_lock, final_metadata, task, url, steps, expected_behavior)
                                
                                # Generate HTML after metadata is created
                                generate_trajectory_html(dirs, metadata)
                                
                                if wrong_behavior:
                                    print("⚠️ Task completed on retry but wrong behavior detected!")
                                else:
                                    print("✅ Task completed on retry, metadata saved.")
                                should_continue = False
                                break
                            if gpt_resp and "updated_goal" in gpt_resp:
                                current_goal = gpt_resp["updated_goal"]
                            description = gpt_resp["description"] if gpt_resp else ""
                            code = gpt_resp.get("code", "") if gpt_resp else ""
                        else:
                            print(f"❌ All {MAX_RETRIES} retries failed.")
                            # Log final Playwright failure
                            update_playwright_error_log(
                                dirs=dirs,
                                step_idx=step_idx,
                                description=description,
                                attempted_code=code,
                                error_message=f"All {MAX_RETRIES} retries failed",
                                thought=gpt_resp.get('thought', '') if gpt_resp else '',
                                current_goal=current_goal,
                            )
                            runtime = time.time() - start_time
                            metadata = create_metadata(
                                "", url, task, full_task_description, None,  # Pass None for final_instruction
                                [step['step'] for step in task_summarizer],
                                False, step_idx, runtime, total_tokens, page, eps_name
                            )
                            if gpt_resp and "output" in gpt_resp:
                                metadata["gpt_output"] = gpt_resp["output"]
                            final_metadata = save_metadata_with_device_browser(metadata, device, browser_type)
                            update_shared_metadata(shared_metadata_path, metadata_lock, final_metadata, task, url, steps, expected_behavior)
                            # Generate HTML after metadata is created
                            generate_trajectory_html(dirs, metadata)
                            
                            # Mark instruction as failed in progress tracker
                            if progress_tracker:
                                progress_tracker.complete_instruction(None, idx, task, eps_name, success=False, error_message=f"All {MAX_RETRIES} retries failed")
                            should_continue = False
                            break
                                        
                if success:
                    page.wait_for_timeout(2000)
                else:
                    # If the step failed, remove both screenshot and axtree files
                    if os.path.exists(screenshot):
                        os.remove(screenshot)
                    if os.path.exists(axtree_file):
                        os.remove(axtree_file)
                    break

                # Prepare user message content
                user_message_file = os.path.join(dirs['user_message'], f"user_message_{step_idx+1:03d}.txt")
                write_user_message(
                    user_message_file=user_message_file,
                    goal=current_goal,
                    execution_history=execution_history,
                    page=page,
                    tree=tree,
                    failed_codes=failed_codes if 'failed_codes' in locals() else None
                )

        # Don't close the page here, just continue to next instruction
                
        finally:
            # Close page, context, and browser at the very end
            if MODE == 1:
                input("🔚 Press Enter to continue...")
            page.close()
            context.close()
            browser.close()
    
    return final_metadata

def main():
    # Print image configuration at start
    print("\n" + "="*60)
    print("🖼️  IMAGE CONFIGURATION")
    print("="*60)
    print(f"Pass Images to GPT: {PASS_IMAGES_TO_GPT}")
    print(f"Create Annotated Images: {CREATE_ANNOTATED_IMAGES}")
    if not PASS_IMAGES_TO_GPT:
        print("ℹ️  Running in TEXT-ONLY mode - Using targeting data only")
    else:
        print("ℹ️  Running in VISION mode - Using screenshots + targeting data")
    print("="*60 + "\n")
    
    # Print StatSig configuration
    print("="*60)
    print("📊 STATSIG CONFIGURATION")
    print("="*60)
    print(f"StatSig Enabled: {ENABLE_STATSIG}")
    if ENABLE_STATSIG:
        print(f"Client Key: {STATSIG_CLIENT_KEY[:20]}...{STATSIG_CLIENT_KEY[-10:] if STATSIG_CLIENT_KEY else 'None'}")
        print(f"Session Replay: {ENABLE_STATSIG_SESSION_REPLAY}")
        print(f"Auto Capture: {ENABLE_STATSIG_AUTO_CAPTURE}")
        print("ℹ️  StatSig will be injected into all test websites")
    else:
        print("ℹ️  StatSig disabled - no client key provided")
    print("="*60 + "\n")
    
    # Initialize progress tracker
    progress_tracker = ProgressTracker(RESULTS_DIR)
    
    # Load instructions
    phase_file = os.path.join(RESULTS_DIR, f"instructions_phase{PHASE}.json")
    try:
        with open(phase_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error loading {phase_file}: {e}")
        return
    
    # Process each instruction
    for idx, instruction_data in enumerate(data):
        url = instruction_data['url']
        task = instruction_data['task']
        steps = instruction_data['steps']
        expected_behavior = instruction_data['expected_behavior']
        devices = instruction_data.get('devices', ['desktop'])
        browsers = instruction_data.get('browsers', ['chrome'])
        
        # Generate base episode name
        base_eps_name = generate_episode_name(url)
        
        # Create base directory and shared metadata path
        base_dir = os.path.join(RESULTS_DIR, base_eps_name)
        os.makedirs(base_dir, exist_ok=True)
        shared_metadata_path = os.path.join(base_dir, 'metadata.json')
        
        # Create a lock for thread-safe metadata updates
        metadata_lock = threading.Lock()
        
        print(f"\n{'='*100}")
        print(f"📋 Instruction {idx + 1}/{len(data)}: {task}")
        print(f"🔧 Running {len(devices)} device(s) × {len(browsers)} browser(s) = {len(devices) * len(browsers)} combinations")
        print(f"📁 Base folder: {base_eps_name}")
        print(f"📄 Shared metadata: {shared_metadata_path}")
        print(f"{'='*100}")
        
        # Create all device-browser combination tasks
        tasks = []
        for device in devices:
            for browser_type in browsers:
                tasks.append((url, task, steps, expected_behavior, device, browser_type, base_eps_name, idx, len(data), shared_metadata_path, metadata_lock, progress_tracker))
        
        # Run all combinations in parallel
        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = [
                executor.submit(run_single_trajectory, *task_args)
                for task_args in tasks
            ]
            for future in futures:
                try:
                    future.result()  # Wait for all to finish
                except Exception as e:
                    print(f"❌ Error in trajectory execution: {e}")
        
        print(f"\n✅ All {len(tasks)} combinations completed for: {base_eps_name}")
    
    # Print final progress summary
    progress_tracker.print_progress_summary()



if __name__ == "__main__":
    main() 
