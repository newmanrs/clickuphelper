#!/usr/bin/env python3
"""
ClickUp Helper Task Batch Processor

A utility script for processing multiple ClickUp tasks using custom algorithms.
Imports clickuphelper as 'ch' and accepts a list of task IDs for batch processing.

Usage:
    python -m clickuphelper.task_batch_processor --task-ids "123456,789012,345678"

    or

    python task_batch_processor.py --task-ids "123456,789012,345678"
"""

import sys
import os
import json

# Add the parent directory to the path so we can import clickuphelper
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import clickuphelper as ch



def main():
    main_task_ids = [
        "868fqfdpt",
        "868fp8gwp",
        "868ftczk2",
        "868fw2f84",
        "868fxpnm5",
        "868fytqdf",
        "868fqb263"
    ]

    qf_task_ids = [
        "868fypdcb",
        "868fyt5xc",
        "868fytqu8",
        "868fyte58",
        "868fyt9ra",
        "868fytxz0",
        "868fz9hpy"
    ]

    main_tasks_map = {}
    for t_id  in main_task_ids:
        try:
            main_tasks_map[t_id] = ch.Task(t_id)
        except Exception as e:
            print(f"Error creating main task {t_id}: {e}")
            main_tasks_map[t_id] = None

    qf_tasks_map = {}
    for t_id  in qf_task_ids:
        try:
            qf_tasks_map[t_id] = ch.Task(t_id)
        except Exception as e:
            print(f"Error creating QF task {t_id}: {e}")
            qf_tasks_map[t_id] = None

    # Create mapping from child task to parent task
    task_parent_mapping = {}
    for child_id, task_obj in qf_tasks_map.items():
        if task_obj is None:
            continue
        try:
            parent_id = task_obj.task['parent']
            if parent_id in main_task_ids:
                task_parent_mapping[child_id] = parent_id
        except Exception as e:
            print(f"Error accessing parent for QF task {child_id}: {e}")

    print("Task Parent Mapping:")
    print(json.dumps(task_parent_mapping, indent=2))

    ## Iterate over each main task. 
    ## Extract the following custom fields from the main task:
    ## - GUEST
    ## - GUEST_ORGANIZATION
    ## - TASK_URL
    ## - RECORDING_DATE (note, you will need to convert this. it is in ms. Use ch.ts_ms_to_dt)
    ## Then, in the qf task, get the value of the following custom fields:
    ## - TASK_URL
    ##
    ## Print this information out in a JSON format as a list with no nesting.
    ## This list will be used to power an online calendar

    # Initialize list to store calendar event data
    calendar_events = []

    # Iterate over each main task
    for main_task_id, main_task in main_tasks_map.items():
        if main_task is None:
            continue

        # Get required fields from main task using proper field extraction
        try:
            guest = main_task.get_field('GUEST')
        except (ch.MissingCustomField, ch.MissingCustomFieldValue):
            guest = ''

        try:
            guest_organization = main_task.get_field('GUEST_ORGANIZATION')
        except (ch.MissingCustomField, ch.MissingCustomFieldValue):
            guest_organization = ''

        try:
            task_url = main_task.get_field('TASK_URL')
        except (ch.MissingCustomField, ch.MissingCustomFieldValue):
            task_url = ''

        try:
            recording_date_dt = main_task.get_field('RECORDING_DATE')
            # recording_date_dt is already a datetime object from get_field()
            # Convert to ISO format string for JSON serialization
            recording_date = recording_date_dt.isoformat()
        except (ch.MissingCustomField, ch.MissingCustomFieldValue, ValueError, TypeError):
            recording_date = ''

        # Find corresponding qf task ID for this main task
        qf_task_id = None
        for child_id, parent_id in task_parent_mapping.items():
            if parent_id == main_task_id:
                qf_task_id = child_id
                break

        # Get TASK_URL from qf task
        qf_task_url = ''
        if qf_task_id and qf_task_id in qf_tasks_map:
            qf_task = qf_tasks_map[qf_task_id]
            if qf_task:
                try:
                    qf_task_url = qf_task.get_field('TASK_URL')
                except (ch.MissingCustomField, ch.MissingCustomFieldValue):
                    qf_task_url = ''

        # Create calendar event data
        event_data = {
            'main_task_id': main_task_id,
            'guest': guest,
            'guest_organization': guest_organization,
            'biography_url': task_url,
            'recording_date': recording_date,
            'question_form': qf_task_url
        }

        calendar_events.append(event_data)

    # Print the calendar events as JSON
    print("\nCalendar Events Data:")
    print(json.dumps(calendar_events, indent=2))

if __name__ == "__main__":
    main()
