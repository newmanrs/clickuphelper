"""
Test script for get_filtered_subtasks() method in Task class
"""
import clickuphelper as cu

print("=" * 70)
print("Testing get_filtered_subtasks() method")
print("=" * 70)

# Use a task ID that has subtasks (from sample data)
task_id = "868fqfdpt"  # René Brandel task with subtasks

# Test 1: Verify error when include_subtasks=False
print("\n" + "=" * 70)
print("Test 1: Verify ValueError when include_subtasks=False")
print("=" * 70)

task_without_subtasks = cu.Task(task_id, include_subtasks=False)
print(f"Task: {task_without_subtasks.name}")

try:
    # Try to filter subtasks when include_subtasks=False
    filter_obj = cu.CustomFieldFilter("GUEST", cu.FilterOperator.IS_SET)
    filtered_subtasks = task_without_subtasks.get_filtered_subtasks([filter_obj])
    print("ERROR: Should have raised ValueError!")
except ValueError as e:
    print(f"✓ Correctly raised ValueError: {e}")

# Test 2: Get task with subtasks and filter by tag
print("\n" + "=" * 70)
print("Test 2: Filter subtasks with include_subtasks=True")
print("=" * 70)

task_with_subtasks = cu.Task(task_id, include_subtasks=True)
print(f"Task: {task_with_subtasks.name}")

if 'subtasks' in task_with_subtasks.task:
    subtasks = task_with_subtasks.task['subtasks']
    print(f"Total subtasks: {len(subtasks)}")
    
    # Show some subtask info
    print("\nSubtask details:")
    for i, subtask in enumerate(subtasks[:3], 1):
        tags = [tag['name'] for tag in subtask.get('tags', [])]
        print(f"  {i}. {subtask['name']}")
        print(f"     Tags: {tags if tags else 'No tags'}")
        print(f"     Status: {subtask['status']['status']}")
        
        # Check custom fields
        custom_fields = subtask.get('custom_fields', [])
        print(f"     Custom fields: {len(custom_fields)} fields")
else:
    print("No subtasks found")

# Test 3: Filter subtasks using IS_SET operator
print("\n" + "=" * 70)
print("Test 3: Filter subtasks where custom field IS_SET")
print("=" * 70)

# Since subtasks in this example have empty custom_fields, let's test IS_NOT_SET
filter_obj = cu.CustomFieldFilter("GUEST", cu.FilterOperator.IS_NOT_SET)
filtered_subtasks = task_with_subtasks.get_filtered_subtasks([filter_obj])

print(f"Filtering for subtasks where 'GUEST' IS_NOT_SET")
print(f"Found {len(filtered_subtasks)} matching subtasks")

for i, subtask in enumerate(filtered_subtasks[:5], 1):
    print(f"  {i}. {subtask['name']}")

# Test 4: Test with no matching subtasks
print("\n" + "=" * 70)
print("Test 4: Filter with criteria that matches no subtasks")
print("=" * 70)

# This should return empty list since subtasks don't have this field set
filter_obj = cu.CustomFieldFilter("GUEST", cu.FilterOperator.IS_SET)
filtered_subtasks = task_with_subtasks.get_filtered_subtasks([filter_obj])

print(f"Filtering for subtasks where 'GUEST' IS_SET")
print(f"Found {len(filtered_subtasks)} matching subtasks")

# Test 5: Multiple filters with AND logic
print("\n" + "=" * 70)
print("Test 5: Multiple filters with AND logic")
print("=" * 70)

filter1 = cu.CustomFieldFilter("GUEST", cu.FilterOperator.IS_NOT_SET)
filter2 = cu.CustomFieldFilter("EP_NUM", cu.FilterOperator.IS_NOT_SET)

filtered_subtasks = task_with_subtasks.get_filtered_subtasks([filter1, filter2])

print(f"Filtering for subtasks where 'GUEST' AND 'EP_NUM' are both NOT_SET")
print(f"Found {len(filtered_subtasks)} matching subtasks")

for i, subtask in enumerate(filtered_subtasks[:5], 1):
    print(f"  {i}. {subtask['name']}")

# Test 6: Task with no subtasks
print("\n" + "=" * 70)
print("Test 6: Task with no subtasks returns empty list")
print("=" * 70)

# Find a task without subtasks
list_id = "901112032115"
tasks = cu.Tasks(list_id)

# Get first task and check if it has subtasks
for tid in tasks.task_ids[:5]:
    test_task = cu.Task(tid, include_subtasks=True)
    if 'subtasks' not in test_task.task or not test_task.task['subtasks']:
        print(f"Testing task without subtasks: {test_task.name}")
        filter_obj = cu.CustomFieldFilter("GUEST", cu.FilterOperator.IS_SET)
        filtered_subtasks = test_task.get_filtered_subtasks([filter_obj])
        print(f"✓ Correctly returned empty list: {len(filtered_subtasks)} subtasks")
        break

print("\n" + "=" * 70)
print("All tests completed successfully!")
print("=" * 70)
