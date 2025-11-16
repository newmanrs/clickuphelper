"""
Debug script to check if subtasks are being fetched correctly
"""
import clickuphelper as cu
import json

print("Testing subtask fetching...")
print("=" * 70)

# Test 1: Fetch a single task with subtasks
print("\nTest 1: Fetching single task with include_subtasks=True")
print("-" * 70)
task_id = "868fqfdpt"  # René Brandel task
task = cu.Task(task_id, include_subtasks=True)

print(f"Task: {task.name}")
print(f"Task ID: {task.id}")

if 'subtasks' in task.task:
    subtasks = task.task['subtasks']
    print(f"Number of subtasks: {len(subtasks)}")
    print("\nSubtasks:")
    for i, subtask in enumerate(subtasks, 1):
        tags = [tag['name'] for tag in subtask.get('tags', [])]
        print(f"  {i}. {subtask['name']}")
        print(f"     ID: {subtask['id']}")
        print(f"     Status: {subtask['status']['status']}")
        print(f"     Tags: {tags if tags else 'No tags'}")
else:
    print("No subtasks found in task data")

# Test 2: Check what the Tasks class returns
print("\n" + "=" * 70)
print("Test 2: Checking Tasks class data")
print("-" * 70)
tasks = cu.Tasks("901112032115")
task_from_list = tasks[task_id]

print(f"Task from Tasks class: {task_from_list.name}")
if 'subtasks' in task_from_list.task:
    print(f"Subtasks in Tasks class data: {len(task_from_list.task['subtasks'])}")
else:
    print("No subtasks in Tasks class data (expected - list endpoint doesn't include them)")

# Test 3: Test the filter with include_subtasks
print("\n" + "=" * 70)
print("Test 3: Testing filter_by_tag with include_subtasks=True")
print("-" * 70)
filtered = tasks.filter_by_tag("guest:rene-brandel", include_subtasks=True)

print(f"Total results: {len(filtered)}")
print("\nResults:")
for task_id, task in filtered.items():
    is_subtask = 'parent' in task.task and task.task['parent']
    tags = [tag['name'] for tag in task.task.get('tags', [])]
    prefix = "  [SUBTASK]" if is_subtask else "[PARENT]  "
    print(f"{prefix} {task.name}")
    print(f"           ID: {task_id}")
    print(f"           Tags: {tags}")
