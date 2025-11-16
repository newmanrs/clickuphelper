#!/usr/bin/env python3
"""
Integration test script for realistic ClickUp queries.

This script demonstrates real-world usage patterns including:
- Finding tasks by tag
- Filtering by custom field values
- Combining multiple filters
- Working with subtasks
- Testing multiple filter operators
- Error handling for missing fields

Setup:
    Required environment variables:
    export CLICKUP_API_KEY="your_api_key"
    export CLICKUP_TEAM_ID="your_team_id"
    
    Optional environment variables for specific tests:
    export TEST_LIST_ID="your_test_list_id"
    export TEST_TAG_NAME="guest:jessica-smith"  # or any tag you want to test
    export TEST_CUSTOM_FIELD="LPT_TASK_TYPE"    # or any custom field name
    export TEST_FIELD_VALUE="LPT_CREATE_THUMBNAIL"  # or any field value
    
Usage:
    python examples/integration_test.py
    
    # Run specific test:
    python examples/integration_test.py --test tag_filter
    
    # Run without pausing between tests:
    python examples/integration_test.py --no-pause
"""

import os
import sys
import json
import argparse

# Add parent directory to path to import clickuphelper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import clickuphelper
from clickuphelper import (
    Tasks, 
    Task,
    FilterOperator, 
    CustomFieldFilter,
    get_all_lists,
    get_task_count,
    MissingCustomField,
    MissingCustomFieldValue
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


def test_filter_operators():
    """
    Example: Test multiple filter operators (EQUALS, CONTAINS, GREATER_THAN, etc.)
    """
    print("=" * 80)
    print("Test: Multiple filter operators")
    print("=" * 80)
    
    list_id = os.environ.get("TEST_LIST_ID")
    if not list_id:
        print("⚠️  TEST_LIST_ID environment variable not set")
        return
    
    print(f"\nSearching in list: {list_id}")
    
    tasks = Tasks(list_id, include_closed=True)
    print(f"Found {tasks.get_count()} total tasks")
    
    # Test EQUALS operator
    print("\n1. Testing EQUALS operator...")
    field_name = os.environ.get("TEST_CUSTOM_FIELD", "LPT_TASK_TYPE")
    field_value = os.environ.get("TEST_FIELD_VALUE", "LPT_CREATE_THUMBNAIL")
    
    filters = [
        CustomFieldFilter(
            field_name=field_name,
            operator=FilterOperator.EQUALS,
            value=field_value
        )
    ]
    
    matching_tasks = tasks.filter_by_custom_fields(filters)
    print(f"   Found {len(matching_tasks)} tasks where {field_name} == '{field_value}'")
    
    # Test CONTAINS operator
    print("\n2. Testing CONTAINS operator...")
    filters = [
        CustomFieldFilter(
            field_name=field_name,
            operator=FilterOperator.CONTAINS,
            value="THUMBNAIL"
        )
    ]
    
    matching_tasks = tasks.filter_by_custom_fields(filters)
    print(f"   Found {len(matching_tasks)} tasks where {field_name} contains 'THUMBNAIL'")
    
    # Test IS_SET operator
    print("\n3. Testing IS_SET operator...")
    filters = [
        CustomFieldFilter(
            field_name=field_name,
            operator=FilterOperator.IS_SET
        )
    ]
    
    matching_tasks = tasks.filter_by_custom_fields(filters)
    print(f"   Found {len(matching_tasks)} tasks where {field_name} is set")
    
    # Test IS_NOT_SET operator
    print("\n4. Testing IS_NOT_SET operator...")
    filters = [
        CustomFieldFilter(
            field_name=field_name,
            operator=FilterOperator.IS_NOT_SET
        )
    ]
    
    matching_tasks = tasks.filter_by_custom_fields(filters)
    print(f"   Found {len(matching_tasks)} tasks where {field_name} is not set")
    
    print("\n✓ Filter operator tests complete")


def test_error_handling():
    """
    Example: Test error handling for missing fields and invalid values
    """
    print("=" * 80)
    print("Test: Error handling")
    print("=" * 80)
    
    list_id = os.environ.get("TEST_LIST_ID")
    if not list_id:
        print("⚠️  TEST_LIST_ID environment variable not set")
        return
    
    print(f"\nTesting error handling in list: {list_id}")
    
    tasks = Tasks(list_id, include_closed=False)
    
    if not tasks.task_ids:
        print("⚠️  No tasks found in list")
        return
    
    # Get first task
    first_task_id = tasks.task_ids[0]
    first_task = tasks[first_task_id]
    
    # Test 1: Access non-existent custom field
    print("\n1. Testing access to non-existent custom field...")
    try:
        value = first_task.get_field("NonExistentField_12345")
        print(f"   ❌ Expected MissingCustomField exception, but got value: {value}")
    except MissingCustomField as e:
        print(f"   ✓ Correctly raised MissingCustomField: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected exception: {type(e).__name__}: {e}")
    
    # Test 2: Filter by non-existent field (should return empty results)
    print("\n2. Testing filter with non-existent field...")
    filters = [
        CustomFieldFilter(
            field_name="NonExistentField_12345",
            operator=FilterOperator.EQUALS,
            value="some_value"
        )
    ]
    
    matching_tasks = tasks.filter_by_custom_fields(filters)
    print(f"   ✓ Filter returned {len(matching_tasks)} tasks (expected 0)")
    
    # Test 3: Access field with no value
    print("\n3. Testing access to field with no value...")
    # Find a field that exists but might not have a value
    available_fields = list(first_task.get_field_names())
    if available_fields:
        test_field = available_fields[0]
        try:
            value = first_task.get_field(test_field)
            print(f"   ✓ Field '{test_field}' has value: {value}")
        except MissingCustomFieldValue as e:
            print(f"   ✓ Field '{test_field}' exists but has no value: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected exception: {type(e).__name__}: {e}")
    
    print("\n✓ Error handling tests complete")


def test_combined_tag_and_custom_field():
    """
    Example: Combine tag filter and custom field filter
    """
    print("=" * 80)
    print("Test: Combined tag and custom field filtering")
    print("=" * 80)
    
    list_id = os.environ.get("TEST_LIST_ID")
    if not list_id:
        print("⚠️  TEST_LIST_ID environment variable not set")
        return
    
    tag_name = os.environ.get("TEST_TAG_NAME", "guest:jessica-smith")
    field_name = os.environ.get("TEST_CUSTOM_FIELD", "LPT_TASK_TYPE")
    field_value = os.environ.get("TEST_FIELD_VALUE", "LPT_CREATE_THUMBNAIL")
    
    print(f"\nSearching in list: {list_id}")
    print(f"Tag: {tag_name}")
    print(f"Custom field: {field_name} == '{field_value}'")
    
    # Load tasks
    tasks = Tasks(list_id, include_closed=True)
    print(f"\nTotal tasks: {tasks.get_count()}")
    
    # Step 1: Filter by tag
    print(f"\n1. Filtering by tag '{tag_name}'...")
    tagged_tasks = tasks.filter_by_tag(tag_name)
    print(f"   Found {len(tagged_tasks)} tasks with tag")
    
    # Step 2: Apply custom field filter to tagged tasks
    print(f"\n2. Applying custom field filter to tagged tasks...")
    filters = [
        CustomFieldFilter(
            field_name=field_name,
            operator=FilterOperator.EQUALS,
            value=field_value
        )
    ]
    
    # Manually filter the tagged tasks
    final_matches = {}
    for task_id, task in tagged_tasks.items():
        try:
            task_field_value = task.get_field(field_name)
            if task_field_value == field_value:
                final_matches[task_id] = task
        except (MissingCustomField, MissingCustomFieldValue):
            pass
    
    print(f"   Found {len(final_matches)} tasks matching both criteria")
    
    # Display results
    if final_matches:
        print("\n✓ Matching tasks:")
        for task_id, task in list(final_matches.items())[:5]:  # Show first 5
            print(f"   - Task ID: {task_id}")
            print(f"     Name: {task.name}")
            print(f"     Status: {task.status}")
            try:
                value = task.get_field(field_name)
                print(f"     {field_name}: {value}")
            except:
                pass
            print()
        
        if len(final_matches) > 5:
            print(f"   ... and {len(final_matches) - 5} more")
    else:
        print("\n⚠️  No tasks found matching both criteria")


def test_status_filtering():
    """
    Example: Filter tasks by status
    """
    print("=" * 80)
    print("Test: Status filtering")
    print("=" * 80)
    
    list_id = os.environ.get("TEST_LIST_ID")
    if not list_id:
        print("⚠️  TEST_LIST_ID environment variable not set")
        return
    
    print(f"\nSearching in list: {list_id}")
    
    tasks = Tasks(list_id, include_closed=True)
    print(f"Total tasks: {tasks.get_count()}")
    
    # Get all unique statuses
    print("\n1. Discovering available statuses...")
    statuses = set()
    for task_id in tasks.task_ids:
        task = tasks[task_id]
        statuses.add(task.status)
    
    print(f"   Found statuses: {', '.join(sorted(statuses))}")
    
    # Filter by specific statuses
    if statuses:
        test_statuses = list(statuses)[:2]  # Test with first 2 statuses
        print(f"\n2. Filtering by statuses: {test_statuses}")
        
        filtered_tasks = tasks.filter_by_statuses(test_statuses)
        print(f"   Found {len(filtered_tasks)} tasks with these statuses")
        
        # Verify results
        for task_id, task in list(filtered_tasks.items())[:3]:
            print(f"   - {task.name}: {task.status}")
    
    print("\n✓ Status filtering test complete")


def test_subtasks_with_filters():
    """
    Example: Get tasks with subtasks and filter subtasks
    """
    print("=" * 80)
    print("Test: Subtasks with filtering")
    print("=" * 80)
    
    list_id = os.environ.get("TEST_LIST_ID")
    if not list_id:
        print("⚠️  TEST_LIST_ID environment variable not set")
        return
    
    print(f"\nSearching in list: {list_id}")
    
    # Get tasks with subtasks
    print("\n1. Loading tasks with subtasks...")
    tasks = Tasks(list_id, include_closed=True, include_subtasks=True)
    
    # Find tasks that have subtasks
    tasks_with_subtasks = []
    for task_id in tasks.task_ids:
        task = tasks[task_id]
        if 'subtasks' in task.task and task.task['subtasks']:
            tasks_with_subtasks.append((task_id, task))
    
    print(f"   Found {len(tasks_with_subtasks)} tasks with subtasks")
    
    if not tasks_with_subtasks:
        print("⚠️  No tasks with subtasks found")
        return
    
    # Test filtering subtasks
    print("\n2. Testing subtask filtering...")
    field_name = os.environ.get("TEST_CUSTOM_FIELD", "LPT_TASK_TYPE")
    
    for task_id, task in tasks_with_subtasks[:3]:  # Test first 3
        print(f"\n   Task: {task.name}")
        print(f"   Subtasks: {len(task.task['subtasks'])}")
        
        # Try to filter subtasks
        try:
            filters = [
                CustomFieldFilter(
                    field_name=field_name,
                    operator=FilterOperator.IS_SET
                )
            ]
            
            filtered_subtasks = task.get_filtered_subtasks(filters)
            print(f"   Filtered subtasks (with {field_name} set): {len(filtered_subtasks)}")
            
            for subtask in filtered_subtasks[:2]:  # Show first 2
                print(f"     - {subtask['name']}")
        
        except ValueError as e:
            print(f"   ⚠️  {e}")
        except Exception as e:
            print(f"   ⚠️  Error filtering subtasks: {e}")
    
    print("\n✓ Subtask filtering test complete")


def test_task_count():
    """
    Example: Count tasks with different filters
    """
    print("=" * 80)
    print("Test: Task counting")
    print("=" * 80)
    
    list_id = os.environ.get("TEST_LIST_ID")
    if not list_id:
        print("⚠️  TEST_LIST_ID environment variable not set")
        return
    
    print(f"\nCounting tasks in list: {list_id}")
    
    # Count all tasks (excluding closed)
    print("\n1. Counting open tasks...")
    count_open = get_task_count(list_id, include_closed=False)
    print(f"   Open tasks: {count_open}")
    
    # Count all tasks (including closed)
    print("\n2. Counting all tasks (including closed)...")
    count_all = get_task_count(list_id, include_closed=True)
    print(f"   All tasks: {count_all}")
    print(f"   Closed tasks: {count_all - count_open}")
    
    # Count filtered tasks
    print("\n3. Counting filtered tasks...")
    tasks = Tasks(list_id, include_closed=True)
    
    tag_name = os.environ.get("TEST_TAG_NAME", "guest:jessica-smith")
    tagged_tasks = tasks.filter_by_tag(tag_name)
    print(f"   Tasks with tag '{tag_name}': {len(tagged_tasks)}")
    
    field_name = os.environ.get("TEST_CUSTOM_FIELD", "LPT_TASK_TYPE")
    filters = [
        CustomFieldFilter(
            field_name=field_name,
            operator=FilterOperator.IS_SET
        )
    ]
    filtered_tasks = tasks.filter_by_custom_fields(filters)
    print(f"   Tasks with {field_name} set: {len(filtered_tasks)}")
    
    print("\n✓ Task counting test complete")


def test_real_world_query_patterns():
    """
    Example: Common real-world query patterns
    """
    print("=" * 80)
    print("Test: Real-world query patterns")
    print("=" * 80)
    
    list_id = os.environ.get("TEST_LIST_ID")
    if not list_id:
        print("⚠️  TEST_LIST_ID environment variable not set")
        return
    
    print(f"\nRunning common queries on list: {list_id}")
    
    tasks = Tasks(list_id, include_closed=True)
    print(f"Total tasks: {tasks.get_count()}")
    
    # Pattern 1: Find high-priority incomplete tasks
    print("\n1. Pattern: Find tasks with specific status...")
    open_statuses = ["Open", "In Progress", "To Do"]
    open_tasks = tasks.filter_by_statuses(open_statuses)
    print(f"   Found {len(open_tasks)} tasks with status in {open_statuses}")
    
    # Pattern 2: Find tasks by tag and status
    print("\n2. Pattern: Find tasks by tag and status...")
    tag_name = os.environ.get("TEST_TAG_NAME", "guest:jessica-smith")
    tagged_tasks = tasks.filter_by_tag(tag_name)
    
    # Filter tagged tasks by status
    tagged_open = {}
    for task_id, task in tagged_tasks.items():
        if task.status in open_statuses:
            tagged_open[task_id] = task
    
    print(f"   Found {len(tagged_open)} tasks with tag '{tag_name}' and open status")
    
    # Pattern 3: Find tasks with specific custom field value and status
    print("\n3. Pattern: Find tasks with custom field value and status...")
    field_name = os.environ.get("TEST_CUSTOM_FIELD", "LPT_TASK_TYPE")
    field_value = os.environ.get("TEST_FIELD_VALUE", "LPT_CREATE_THUMBNAIL")
    
    filters = [
        CustomFieldFilter(
            field_name=field_name,
            operator=FilterOperator.EQUALS,
            value=field_value
        )
    ]
    
    field_filtered = tasks.filter_by_custom_fields(filters)
    
    # Further filter by status
    field_and_status = {}
    for task_id, task in field_filtered.items():
        if task.status in open_statuses:
            field_and_status[task_id] = task
    
    print(f"   Found {len(field_and_status)} tasks with {field_name}='{field_value}' and open status")
    
    # Pattern 4: Count tasks by status
    print("\n4. Pattern: Count tasks by status...")
    status_counts = {}
    for task_id in tasks.task_ids:
        task = tasks[task_id]
        status = task.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in sorted(status_counts.items()):
        print(f"   {status}: {count}")
    
    print("\n✓ Real-world query patterns test complete")


def main():
    """Run all integration tests"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ClickUp Helper Integration Tests')
    parser.add_argument('--test', type=str, help='Run specific test by name')
    parser.add_argument('--no-pause', action='store_true', help='Run without pausing between tests')
    parser.add_argument('--list-tests', action='store_true', help='List available tests')
    args = parser.parse_args()
    
    # Check environment variables
    if not os.environ.get("CLICKUP_API_KEY"):
        print("❌ Error: CLICKUP_API_KEY environment variable not set")
        print("\nPlease set your ClickUp API key:")
        print("  export CLICKUP_API_KEY='your_api_key_here'")
        print("  export CLICKUP_TEAM_ID='your_team_id_here'")
        print("\nOptional (for specific tests):")
        print("  export TEST_LIST_ID='your_test_list_id_here'")
        print("  export TEST_TAG_NAME='guest:jessica-smith'")
        print("  export TEST_CUSTOM_FIELD='LPT_TASK_TYPE'")
        print("  export TEST_FIELD_VALUE='LPT_CREATE_THUMBNAIL'")
        return 1
    
    # Define all tests
    tests = [
        ("discover_lists", "Discover Lists", test_discover_lists),
        ("field_availability", "Check Field Availability", test_check_field_availability),
        ("tag_and_custom_field", "Find by Tag and Custom Field", test_find_task_by_tag_and_custom_field),
        ("combined_filters", "Combined Filters Method", test_combined_filters_method),
        ("multiple_custom_fields", "Multiple Custom Field Filters", test_multiple_custom_field_filters),
        ("text_pattern", "Text Pattern Matching", test_text_pattern_matching),
        ("filter_operators", "Filter Operators", test_filter_operators),
        ("error_handling", "Error Handling", test_error_handling),
        ("combined_tag_custom", "Combined Tag and Custom Field", test_combined_tag_and_custom_field),
        ("status_filtering", "Status Filtering", test_status_filtering),
        ("subtasks_filters", "Subtasks with Filters", test_subtasks_with_filters),
        ("task_count", "Task Counting", test_task_count),
        ("real_world_patterns", "Real-world Query Patterns", test_real_world_query_patterns),
    ]
    
    # List tests if requested
    if args.list_tests:
        print("\nAvailable tests:")
        for test_id, test_name, _ in tests:
            print(f"  {test_id:25} - {test_name}")
        return 0
    
    print("\n" + "=" * 80)
    print("ClickUp Helper - Integration Tests")
    print(f"Version: {clickuphelper.__version__}")
    print("=" * 80)
    print()
    
    # Filter tests if specific test requested
    if args.test:
        tests = [(tid, tname, tfunc) for tid, tname, tfunc in tests if tid == args.test or tname == args.test]
        if not tests:
            print(f"❌ Test '{args.test}' not found")
            print("\nUse --list-tests to see available tests")
            return 1
    
    # Run tests
    passed = 0
    failed = 0
    
    for test_id, test_name, test_func in tests:
        try:
            print()
            test_func()
            print()
            passed += 1
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error:")
            print(f"   {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        
        # Pause between tests unless --no-pause specified
        if not args.no_pause and (test_id, test_name, test_func) != tests[-1]:
            print()
            input("Press Enter to continue to next test...")
    
    print("\n" + "=" * 80)
    print("Integration tests complete!")
    print(f"Passed: {passed}, Failed: {failed}")
    print("=" * 80)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
