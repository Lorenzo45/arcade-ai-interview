#!/usr/bin/env python3
"""
Script to parse flow.json and extract specified fields from steps.
Extracts: type, title, subtitle, url, hotspots, clickContext
"""

import json
import sys
import os
import base64
from typing import Dict, List, Any, Optional
try:
    import openai
except ImportError:
    openai = None


def extract_step_fields(step: Dict[str, Any]) -> Dict[str, Any]:
    """Extract specified fields from a step."""
    extracted = {}

    # Always include type
    if 'type' in step:
        extracted['type'] = step['type']

    # Include title if present
    if 'title' in step:
        extracted['title'] = step['title']

    # Include subtitle if present
    if 'subtitle' in step:
        extracted['subtitle'] = step['subtitle']

    # Include hotspots if present (only keep label field from each hotspot)
    if 'hotspots' in step:
        hotspots = step['hotspots']
        filtered_hotspots = []

        for hotspot in hotspots:
            if 'label' in hotspot:
                filtered_hotspots.append({'label': hotspot['label']})

        if filtered_hotspots:
            extracted['hotspots'] = filtered_hotspots

    # Include clickContext if present (only keep specified fields)
    if 'clickContext' in step:
        click_context = step['clickContext']
        filtered_click_context = {}

        if 'cssSelector' in click_context:
            filtered_click_context['cssSelector'] = click_context['cssSelector']
        if 'text' in click_context:
            filtered_click_context['text'] = click_context['text']
        if 'elementType' in click_context:
            filtered_click_context['elementType'] = click_context['elementType']

        if filtered_click_context:
            extracted['clickContext'] = filtered_click_context

    return extracted


def parse_flow_json(file_path: str) -> List[Dict[str, Any]]:
    """Parse flow.json and extract specified fields from steps."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'steps' not in data:
            print("Warning: No 'steps' field found in JSON", file=sys.stderr)
            return []

        extracted_steps = []
        for step in data['steps']:
            extracted = extract_step_fields(step)
            extracted_steps.append(extracted)

        return extracted_steps

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{file_path}': {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []


def generate_summary_with_openai(extracted_data: List[Dict[str, Any]]) -> str:
    """Generate a summary of the extracted flow data using OpenAI API."""
    if openai is None:
        return "Error: OpenAI library not installed. Run 'pip install openai' to use summary feature."

    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "Error: OPENAI_API_KEY environment variable not set."

    try:
        client = openai.OpenAI(api_key=api_key)

        # Prepare the prompt
        data_str = json.dumps(extracted_data, indent=2)
        prompt = f"""
Analyze the following data and provide two things in markdown format:
## User Interactions: a numbered, non-technical list of user actions (e.g. "Clicked on checkout", "Search for X")
## Summary: a clear, readable summary of what the user was trying to accomplish

Note: Chapters are not user actions but can be used for context to understand actions

Raw data:

{data_str}
"""

        response = client.responses.create(
            model="gpt-5-mini",
            reasoning={"effort": "low"},
            input=prompt
        )

        return response.output_text

    except Exception as e:
        return f"Error generating summary: {str(e)}"


def generate_flow_image(summary: str) -> bool:
    """Generate a professional image depicting the main actions of the flow."""
    if openai is None:
        print("Error: OpenAI library not installed.")
        return False

    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return False

    try:
        client = openai.OpenAI(api_key=api_key)

        # Create image prompt based on the summary
        image_prompt = f"""Based on the following user journey, generate a professional, clean illustration for a branded social media post. The image should look like a feature announcement/highlight and does not need to include all steps.

User Journey:
{summary}"""

        response = client.responses.create(
            model="gpt-5",
            input=image_prompt,
            tools=[{"type": "image_generation"}],
        )

        # Save the image to a file
        image_data = [
            output.result
            for output in response.output
            if output.type == "image_generation_call"
        ]

        if image_data:
            image_base64 = image_data[0]
            os.makedirs('output', exist_ok=True)
            with open("output/flow_image.png", "wb") as f:
                f.write(base64.b64decode(image_base64))
            print("Image saved to output/flow_image.png")
            return True
        else:
            print("No image data received from API")
            return False

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return False


def main():
    """Main function to parse flow.json and output extracted data."""
    file_path = 'flow.json'

    # Allow custom file path as command line argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    extracted_steps = parse_flow_json(file_path)

    if extracted_steps:
        print("Generating flow summary...")
        summary = generate_summary_with_openai(extracted_steps)

        # Write summary to file in output folder
        os.makedirs('output', exist_ok=True)
        with open('output/flow_summary.md', 'w', encoding='utf-8') as f:
            f.write(summary)

        print("Summary written to output/flow_summary.md")
        print("Generating image...")

        # Generate and save image
        generate_flow_image(summary)
    else:
        print("Error extracting flow summary")
        sys.exit(1)


if __name__ == "__main__":
    main()