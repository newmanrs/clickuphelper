"""
Example: Filter tasks by tag including subtasks
"""
import clickuphelper as cu
import time

# Example 1: Filter without subtasks (default behavior)
print("=" * 60)
print("Example 1: Filter tasks by tag (parent tasks only)")
print("=" * 60)

list_id = "901112032115"
tasks = cu.Tasks(list_id)

# Filter for tasks with the tag (parent tasks only)
filtered_tasks = tasks.filter_by_tag("guest:rene-brandel")

print(f"\nFound {len(filtered_tasks)} parent tasks with tag 'guest:rene-brandel':\n")
for task_id, task in filtered_tasks.items():
    print(f"Task ID: {task_id}")
    print(f"  Name: {task.name}")
    print(f"  Status: {task.status}")
    print()


# Example 2: Filter including subtasks
print("=" * 60)
print("Example 2: Filter tasks by tag (including subtasks)")
print("=" * 60)

# Filter for tasks with the tag, including subtasks
filtered_tasks_with_subtasks = tasks.filter_by_tag(
    "guest:rene-brandel", 
    include_subtasks=True
)

print(f"\nFound {len(filtered_tasks_with_subtasks)} tasks (parent + subtasks) with tag 'guest:rene-brandel':\n")
for task_id, task in filtered_tasks_with_subtasks.items():
    print(f"Task ID: {task_id}")
    print(f"  Name: {task.name}")
    print(f"  Status: {task.status}")
    
    # Check if this is a subtask by looking for parent field
    if 'parent' in task.task and task.task['parent']:
        print(f"  (Subtask of: {task.task['parent']})")
    print()

# Small delay to avoid rate limits
time.sleep(2)

# Example 3: Filter by multiple tags with subtasks
print("=" * 60)
print("Example 3: Filter by multiple tags (OR logic) with subtasks")
print("=" * 60)

# Filter for tasks with any of these tags
filtered_multi = tasks.filter_by_tag(
    ["guest:rene-brandel", "guest:elizabeth-leone", "guest:jessica-smith"],
    include_subtasks=True
)

print(f"\nFound {len(filtered_multi)} tasks with any of the specified guest tags:\n")
for task_id, task in filtered_multi.items():
    # Show which tags this task has
    task_tags = [tag['name'] for tag in task.task.get('tags', [])]
    is_subtask = 'parent' in task.task and task.task['parent']
    
    print(f"{'  [SUBTASK] ' if is_subtask else ''}{task.name}")
    print(f"    Tags: {', '.join(task_tags)}")
    print(f"    Status: {task.status}")
    print()


# Example 4: Using with get_list_tasks helper (commented out - use if you prefer this method)
# print("=" * 60)
# print("Example 4: Using with get_list_tasks helper")
# print("=" * 60)
# 
# space_name = "Your Space"
# folder_name = "Your Folder"  # or None if list is in space directly
# list_name = "Your List"
# 
# tasks = cu.get_list_tasks(space_name, folder_name, list_name)

# Reuse tasks from Example 1 for remaining examples
tasks = cu.Tasks(list_id)

# Filter with subtasks
filtered = tasks.filter_by_tag("guest:rene-brandel", include_subtasks=True)

print(f"\nTasks and subtasks with 'guest:rene-brandel' tag:")
for task_id, task in filtered.items():
    is_subtask = 'parent' in task.task and task.task['parent']
    prefix = "  └─ " if is_subtask else "• "
    print(f"{prefix}{task.name} ({task.status})")


# Example 5: Separate parent tasks and subtasks
print("=" * 60)
print("Example 5: Separate parent tasks and subtasks")
print("=" * 60)

filtered = tasks.filter_by_tag("guest:rene-brandel", include_subtasks=True)

parent_tasks = {}
subtasks = {}

for task_id, task in filtered.items():
    if 'parent' in task.task and task.task['parent']:
        subtasks[task_id] = task
    else:
        parent_tasks[task_id] = task

print(f"\nParent Tasks ({len(parent_tasks)}):")
for task_id, task in parent_tasks.items():
    print(f"  • {task.name}")

print(f"\nSubtasks ({len(subtasks)}):")
for task_id, task in subtasks.items():
    parent_id = task.task.get('parent', 'Unknown')
    print(f"  └─ {task.name} (parent: {parent_id})")
