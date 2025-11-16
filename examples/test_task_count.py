"""
Test script for get_count() method and get_task_count() function
"""
import clickuphelper as cu

# Use the same list_id from the example files
list_id = "901112032115"

print("=" * 70)
print("Testing task count functionality")
print("=" * 70)

# Test 1: get_count() method on Tasks instance
print("\n" + "=" * 70)
print("Test 1: Tasks.get_count() method")
print("=" * 70)

tasks = cu.Tasks(list_id, include_closed=False)
count = tasks.get_count()
print(f"\nTasks in list (closed excluded): {count}")
print(f"Verification using len(task_ids): {len(tasks.task_ids)}")
print(f"Match: {count == len(tasks.task_ids)}")

# Test 2: get_count() with closed tasks included
print("\n" + "=" * 70)
print("Test 2: Tasks.get_count() with closed tasks")
print("=" * 70)

tasks_with_closed = cu.Tasks(list_id, include_closed=True)
count_with_closed = tasks_with_closed.get_count()
print(f"\nTasks in list (closed included): {count_with_closed}")
print(f"Verification using len(task_ids): {len(tasks_with_closed.task_ids)}")
print(f"Match: {count_with_closed == len(tasks_with_closed.task_ids)}")

# Test 3: get_task_count() helper function
print("\n" + "=" * 70)
print("Test 3: get_task_count() helper function")
print("=" * 70)

count_helper = cu.get_task_count(list_id, include_closed=False)
print(f"\nget_task_count(include_closed=False): {count_helper}")
print(f"Match with Tasks.get_count(): {count_helper == count}")

count_helper_with_closed = cu.get_task_count(list_id, include_closed=True)
print(f"\nget_task_count(include_closed=True): {count_helper_with_closed}")
print(f"Match with Tasks.get_count(): {count_helper_with_closed == count_with_closed}")

# Test 4: Verify difference between closed and non-closed
print("\n" + "=" * 70)
print("Test 4: Difference between closed and non-closed counts")
print("=" * 70)

difference = count_with_closed - count
print(f"\nOpen tasks: {count}")
print(f"All tasks (including closed): {count_with_closed}")
print(f"Closed tasks: {difference}")

print("\n" + "=" * 70)
print("All tests completed successfully!")
print("=" * 70)
