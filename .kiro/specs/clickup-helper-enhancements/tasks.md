# Implementation Plan

## Core Infrastructure

- [x] 1. Implement Teams class for workspace discovery
  - Create Teams class with initialization that calls ClickUp API endpoint GET /team
  - Implement get_team_ids() method to return list of team IDs
  - Implement get_team_names() method to return list of team names
  - Implement get_team_by_id() and get_team_by_name() methods
  - Implement __getitem__ and __iter__ magic methods for convenient access
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 2. Implement unified list retrieval function
  - Create get_all_lists() function that accepts team_id parameter
  - Use existing Spaces, Folders, SpaceLists, and FolderLists classes to traverse hierarchy
  - Aggregate lists from both space-level and folder-level locations
  - Return list of dictionaries with id, name, space_id, space_name, folder_id, folder_name
  - Handle archived parameter to include/exclude archived lists
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 3. Implement tag management functions
  - Create get_space_tags() function that calls GET /space/{space_id}/tag
  - Create create_space_tag() function that calls POST /space/{space_id}/tag
  - Handle optional color parameters for tag creation
  - Return tag data including tag ID and name
  - Handle empty tag lists gracefully
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3_

## Task Filtering Enhancements

- [ ] 4. Add tag filtering to Tasks class
  - Implement filter_by_tag() method in Tasks class
  - Support both single tag name (string) and multiple tag names (list)
  - Apply OR logic when multiple tags are provided
  - Filter tasks where task['tags'] contains any of the specified tag names
  - Return dictionary of task_id -> Task object for matching tasks
  - _Requirements: 5.1, 5.2, 5.3, 15.1, 15.2, 15.3_

- [ ] 5. Add status filtering to Tasks class
  - Implement filter_by_statuses() method in Tasks class
  - Accept list of status names as parameter
  - Apply OR logic to match tasks with any of the provided statuses
  - Filter based on task['status']['status'] field
  - Return dictionary of task_id -> Task object for matching tasks
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 6. Implement advanced custom field filtering infrastructure
  - [ ] 6.1 Create FilterOperator enum and CustomFieldFilter class
    - Define FilterOperator enum with all comparison operators (EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN_OR_EQUAL, CONTAINS, STARTS_WITH, REGEX, IN, IS_SET, IS_NOT_SET)
    - Create CustomFieldFilter class with field_name, operator, and value attributes
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 9.1, 9.2, 9.3_
  - [ ] 6.2 Implement filter_by_custom_fields method
    - Add filter_by_custom_fields() method to Tasks class
    - Accept list of CustomFieldFilter objects
    - Implement AND logic across all filters
    - For each task, evaluate all filters using Task.get_field() method
    - Handle MissingCustomFieldValue exceptions for IS_SET/IS_NOT_SET operators
    - Implement operator-specific comparison logic for each FilterOperator type (number comparisons, text matching with CONTAINS/STARTS_WITH/REGEX, multiselect label checking, null checking)
    - Return dictionary of task_id -> Task object for matching tasks
    - _Requirements: 10.1, 10.2, 10.3_

- [ ] 7. Add task count functionality
  - Implement get_count() method in Tasks class that returns len(self.task_ids)
  - Create get_task_count() helper function that instantiates Tasks and returns count
  - Support include_closed parameter
  - _Requirements: 11.1, 11.2, 11.3_

## Subtask Support

- [ ] 8. Enhance Tasks class for subtask retrieval
  - [ ] 8.1 Add include_subtasks parameter to Tasks.__init__()
    - Store include_subtasks as instance variable
    - Pass include_subtasks to Task object creation when iterating tasks
    - _Requirements: 13.1, 13.2, 13.3_
  - [ ] 8.2 Implement get_tasks_with_subtasks method
    - Add get_tasks_with_subtasks() method to Tasks class
    - Accept optional filters, tag_filter, and status_filter parameters
    - Apply filters to parent tasks only
    - For each matching parent task, retrieve with include_subtasks=True
    - Return dictionary with structure: {task_id: {'task': Task, 'subtasks': [Task, ...]}}
    - Include all subtasks regardless of whether they match parent filters
    - _Requirements: 14.1, 14.2, 14.3_

- [ ] 9. Implement subtask filtering in Task class
  - Add get_filtered_subtasks() method to Task class
  - Accept list of CustomFieldFilter objects
  - Verify task was initialized with include_subtasks=True, raise ValueError if not
  - For each subtask, create Task object and evaluate filters
  - Apply AND logic across all filters
  - Return list of subtask dictionaries that match all filters
  - _Requirements: 12.1, 12.2, 12.3_

## Documentation and Versioning

- [ ] 10. Implement module version and capabilities documentation
  - Add __version__ variable at module level (set to "0.4.0")
  - Update setup.py version from "0.3.6" to "0.4.0"
  - Create get_capabilities() function that returns structured dictionary of all classes, methods, and functions
  - Create print_capabilities() function that outputs human-readable capability summary
  - Include documentation for all classes (Task, Tasks, List, Teams, Spaces, Folders, SpaceLists, FolderLists)
  - Include documentation for all functions (get_all_lists, get_space_tags, create_space_tag, get_list_id, get_list_tasks, get_task_count, post_task, display_tree)
  - Document filtering capabilities and supported custom field types
  - Format output to be easily parseable by LLMs
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_
