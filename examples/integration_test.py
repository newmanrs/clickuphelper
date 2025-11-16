#!/usr/bin/env python3
"""
Integration test script for realistic ClickUp queries.

This script demonstrates real-world usage patterns including:
- Finding tasks by tag
- Filtering by custom field values
- Combining multiple filters
- Working with subtasks

Setup:
    export CLICKUP_API_KEY="your_api_key"
    export CLICKUP_TEAM_ID="your_team_id"
    
Usage:
    python examples/integration_test.py
"""

import os
import sys
import json

# Add parent directory to path to import clickuphelper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import clickuphelper
from clickuphelper import (
    Tasks, 
    FilterOperator, 
    CustomFieldFilter,
    get_all_lists
)


def test_find_task_by_tag_and_custom_field():
    """
    Example: Find tasks with tag 'guest:jessica-smith' and 
    custom field LPT_TASK_TYPE == 'LPT_CREATE_THUMBNAIL'
    """
    print("=" * 80)
    print("Test: Find tasks by tag and custom field")
    print("=" * 80)
    
    # Replace with your actual list ID
    list_id = os.environ.get("TEST_LIST_ID")
    if not list_id:
        print("⚠️  TEST_LIST_ID environment variable not set")
        print("   Set it to test with a real list:")
        print("   export TEST_LIST_ID='your_list_id'")
        return
    
    print(f"\nSearching in list: {list_id}")
    
    # Step 1: Get all tasks from the list
    print("\n1. Loading tasks from list...")
    tasks = Tasks(list_id, include_closed=True)
    print(f"   Found {tasks.get_count()} total tasks")
    
    # Step 2: Filter by tag
    print("\n2. Filtering by tag 'guest:jessica-smith'...")
    tagged_tasks = tasks.filter_by_tag("guest:jessica-smith")
    print(f"   Found {len(tagged_tasks)} tasks with tag")
    
    # Step 3: Filter by custom field
    print("\n3. Applying custom field filter: LPT_TASK_TYPE == 'LPT_CREATE_THUMBNAIL'...")
    
    # Create custom field filter
    filters = [
        CustomFieldFilter(
            field_name="LPT_TASK_TYPE",
            operator=FilterOperator.EQUALS,
            value="LPT_CREATE_THUMBNAIL"
        )
    ]
    
    # Apply filter to tagged tasks
    matching_tasks = {}
    for task_id, task in tagged_tasks.items():
        try:
            field_value = task.get_field("LPT_TASK_TYPE")
            if field_value == "LPT_CREATE_THUMBNAIL":
                matching_tasks[task_id] = task
        except Exception as e:
            # Task doesn't have this field or value doesn't match
            pass
    
    print(f"   Found {len(matching_tasks)} tasks matching both criteria")
    
    # Display results
    if matching_tasks:
        print("\n✓ Matching tasks:")
        for task_id, task in matching_tasks.items():
            print(f"   - Task ID: {task_id}")
            print(f"     Name: {task.name}")
            print(f"     Status: {task.status}")
            try:
                lpt_type = task.get_field("LPT_TASK_TYPE")
                print(f"     LPT_TASK_TYPE: {lpt_type}")
            except:
                pass
            print()
    else:
        print("\n⚠️  No tasks found matching both criteria")
    
    return matching_tasks


def test_combined_filters_method():
    """
    Example: Use filter_by_custom_fields with tag filtering
    """
    print("=" * 80)
    print("Test: Combined filtering using built-in methods")
    print("=" * 80)
    
    list_id = os.environ.get("TEST_LIST_ID")
    if not list_id:
        print("⚠️  TEST_LIST_ID environment variable not set")
        return
    
    print(f"\nSearching in list: {list_id}")
    
    # Load tasks
    print("\n1. Loading tasks...")
    tasks = Tasks(list_id, include_closed=True)
    print(f"   Found {tasks.get_count()} total tasks")
    
    # Filter by tag first
    print("\n2. Filtering by tag...")
    tagged_tasks_dict = tasks.filter_by_tag("guest:jessica-smith")
    print(f"   Found {len(tagged_tasks_dict)} tasks with tag")
    
    # Now filter by custom field
    print("\n3. Filtering by custom field...")
    filters = [
        CustomFieldFilter(
            field_name="LPT_TASK_TYPE",
            operator=FilterOperator.EQUALS,
            value="LPT_CREATE_THUMBNAIL"
        )
    ]
    
    # Create a new Tasks-like object from filtered results
    # Note: This is a workaround since filter_by_custom_fields works on the full Tasks object
    matching_count = 0
    for task_id, task in tagged_tasks_dict.items():
        try:
            if task.get_field("LPT_TASK_TYPE") == "LPT_CREATE_THUMBNAIL":
                matching_count += 1
                print(f"   ✓ Match: {task.name} (ID: {task_id})")
        except:
            pass
    
    print(f"\n   Total matches: {matching_count}")


def test_multiple_custom_field_filters():
    """
    Example: Filter by multiple custom fields with AND logic
    """
    print("=" * 80)
    print("Test: Multiple custom field filters (AND logic)")
    print("=" * 80)
    
    list_id = os.environ.get("TEST_LIST_ID")
    if not list_id:
        print("⚠️  TEST_LIST_ID environment variable not set")
        return
    
    print(f"\nSearching in list: {list_id}")
    
    # Load tasks
    tasks = Tasks(list_id, include_closed=True)
    print(f"Found {tasks.get_count()} total tasks")
    
    # Define multiple filters
    filters = [
        CustomFieldFilter(
            field_name="LPT_TASK_TYPE",
            operator=FilterOperator.EQUALS,
            value="LPT_CREATE_THUMBNAIL"
        ),
        # Add more filters as needed
        # CustomFieldFilter(
        #     field_name="Priority",
        #     operator=FilterOperator.GREATER_THAN,
        #     value=2
        # ),
    ]
    
    print(f"\nApplying {len(filters)} custom field filter(s)...")
    matching_tasks = tasks.filter_by_custom_fields(filters)
    
    print(f"Found {len(matching_tasks)} matching tasks")
    
    if matching_tasks:
        print("\nMatching tasks:")
        for task_id, task in matching_tasks.items():
            print(f"  - {task.name} (ID: {task_id})")


def test_text_pattern_matching():
    """
    Example: Use CONTAINS and STARTS_WITH operators
    """
    print("=" * 80)
    print("Test: Text pattern matching")
    print("=" * 80)
    
    list_id = os.environ.get("TEST_LIST_ID")
    if not list_id:
        print("⚠️  TEST_LIST_ID environment variable not set")
        return
    
    print(f"\nSearching in list: {list_id}")
    
    tasks = Tasks(list_id, include_closed=True)
    
    # Example: Find tasks where a text field contains "thumbnail"
    filters = [
        CustomFieldFilter(
            field_name="LPT_TASK_TYPE",
            operator=FilterOperator.CONTAINS,
            value="THUMBNAIL"
        )
    ]
    
    print("\nSearching for tasks with 'THUMBNAIL' in LPT_TASK_TYPE...")
    matching_tasks = tasks.filter_by_custom_fields(filters)
    
    print(f"Found {len(matching_tasks)} matching tasks")
    
    for task_id, task in matching_tasks.items():
        try:
            value = task.get_field("LPT_TASK_TYPE")
            print(f"  - {task.name}: {value}")
        except:
            pass


def test_discover_lists():
    """
    Example: Discover all lists in workspace
    """
    print("=" * 80)
    print("Test: Discover all lists in workspace")
    print("=" * 80)
    
    team_id = os.environ.get("CLICKUP_TEAM_ID")
    if not team_id:
        print("⚠️  CLICKUP_TEAM_ID environment variable not set")
        return
    
    print(f"\nDiscovering lists in team: {team_id}")
    
    all_lists = get_all_lists(team_id)
    
    print(f"\nFound {len(all_lists)} lists:")
    for lst in all_lists[:10]:  # Show first 10
        print(f"  - {lst['name']}")
        print(f"    ID: {lst['id']}")
        print(f"    Space: {lst['space_name']}")
        if lst['folder_name']:
            print(f"    Folder: {lst['folder_name']}")
        print()
    
    if len(all_lists) > 10:
        print(f"  ... and {len(all_lists) - 10} more")


def test_check_field_availability():
    """
    Example: Check what custom fields are available in tasks
    """
    print("=" * 80)
    print("Test: Discover available custom fields")
    print("=" * 80)
    
    list_id = os.environ.get("TEST_LIST_ID")
    if not list_id:
        print("⚠️  TEST_LIST_ID environment variable not set")
        return
    
    print(f"\nChecking custom fields in list: {list_id}")
    
    tasks = Tasks(list_id, include_closed=False)
    
    if tasks.task_ids:
        # Get first task to see available fields
        first_task_id = tasks.task_ids[0]
        first_task = tasks[first_task_id]
        
        print(f"\nCustom fields in task '{first_task.name}':")
        for field_name in first_task.get_field_names():
            try:
                value = first_task.get_field(field_name)
                field_type = first_task.get_field_type(field_name)
                print(f"  - {field_name} ({field_type}): {value}")
            except Exception as e:
                print(f"  - {field_name}: <no value>")
    else:
        print("No tasks found in list")


def main():
    """Run all integration tests"""
    
    # Check environment variables
    if not os.environ.get("CLICKUP_API_KEY"):
        print("❌ Error: CLICKUP_API_KEY environment variable not set")
        print("\nPlease set your ClickUp API key:")
        print("  export CLICKUP_API_KEY='your_api_key_here'")
        print("  export CLICKUP_TEAM_ID='your_team_id_here'")
        print("  export TEST_LIST_ID='your_test_list_id_here'")
        return 1
    
    print("\n" + "=" * 80)
    print("ClickUp Helper - Integration Tests")
    print(f"Version: {clickuphelper.__version__}")
    print("=" * 80)
    print()
    
    # Run tests
    tests = [
        ("Discover Lists", test_discover_lists),
        ("Check Field Availability", test_check_field_availability),
        ("Find by Tag and Custom Field", test_find_task_by_tag_and_custom_field),
        ("Combined Filters", test_combined_filters_method),
        ("Multiple Custom Field Filters", test_multiple_custom_field_filters),
        ("Text Pattern Matching", test_text_pattern_matching),
    ]
    
    for test_name, test_func in tests:
        try:
            print()
            test_func()
            print()
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error:")
            print(f"   {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        input("Press Enter to continue to next test...")
    
    print("\n" + "=" * 80)
    print("Integration tests complete!")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
