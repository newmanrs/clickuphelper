"""
Example: Getting task counts from a ClickUp list

This example demonstrates two ways to get task counts:
1. Using the Tasks class with get_count() method
2. Using the get_task_count() helper function
"""
import clickuphelper as cu

# Specify the list ID
list_id = "901112032115"

print("=" * 70)
print("Task Count Example")
print("=" * 70)

# Method 1: Using Tasks class with get_count()
print("\nMethod 1: Using Tasks class")
print("-" * 70)

# Get open tasks only (default)
tasks = cu.Tasks(list_id, include_closed=False)
open_count = tasks.get_count()
print(f"Open tasks: {open_count}")

# Get all tasks including closed
tasks_all = cu.Tasks(list_id, include_closed=True)
total_count = tasks_all.get_count()
print(f"Total tasks (including closed): {total_count}")
print(f"Closed tasks: {total_count - open_count}")

# Method 2: Using get_task_count() helper function
print("\nMethod 2: Using get_task_count() helper function")
print("-" * 70)

# Quick one-liner to get open task count
open_count_helper = cu.get_task_count(list_id, include_closed=False)
print(f"Open tasks: {open_count_helper}")

# Quick one-liner to get total task count
total_count_helper = cu.get_task_count(list_id, include_closed=True)
print(f"Total tasks (including closed): {total_count_helper}")

# Show some task details
print("\nSample tasks from the list:")
print("-" * 70)
for i, task_id in enumerate(tasks.task_ids[:5], 1):
    task = tasks[task_id]
    print(f"{i}. {task.name} (Status: {task.status})")

if len(tasks.task_ids) > 5:
    print(f"... and {len(tasks.task_ids) - 5} more tasks")

print("\n" + "=" * 70)
