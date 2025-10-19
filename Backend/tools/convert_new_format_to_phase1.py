"""
Script to convert new format (tasks_united_com.json, tasks_airfrance_us.json) 
to instructions_phase1.json format.

This script will CLEAR and REPLACE the contents of instructions_phase1.json with the converted data.

Usage:
    python convert_new_format_to_phase1.py <input_file>
    
Example:
    python convert_new_format_to_phase1.py data/peter_data/tasks_united_com.json
"""

import json
import re
import sys
from pathlib import Path


def extract_url_from_steps(steps):
    """
    Extract URL from steps array.
    Looks for patterns like:
    - "Navigate to 'URL'"
    - "Go to url 'URL'"
    - "Visit 'URL'"
    """
    url_patterns = [
        r"Navigate to ['\"]([^'\"]+)['\"]",
        r"Go to url ['\"]([^'\"]+)['\"]",
        r"Visit ['\"]([^'\"]+)['\"]",
        r"to ['\"]([^'\"]+)['\"].*with.*booking",
        r"https?://[^\s'\"]+",
    ]
    
    for step in steps:
        for pattern in url_patterns:
            match = re.search(pattern, step, re.IGNORECASE)
            if match:
                url = match.group(1) if match.lastindex else match.group(0)
                # Ensure URL starts with http/https
                if not url.startswith('http'):
                    continue
                return url
    return None


def find_url_in_file(data):
    """
    Find URL by checking objects in the file until one is found.
    """
    for item in data:
        if 'steps' in item:
            url = extract_url_from_steps(item['steps'])
            if url:
                return url
    return None


def convert_new_format_to_phase1(input_file, output_file=None):
    """
    Convert new format to instructions_phase1.json format.
    
    Args:
        input_file: Path to input JSON file (new format)
        output_file: Path to output JSON file (phase1 format). If None, returns the data.
    
    Returns:
        Converted data in phase1 format
    """
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    # Find URL from the file
    url = find_url_in_file(input_data)
    
    if not url:
        print(f"Warning: No URL found in {input_file}. Using empty string.")
        url = ""
    else:
        print(f"Found URL: {url}")
    
    # Convert to phase1 format
    phase1_data = []
    
    for item in input_data:
        # Get mid_level instruction
        mid_level_instruction = ""
        if 'instruction' in item and isinstance(item['instruction'], dict):
            mid_level_instruction = item['instruction'].get('mid_level', '')
        
        # Create phase1 format object
        phase1_item = {
            "persona": "",
            "url": url,
            "instructions": [mid_level_instruction],
            "augmented_instructions": [mid_level_instruction]
        }
        
        phase1_data.append(phase1_item)
    
    # Write output file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(phase1_data, f, indent=2)
        print(f"Converted {len(phase1_data)} instructions from {input_file} to {output_file}")
    
    return phase1_data


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_new_format_to_phase1.py <input_file>")
        print("\nExample:")
        print("  python convert_new_format_to_phase1.py data/peter_data/tasks_united_com.json")
        print("\nNote: This will CLEAR and REPLACE data/results/instructions_phase1.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    # Default output to instructions_phase1.json
    script_dir = Path(__file__).parent.parent  # Go up from tools/ to DataGenPipeline/
    output_file = str(script_dir / "data" / "results" / "instructions_phase1.json")
    
    # Warn user about clearing the file
    print(f"⚠️  Warning: This will CLEAR and REPLACE {output_file}")
    print(f"Converting from: {input_file}")
    
    # Convert
    try:
        convert_new_format_to_phase1(input_file, output_file)
        print(f"\n✓ Conversion successful!")
        print(f"  Input:  {input_file}")
        print(f"  Output: {output_file}")
        print(f"  Total instructions: {len(json.load(open(output_file)))}")
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
