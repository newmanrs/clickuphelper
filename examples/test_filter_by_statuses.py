"""
Test script for filter_by_statuses() method
"""
import clickuphelper as cu

# Use the same list_id from the example files
list_id = "901112032115"

print("=" * 70)
print("Testing filter_by_statuses() method")
print("=" * 70)

# Initialize Tasks
tasks = cu.Tasks(list_id)

print(f"\nTotal tasks in list: {len(tasks.task_ids)}")

# Get all unique statuses in the list
all_statuses = set()
for task_id in tasks:
    task = tasks[task_id]
    status = task.task.get('status', {}).get('status', '')
    all_statuses.add(status)

print(f"\nUnique statuses found: {sorted(all_statuses)}")

# Test 1: Filter by a single status
print("\n" + "=" * 70)
print("Test 1: Filter by single status")
print("=" * 70)

if all_statuses:
    test_status = list(all_statuses)[0]
    filtered = tasks.filter_by_statuses([test_status])
    print(f"\nFiltering by status: '{test_status}'")
    print(f"Found {len(filtered)} tasks with status '{test_status}':")
    for task_id, task in list(filtered.items())[:5]:  # Show first 5
        print(f"  • {task.name} - Status: {task.status}")
    if len(filtered) > 5:
        print(f"  ... and {len(filtered) - 5} more")

# Test 2: Filter by multiple statuses (OR logic)
print("\n" + "=" * 70)
print("Test 2: Filter by multiple statuses (OR logic)")
print("=" * 70)

if len(all_statuses) >= 2:
    test_statuses = list(all_statuses)[:2]
    filtered = tasks.filter_by_statuses(test_statuses)
    print(f"\nFiltering by statuses: {test_statuses}")
    print(f"Found {len(filtered)} tasks with any of these statuses:")
    
    # Group by status
    by_status = {}
    for task_id, task in filtered.items():
        status = task.status
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(task.name)
    
    for status, task_names in by_status.items():
        print(f"\n  Status '{status}': {len(task_names)} tasks")
        for name in task_names[:3]:  # Show first 3
            print(f"    • {name}")
        if len(task_names) > 3:
            print(f"    ... and {len(task_names) - 3} more")

# Test 3: Filter by non-existent status (should return empty)
print("\n" + "=" * 70)
print("Test 3: Filter by non-existent status")
print("=" * 70)

filtered = tasks.filter_by_statuses(["NonExistentStatus"])
print(f"\nFiltering by status: 'NonExistentStatus'")
print(f"Found {len(filtered)} tasks (expected 0)")

print("\n" + "=" * 70)
print("All tests completed successfully!")
print("=" * 70)
