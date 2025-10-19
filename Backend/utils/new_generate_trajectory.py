from dataclasses import dataclass
from openai import OpenAI
import json
import base64
import os
from dotenv import load_dotenv
import json
from openai import OpenAI
from PIL import Image
from io import BytesIO
import requests

from prompts.generation_prompt import (
    PLAYWRIGHT_CODE_SYSTEM_MSG_FAILED,
    PLAYWRIGHT_CODE_SYSTEM_MSG_CALENDAR,
)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def log_token_usage(resp):
    """Prints a detailed breakdown of token usage from OpenAI response."""
    if hasattr(resp, "usage"):
        input_tokens = getattr(resp.usage, "prompt_tokens", None)
        output_tokens = getattr(resp.usage, "completion_tokens", None)
        total_tokens = getattr(resp.usage, "total_tokens", None)
        print("\n📊 Token Usage Report:")
        print(f"📝 Input (Prompt) tokens: {input_tokens}")
        print(f"💬 Output (Completion) tokens: {output_tokens}")
        print(f"🔢 Total tokens charged: {total_tokens}")
    else:
        print("⚠️ Token usage info not available from API response.")


def clean_code_response(raw_content):
    """Clean the raw response and return the parsed JSON object."""
    raw_content = raw_content.strip()
    
    # Handle null response
    if raw_content == "null":
        return None
        
    # Remove markdown code block if present
    if raw_content.startswith("```json"):
        raw_content = raw_content[len("```json"):].strip()
    elif raw_content.startswith("```"):
        raw_content = raw_content[len("```"):].strip()
    if raw_content.endswith("```"):
        raw_content = raw_content[:-3].strip()
        
    try:
        # Parse and return the entire JSON response
        return json.loads(raw_content)
    except json.JSONDecodeError:
        print("Error: Response was not valid JSON")
        return None

client = OpenAI(api_key=api_key)

@dataclass
class TaskStep:
    action: str
    target: dict
    value: str = None

task_summarizer = []

def chat_ai_playwright_code(previous_steps=None, task=None, steps=None, expected_behavior=None, taskPlan=None, image_path=None, failed_codes=None, is_deletion_task=False, url=None, error_log=None, trajectory_context="", targeting_data=""):
    """Get Playwright code directly from GPT to execute the next step.
    
    Args:
        previous_steps: List of previous steps taken
        task: High-level task description
        steps: List of step-by-step instructions
        expected_behavior: Expected outcome when task is complete
        taskPlan: The current specific goal/plan to execute
        image_path: Path to the clean screenshot of the current page
        failed_codes: List of previously failed code attempts
        is_deletion_task: Whether this is a deletion task
        url: The URL of the current page
        error_log: The error log for the current task
        trajectory_context: Context from previous trajectories
        targeting_data: Summary of interactive elements
    """
    # Base system message
    print(f"\n{'='*60}")
    print("🎯 SELECTING SYSTEM PROMPT FOR GPT CALL")
    print(f"{'='*60}")
    
    if failed_codes and len(failed_codes) > 0:
            base_system_message = PLAYWRIGHT_CODE_SYSTEM_MSG_FAILED
            print("🤖 SELECTED: FAILED ATTEMPT prompt")
            print("📝 Reason: Previous attempts failed, using retry prompt")
    else:
        # Select prompt based on URL
        if url:
            print(f"🌐 Current URL: {url}")
            if "mail.google.com" in url or "gmail.com" in url:
                base_system_message = PLAYWRIGHT_CODE_SYSTEM_MSG_GMAIL
                print("🤖 SELECTED: GMAIL prompt")
                print("📝 Reason: Detected Gmail/Google Mail URL")
            elif "calendar.google.com" in url:
                # Use NO_IMAGE version if no image is provided
                if image_path is None:
                    base_system_message = PLAYWRIGHT_CODE_SYSTEM_MSG_CALENDAR_NO_IMAGE
                    print(f"🤖 SELECTED: CALENDAR (TEXT-ONLY) prompt")
                    print(f"📝 Reason: Detected Google Calendar URL, running in text-only mode")
                else:
                    base_system_message = PLAYWRIGHT_CODE_SYSTEM_MSG_DELETION_CALENDAR if is_deletion_task else PLAYWRIGHT_CODE_SYSTEM_MSG_CALENDAR
                    prompt_type = "DELETION CALENDAR" if is_deletion_task else "CALENDAR"
                    print(f"🤖 SELECTED: {prompt_type} prompt")
                    print(f"📝 Reason: Detected Google Calendar URL (deletion task: {is_deletion_task})")
            elif "maps.google.com" in url:
                base_system_message = PLAYWRIGHT_CODE_SYSTEM_MSG_MAPS
                print("🤖 SELECTED: MAPS prompt")
                print("📝 Reason: Detected Google Maps URL")
            elif "flights.google.com" in url or "google.com/travel/flights" in url:
                base_system_message = PLAYWRIGHT_CODE_SYSTEM_MSG_FLIGHTS
                print("🤖 SELECTED: FLIGHTS prompt")
                print("📝 Reason: Detected Google Flights URL")
            elif "scholar.google.com" in url:
                base_system_message = PLAYWRIGHT_CODE_SYSTEM_MSG_SCHOLAR
                print("🤖 SELECTED: SCHOLAR prompt")
                print("📝 Reason: Detected Google Scholar URL")
            elif "docs.google.com" in url:
                base_system_message = PLAYWRIGHT_CODE_SYSTEM_MSG_DOCS
                print("🤖 SELECTED: DOCS prompt")
                print("📝 Reason: Detected Google Docs URL")
            else:
                # Default to calendar for backward compatibility
                # Use NO_IMAGE version if no image is provided
                if image_path is None:
                    base_system_message = PLAYWRIGHT_CODE_SYSTEM_MSG_CALENDAR_NO_IMAGE
                    print("🤖 SELECTED: DEFAULT (CALENDAR TEXT-ONLY) prompt")
                    print(f"📝 Reason: Unknown URL pattern, using fallback text-only prompt")
                else:
                    base_system_message = PLAYWRIGHT_CODE_SYSTEM_MSG_CALENDAR
                    print("🤖 SELECTED: DEFAULT (CALENDAR) prompt")
                    print(f"📝 Reason: Unknown URL pattern, using fallback prompt")
        else:
            # Default to calendar for backward compatibility
            # Use NO_IMAGE version if no image is provided
            if image_path is None:
                base_system_message = PLAYWRIGHT_CODE_SYSTEM_MSG_CALENDAR_NO_IMAGE
                print("🤖 SELECTED: DEFAULT (CALENDAR TEXT-ONLY) prompt")
                print("📝 Reason: No URL provided, using fallback text-only prompt")
            else:
                base_system_message = PLAYWRIGHT_CODE_SYSTEM_MSG_TAB_CHANGE_FLIGHTS
                print("🤖 SELECTED: DEFAULT (TAB CHANGE FLIGHTS) prompt")
                print("📝 Reason: No URL provided, using fallback prompt")
    
    print(f"✅ System prompt selected successfully")
    print(f"{'='*60}")

    if previous_steps is not None:
        try:
            # Print previous steps for debugging
            # print(f"\n{'='*60}")
            # print("📋 PREVIOUS STEPS BEING SENT TO GPT:")
            # print(f"{'='*60}")
            # print(json.dumps(previous_steps, indent=2))
            # print(f"{'='*60}")
            
            # Prepare content array for GPT
            # Steps is now a string, no need to format
            task_info = f"Task: {task}\n\nSteps:\n{steps}\n\nExpected Behavior:\n{expected_behavior}"
            
            content = [
                {
                    "type": "text",
                    "text": f"{task_info}\n\nCurrent plan: {taskPlan}\nPrevious steps(The playwright codes here are generated, take them with a grain of salt.): {json.dumps(previous_steps, indent=2)}{trajectory_context}\n\nInteractive elements: {targeting_data}\n\nError log: {error_log if error_log else 'No errors'}"
                }
            ]
            
            # Add clean screenshot only if image_path is provided
            if image_path:
                print("🖼️ Adding screenshot to GPT request")
                with Image.open(image_path) as img:
                    if img.width > 512:
                        aspect_ratio = img.height / img.width
                        new_height = int(512 * aspect_ratio)
                        img = img.resize((512, new_height), Image.LANCZOS)
                    
                    buffer = BytesIO()
                    img.save(buffer, format="PNG", optimize=True)
                    clean_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
                
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{clean_image}"
                    }
                })
            else:
                print("📝 Running in TEXT-ONLY mode - no screenshot sent to GPT")
            
            

            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": base_system_message 
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )
            log_token_usage(response)
            gpt_response = clean_code_response(response.choices[0].message.content)
            print("GPT Response:", gpt_response)
            
            if gpt_response is None:
                print("✅ Task completed!")
                return None
            
            # Add token usage and system message to the response
            if hasattr(response, "usage"):
                gpt_response["total_tokens"] = response.usage.total_tokens
                gpt_response["prompt_tokens"] = response.usage.prompt_tokens
                gpt_response["completion_tokens"] = response.usage.completion_tokens
            
            # Add the system message to the response
            # gpt_response["system_message"] = base_system_message
                
            return gpt_response
            
        except Exception as e:
            print(f"❌ Error in GPT call: {str(e)}")
    else:
        print("⚠️ Error: Missing previous steps")