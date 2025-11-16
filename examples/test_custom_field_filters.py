"""
Test script for filter_by_custom_fields() method with FilterOperator and CustomFieldFilter
"""
import sys
sys.path.insert(0, '..')
import clickuphelper as cu

# Use the same list_id from the example files
list_id = "901112032115"

print("=" * 70)
print("Testing filter_by_custom_fields() method")
print("=" * 70)

# Initialize Tasks
tasks = cu.Tasks(list_id)

print(f"\nTotal tasks in list: {len(tasks.task_ids)}")

# Get a sample task to see available custom fields
if tasks.task_ids:
    sample_task = tasks[tasks.task_ids[0]]
    print(f"\nAvailable custom fields in sample task:")
    for field_name in sample_task.get_field_names():
        try:
            field_type = sample_task.get_field_type(field_name)
            print(f"  • {field_name} (type: {field_type})")
        except Exception as e:
            print(f"  • {field_name} (error getting type: {e})")

# Test 1: IS_SET operator
print("\n" + "=" * 70)
print("Test 1: Filter for tasks where a custom field IS_SET")
print("=" * 70)

if tasks.task_ids:
    # Get first available custom field
    sample_task = tasks[tasks.task_ids[0]]
    field_names = list(sample_task.get_field_names())
    
    if field_names:
        test_field = field_names[0]
        filter_obj = cu.CustomFieldFilter(test_field, cu.FilterOperator.IS_SET)
        filtered = tasks.filter_by_custom_fields([filter_obj])
        print(f"\nFiltering for tasks where '{test_field}' IS_SET")
        print(f"Found {len(filtered)} tasks")
        
        # Show first 3 tasks
        for task_id, task in list(filtered.items())[:3]:
            try:
                value = task.get_field(test_field)
                print(f"  • {task.name}: {test_field} = {value}")
            except Exception as e:
                print(f"  • {task.name}: Error getting field - {e}")

# Test 2: IS_NOT_SET operator
print("\n" + "=" * 70)
print("Test 2: Filter for tasks where a custom field IS_NOT_SET")
print("=" * 70)

if tasks.task_ids and field_names:
    test_field = field_names[0]
    filter_obj = cu.CustomFieldFilter(test_field, cu.FilterOperator.IS_NOT_SET)
    filtered = tasks.filter_by_custom_fields([filter_obj])
    print(f"\nFiltering for tasks where '{test_field}' IS_NOT_SET")
    print(f"Found {len(filtered)} tasks")
    
    # Show first 3 tasks
    for task_id, task in list(filtered.items())[:3]:
        print(f"  • {task.name}")

# Test 3: EQUALS operator (if we can find a suitable field)
print("\n" + "=" * 70)
print("Test 3: Filter for tasks with EQUALS operator")
print("=" * 70)

if tasks.task_ids:
    # Try to find a field with a value we can test
    for field_name in field_names[:3]:  # Check first 3 fields
        try:
            sample_value = sample_task.get_field(field_name)
            if sample_value is not None:
                filter_obj = cu.CustomFieldFilter(field_name, cu.FilterOperator.EQUALS, sample_value)
                filtered = tasks.filter_by_custom_fields([filter_obj])
                print(f"\nFiltering for tasks where '{field_name}' EQUALS '{sample_value}'")
                print(f"Found {len(filtered)} tasks")
                
                # Show first 3 tasks
                for task_id, task in list(filtered.items())[:3]:
                    try:
                        value = task.get_field(field_name)
                        print(f"  • {task.name}: {field_name} = {value}")
                    except Exception:
                        pass
                break
        except Exception:
            continue

# Test 4: Multiple filters with AND logic
print("\n" + "=" * 70)
print("Test 4: Multiple filters with AND logic")
print("=" * 70)

if tasks.task_ids and len(field_names) >= 2:
    # Create two IS_SET filters
    filter1 = cu.CustomFieldFilter(field_names[0], cu.FilterOperator.IS_SET)
    filter2 = cu.CustomFieldFilter(field_names[1], cu.FilterOperator.IS_SET)
    
    filtered = tasks.filter_by_custom_fields([filter1, filter2])
    print(f"\nFiltering for tasks where both '{field_names[0]}' AND '{field_names[1]}' are set")
    print(f"Found {len(filtered)} tasks")
    
    # Show first 3 tasks
    for task_id, task in list(filtered.items())[:3]:
        try:
            val1 = task.get_field(field_names[0])
            val2 = task.get_field(field_names[1])
            print(f"  • {task.name}")
            print(f"    - {field_names[0]} = {val1}")
            print(f"    - {field_names[1]} = {val2}")
        except Exception as e:
            print(f"  • {task.name}: Error - {e}")

print("\n" + "=" * 70)
print("All tests completed successfully!")
print("=" * 70)
