"""
Simple test: Filter tasks with tag 'guest:rene-brandel' including subtasks
List ID: 901112032115
"""
import clickuphelper as cu

print("Loading tasks from list 901112032115...")
tasks = cu.Tasks("901112032115")

print(f"Total tasks in list: {len(tasks.task_ids)}\n")

# Filter for tasks with the tag, including subtasks
print("=" * 70)
print("Filtering for tag: 'guest:rene-brandel' (including subtasks)")
print("=" * 70)

filtered = tasks.filter_by_tag("guest:rene-brandel", include_subtasks=True)

print(f"\nFound {len(filtered)} tasks/subtasks with tag 'guest:rene-brandel':\n")

# Separate parent tasks and subtasks for clearer display
parent_tasks = []
subtasks = []

for task_id, task in filtered.items():
    is_subtask = 'parent' in task.task and task.task['parent']
    if is_subtask:
        subtasks.append((task_id, task))
    else:
        parent_tasks.append((task_id, task))

# Display parent tasks
if parent_tasks:
    print(f"PARENT TASKS ({len(parent_tasks)}):")
    print("-" * 70)
    for task_id, task in parent_tasks:
        tags = [tag['name'] for tag in task.task.get('tags', [])]
        print(f"• {task.name}")
        print(f"  ID: {task_id}")
        print(f"  Status: {task.status}")
        print(f"  Tags: {', '.join(tags)}")
        print(f"  URL: {task.task.get('url', 'N/A')}")
        print()

# Display subtasks
if subtasks:
    print(f"\nSUBTASKS ({len(subtasks)}):")
    print("-" * 70)
    for task_id, task in subtasks:
        tags = [tag['name'] for tag in task.task.get('tags', [])]
        parent_id = task.task.get('parent', 'Unknown')
        print(f"└─ {task.name}")
        print(f"   ID: {task_id}")
        print(f"   Parent: {parent_id}")
        print(f"   Status: {task.status}")
        print(f"   Tags: {', '.join(tags)}")
        print(f"   URL: {task.task.get('url', 'N/A')}")
        print()

if not filtered:
    print("No tasks found with tag 'guest:rene-brandel'")
    print("\nAvailable tags in this list:")
    all_tags = set()
    for task_id in tasks:
        task = tasks[task_id]
        for tag in task.task.get('tags', []):
            all_tags.add(tag['name'])
    for tag in sorted(all_tags):
        print(f"  - {tag}")
