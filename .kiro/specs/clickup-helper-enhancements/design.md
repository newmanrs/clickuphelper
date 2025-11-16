# Design Document: ClickUp Helper Enhancements

## Overview

This design document outlines the architecture and implementation approach for enhancing the clickuphelper Python module. The enhancements add critical functionality for workspace discovery, unified list retrieval, tag management, and advanced task filtering capabilities. The design maintains backward compatibility with existing code while extending the module's capabilities to support comprehensive ClickUp API operations.

## Architecture

### Design Principles

1. **Consistency**: New classes and methods follow the existing patterns established in clickuphelper
2. **Backward Compatibility**: All existing functionality remains unchanged
3. **Lazy Loading**: API calls are made only when data is requested
4. **Error Handling**: Graceful handling of missing data and API errors
5. **Type Flexibility**: Support both string names and IDs where appropriate

### Module Structure

The enhancements will be added to the existing `clickuphelper/__init__.py` file, maintaining the current single-module structure. New classes and functions will be organized alongside existing ones.

## Components and Interfaces

### 1. Teams Class (New)

**Purpose**: Discover and retrieve workspace/team information accessible to the API key.

**API Endpoint**: `GET https://api.clickup.com/api/v2/team`

**Class Interface**:
```python
class Teams:
    def __init__(self):
        """
        Retrieve all teams/workspaces accessible to the API key.
        Stores team data in self.teams list.
        """
        pass
    
    def get_team_ids(self) -> List[str]:
        """Return list of team IDs"""
        pass
    
    def get_team_names(self) -> List[str]:
        """Return list of team names"""
        pass
    
    def get_team_by_id(self, team_id: str) -> dict:
        """Return team metadata by ID"""
        pass
    
    def get_team_by_name(self, team_name: str) -> dict:
        """Return team metadata by name"""
        pass
    
    def __getitem__(self, name: str) -> str:
        """Allow indexing by team name to get team ID"""
        pass
    
    def __iter__(self):
        """Allow iteration over teams"""
        pass
```

**Data Structure**:
- `self.teams`: List of team dictionaries from API response
- `self.team_names`: List of team names
- `self.team_ids`: List of team IDs
- `self.team_lookup`: Dictionary mapping team names to team IDs

**Requirements Addressed**: 1.1, 1.2, 1.3, 1.4

### 2. get_all_lists Function (New)

**Purpose**: Retrieve all lists across a workspace without requiring knowledge of space/folder hierarchy.

**API Endpoints Used**:
- `GET https://api.clickup.com/api/v2/team/{team_id}/space` (get all spaces)
- `GET https://api.clickup.com/api/v2/space/{space_id}/folder` (get folders in each space)
- `GET https://api.clickup.com/api/v2/space/{space_id}/list` (get space-level lists)
- `GET https://api.clickup.com/api/v2/folder/{folder_id}/list` (get folder-level lists)

**Function Interface**:
```python
def get_all_lists(team_id: str, archived: bool = False) -> List[dict]:
    """
    Get all lists in a workspace regardless of space/folder location.
    
    Args:
        team_id: The workspace/team ID
        archived: Whether to include archived lists (default False)
    
    Returns:
        List of dictionaries with structure:
        {
            'id': str,
            'name': str,
            'space_id': str,
            'space_name': str,
            'folder_id': str or None,
            'folder_name': str or None
        }
    """
    pass
```

**Implementation Strategy**:
1. Use existing Spaces class to get all spaces
2. For each space:
   - Use SpaceLists to get lists directly in space
   - Use Folders class to get all folders
   - For each folder, use FolderLists to get lists
3. Aggregate all lists with metadata about their location

**Requirements Addressed**: 2.1, 2.2, 2.3, 2.4

### 3. Tag Management Functions (New)

**Purpose**: Retrieve and create tags within spaces.

**API Endpoints**:
- `GET https://api.clickup.com/api/v2/space/{space_id}/tag`
- `POST https://api.clickup.com/api/v2/space/{space_id}/tag`

**Function Interfaces**:
```python
def get_space_tags(space_id: str) -> List[dict]:
    """
    Get all tags in a space.
    
    Args:
        space_id: The space ID
    
    Returns:
        List of tag dictionaries with 'name' and 'tag' (ID) keys
    """
    pass

def create_space_tag(space_id: str, tag_name: str, tag_fg_color: str = None, tag_bg_color: str = None) -> dict:
    """
    Create a new tag in a space.
    
    Args:
        space_id: The space ID
        tag_name: Name for the new tag
        tag_fg_color: Foreground color hex code (optional)
        tag_bg_color: Background color hex code (optional)
    
    Returns:
        Created tag dictionary from API response
    """
    pass
```

**Requirements Addressed**: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3

### 4. Tasks Class Enhancements

**Purpose**: Add advanced filtering capabilities to the existing Tasks class.

#### 4.1 Tag Filtering

**New Method**:
```python
class Tasks:
    def filter_by_tag(self, tag_names: Union[str, List[str]]) -> dict:
        """
        Filter tasks by tag name(s).
        
        Args:
            tag_names: Single tag name or list of tag names (OR logic)
        
        Returns:
            Dictionary of task_id -> Task object for matching tasks
        """
        pass
```

**Implementation**: Filter tasks where `task['tags']` list contains any of the specified tag names.

**Requirements Addressed**: 5.1, 5.2, 5.3

#### 4.2 Status Filtering

**New Method**:
```python
class Tasks:
    def filter_by_statuses(self, status_names: List[str]) -> dict:
        """
        Filter tasks by multiple status values (OR logic).
        
        Args:
            status_names: List of status names to match
        
        Returns:
            Dictionary of task_id -> Task object for matching tasks
        """
        pass
```

**Implementation**: Filter tasks where `task['status']['status']` matches any of the provided status names.

**Requirements Addressed**: 6.1, 6.2, 6.3

#### 4.3 Advanced Custom Field Filtering

**New Data Structures**:
```python
from enum import Enum
from typing import Union, List, Any, Optional

class FilterOperator(Enum):
    """Comparison operators for custom field filtering"""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    REGEX = "regex"
    IN = "in"
    IS_SET = "is_set"
    IS_NOT_SET = "is_not_set"

class CustomFieldFilter:
    """Represents a single custom field filter"""
    def __init__(
        self,
        field_name: str,
        operator: FilterOperator,
        value: Any = None
    ):
        self.field_name = field_name
        self.operator = operator
        self.value = value
```

**New Method**:
```python
class Tasks:
    def filter_by_custom_fields(self, filters: List[CustomFieldFilter]) -> dict:
        """
        Apply complex custom field filters with AND logic.
        
        Args:
            filters: List of CustomFieldFilter objects
        
        Returns:
            Dictionary of task_id -> Task object for matching tasks
        """
        pass
```

**Implementation Strategy**:
1. For each task, evaluate all filters
2. A task matches only if ALL filters evaluate to True (AND logic)
3. For each filter:
   - Get the custom field value using existing `Task.get_field()` method
   - Apply the operator-specific comparison
   - Handle MissingCustomFieldValue exceptions for IS_SET/IS_NOT_SET operators

**Filter Type Implementations**:
- **Number comparisons**: Use standard Python comparison operators
- **Text matching**: 
  - CONTAINS: Use `in` operator
  - STARTS_WITH: Use `str.startswith()`
  - REGEX: Use `re.match()` or `re.search()`
- **Multiselect (labels)**: Check if any filter value is in the field's value list
- **Null checking**: Catch MissingCustomFieldValue exception

**Requirements Addressed**: 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 9.1, 9.2, 9.3, 10.1, 10.2, 10.3

#### 4.4 Task Count

**New Method**:
```python
class Tasks:
    def get_count(self) -> int:
        """
        Get count of tasks in the list.
        
        Returns:
            Number of tasks
        """
        return len(self.task_ids)
```

**Alternative Function**:
```python
def get_task_count(list_id: str, include_closed: bool = False) -> int:
    """
    Get count of tasks in a list.
    
    Args:
        list_id: The list ID
        include_closed: Whether to include closed tasks
    
    Returns:
        Number of tasks in the list
    """
    tasks = Tasks(list_id, include_closed=include_closed)
    return len(tasks.task_ids)
```

**Requirements Addressed**: 11.1, 11.2, 11.3

#### 4.5 Subtask Retrieval with Filtering

**Enhancement to Tasks Class**:
```python
class Tasks:
    def __init__(self, list_id, include_closed=False, include_subtasks=False):
        """
        Add include_subtasks parameter to retrieve tasks with their subtasks.
        """
        self.include_subtasks = include_subtasks
        # Existing initialization code...
```

**New Method**:
```python
class Tasks:
    def get_tasks_with_subtasks(
        self,
        filters: Optional[List[CustomFieldFilter]] = None,
        tag_filter: Optional[Union[str, List[str]]] = None,
        status_filter: Optional[List[str]] = None
    ) -> dict:
        """
        Get tasks (optionally filtered) with all their subtasks.
        
        Args:
            filters: Optional custom field filters for parent tasks
            tag_filter: Optional tag filter for parent tasks
            status_filter: Optional status filter for parent tasks
        
        Returns:
            Dictionary of task_id -> dict with structure:
            {
                'task': Task object,
                'subtasks': List of Task objects
            }
        """
        pass
```

**Implementation Strategy**:
1. Apply filters to parent tasks only
2. For each matching parent task, retrieve all subtasks using `Task(task_id, include_subtasks=True)`
3. Return structure preserving parent-child relationships

**Requirements Addressed**: 13.1, 13.2, 13.3, 14.1, 14.2, 14.3, 15.1, 15.2, 15.3

### 5. Task Class Enhancements

**Purpose**: Add subtask filtering capability to individual tasks.

**New Method**:
```python
class Task:
    def get_filtered_subtasks(self, filters: List[CustomFieldFilter]) -> List[dict]:
        """
        Get subtasks matching custom field filters.
        
        Args:
            filters: List of CustomFieldFilter objects
        
        Returns:
            List of subtask dictionaries matching all filters
        """
        pass
```

**Implementation Strategy**:
1. Ensure task was initialized with `include_subtasks=True`
2. For each subtask in `self.task['subtasks']`:
   - Create a Task object from the subtask dictionary
   - Evaluate all filters against the subtask
   - Include subtask if all filters match
3. Return list of matching subtask dictionaries

**Requirements Addressed**: 12.1, 12.2, 12.3

## Data Models

### Team Data Model
```python
{
    "id": "string",
    "name": "string",
    "color": "string",
    "avatar": "string",
    "members": [...]
}
```

### List Metadata Model (for get_all_lists)
```python
{
    "id": "string",
    "name": "string",
    "space_id": "string",
    "space_name": "string",
    "folder_id": "string | None",
    "folder_name": "string | None"
}
```

### Tag Data Model
```python
{
    "name": "string",
    "tag_fg": "string",  # Hex color
    "tag_bg": "string",  # Hex color
    "creator": "integer"
}
```

### Task with Subtasks Model
```python
{
    "task": Task,  # Task object
    "subtasks": [Task, ...]  # List of Task objects
}
```

## Error Handling

### API Error Responses
- **401 Unauthorized**: Invalid or expired API key
- **404 Not Found**: Resource (space, list, task) does not exist
- **429 Rate Limit**: Too many requests
- **500 Server Error**: ClickUp API internal error

### Error Handling Strategy
1. **Network Errors**: Allow requests exceptions to propagate
2. **Missing Resources**: Raise KeyError with helpful message listing available options
3. **Missing Custom Fields**: Use existing MissingCustomField and MissingCustomFieldValue exceptions
4. **Empty Results**: Return empty lists/dicts rather than raising exceptions
5. **Invalid Filters**: Raise ValueError with descriptive message

### Specific Error Cases
- **Teams class with no accessible teams**: Return empty lists
- **get_all_lists with invalid team_id**: Allow API error to propagate
- **Tag operations on invalid space_id**: Allow API error to propagate
- **Filtering with non-existent custom field**: Raise MissingCustomField
- **Filtering subtasks when include_subtasks=False**: Raise ValueError with instruction to reinitialize

## Testing Strategy

### Unit Testing Approach
1. **Mock API Responses**: Use unittest.mock to mock requests.get/post calls
2. **Test Data**: Create fixture JSON responses matching ClickUp API structure
3. **Isolation**: Test each class and function independently

### Test Coverage Areas

#### Teams Class Tests
- Test initialization with multiple teams
- Test initialization with no teams
- Test get_team_ids and get_team_names
- Test indexing by name
- Test iteration

#### get_all_lists Function Tests
- Test with workspace containing spaces only
- Test with workspace containing folders
- Test with mixed space-level and folder-level lists
- Test with empty workspace
- Test archived parameter

#### Tag Management Tests
- Test get_space_tags with tags present
- Test get_space_tags with no tags
- Test create_space_tag success
- Test create_space_tag with duplicate name

#### Tasks Filtering Tests
- Test filter_by_tag with single tag
- Test filter_by_tag with multiple tags
- Test filter_by_statuses with multiple statuses
- Test filter_by_custom_fields with each operator type
- Test filter_by_custom_fields with multiple filters (AND logic)
- Test filter_by_custom_fields with missing fields
- Test get_tasks_with_subtasks with and without filters

#### Task Subtask Filtering Tests
- Test get_filtered_subtasks with matching subtasks
- Test get_filtered_subtasks with no matches
- Test get_filtered_subtasks when include_subtasks=False

### Integration Testing
- Test against live ClickUp API with test workspace
- Verify pagination handling in Tasks class
- Verify rate limiting behavior
- Test end-to-end workflows combining multiple operations

### Manual Testing Checklist
- Verify backward compatibility with existing code
- Test with various custom field types
- Test with tasks having no custom fields
- Test with deeply nested subtask hierarchies
- Verify performance with large lists (1000+ tasks)

## Performance Considerations

### API Call Optimization
1. **get_all_lists**: Makes N+1 API calls (1 for spaces, N for folders). Consider caching for repeated calls.
2. **Tasks class**: Already implements pagination efficiently
3. **Filtering**: All filtering happens client-side after fetching tasks. For very large lists, consider using ClickUp API query parameters where available.

### Memory Usage
- **Tasks class**: Loads all tasks into memory. For lists with thousands of tasks, this could be memory-intensive.
- **get_all_lists**: Aggregates all lists across workspace. Should be acceptable for typical workspace sizes.

### Caching Strategy
- No caching implemented in initial version
- Future enhancement: Add optional caching with TTL for Teams, Spaces, and Lists data
- Task data should not be cached due to frequent updates

## Migration and Backward Compatibility

### Backward Compatibility Guarantees
1. All existing classes and functions remain unchanged
2. No changes to existing method signatures
3. No changes to existing return types
4. Existing code will continue to work without modifications

### New Dependencies
- No new external dependencies required
- Uses only existing dependencies: requests, json, datetime, os, operator
- May add typing imports for type hints (Python 3.5+)

### Environment Variables
- Existing: `CLICKUP_API_KEY`, `CLICKUP_TEAM_ID`
- No new environment variables required
- Teams class allows dynamic team discovery, reducing reliance on `CLICKUP_TEAM_ID`

### 6. Module Version and Capabilities Documentation

**Purpose**: Provide programmatic access to module version and capability information for introspection by developers and LLMs.

**Module-Level Variables**:
```python
__version__ = "0.4.0"  # Synchronized with setup.py
```

**Function Interfaces**:
```python
def get_capabilities() -> dict:
    """
    Return structured dictionary of module capabilities.
    
    Returns:
        Dictionary with structure:
        {
            'version': str,
            'classes': {
                'ClassName': {
                    'description': str,
                    'key_methods': [str, ...],
                    'use_cases': [str, ...]
                },
                ...
            },
            'functions': {
                'function_name': {
                    'description': str,
                    'parameters': [str, ...],
                    'returns': str
                },
                ...
            }
        }
    """
    pass

def print_capabilities():
    """
    Print human-readable summary of module capabilities to stdout.
    Useful for quick reference and LLM inspection.
    """
    pass
```

**Capabilities Documentation Content**:

The capabilities documentation will include:

1. **Version Information**: Current module version
2. **Classes**:
   - Task: Single task operations (get fields, post comments, update status, add tags/attachments)
   - Tasks: Bulk task operations (retrieve, filter by custom fields/tags/status, get with subtasks)
   - List: List metadata and custom field schemas
   - Teams: Workspace discovery and metadata
   - Spaces: Space discovery within workspace
   - Folders: Folder discovery within space
   - SpaceLists: Lists directly under a space
   - FolderLists: Lists within a folder
3. **Functions**:
   - get_all_lists(): Unified list retrieval across workspace
   - get_space_tags(): Retrieve tags in a space
   - create_space_tag(): Create new tag in a space
   - get_list_id(): Get list ID from names
   - get_list_tasks(): Get tasks in a list
   - get_task_count(): Count tasks in a list
   - post_task(): Create new task
   - display_tree(): Display workspace hierarchy
4. **Filtering Capabilities**:
   - Custom field filtering with multiple operators
   - Tag filtering with OR logic
   - Status filtering with OR logic
   - Combined filters with AND logic
5. **Custom Field Types Supported**:
   - number, text, short_text, url, date, drop_down, labels, tasks, attachment

**Implementation Notes**:
- Keep capabilities documentation in sync with actual implementation
- Use docstrings as source of truth where possible
- Format output for easy parsing by LLMs
- Include version history notes for major capability additions

**Requirements Addressed**: 16.1, 16.2, 16.3, 16.4, 16.5

## Future Enhancements

### Potential Additions
1. **Async Support**: Add async versions of API calls using aiohttp
2. **Caching Layer**: Implement configurable caching for read operations
3. **Batch Operations**: Support bulk task updates
4. **Webhook Support**: Add webhook handling for real-time updates
5. **Query Parameter Filtering**: Use ClickUp API's native filtering where available
6. **Custom Field Schema Validation**: Validate custom field values against list schema before posting

### API Coverage Gaps
- Time tracking operations (partially implemented)
- User management
- Goal operations
- Doc operations
- Dependency management
- Custom task types
