#!/usr/bin/env python3
"""
Example Custom Task Processor

This example demonstrates how to extend the TaskBatchProcessor class
to implement your own custom algorithms for processing ClickUp tasks.

Replace the algorithm in the process_tasks() method with your specific logic.
"""

import sys
import os
from typing import Dict, Any, List

# Add the parent directory to the path so we can import clickuphelper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import clickuphelper as ch
from task_batch_processor import TaskBatchProcessor


class CustomTaskProcessor(TaskBatchProcessor):
    """
    Example custom processor that demonstrates how to implement your own algorithm.
    """

    def __init__(self, task_ids: List[str], priority_threshold: str = "high", verbose: bool = False):
        """
        Initialize with custom parameters for your algorithm.

        Args:
            task_ids: List of ClickUp task IDs to process
            priority_threshold: Example parameter for filtering tasks by priority
            verbose: Whether to print detailed information during processing
        """
        super().__init__(task_ids, verbose)
        self.priority_threshold = priority_threshold

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
                "priority_threshold": self.priority_threshold
            }
        }

        # EXAMPLE ALGORITHM: Filter tasks by priority and add comments
        # Replace this with your actual algorithm

        for task_id, task in self.tasks.items():
            try:
                # Get task priority (assuming you have a custom field called "Priority")
                try:
                    priority = task.get_field("Priority")
                except (ch.MissingCustomField, ch.MissingCustomFieldValue):
                    priority = "Unknown"

                # Example logic: Process only high priority tasks
                if priority.lower() == self.priority_threshold.lower():
                    task_result = {
                        "id": task.id,
                        "name": task.name,
                        "priority": priority,
                        "status": task.status,
                        "processed": True,
                        "action_taken": f"Added comment for {priority} priority task"
                    }

                    # Example action: Add a comment to the task
                    try:
                        comment_text = f"Automated processing: {priority} priority task reviewed."
                        task.post_comment(comment_text, notify_all=False)
                        if self.verbose:
                            print(f"Added comment to task {task_id}")
                    except Exception as e:
                        task_result["action_taken"] = f"Failed to add comment: {e}"
                        if self.verbose:
                            print(f"Failed to add comment to task {task_id}: {e}")

                else:
                    task_result = {
                        "id": task.id,
                        "name": task.name,
                        "priority": priority,
                        "status": task.status,
                        "processed": False,
                        "reason": f"Priority {priority} below threshold {self.priority_threshold}"
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

        results["summary"] = self._generate_custom_summary(results["task_results"])
        return results

    def _generate_custom_summary(self, task_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary specific to your algorithm.

        Args:
            task_results: Dictionary of task processing results

        Returns:
            Summary statistics specific to your algorithm
        """
        summary = {
            "total_tasks": len(task_results),
            "processed_tasks": 0,
            "skipped_tasks": 0,
            "failed_tasks": 0,
            "priorities_found": {},
            "actions_taken": 0
        }

        for task_id, result in task_results.items():
            if "error" in result:
                summary["failed_tasks"] += 1
            elif result.get("processed", False):
                summary["processed_tasks"] += 1
                if "action_taken" in result:
                    summary["actions_taken"] += 1
            else:
                summary["skipped_tasks"] += 1

            # Count priorities
            priority = result.get("priority", "Unknown")
            summary["priorities_found"][priority] = summary["priorities_found"].get(priority, 0) + 1

        return summary


def example_usage():
    """Example of how to use the custom processor programmatically."""
    # Example task IDs - replace with your actual task IDs
    task_ids = ["12345678", "87654321", "11223344"]

    # Create custom processor with your parameters
    processor = CustomTaskProcessor(
        task_ids=task_ids,
        priority_threshold="high",
        verbose=True
    )

    # Process tasks and get results
    results = processor.process_tasks()

    # Print results in different formats
    print("\n=== JSON Format ===")
    processor.print_results(results, format="json")

    print("\n=== Summary Format ===")
    processor.print_results(results, format="summary")

    return results


if __name__ == "__main__":
    print("Custom Task Processor Example")
    print("=" * 40)

    # Run example usage
    results = example_usage()

    print(f"\nProcessed {results['processed_tasks']} tasks successfully!")
