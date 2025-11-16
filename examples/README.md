# ClickUp Helper Examples

This directory contains example scripts demonstrating real-world usage of the clickuphelper module.

## Setup

Before running any examples, set your ClickUp API credentials:

```bash
export CLICKUP_API_KEY="your_api_key_here"
export CLICKUP_TEAM_ID="your_team_id_here"
export TEST_LIST_ID="your_test_list_id_here"  # For list-specific examples
```

You can find your API key in ClickUp: Settings → Apps → API Token

## Examples

### find_guest_task.py

**Purpose:** Find tasks matching both a tag and a custom field value.

**Use Case:** Find tasks with tag `guest:jessica-smith` and custom field `LPT_TASK_TYPE == 'LPT_CREATE_THUMBNAIL'`

**Usage:**
```bash
python examples/find_guest_task.py
```

**What it demonstrates:**
- Loading tasks from a list
- Filtering by tag name
- Filtering by custom field value
- Combining multiple filter criteria
- Displaying task details

### integration_test.py

**Purpose:** Comprehensive integration testing with production data.

**Usage:**
```bash
python examples/integration_test.py
```

**What it demonstrates:**
- Discovering all lists in a workspace
- Checking available custom fields
- Finding tasks by tag and custom field
- Using multiple custom field filters with AND logic
- Text pattern matching (CONTAINS, STARTS_WITH)
- Error handling for missing fields

### test_custom_field_filters.py

**Purpose:** Test all FilterOperator types with custom fields.

**Usage:**
```bash
python examples/test_custom_field_filters.py
```

**What it demonstrates:**
- All FilterOperator types (EQUALS, NOT_EQUALS, GREATER_THAN, etc.)
- Filtering with different custom field types
- IS_SET and IS_NOT_SET operators
- Text pattern matching with CONTAINS, STARTS_WITH, REGEX
- Multiselect field filtering with IN operator

## Common Patterns

### Pattern 1: Find tasks by tag

```python
from clickuphelper import Tasks

tasks = Tasks(list_id, include_closed=True)
tagged_tasks = tasks.filter_by_tag("guest:jessica-smith")

for task_id, task in tagged_tasks.items():
    print(f"{task.name} - {task.status}")
```

### Pattern 2: Find tasks by custom field

```python
from clickuphelper import Tasks, FilterOperator, CustomFieldFilter

tasks = Tasks(list_id)

filters = [
    CustomFieldFilter(
        field_name="LPT_TASK_TYPE",
        operator=FilterOperator.EQUALS,
        value="LPT_CREATE_THUMBNAIL"
    )
]

matching_tasks = tasks.filter_by_custom_fields(filters)
```

### Pattern 3: Combine tag and custom field filters

```python
from clickuphelper import Tasks, FilterOperator, CustomFieldFilter

# Load tasks
tasks = Tasks(list_id, include_closed=True)

# Filter by tag first
tagged_tasks = tasks.filter_by_tag("guest:jessica-smith")

# Then filter by custom field
matching_tasks = {}
for task_id, task in tagged_tasks.items():
    try:
        if task.get_field("LPT_TASK_TYPE") == "LPT_CREATE_THUMBNAIL":
            matching_tasks[task_id] = task
    except:
        pass
```

### Pattern 4: Multiple custom field filters (AND logic)

```python
from clickuphelper import Tasks, FilterOperator, CustomFieldFilter

tasks = Tasks(list_id)

filters = [
    CustomFieldFilter("Priority", FilterOperator.GREATER_THAN, 2),
    CustomFieldFilter("Status_Field", FilterOperator.EQUALS, "In Progress"),
    CustomFieldFilter("Assignee", FilterOperator.IS_SET)
]

matching_tasks = tasks.filter_by_custom_fields(filters)
```

### Pattern 5: Text pattern matching

```python
from clickuphelper import Tasks, FilterOperator, CustomFieldFilter

tasks = Tasks(list_id)

# Find tasks where description contains "urgent"
filters = [
    CustomFieldFilter(
        field_name="Description",
        operator=FilterOperator.CONTAINS,
        value="urgent"
    )
]

matching_tasks = tasks.filter_by_custom_fields(filters)
```

## Troubleshooting

### "No module named 'requests'"

Install dependencies:
```bash
pip install requests click
```

Or use uv:
```bash
uv run python examples/find_guest_task.py
```

### "CLICKUP_API_KEY environment variable not set"

Make sure you've exported your API key:
```bash
export CLICKUP_API_KEY="your_key"
```

### "MissingCustomField" error

The custom field name doesn't exist in the task. Check available fields:
```python
task = Task(task_id)
print(list(task.get_field_names()))
```

### "MissingCustomFieldValue" error

The custom field exists but has no value. Use IS_SET/IS_NOT_SET operators to check:
```python
filters = [
    CustomFieldFilter("FieldName", FilterOperator.IS_SET)
]
```

## Additional Resources

- [ClickUp API Documentation](https://clickup.com/api)
- [Module Capabilities](../DOCS.md)
- Run `python -c "import clickuphelper; clickuphelper.print_capabilities()"` to see all available features
