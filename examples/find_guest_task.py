#!/usr/bin/env python3
"""
Simple example: Find tasks with specific tag and custom field value.

This script demonstrates how to find tasks that match:
- Tag: guest:jessica-smith
- Custom field: LPT_TASK_TYPE == 'LPT_CREATE_THUMBNAIL'

Setup:
    export CLICKUP_API_KEY="your_api_key"
    export CLICKUP_TEAM_ID="your_team_id"
    export TEST_LIST_ID="your_list_id"
    
Usage:
    python examples/find_guest_task.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clickuphelper import Tasks, FilterOperator, CustomFieldFilter


def find_guest_tasks(list_id, tag_name, field_name, field_value):
    """
    Find tasks matching both a tag and a custom field value.
    
    Args:
        list_id: The ClickUp list ID to search
        tag_name: Tag name to filter by (e.g., "guest:jessica-smith")
        field_name: Custom field name (e.g., "LPT_TASK_TYPE")
        field_value: Expected field value (e.g., "LPT_CREATE_THUMBNAIL")
    
    Returns:
        Dictionary of matching task_id -> Task objects
    """
    print(f"Searching for tasks in list {list_id}")
    print(f"  Tag: {tag_name}")
    print(f"  Field: {field_name} == {field_value}")
    print()
    
    # Step 1: Load all tasks from the list
    print("Loading tasks...")
    tasks = Tasks(list_id, include_closed=True)
    total_count = tasks.get_count()
    print(f"✓ Loaded {total_count} tasks")
    print()
    
    # Step 2: Filter by tag
    print(f"Filtering by tag '{tag_name}'...")
    tagged_tasks = tasks.filter_by_tag(tag_name)
    print(f"✓ Found {len(tagged_tasks)} tasks with tag")
    print()
    
    # Step 3: Filter by custom field
    print(f"Filtering by {field_name} == '{field_value}'...")
    matching_tasks = {}
    
    for task_id, task in tagged_tasks.items():
        try:
            # Get the custom field value
            actual_value = task.get_field(field_name)
            
            # Check if it matches
            if actual_value == field_value:
                matching_tasks[task_id] = task
                print(f"  ✓ Match: {task.name} (ID: {task_id})")
        except Exception as e:
            # Task doesn't have this field or can't read it
            pass
    
    print()
    print(f"✓ Found {len(matching_tasks)} tasks matching both criteria")
    print()
    
    return matching_tasks


def display_task_details(task):
    """Display detailed information about a task."""
    print("=" * 80)
    print(f"Task: {task.name}")
    print("=" * 80)
    print(f"ID: {task.id}")
    print(f"Status: {task.status}")
    print(f"Creator: {task.creator}")
    print(f"Created: {task.created}")
    print(f"Updated: {task.updated}")
    print()
    
    # Display tags
    tags = task.task.get('tags', [])
    if tags:
        print("Tags:")
        for tag in tags:
            print(f"  - {tag['name']}")
        print()
    
    # Display custom fields
    print("Custom Fields:")
    for field_name in task.get_field_names():
        try:
            value = task.get_field(field_name)
            field_type = task.get_field_type(field_name)
            print(f"  - {field_name} ({field_type}): {value}")
        except:
            print(f"  - {field_name}: <no value>")
    print()


def main():
    # Check environment variables
    api_key = os.environ.get("CLICKUP_API_KEY")
    list_id = os.environ.get("TEST_LIST_ID")
    
    if not api_key:
        print("❌ Error: CLICKUP_API_KEY not set")
        print("\nSet your environment variables:")
        print("  export CLICKUP_API_KEY='your_api_key'")
        print("  export CLICKUP_TEAM_ID='your_team_id'")
        print("  export TEST_LIST_ID='your_list_id'")
        return 1
    
    if not list_id:
        print("❌ Error: TEST_LIST_ID not set")
        print("\nSet the list ID to search:")
        print("  export TEST_LIST_ID='your_list_id'")
        return 1
    
    print()
    print("=" * 80)
    print("Find Guest Tasks Example")
    print("=" * 80)
    print()
    
    # Find tasks matching criteria
    matching_tasks = find_guest_tasks(
        list_id=list_id,
        tag_name="guest:jessica-smith",
        field_name="LPT_TASK_TYPE",
        field_value="LPT_CREATE_THUMBNAIL"
    )
    
    # Display details for each matching task
    if matching_tasks:
        print("=" * 80)
        print("MATCHING TASKS")
        print("=" * 80)
        print()
        
        for task_id, task in matching_tasks.items():
            display_task_details(task)
    else:
        print("No tasks found matching the criteria.")
        print()
        print("Troubleshooting:")
        print("  1. Verify the list ID is correct")
        print("  2. Check that tasks exist with tag 'guest:jessica-smith'")
        print("  3. Verify the custom field name is 'LPT_TASK_TYPE'")
        print("  4. Confirm the field value is 'LPT_CREATE_THUMBNAIL'")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
