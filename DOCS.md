# ClickUp Helper Documentation

**Version:** 0.4.0

## Table of Contents

1. [Setup and Configuration](#setup-and-configuration)
2. [Workspace Discovery (Teams)](#workspace-discovery-teams)
3. [Unified List Retrieval](#unified-list-retrieval)
4. [Tag Management](#tag-management)
5. [Task Filtering by Tags](#task-filtering-by-tags)
6. [Task Filtering by Status](#task-filtering-by-status)
7. [Advanced Custom Field Filtering](#advanced-custom-field-filtering)
8. [Task Count Retrieval](#task-count-retrieval)
9. [Subtask Retrieval](#subtask-retrieval)
10. [Subtask Filtering](#subtask-filtering)
11. [Module Capabilities](#module-capabilities)
12. [Error Handling](#error-handling)
13. [Combining Multiple Filters](#combining-multiple-filters)

---

## Setup and Configuration

### Environment Variables

The ClickUp Helper module requires the following environment variables:

```bash
# Required: Your ClickUp API key
export CLICKUP_API_KEY="your_api_key_here"

# Optional: Default team/workspace ID (can be discovered dynamically)
export CLICKUP_TEAM_ID="your_team_id_here"
```

### Installation

```bash
pip install -e .
```

### Basic Import

```python
import clickuphelper as cu
```

---

## Workspace Discovery (Teams)

### Overview

The `Teams` class allows you to discover all workspaces (teams) accessible to your API key without hardcoding team IDs.

### Use Cases

- Dynamically discover available workspaces
- Build multi-workspace applications
- Get team IDs for API operations

### Example Usage

```python
import clickuphelper as cu

# Initialize Teams to discover all workspaces
teams = cu.Teams()

# Get all team names
team_names = teams.get_team_names()
print(f"Available teams: {team_names}")

# Get all team IDs
team_ids = teams.get_team_ids()
print(f"Team IDs: {team_ids}")

# Get team ID by name (using indexing)
team_id = teams["My Workspace"]
print(f"Team ID for 'My Workspace': {team_id}")

# Get team metadata by name
team_info = teams.get_team_by_name("My Workspace")
print(f"Team info: {team_info}")

# Get team metadata by ID
team_info = teams.get_team_by_id("123456")

# Iterate over all teams
for team in teams:
    print(f"Team: {team['name']} (ID: {team['id']})")
```

### Methods

- `get_team_ids()` - Returns list of team IDs
- `get_team_names()` - Returns list of team names
- `get_team_by_id(team_id)` - Returns team metadata dictionary
- `get_team_by_name(team_name)` - Returns team metadata dictionary
- `__getitem__(name)` - Allows indexing by team name to get team ID
- `__iter__()` - Allows iteration over teams

---

## Unified List Retrieval

### Overview

The `get_all_lists()` function retrieves all lists across a workspace without requiring you to navigate the space and folder hierarchy manually.

### Use Cases

- Get a complete inventory of all lists in a workspace
- Find lists without knowing their location in the hierarchy
- Build list selection interfaces

### Example Usage

```python
import clickuphelper as cu

# Get team ID
teams = cu.Teams()
team_id = teams["My Workspace"]

# Get all lists in the workspace
all_lists = cu.get_all_lists(team_id)

# Print list information
for list_item in all_lists:
    print(f"List: {list_item['name']}")
    print(f"  ID: {list_item['id']}")
    print(f"  Space: {list_item['space_name']} ({list_item['space_id']})")
    if list_item['folder_id']:
        print(f"  Folder: {list_item['folder_name']} ({list_item['folder_id']})")
    else:
        print(f"  Location: Directly in space")
    print()

# Include archived lists
all_lists_with_archived = cu.get_all_lists(team_id, archived=True)

# Find a specific list by name
target_list = next((l for l in all_lists if l['name'] == "My List"), None)
if target_list:
    print(f"Found list: {target_list['id']}")
```

### Function Signature

```python
get_all_lists(team_id: str, archived: bool = False) -> List[dict]
```

### Parameters

- `team_id` (str) - The workspace/team ID
- `archived` (bool) - Whether to include archived lists (default: False)

### Returns

List of dictionaries with the following structure:
```python
{
    'id': str,              # List ID
    'name': str,            # List name
    'space_id': str,        # Parent space ID
    'space_name': str,      # Parent space name
    'folder_id': str | None,  # Parent folder ID (None if directly in space)
    'folder_name': str | None # Parent folder name (None if directly in space)
}
```

---

## Tag Management

### Overview

Functions to retrieve and create tags within ClickUp spaces.

### Use Cases

- Discover available tags for filtering
- Programmatically create tags for categorization
- Build tag-based workflows

### Get Space Tags

```python
import clickuphelper as cu

# Get space ID
spaces = cu.Spaces()
space_id = spaces["My Space"]

# Get all tags in the space
tags = cu.get_space_tags(space_id)

# Print tag information
for tag in tags:
    print(f"Tag: {tag['name']} (ID: {tag['tag']})")

# Handle spaces with no tags (returns empty list)
if not tags:
    print("No tags found in this space")
```

### Create Space Tag

```python
import clickuphelper as cu

# Get space ID
spaces = cu.Spaces()
space_id = spaces["My Space"]

# Create a simple tag
result = cu.create_space_tag(space_id, "urgent")
print(f"Created tag: {result}")

# Create a tag with custom colors
result = cu.create_space_tag(
    space_id,
    "high-priority",
    tag_fg_color="#FFFFFF",
    tag_bg_color="#FF0000"
)
print(f"Created colored tag: {result}")
```

### Function Signatures

```python
get_space_tags(space_id: str) -> List[dict]

create_space_tag(
    space_id: str,
    tag_name: str,
    tag_fg_color: str = None,
    tag_bg_color: str = None
) -> dict
```

### Error Handling

```python
# If tag already exists, API returns an error
try:
    result = cu.create_space_tag(space_id, "existing-tag")
except Exception as e:
    print(f"Tag creation failed: {e}")
```

---

## Task Filtering by Tags

### Overview

Filter tasks by one or more tag names using OR logic.

### Use Cases

- Find all tasks with a specific tag
- Retrieve tasks matching any of several tags
- Filter tasks by category or label

### Example Usage

```python
import clickuphelper as cu

# Get tasks from a list
list_id = "123456789"
tasks = cu.Tasks(list_id)

# Filter by a single tag
tagged_tasks = tasks.filter_by_tag("urgent")
print(f"Found {len(tagged_tasks)} urgent tasks")

# Filter by multiple tags (OR logic - matches any tag)
multi_tag_tasks = tasks.filter_by_tag(["urgent", "bug", "feature"])
print(f"Found {len(multi_tag_tasks)} tasks with urgent, bug, or feature tags")

# Iterate over filtered tasks
for task_id, task in tagged_tasks.items():
    print(f"Task: {task.name} (ID: {task_id})")
    print(f"  Status: {task.status}")
    print(f"  Tags: {[tag['name'] for tag in task.task['tags']]}")

# Check if any tasks match
if not tagged_tasks:
    print("No tasks found with the specified tags")
```

### Method Signature

```python
Tasks.filter_by_tag(tag_names: Union[str, List[str]]) -> dict
```

### Parameters

- `tag_names` - Single tag name (string) or list of tag names

### Returns

Dictionary of `task_id -> Task object` for tasks matching any of the specified tags (OR logic)

### Practical Example: Find Guest Tasks

```python
import clickuphelper as cu

# Find all tasks tagged with a specific guest
list_id = "123456789"
tasks = cu.Tasks(list_id)

guest_tasks = tasks.filter_by_tag("guest:jessica-smith")

for task_id, task in guest_tasks.items():
    print(f"Guest task: {task.name}")
    print(f"  Created: {task.created}")
    print(f"  Status: {task.status}")
```

---

## Task Filtering by Status

### Overview

Filter tasks by one or more status values using OR logic.

### Use Cases

- Find tasks in specific workflow states
- Get all active tasks (multiple "in progress" statuses)
- Filter by completion status

### Example Usage

```python
import clickuphelper as cu

# Get tasks from a list
list_id = "123456789"
tasks = cu.Tasks(list_id, include_closed=True)

# Filter by a single status
open_tasks = tasks.filter_by_statuses(["Open"])
print(f"Found {len(open_tasks)} open tasks")

# Filter by multiple statuses (OR logic)
active_tasks = tasks.filter_by_statuses(["In Progress", "In Review", "Testing"])
print(f"Found {len(active_tasks)} active tasks")

# Iterate over filtered tasks
for task_id, task in active_tasks.items():
    print(f"Task: {task.name}")
    print(f"  Status: {task.status}")
    print(f"  Updated: {task.updated}")

# Combine with other operations
completed_tasks = tasks.filter_by_statuses(["Complete", "Closed"])
print(f"Completed: {len(completed_tasks)} tasks")
```

### Method Signature

```python
Tasks.filter_by_statuses(status_names: List[str]) -> dict
```

### Parameters

- `status_names` - List of status names to match

### Returns

Dictionary of `task_id -> Task object` for tasks matching any of the specified statuses (OR logic)

---

## Advanced Custom Field Filtering

### Overview

Filter tasks using complex custom field criteria with support for multiple operators and data types. Multiple filters use AND logic.

### Use Cases

- Find tasks with specific custom field values
- Filter by numeric ranges
- Search text fields with pattern matching
- Check for missing or set fields
- Filter multiselect (labels) fields

### FilterOperator Types

The `FilterOperator` enum provides the following comparison operators:

| Operator | Description | Use Case |
|----------|-------------|----------|
| `EQUALS` | Exact match | Find tasks where field equals a specific value |
| `NOT_EQUALS` | Not equal to | Exclude tasks with a specific value |
| `GREATER_THAN` | Numeric > | Find tasks with values above a threshold |
| `GREATER_THAN_OR_EQUAL` | Numeric >= | Find tasks with values at or above a threshold |
| `LESS_THAN` | Numeric < | Find tasks with values below a threshold |
| `LESS_THAN_OR_EQUAL` | Numeric <= | Find tasks with values at or below a threshold |
| `CONTAINS` | Substring match (case-insensitive) | Search text fields for keywords |
| `STARTS_WITH` | Prefix match (case-insensitive) | Find text fields starting with a pattern |
| `REGEX` | Regular expression match | Complex text pattern matching |
| `IN` | Value in list | Check if value is in a list of options |
| `IS_SET` | Field has a value | Find tasks where field is populated |
| `IS_NOT_SET` | Field is empty | Find tasks with missing field values |

### Supported Custom Field Types

- `number` - Numeric values (int or float)
- `text` - Long text fields
- `short_text` - Short text fields
- `url` - URL fields
- `date` - Date/datetime fields
- `drop_down` - Single-select dropdown
- `labels` - Multi-select labels/tags
- `tasks` - Task relationship fields
- `attachment` - File attachment fields

### Basic Example

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

# Get tasks from a list
list_id = "123456789"
tasks = cu.Tasks(list_id)

# Create a simple filter
filters = [
    CustomFieldFilter("Priority", FilterOperator.EQUALS, "High")
]

# Apply the filter
filtered_tasks = tasks.filter_by_custom_fields(filters)

for task_id, task in filtered_tasks.items():
    print(f"High priority task: {task.name}")
```

### Numeric Filtering

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

tasks = cu.Tasks(list_id)

# Find tasks with estimated hours greater than 8
filters = [
    CustomFieldFilter("Estimated Hours", FilterOperator.GREATER_THAN, 8)
]

large_tasks = tasks.filter_by_custom_fields(filters)

# Find tasks within a range (using multiple filters with AND logic)
filters = [
    CustomFieldFilter("Estimated Hours", FilterOperator.GREATER_THAN_OR_EQUAL, 4),
    CustomFieldFilter("Estimated Hours", FilterOperator.LESS_THAN_OR_EQUAL, 8)
]
medium_tasks = tasks.filter_by_custom_fields(filters)
print(f"Found {len(medium_tasks)} tasks with 4-8 hour estimates")
```

### Text Filtering

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

tasks = cu.Tasks(list_id)

# Find tasks containing a keyword (case-insensitive)
filters = [
    CustomFieldFilter("Description", FilterOperator.CONTAINS, "database")
]
db_tasks = tasks.filter_by_custom_fields(filters)

# Find tasks starting with a prefix
filters = [
    CustomFieldFilter("Task Type", FilterOperator.STARTS_WITH, "BUG-")
]
bug_tasks = tasks.filter_by_custom_fields(filters)

# Use regex for complex patterns
filters = [
    CustomFieldFilter("Task ID", FilterOperator.REGEX, r"^PROJ-\d{4}$")
]
matching_tasks = tasks.filter_by_custom_fields(filters)
```

### Multiselect (Labels) Filtering

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

tasks = cu.Tasks(list_id)

# Find tasks with any of the specified labels (OR logic within the field)
filters = [
    CustomFieldFilter("Categories", FilterOperator.IN, ["Frontend", "Backend"])
]
dev_tasks = tasks.filter_by_custom_fields(filters)

# Note: The IN operator checks if any task label matches any filter value
```

### Null Checking

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

tasks = cu.Tasks(list_id)

# Find tasks with missing assignee
filters = [
    CustomFieldFilter("Assignee", FilterOperator.IS_NOT_SET)
]
unassigned_tasks = tasks.filter_by_custom_fields(filters)

# Find tasks with a value set
filters = [
    CustomFieldFilter("Due Date", FilterOperator.IS_SET)
]
tasks_with_due_date = tasks.filter_by_custom_fields(filters)
```

### Multiple Filters (AND Logic)

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

tasks = cu.Tasks(list_id)

# Combine multiple filters - ALL must match (AND logic)
filters = [
    CustomFieldFilter("Priority", FilterOperator.EQUALS, "High"),
    CustomFieldFilter("Status", FilterOperator.NOT_EQUALS, "Complete"),
    CustomFieldFilter("Estimated Hours", FilterOperator.GREATER_THAN, 4)
]

urgent_incomplete_tasks = tasks.filter_by_custom_fields(filters)
print(f"Found {len(urgent_incomplete_tasks)} urgent incomplete tasks")
```

### Method Signature

```python
Tasks.filter_by_custom_fields(filters: List[CustomFieldFilter]) -> dict
```

### Parameters

- `filters` - List of `CustomFieldFilter` objects

### Returns

Dictionary of `task_id -> Task object` for tasks matching ALL filters (AND logic)

### Practical Example: Find Specific Task Type

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

# Find all thumbnail creation tasks
list_id = "123456789"
tasks = cu.Tasks(list_id)

filters = [
    CustomFieldFilter("LPT_TASK_TYPE", FilterOperator.EQUALS, "LPT_CREATE_THUMBNAIL")
]

thumbnail_tasks = tasks.filter_by_custom_fields(filters)

for task_id, task in thumbnail_tasks.items():
    print(f"Thumbnail task: {task.name}")
    try:
        task_type = task.get_field("LPT_TASK_TYPE")
        print(f"  Type: {task_type}")
    except cu.MissingCustomFieldValue:
        print(f"  Type: Not set")
```

---

## Task Count Retrieval

### Overview

Get the count of tasks in a list without loading all task data.

### Use Cases

- Check list size before processing
- Display task counts in dashboards
- Monitor list growth

### Example Usage

```python
import clickuphelper as cu

# Method 1: Using Tasks class
list_id = "123456789"
tasks = cu.Tasks(list_id)
count = tasks.get_count()
print(f"Task count: {count}")

# Method 2: Using helper function
count = cu.get_task_count(list_id)
print(f"Task count: {count}")

# Include closed tasks
count_with_closed = cu.get_task_count(list_id, include_closed=True)
print(f"Total tasks (including closed): {count_with_closed}")

# Get counts for multiple lists
list_ids = ["123", "456", "789"]
for lid in list_ids:
    count = cu.get_task_count(lid)
    print(f"List {lid}: {count} tasks")
```

### Method Signatures

```python
Tasks.get_count() -> int

get_task_count(list_id: str, include_closed: bool = False) -> int
```

### Parameters

- `list_id` (str) - The list ID
- `include_closed` (bool) - Whether to include closed tasks (default: False)

### Returns

Integer count of tasks in the list

---

## Subtask Retrieval

### Overview

Retrieve tasks with their complete subtask hierarchies. Supports filtering parent tasks while including all subtasks.

### Use Cases

- Get complete task hierarchies
- Process parent tasks and their children together
- Filter parent tasks while preserving subtask relationships

### Basic Subtask Retrieval

```python
import clickuphelper as cu

# Initialize Tasks with include_subtasks=True
list_id = "123456789"
tasks = cu.Tasks(list_id, include_subtasks=True)

# Access subtasks from a task
for task_id in tasks.task_ids:
    task = tasks[task_id]
    if 'subtasks' in task.task:
        print(f"Task: {task.name}")
        print(f"  Subtasks: {len(task.task['subtasks'])}")
        for subtask in task.task['subtasks']:
            print(f"    - {subtask['name']}")
```

### Filtered Tasks with All Subtasks

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

list_id = "123456789"
tasks = cu.Tasks(list_id)

# Get tasks matching filters, with all their subtasks
# Filters apply to parent tasks only
result = tasks.get_tasks_with_subtasks(
    tag_filter="urgent"
)

for task_id, data in result.items():
    parent_task = data['task']
    subtasks = data['subtasks']
    
    print(f"Parent: {parent_task.name}")
    print(f"  Subtasks: {len(subtasks)}")
    for subtask in subtasks:
        print(f"    - {subtask.name} (Status: {subtask.status})")
```

### Filter Parent Tasks with Custom Fields

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

list_id = "123456789"
tasks = cu.Tasks(list_id)

# Filter parent tasks by custom field, include all subtasks
filters = [
    CustomFieldFilter("Priority", FilterOperator.EQUALS, "High")
]

result = tasks.get_tasks_with_subtasks(filters=filters)

for task_id, data in result.items():
    parent = data['task']
    subtasks = data['subtasks']
    
    print(f"High priority task: {parent.name}")
    print(f"  Has {len(subtasks)} subtasks (all included regardless of priority)")
```

### Combine Multiple Parent Filters

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

list_id = "123456789"
tasks = cu.Tasks(list_id)

# Apply multiple filters to parent tasks
filters = [
    CustomFieldFilter("Department", FilterOperator.EQUALS, "Engineering")
]

result = tasks.get_tasks_with_subtasks(
    filters=filters,
    tag_filter="sprint-23",
    status_filter=["In Progress", "In Review"]
)

print(f"Found {len(result)} matching parent tasks with subtasks")
```

### Method Signature

```python
Tasks.get_tasks_with_subtasks(
    filters: Optional[List[CustomFieldFilter]] = None,
    tag_filter: Optional[Union[str, List[str]]] = None,
    status_filter: Optional[List[str]] = None
) -> dict
```

### Parameters

- `filters` - Optional list of CustomFieldFilter objects (applied to parent tasks only)
- `tag_filter` - Optional tag name or list of tag names (applied to parent tasks only)
- `status_filter` - Optional list of status names (applied to parent tasks only)

### Returns

Dictionary with structure:
```python
{
    task_id: {
        'task': Task object,           # Parent task
        'subtasks': [Task, Task, ...]  # List of subtask Task objects
    }
}
```

**Important:** All subtasks are included regardless of whether they match the parent filters.

---

## Subtask Filtering

### Overview

Filter subtasks of a specific task based on custom field criteria.

### Use Cases

- Find specific subtasks within a task hierarchy
- Filter subtasks by custom field values
- Process only relevant subtasks

### Example Usage

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

# Get a task with subtasks
task_id = "abc123"
task = cu.Task(task_id, include_subtasks=True)

# Filter subtasks by custom field
filters = [
    CustomFieldFilter("Status", FilterOperator.EQUALS, "Complete")
]

completed_subtasks = task.get_filtered_subtasks(filters)

print(f"Found {len(completed_subtasks)} completed subtasks")
for subtask in completed_subtasks:
    print(f"  - {subtask['name']}")
```

### Multiple Filter Criteria

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

task = cu.Task(task_id, include_subtasks=True)

# Apply multiple filters (AND logic)
filters = [
    CustomFieldFilter("Priority", FilterOperator.EQUALS, "High"),
    CustomFieldFilter("Assignee", FilterOperator.IS_SET)
]

urgent_assigned_subtasks = task.get_filtered_subtasks(filters)

for subtask in urgent_assigned_subtasks:
    print(f"Urgent subtask: {subtask['name']}")
```

### Error Handling

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

# Task must be initialized with include_subtasks=True
task = cu.Task(task_id, include_subtasks=False)

try:
    filters = [CustomFieldFilter("Status", FilterOperator.EQUALS, "Open")]
    subtasks = task.get_filtered_subtasks(filters)
except ValueError as e:
    print(f"Error: {e}")
    # Reinitialize with subtasks
    task = cu.Task(task_id, include_subtasks=True)
    subtasks = task.get_filtered_subtasks(filters)
```

### Method Signature

```python
Task.get_filtered_subtasks(filters: List[CustomFieldFilter]) -> List[dict]
```

### Parameters

- `filters` - List of CustomFieldFilter objects

### Returns

List of subtask dictionaries matching ALL filters (AND logic)

### Raises

- `ValueError` - If task was not initialized with `include_subtasks=True`

---

## Module Capabilities

### Overview

Programmatically query the module version and available capabilities. Useful for introspection and documentation.

### Use Cases

- Discover available features
- Check module version
- Generate documentation
- LLM tool discovery

### Get Capabilities (Structured Data)

```python
import clickuphelper as cu

# Get structured capabilities dictionary
capabilities = cu.get_capabilities()

# Access version
print(f"Version: {capabilities['version']}")

# List all classes
for class_name, class_info in capabilities['classes'].items():
    print(f"\nClass: {class_name}")
    print(f"Description: {class_info['description']}")
    print("Methods:")
    for method in class_info['key_methods']:
        print(f"  - {method}")

# List all functions
for func_name, func_info in capabilities['functions'].items():
    print(f"\nFunction: {func_name}")
    print(f"Description: {func_info['description']}")

# Check supported filter operators
operators = capabilities['filtering']['operators']
print(f"Supported operators: {operators}")

# Check supported custom field types
field_types = capabilities['filtering']['custom_field_types']
print(f"Supported field types: {field_types}")
```

### Print Capabilities (Human-Readable)

```python
import clickuphelper as cu

# Print formatted capabilities to stdout
cu.print_capabilities()
```

This outputs a comprehensive, human-readable summary of all module capabilities including:
- Version information
- All classes with methods and use cases
- All functions with parameters and return types
- Filtering capabilities and operators
- Supported custom field types
- Exception types
- Required environment variables

### Function Signatures

```python
get_capabilities() -> dict
print_capabilities() -> None
```

---

## Error Handling

### Overview

The module provides specific exceptions for common error cases.

### Exception Types

#### MissingCustomField

Raised when a custom field name does not exist in the task schema.

```python
import clickuphelper as cu

task = cu.Task(task_id)

try:
    value = task.get_field("NonexistentField")
except cu.MissingCustomField as e:
    print(f"Field not found: {e}")
    # Get available fields
    available_fields = task.get_field_names()
    print(f"Available fields: {list(available_fields)}")
```

#### MissingCustomFieldValue

Raised when a custom field exists but has no value set.

```python
import clickuphelper as cu

task = cu.Task(task_id)

try:
    value = task.get_field("OptionalField")
except cu.MissingCustomFieldValue as e:
    print(f"Field has no value: {e}")
    # Handle missing value
    value = None  # or provide a default
```

### Handling Missing Fields in Filters

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

tasks = cu.Tasks(list_id)

# Use IS_SET/IS_NOT_SET to handle missing values gracefully
filters = [
    CustomFieldFilter("OptionalField", FilterOperator.IS_SET)
]

tasks_with_field = tasks.filter_by_custom_fields(filters)

# Or check for missing values
filters = [
    CustomFieldFilter("OptionalField", FilterOperator.IS_NOT_SET)
]

tasks_without_field = tasks.filter_by_custom_fields(filters)
```

### API Errors

```python
import clickuphelper as cu
import requests

try:
    # Invalid space ID
    tags = cu.get_space_tags("invalid_space_id")
except requests.exceptions.HTTPError as e:
    print(f"API error: {e}")
    print(f"Status code: {e.response.status_code}")
    print(f"Response: {e.response.text}")
```

### KeyError for Invalid Names

```python
import clickuphelper as cu

teams = cu.Teams()

try:
    team_id = teams["Nonexistent Team"]
except KeyError as e:
    print(f"Team not found: {e}")
    # Get available teams
    available_teams = teams.get_team_names()
    print(f"Available teams: {available_teams}")
```

---

## Combining Multiple Filters

### Overview

Combine different filtering methods to create powerful queries.

### Example 1: Tag + Custom Field Filter

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

list_id = "123456789"
tasks = cu.Tasks(list_id)

# First filter by tag
tagged_tasks = tasks.filter_by_tag("urgent")

# Then filter by custom field
# Note: We need to create a new Tasks-like structure or iterate manually
filtered_results = {}
for task_id, task in tagged_tasks.items():
    try:
        priority = task.get_field("Priority")
        if priority == "High":
            filtered_results[task_id] = task
    except cu.MissingCustomFieldValue:
        pass

print(f"Found {len(filtered_results)} urgent high-priority tasks")
```

### Example 2: Status + Custom Field Filter

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

list_id = "123456789"
tasks = cu.Tasks(list_id, include_closed=True)

# Filter by status first
active_tasks = tasks.filter_by_statuses(["In Progress", "In Review"])

# Then apply custom field filters
filtered_results = {}
for task_id, task in active_tasks.items():
    try:
        estimated_hours = task.get_field("Estimated Hours")
        assignee = task.get_field("Assignee")
        
        if estimated_hours > 8 and assignee:
            filtered_results[task_id] = task
    except cu.MissingCustomFieldValue:
        pass

print(f"Found {len(filtered_results)} large active assigned tasks")
```

### Example 3: Complex Multi-Stage Filter

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

list_id = "123456789"
tasks = cu.Tasks(list_id)

# Stage 1: Filter by custom fields
filters = [
    CustomFieldFilter("Department", FilterOperator.EQUALS, "Engineering"),
    CustomFieldFilter("Estimated Hours", FilterOperator.GREATER_THAN, 4)
]
engineering_tasks = tasks.filter_by_custom_fields(filters)

# Stage 2: Filter by tag
tagged_tasks = {}
for task_id, task in engineering_tasks.items():
    task_tags = [tag['name'] for tag in task.task.get('tags', [])]
    if 'sprint-23' in task_tags:
        tagged_tasks[task_id] = task

# Stage 3: Filter by status
final_tasks = {}
for task_id, task in tagged_tasks.items():
    if task.status in ['In Progress', 'In Review']:
        final_tasks[task_id] = task

print(f"Found {len(final_tasks)} matching tasks")
for task_id, task in final_tasks.items():
    print(f"  - {task.name} ({task.status})")
```

### Example 4: Tag + Custom Field with Subtasks

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

list_id = "123456789"
tasks = cu.Tasks(list_id)

# Find parent tasks by tag and custom field, include all subtasks
filters = [
    CustomFieldFilter("LPT_TASK_TYPE", FilterOperator.EQUALS, "LPT_CREATE_THUMBNAIL")
]

result = tasks.get_tasks_with_subtasks(
    filters=filters,
    tag_filter="guest:jessica-smith"
)

for task_id, data in result.items():
    parent = data['task']
    subtasks = data['subtasks']
    
    print(f"Guest thumbnail task: {parent.name}")
    print(f"  Subtasks: {len(subtasks)}")
    
    # Further filter subtasks
    for subtask in subtasks:
        try:
            subtask_obj = cu.Task(subtask.id, raw_task=subtask.task)
            status = subtask_obj.status
            if status == "Complete":
                print(f"    ✓ {subtask.name}")
            else:
                print(f"    ○ {subtask.name} ({status})")
        except Exception:
            print(f"    - {subtask.name}")
```

### Example 5: Find Tasks with Specific Tag and Field Combination

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

def find_tasks_by_tag_and_field(list_id, tag_name, field_name, field_value):
    """
    Find tasks matching both a tag and a custom field value.
    """
    tasks = cu.Tasks(list_id)
    
    # Filter by tag
    tagged_tasks = tasks.filter_by_tag(tag_name)
    
    # Filter by custom field
    results = {}
    for task_id, task in tagged_tasks.items():
        try:
            value = task.get_field(field_name)
            if value == field_value:
                results[task_id] = task
        except (cu.MissingCustomField, cu.MissingCustomFieldValue):
            pass
    
    return results

# Usage
matching_tasks = find_tasks_by_tag_and_field(
    list_id="123456789",
    tag_name="guest:jessica-smith",
    field_name="LPT_TASK_TYPE",
    field_value="LPT_CREATE_THUMBNAIL"
)

print(f"Found {len(matching_tasks)} matching tasks")
```

### Best Practices for Combining Filters

1. **Order matters for performance**: Apply the most restrictive filter first to reduce the dataset size
2. **Handle exceptions**: Always wrap custom field access in try-except blocks
3. **Use appropriate operators**: Choose IS_SET/IS_NOT_SET for optional fields
4. **Consider filter logic**: Remember that custom field filters use AND logic, while tag/status filters use OR logic
5. **Cache intermediate results**: Store filtered results if you need to apply multiple sequential filters

---

## Additional Examples

### Example: Build a Task Report

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter

def generate_task_report(list_id):
    """Generate a comprehensive task report."""
    tasks = cu.Tasks(list_id, include_closed=True)
    
    # Get counts by status
    status_counts = {}
    for task_id in tasks.task_ids:
        task = tasks[task_id]
        status = task.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("Task Report")
    print("=" * 50)
    print(f"Total tasks: {tasks.get_count()}")
    print("\nBy Status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    
    # Find high priority tasks
    filters = [
        CustomFieldFilter("Priority", FilterOperator.EQUALS, "High")
    ]
    high_priority = tasks.filter_by_custom_fields(filters)
    print(f"\nHigh priority tasks: {len(high_priority)}")
    
    # Find unassigned tasks
    filters = [
        CustomFieldFilter("Assignee", FilterOperator.IS_NOT_SET)
    ]
    unassigned = tasks.filter_by_custom_fields(filters)
    print(f"Unassigned tasks: {len(unassigned)}")

# Usage
generate_task_report("123456789")
```

### Example: Workspace Explorer

```python
import clickuphelper as cu

def explore_workspace():
    """Explore and display workspace structure."""
    # Discover teams
    teams = cu.Teams()
    print("Available Workspaces:")
    for team in teams:
        print(f"  - {team['name']} (ID: {team['id']})")
    
    # Get first team
    team_id = teams.get_team_ids()[0]
    team_name = teams.get_team_names()[0]
    print(f"\nExploring workspace: {team_name}")
    
    # Get all lists
    all_lists = cu.get_all_lists(team_id)
    print(f"\nTotal lists: {len(all_lists)}")
    
    # Group by space
    spaces = {}
    for list_item in all_lists:
        space_name = list_item['space_name']
        if space_name not in spaces:
            spaces[space_name] = []
        spaces[space_name].append(list_item)
    
    # Display structure
    for space_name, lists in spaces.items():
        print(f"\nSpace: {space_name}")
        for list_item in lists:
            location = f"Folder: {list_item['folder_name']}" if list_item['folder_id'] else "Direct"
            print(f"  - {list_item['name']} ({location})")
            
            # Get task count
            count = cu.get_task_count(list_item['id'])
            print(f"    Tasks: {count}")

# Usage
explore_workspace()
```

### Example: Tag-Based Task Migration

```python
import clickuphelper as cu

def migrate_tagged_tasks(source_list_id, target_list_id, tag_name):
    """
    Find tasks with a specific tag and create copies in another list.
    """
    # Get tasks with the tag
    source_tasks = cu.Tasks(source_list_id)
    tagged_tasks = source_tasks.filter_by_tag(tag_name)
    
    print(f"Found {len(tagged_tasks)} tasks with tag '{tag_name}'")
    
    # Get target list to understand custom fields
    target_list = cu.List(target_list_id)
    
    for task_id, task in tagged_tasks.items():
        print(f"Migrating: {task.name}")
        
        # Extract custom fields that exist in target list
        custom_fields = {}
        for field_name in target_list.get_field_names():
            try:
                value = task.get_field(field_name)
                custom_fields[field_name] = value
            except (cu.MissingCustomField, cu.MissingCustomFieldValue):
                pass
        
        # Create task in target list
        try:
            response = cu.post_task(
                target_list_id,
                task.name,
                task_description=task.task.get('description', ''),
                status=task.status,
                custom_fields=custom_fields
            )
            print(f"  ✓ Created task in target list")
        except Exception as e:
            print(f"  ✗ Error: {e}")

# Usage
# migrate_tagged_tasks("source_list_id", "target_list_id", "migrate")
```

---

## Quick Reference

### Common Imports

```python
import clickuphelper as cu
from clickuphelper import FilterOperator, CustomFieldFilter
```

### Common Patterns

```python
# Get workspace info
teams = cu.Teams()
team_id = teams["My Workspace"]

# Get all lists
all_lists = cu.get_all_lists(team_id)

# Get tasks from a list
tasks = cu.Tasks(list_id)

# Filter by tag
tagged = tasks.filter_by_tag("urgent")

# Filter by status
active = tasks.filter_by_statuses(["In Progress", "In Review"])

# Filter by custom field
filters = [CustomFieldFilter("Priority", FilterOperator.EQUALS, "High")]
high_priority = tasks.filter_by_custom_fields(filters)

# Get task count
count = tasks.get_count()

# Get tasks with subtasks
result = tasks.get_tasks_with_subtasks(tag_filter="sprint-23")

# Get single task with subtasks
task = cu.Task(task_id, include_subtasks=True)
filtered_subtasks = task.get_filtered_subtasks(filters)
```

---

## Version History

### 0.4.0 (Current)
- Added Teams class for workspace discovery
- Added get_all_lists() for unified list retrieval
- Added tag management (get_space_tags, create_space_tag)
- Added task filtering by tags (filter_by_tag)
- Added task filtering by status (filter_by_statuses)
- Added advanced custom field filtering with FilterOperator and CustomFieldFilter
- Added task count functionality (get_count, get_task_count)
- Added subtask retrieval and filtering
- Added module capabilities introspection (get_capabilities, print_capabilities)
- Added __version__ module variable

### 0.3.6 (Previous)
- Base functionality for Task, Tasks, List, Spaces, Folders, etc.

---

## Support and Resources

### Environment Setup

```bash
# Set required environment variables
export CLICKUP_API_KEY="your_api_key_here"
export CLICKUP_TEAM_ID="your_team_id_here"  # Optional with Teams class
```

### Getting Your API Key

1. Log in to ClickUp
2. Go to Settings → Apps
3. Click "Generate" under API Token
4. Copy your API key

### Module Capabilities

To see all available features:

```python
import clickuphelper as cu
cu.print_capabilities()
```

---

**End of Documentation**
