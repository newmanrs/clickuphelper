# ClickUp Task Batch Processor

A utility script for processing multiple ClickUp tasks using custom algorithms. This tool imports `clickuphelper` as `ch` and accepts a list of task IDs for batch processing.

## Quick Start

### Basic Usage

```bash
# Process tasks with comma-separated IDs
python -m clickuphelper.task_batch_processor --task-ids "123456,789012,345678"

# With verbose output
python -m clickuphelper.task_batch_processor --task-ids "123456,789012" --verbose

# JSON output format
python -m clickuphelper.task_batch_processor --task-ids "123456,789012" --format json
```

### Alternative execution methods

```bash
# Run directly if in the clickuphelper directory
python clickuphelper/task_batch_processor.py --task-ids "123456,789012"

# Run the example custom processor
python clickuphelper/example_custom_processor.py
```

## How It Works

The utility consists of two main components:

1. **`TaskBatchProcessor`** - Base class that handles task loading and provides a framework for custom algorithms
2. **`CustomTaskProcessor`** - Example implementation showing how to extend the base class

## Implementing Your Algorithm

### Step 1: Extend the Base Class

Create a new file (e.g., `my_processor.py`) and extend `TaskBatchProcessor`:

```python
import sys
import os
from typing import Dict, Any, List

# Add the parent directory to the path so we can import clickuphelper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import clickuphelper as ch
from task_batch_processor import TaskBatchProcessor

class MyCustomProcessor(TaskBatchProcessor):
    """
    Your custom task processor implementation.
    """

    def __init__(self, task_ids: List[str], custom_param: str = "default", verbose: bool = False):
        """
        Initialize with your custom parameters.

        Args:
            task_ids: List of ClickUp task IDs to process
            custom_param: Your custom parameter for the algorithm
            verbose: Whether to print detailed information during processing
        """
        super().__init__(task_ids, verbose)
        self.custom_param = custom_param

    def process_tasks(self) -> Dict[str, Any]:
        """
        Implement your custom algorithm here.

        This method is called for each batch of tasks and should contain
        your specific business logic for processing the tasks.
        """
        results = {
            "processed_tasks": len(self.tasks),
            "task_results": {},
            "summary": {},
            "algorithm_parameters": {
                "custom_param": self.custom_param
            }
        }

        # YOUR ALGORITHM GOES HERE
        for task_id, task in self.tasks.items():
            try:
                # Example: Get task information
                task_name = task.name
                task_status = task.status

                # Example: Access custom fields
                try:
                    priority = task.get_field("Priority")
                except (ch.MissingCustomField, ch.MissingCustomFieldValue):
                    priority = "Not Set"

                # YOUR CUSTOM LOGIC HERE
                # - Filter tasks based on criteria
                # - Update task fields
                # - Add comments
                # - Change status
                # - Create subtasks
                # - etc.

                # Example: Update task status based on priority
                if priority == "High" and task_status == "Open":
                    task.post_status("In Progress")
                    action_taken = "Changed status to In Progress"
                else:
                    action_taken = "No action needed"

                task_result = {
                    "id": task.id,
                    "name": task_name,
                    "priority": priority,
                    "status": task_status,
                    "processed": True,
                    "action_taken": action_taken
                }

                results["task_results"][task_id] = task_result

            except Exception as e:
                results["task_results"][task_id] = {
                    "id": task_id,
                    "error": str(e),
                    "processed": False
                }
                if self.verbose:
                    print(f"Error processing task {task_id}: {e}")

        results["summary"] = self._generate_summary(results["task_results"])
        return results

    def _generate_summary(self, task_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of your algorithm results.

        Args:
            task_results: Dictionary of task processing results

        Returns:
            Summary statistics specific to your algorithm
        """
        summary = {
            "total_tasks": len(task_results),
            "processed_tasks": 0,
            "failed_tasks": 0,
            "high_priority_tasks": 0,
            "status_changes": 0
        }

        for task_id, result in task_results.items():
            if "error" in result:
                summary["failed_tasks"] += 1
            else:
                summary["processed_tasks"] += 1
                if result.get("priority") == "High":
                    summary["high_priority_tasks"] += 1
                if "status to In Progress" in result.get("action_taken", ""):
                    summary["status_changes"] += 1

        return summary
```

### Step 2: Use Your Custom Processor

```python
def main():
    # Your task IDs
    task_ids = ["12345678", "87654321", "11223344"]

    # Create and run your custom processor
    processor = MyCustomProcessor(
        task_ids=task_ids,
        custom_param="your_value",
        verbose=True
    )

    results = processor.process_tasks()
    processor.print_results(results, format="json")

if __name__ == "__main__":
    main()
```

## Available Task Operations

The `ch.Task` object provides many operations you can use in your algorithm:

### Read Task Information
```python
# Basic info
task.name           # Task name
task.status         # Task status
task.creator        # Who created the task
task.created        # Creation date
task.updated        # Last update date

# Custom fields
field_names = task.get_field_names()  # List all custom field names
priority = task.get_field("Priority")  # Get specific field value
field_id = task.get_field_id("Priority")  # Get field ID
field_type = task.get_field_type("Priority")  # Get field type

# Direct field access (same as get_field)
priority = task["Priority"]
```

### Modify Tasks
```python
# Post comments
task.post_comment("Your comment here", notify_all=False)

# Update custom fields
task.post_custom_field("Priority", "High")

# Change status
task.post_status("In Progress")

# Add tags
task.add_tags(["tag1", "tag2"])

# Add attachments
task.add_attachment("/path/to/file.pdf")
```

### Error Handling
```python
try:
    priority = task.get_field("Priority")
except ch.MissingCustomField:
    print("Priority field doesn't exist")
except ch.MissingCustomFieldValue:
    print("Priority field exists but has no value")
```

## Command Line Options

- `--task-ids`: Comma-separated list of task IDs (required)
- `--verbose`, `-v`: Enable verbose output
- `--format`: Output format (`text`, `json`, `summary`)

## Example Output Formats

### Text Format (Default)
```
=== Task Batch Processing Results ===
Processed 3 tasks

=== Task Details ===

Task ID: 12345678
  Name: Example Task 1
  Status: Open
  Creator: john.doe
  Created: 2023-10-01T10:30:00
  Updated: 2023-10-05T14:20:00
  Custom Fields:
    Priority: High
    Department: Engineering

=== Summary ===
Total tasks: 3
Tasks with custom fields: 3
Total custom fields: 6

Status breakdown:
  Open: 2
  In Progress: 1

Creator breakdown:
  john.doe: 2
  jane.smith: 1
```

### JSON Format
```json
{
  "processed_tasks": 3,
  "task_results": {
    "12345678": {
      "id": "12345678",
      "name": "Example Task 1",
      "status": "Open",
      "creator": "john.doe",
      "created": "2023-10-01T10:30:00",
      "updated": "2023-10-05T14:20:00",
      "custom_fields": {
        "Priority": "High",
        "Department": "Engineering"
      }
    }
  },
  "summary": {
    "total_tasks": 3,
    "statuses": {
      "Open": 2,
      "In Progress": 1
    },
    "creators": {
      "john.doe": 2,
      "jane.smith": 1
    },
    "tasks_with_custom_fields": 3,
    "total_custom_fields": 6
  }
}
```

## Integration with Existing ClickUp Tools

You can combine this with existing ClickUp CLI tools:

```bash
# Get task IDs from a list first
clickuplist "My Workspace" "My Folder" "My List" --display task_ids

# Then process those tasks
python -m clickuphelper.task_batch_processor --task-ids "$(clickuplist "My Workspace" "My Folder" "My List" --display task_ids | tr '\n' ',')"
```

## Environment Setup

Make sure your ClickUp API credentials are set in environment variables:

```bash
export CLICKUP_API_KEY="your_api_key_here"
export CLICKUP_TEAM_ID="your_team_id_here"
```

## Troubleshooting

### Common Issues

1. **"No module named 'clickuphelper'"**: Make sure you're running from the correct directory or use the full module path.

2. **"Error loading task"**: Check that task IDs are valid and you have permission to access them.

3. **"Missing custom field"**: Verify the custom field name exists in your ClickUp workspace.

4. **API rate limits**: The ClickUp API has rate limits. Add delays if processing many tasks.

### Debug Mode

Use the `--verbose` flag to see detailed information about what's happening during processing.

## Contributing

When implementing your algorithm:

1. Handle errors gracefully
2. Provide meaningful progress feedback
3. Document your algorithm's purpose and parameters
4. Test with a small set of tasks first
5. Consider API rate limits for large batches
