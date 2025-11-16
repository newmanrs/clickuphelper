# Requirements Document

## Introduction

This document specifies the requirements for enhancing the clickuphelper Python module to support comprehensive ClickUp API operations. The enhancements will enable workspace discovery, advanced task filtering, tag management, and unified list retrieval capabilities. These improvements are critical for building a Model Context Protocol (MCP) server that provides full-featured ClickUp integration.

## Glossary

- **ClickUp Helper**: A Python module that provides classes and functions to interact with the ClickUp API
- **Workspace**: A ClickUp team or organization container that holds spaces, folders, lists, and tasks
- **Team**: Synonym for workspace in ClickUp API terminology
- **Space**: A top-level organizational unit within a workspace containing folders and lists
- **Folder**: An organizational container within a space that contains lists
- **List**: A container for tasks, can exist directly in a space or within a folder
- **Task**: A work item within a list that can have custom fields, tags, status, and subtasks
- **Subtask**: A child task nested under a parent task
- **Custom Field**: A user-defined field on a task with typed values (number, text, dropdown, date, labels, etc.)
- **Tag**: A label that can be applied to tasks for categorization and filtering
- **API Key**: Authentication credential for accessing the ClickUp API
- **MCP Server**: Model Context Protocol server that exposes ClickUp operations as tools

## Requirements

### Requirement 1: Workspace Discovery

**User Story:** As a developer, I want to discover all workspaces accessible to my API key, so that I can dynamically query ClickUp data without hardcoding team IDs.

#### Acceptance Criteria

1. WHEN the Teams class is instantiated, THE ClickUp Helper SHALL retrieve all workspaces accessible to the configured API key
2. THE ClickUp Helper SHALL provide a method to return a list of workspace IDs
3. THE ClickUp Helper SHALL provide a method to return a list of workspace names
4. THE ClickUp Helper SHALL provide a method to retrieve workspace metadata by workspace ID

### Requirement 2: Unified List Retrieval

**User Story:** As a developer, I want to retrieve all lists across a workspace without navigating the space and folder hierarchy, so that I can efficiently access list data.

#### Acceptance Criteria

1. WHEN a workspace ID is provided, THE ClickUp Helper SHALL retrieve all lists within that workspace
2. THE ClickUp Helper SHALL return list data including list ID, list name, parent space ID, and parent folder ID where applicable
3. THE ClickUp Helper SHALL retrieve lists from both space-level and folder-level locations
4. THE ClickUp Helper SHALL exclude archived lists from the results

### Requirement 3: Tag Discovery

**User Story:** As a developer, I want to retrieve all tags within a space, so that I can discover available tags for filtering and categorization.

#### Acceptance Criteria

1. WHEN a space ID is provided, THE ClickUp Helper SHALL retrieve all tags defined in that space
2. THE ClickUp Helper SHALL return tag data including tag ID and tag name
3. THE ClickUp Helper SHALL handle spaces with no tags without raising exceptions

### Requirement 4: Tag Creation

**User Story:** As a developer, I want to create new tags in a space, so that I can programmatically manage task categorization.

#### Acceptance Criteria

1. WHEN a space ID and tag name are provided, THE ClickUp Helper SHALL create a new tag in the specified space
2. THE ClickUp Helper SHALL return the created tag data including tag ID
3. IF a tag with the same name already exists, THEN THE ClickUp Helper SHALL return an error response from the API

### Requirement 5: Task Filtering by Tag

**User Story:** As a developer, I want to filter tasks by tag name, so that I can retrieve tasks belonging to specific categories.

#### Acceptance Criteria

1. WHEN a tag name is provided to the Tasks class, THE ClickUp Helper SHALL filter tasks to include only those with the specified tag
2. THE ClickUp Helper SHALL support filtering by a single tag name
3. THE ClickUp Helper SHALL return an empty result set when no tasks match the tag filter

### Requirement 6: Task Filtering by Multiple Statuses

**User Story:** As a developer, I want to filter tasks by multiple status values using OR logic, so that I can retrieve tasks in any of several states.

#### Acceptance Criteria

1. WHEN multiple status names are provided to the Tasks class, THE ClickUp Helper SHALL filter tasks to include those matching any of the provided statuses
2. THE ClickUp Helper SHALL apply OR logic when multiple statuses are specified
3. THE ClickUp Helper SHALL return tasks that match at least one of the provided status values

### Requirement 7: Advanced Custom Field Filtering with Text Matching

**User Story:** As a developer, I want to filter tasks by text custom fields using pattern matching, so that I can find tasks with specific text content.

#### Acceptance Criteria

1. WHEN a text custom field filter with a pattern is provided, THE ClickUp Helper SHALL filter tasks where the field value matches the pattern
2. THE ClickUp Helper SHALL support substring matching for text fields
3. THE ClickUp Helper SHALL support case-insensitive text matching
4. THE ClickUp Helper SHALL support regular expression pattern matching for text fields

### Requirement 8: Advanced Custom Field Filtering with Multiselect Fields

**User Story:** As a developer, I want to filter tasks by multiselect custom fields, so that I can find tasks with specific label combinations.

#### Acceptance Criteria

1. WHEN a multiselect custom field filter is provided, THE ClickUp Helper SHALL filter tasks where the field contains any of the specified values
2. THE ClickUp Helper SHALL apply OR logic when multiple values are specified for a multiselect field
3. THE ClickUp Helper SHALL handle tasks where the multiselect field is empty

### Requirement 9: Advanced Custom Field Filtering with Null Checking

**User Story:** As a developer, I want to filter tasks by whether a custom field is set or unset, so that I can find tasks with missing data.

#### Acceptance Criteria

1. WHEN a null check filter is provided for a custom field, THE ClickUp Helper SHALL filter tasks where the field is set or unset based on the filter criteria
2. THE ClickUp Helper SHALL distinguish between fields with null values and fields with empty string values
3. THE ClickUp Helper SHALL support filtering for both "is set" and "is not set" conditions

### Requirement 10: Combined Custom Field Filtering with AND Logic

**User Story:** As a developer, I want to apply multiple custom field filters with AND logic, so that I can find tasks matching all specified criteria.

#### Acceptance Criteria

1. WHEN multiple custom field filters are provided, THE ClickUp Helper SHALL filter tasks to include only those matching all filter criteria
2. THE ClickUp Helper SHALL apply AND logic across different custom field filters
3. THE ClickUp Helper SHALL support combining different filter types in a single query

### Requirement 11: Task Count Retrieval

**User Story:** As a developer, I want to retrieve the count of tasks in a list without fetching all task data, so that I can efficiently check list size.

#### Acceptance Criteria

1. WHEN a list ID is provided, THE ClickUp Helper SHALL return the count of tasks in that list
2. THE ClickUp Helper SHALL retrieve the count without loading full task data
3. THE ClickUp Helper SHALL include or exclude closed tasks based on a parameter

### Requirement 12: Subtask Filtering by Custom Fields

**User Story:** As a developer, I want to filter subtasks of a task by custom field values, so that I can find specific subtasks within a task hierarchy.

#### Acceptance Criteria

1. WHEN custom field filters are provided for a task, THE ClickUp Helper SHALL filter the task's subtasks based on those criteria
2. THE ClickUp Helper SHALL return only subtasks matching all specified custom field filters
3. THE ClickUp Helper SHALL handle tasks with no subtasks without raising exceptions

### Requirement 13: Bulk Task Retrieval with Subtasks

**User Story:** As a developer, I want to retrieve multiple tasks with their subtasks in a single operation, so that I can efficiently load task hierarchies.

#### Acceptance Criteria

1. WHEN the Tasks class is configured to include subtasks, THE ClickUp Helper SHALL retrieve all tasks with their nested subtasks
2. THE ClickUp Helper SHALL return subtasks regardless of whether they match parent task filters
3. THE ClickUp Helper SHALL maintain the parent-child relationship structure in the returned data

### Requirement 14: Filtered Task Retrieval with All Subtasks

**User Story:** As a developer, I want to retrieve filtered parent tasks and include all their subtasks regardless of filter match, so that I can see complete task hierarchies.

#### Acceptance Criteria

1. WHEN parent task filters are applied with subtask inclusion enabled, THE ClickUp Helper SHALL return parent tasks matching the filters
2. THE ClickUp Helper SHALL include all subtasks of matching parent tasks regardless of whether subtasks match the filters
3. THE ClickUp Helper SHALL preserve the complete subtask hierarchy for each matching parent task

### Requirement 15: Task Retrieval by Tag with Subtasks

**User Story:** As a developer, I want to retrieve tasks by tag and include their subtasks, so that I can work with complete tagged task hierarchies.

#### Acceptance Criteria

1. WHEN a tag filter is applied with subtask inclusion enabled, THE ClickUp Helper SHALL return tasks matching the tag
2. THE ClickUp Helper SHALL include all subtasks of tagged tasks regardless of whether subtasks have the tag
3. THE ClickUp Helper SHALL handle tasks with no subtasks without errors

### Requirement 16: Module Version and Capabilities Documentation

**User Story:** As a developer or LLM, I want to query the module version and available capabilities, so that I can understand what functionality is available without reading source code.

#### Acceptance Criteria

1. THE ClickUp Helper SHALL expose a version string accessible via `clickuphelper.__version__`
2. THE ClickUp Helper SHALL provide a `get_capabilities()` function that returns a structured description of available features
3. THE ClickUp Helper SHALL provide a `print_capabilities()` function that outputs a human-readable summary of module capabilities
4. THE ClickUp Helper SHALL include in the capabilities documentation all available classes, their key methods, and available standalone functions
5. THE ClickUp Helper SHALL keep the version string synchronized with the version in setup.py
