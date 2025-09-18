#!/usr/bin/env python3
"""
Script to parse flow.json and extract specified fields from steps.
Extracts: type, title, subtitle, url, hotspots, clickContext
"""

import json
import sys
from typing import Dict, List, Any, Optional


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

    # Include url if present
    if 'url' in step:
        extracted['url'] = step['url']

    # Include hotspots if present
    if 'hotspots' in step:
        extracted['hotspots'] = step['hotspots']

    # Include clickContext if present
    if 'clickContext' in step:
        extracted['clickContext'] = step['clickContext']

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


def main():
    """Main function to parse flow.json and output extracted data."""
    file_path = 'flow.json'

    # Allow custom file path as command line argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    extracted_steps = parse_flow_json(file_path)

    if extracted_steps:
        # Output as pretty-printed JSON
        print(json.dumps(extracted_steps, indent=2))
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()