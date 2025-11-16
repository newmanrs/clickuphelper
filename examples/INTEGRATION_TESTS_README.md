# ClickUp Helper Integration Tests

This document describes how to set up and run integration tests for the ClickUp Helper module with real production data.

## Overview

The integration test suite (`integration_test.py`) provides comprehensive testing of all major features including:

- Workspace and list discovery
- Task filtering by tags
- Task filtering by custom fields
- Combined filtering (tags + custom fields + status)
- Multiple filter operators (EQUALS, CONTAINS, GREATER_THAN, etc.)
- Subtask retrieval and filtering
- Task counting
- Error handling for missing fields
- Real-world query patterns

## Setup

### Required Environment Variables

```bash
# Your ClickUp API key (required)
export CLICKUP_API_KEY="pk_your_api_key_here"

# Your ClickUp team/workspace ID (required)
export CLICKUP_TEAM_ID="your_team_id_here"
```

### Optional Environment Variables

These are used for specific tests. If not set, tests will skip or use default values:

```bash
# List ID to run tests against
export TEST_LIST_ID="your_test_list_id"

# Tag name to test filtering (default: "guest:jessica-smith")
export TEST_TAG_NAME="guest:jessica-smith"

# Custom field name to test (default: "LPT_TASK_TYPE")
export TEST_CUSTOM_FIELD="LPT_TASK_TYPE"

# Custom field value to test (default: "LPT_CREATE_THUMBNAIL")
export TEST_FIELD_VALUE="LPT_CREATE_THUMBNAIL"
```

### Finding Your Credentials

#### API Key
1. Go to ClickUp Settings → Apps
2. Click "Generate" under API Token
3. Copy the generated token

#### Team ID
1. Go to your ClickUp workspace
2. Look at the URL: `https://app.clickup.com/{team_id}/...`
3. Or use the Teams class to discover it programmatically:
   ```python
   from clickuphelper import Teams
   teams = Teams()
   print(teams.get_team_ids())
   ```

#### List ID
1. Open a list in ClickUp
2. Look at the URL: `https://app.clickup.com/{team_id}/v/li/{list_id}`
3. Or use `get_all_lists()` to discover lists:
   ```python
   from clickuphelper import get_all_lists
   lists = get_all_lists(team_id)
   for lst in lists:
       print(f"{lst['name']}: {lst['id']}")
   ```

## Running Tests

### Run All Tests

```bash
python examples/integration_test.py
```

This will run all tests sequentially, pausing between each test for review.

### Run Without Pausing

```bash
python examples/integration_test.py --no-pause
```

### Run Specific Test

```bash
python examples/integration_test.py --test filter_operators
```

### List Available Tests

```bash
python examples/integration_test.py --list-tests
```

## Available Tests

### 1. Discover Lists (`discover_lists`)
Tests workspace discovery and list retrieval across all spaces and folders.

**What it tests:**
- `get_all_lists()` function
- Retrieving lists from spaces and folders
- List metadata (name, ID, space, folder)

**Requirements tested:** 2.1, 2.2, 2.3, 2.4

### 2. Check Field Availability (`field_availability`)
Discovers available custom fields in tasks.

**What it tests:**
- `get_field_names()` method
- `get_field()` method
- `get_field_type()` method
- Custom field discovery

### 3. Find by Tag and Custom Field (`tag_and_custom_field`)
Tests finding tasks with a specific tag and custom field value.

**What it tests:**
- `filter_by_tag()` method
- Manual custom field filtering
- Combining tag and field filters

**Requirements tested:** 5.1, 5.2, 7.1, 7.2

### 4. Combined Filters Method (`combined_filters`)
Tests using built-in filtering methods together.

**What it tests:**
- `filter_by_tag()` method
- `filter_by_custom_fields()` method
- Chaining filters

**Requirements tested:** 5.1, 5.2, 10.1, 10.2

### 5. Multiple Custom Field Filters (`multiple_custom_fields`)
Tests filtering with multiple custom field criteria (AND logic).

**What it tests:**
- `filter_by_custom_fields()` with multiple filters
- AND logic across filters
- CustomFieldFilter class

**Requirements tested:** 10.1, 10.2, 10.3

### 6. Text Pattern Matching (`text_pattern`)
Tests text-based filtering operators.

**What it tests:**
- CONTAINS operator
- STARTS_WITH operator
- Text field filtering

**Requirements tested:** 7.1, 7.2, 7.3

### 7. Filter Operators (`filter_operators`)
Tests all available filter operators.

**What it tests:**
- EQUALS operator
- CONTAINS operator
- IS_SET operator
- IS_NOT_SET operator
- All FilterOperator enum values

**Requirements tested:** 7.1, 7.2, 7.3, 7.4, 9.1, 9.2, 9.3

### 8. Error Handling (`error_handling`)
Tests error handling for missing fields and invalid values.

**What it tests:**
- MissingCustomField exception
- MissingCustomFieldValue exception
- Graceful handling of missing data
- Filter behavior with non-existent fields

**Requirements tested:** All (error handling aspect)

### 9. Combined Tag and Custom Field (`combined_tag_custom`)
Tests combining tag filters with custom field filters.

**What it tests:**
- Tag filtering followed by custom field filtering
- Multi-stage filtering
- Real-world filtering patterns

**Requirements tested:** 5.1, 5.2, 7.1, 7.2, 10.1, 10.2

### 10. Status Filtering (`status_filtering`)
Tests filtering tasks by status.

**What it tests:**
- `filter_by_statuses()` method
- OR logic for multiple statuses
- Status discovery

**Requirements tested:** 6.1, 6.2, 6.3

### 11. Subtasks with Filters (`subtasks_filters`)
Tests retrieving and filtering subtasks.

**What it tests:**
- `include_subtasks` parameter
- `get_filtered_subtasks()` method
- Subtask filtering with custom fields

**Requirements tested:** 12.1, 12.2, 12.3, 13.1, 13.2, 13.3

### 12. Task Counting (`task_count`)
Tests task counting functionality.

**What it tests:**
- `get_task_count()` function
- `get_count()` method
- Counting with filters
- Open vs. closed task counts

**Requirements tested:** 11.1, 11.2, 11.3

### 13. Real-world Query Patterns (`real_world_patterns`)
Tests common real-world query patterns.

**What it tests:**
- Finding tasks by status
- Combining tag, status, and custom field filters
- Counting tasks by status
- Multi-criteria queries

**Requirements tested:** 5.1, 5.2, 6.1, 6.2, 7.1, 7.2, 10.1, 10.2

## Common Query Patterns

### Find Tasks by Tag

```python
from clickuphelper import Tasks

tasks = Tasks(list_id, include_closed=True)
tagged_tasks = tasks.filter_by_tag("guest:jessica-smith")

for task_id, task in tagged_tasks.items():
    print(f"{task.name}: {task.status}")
```

### Find Tasks by Custom Field

```python
from clickuphelper import Tasks, FilterOperator, CustomFieldFilter

tasks = Tasks(list_id, include_closed=True)

filters = [
    CustomFieldFilter(
        field_name="LPT_TASK_TYPE",
        operator=FilterOperator.EQUALS,
        value="LPT_CREATE_THUMBNAIL"
    )
]

matching_tasks = tasks.filter_by_custom_fields(filters)
print(f"Found {len(matching_tasks)} matching tasks")
```

### Combine Tag and Custom Field Filters

```python
from clickuphelper import Tasks, FilterOperator, CustomFieldFilter

tasks = Tasks(list_id, include_closed=True)

# First filter by tag
tagged_tasks = tasks.filter_by_tag("guest:jessica-smith")

# Then filter by custom field
final_matches = {}
for task_id, task in tagged_tasks.items():
    try:
        if task.get_field("LPT_TASK_TYPE") == "LPT_CREATE_THUMBNAIL":
            final_matches[task_id] = task
    except:
        pass

print(f"Found {len(final_matches)} tasks matching both criteria")
```

### Find Tasks with Specific Status and Custom Field

```python
from clickuphelper import Tasks, FilterOperator, CustomFieldFilter

tasks = Tasks(list_id, include_closed=True)

# Filter by status
open_tasks = tasks.filter_by_statuses(["Open", "In Progress"])

# Filter by custom field
filters = [
    CustomFieldFilter(
        field_name="Priority",
        operator=FilterOperator.GREATER_THAN,
        value=2
    )
]

high_priority_open = {}
for task_id, task in open_tasks.items():
    # Apply custom field filter
    try:
        if task.get_field("Priority") > 2:
            high_priority_open[task_id] = task
    except:
        pass
```

### Find Tasks with Subtasks Matching Criteria

```python
from clickuphelper import Tasks, FilterOperator, CustomFieldFilter

tasks = Tasks(list_id, include_closed=True)

# Get tasks with subtasks
tasks_with_subtasks = tasks.get_tasks_with_subtasks(
    tag_filter="guest:jessica-smith"
)

for task_id, data in tasks_with_subtasks.items():
    parent_task = data['task']
    subtasks = data['subtasks']
    
    print(f"Parent: {parent_task.name}")
    print(f"Subtasks: {len(subtasks)}")
    
    # Filter subtasks
    filters = [
        CustomFieldFilter(
            field_name="Status",
            operator=FilterOperator.EQUALS,
            value="Complete"
        )
    ]
    
    completed_subtasks = parent_task.get_filtered_subtasks(filters)
    print(f"Completed subtasks: {len(completed_subtasks)}")
```

### Count Tasks Matching Complex Filters

```python
from clickuphelper import Tasks, FilterOperator, CustomFieldFilter

tasks = Tasks(list_id, include_closed=True)

# Count all tasks
total = tasks.get_count()

# Count tasks with specific tag
tagged = tasks.filter_by_tag("urgent")
tagged_count = len(tagged)

# Count tasks with custom field set
filters = [
    CustomFieldFilter(
        field_name="Due Date",
        operator=FilterOperator.IS_SET
    )
]
with_due_date = tasks.filter_by_custom_fields(filters)
due_date_count = len(with_due_date)

print(f"Total: {total}")
print(f"Tagged 'urgent': {tagged_count}")
print(f"With due date: {due_date_count}")
```

## Troubleshooting

### "CLICKUP_API_KEY environment variable not set"

Make sure you've exported your API key:
```bash
export CLICKUP_API_KEY="pk_your_key_here"
```

### "TEST_LIST_ID environment variable not set"

Some tests require a specific list ID. Either:
1. Set the environment variable: `export TEST_LIST_ID="your_list_id"`
2. Or the test will skip with a warning

### "No tasks found in list"

The list might be empty. Try a different list with tasks, or create some test tasks.

### "MissingCustomField" errors

The custom field name doesn't exist in the list. Check available fields:
```python
from clickuphelper import Tasks

tasks = Tasks(list_id)
if tasks.task_ids:
    task = tasks[tasks.task_ids[0]]
    print("Available fields:", list(task.get_field_names()))
```

### Rate Limiting

If you hit ClickUp API rate limits:
- Add delays between tests
- Reduce the number of tasks being processed
- Use a smaller test list

## Best Practices

1. **Use a test workspace**: Don't run tests on production data
2. **Set up test data**: Create a list with known tasks, tags, and custom fields
3. **Document your test data**: Keep track of what tags and fields exist
4. **Run tests regularly**: Ensure new changes don't break existing functionality
5. **Check results manually**: Verify that filter results match expectations

## Contributing

When adding new tests:
1. Follow the existing test function pattern
2. Add descriptive docstrings
3. Include error handling
4. Print clear output showing what's being tested
5. Update this README with the new test description
6. Reference the requirements being tested

## Support

For issues or questions:
- Check the main DOCS.md for API documentation
- Review the ClickUp API documentation
- Open an issue on the project repository
