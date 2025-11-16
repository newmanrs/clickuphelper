#!/usr/bin/env python3
"""
Debug script to check what fields are available and their values
"""
import sys
import os

# Add the current directory to the path so we can import clickuphelper
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import clickuphelper as ch

def debug_task_fields():
    """Debug what fields are available in main tasks"""
    main_task_ids = [
        "868fqfdpt",
        "868fp8gwp",
        "868ftczk2",
        "868fw2f84",
        "868fxpnm5",
        "868fytqdf",
        "868fqb263"
    ]

    for task_id in main_task_ids:
        try:
            print(f"\n=== Task: {task_id} ===")
            task = ch.Task(task_id)
            print(f"Task name: {task.name}")

            # Get all available custom fields
            field_names = list(task.get_field_names())
            print(f"Available fields: {field_names}")

            # Check each field that might contain URLs
            url_fields = ['TASK_URL', 'BIOGRAPHY_URL', 'LINKEDIN', 'WEBSITE', 'URL']

            for field_name in url_fields:
                if field_name in field_names:
                    try:
                        value = task.get_field(field_name)
                        print(f"{field_name}: {value}")
                    except Exception as e:
                        print(f"{field_name}: ERROR - {e}")
                else:
                    print(f"{field_name}: NOT FOUND")

        except Exception as e:
            print(f"Error accessing task {task_id}: {e}")

if __name__ == "__main__":
    debug_task_fields()

