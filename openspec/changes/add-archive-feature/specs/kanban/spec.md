# Delta for Kanban

## ADDED Requirements

### Requirement: Automatic Task Archiving
The system SHALL automatically archive completed tasks when they exceed 10 items, keeping only the 10 most recent completed tasks in the main view.

#### Scenario: Archive trigger on status change
- GIVEN there are 10 completed tasks in the main view
- WHEN a task is moved to "done" status
- THEN the oldest completed task is automatically archived
- AND the archived task is moved to the archive storage

#### Scenario: Archive trigger on initial load
- GIVEN there are more than 10 completed tasks in the main data file
- WHEN the system starts or reloads
- THEN the excess completed tasks (oldest first) are automatically archived

### Requirement: Archive Storage
The system SHALL store archived tasks in a separate file structure organized by month.

#### Scenario: Archive file organization
- GIVEN a task is being archived
- WHEN the archive operation occurs
- THEN the task is stored in `data/archive/YYYY-MM.json`
- AND the task retains all its original data plus an `archived_at` timestamp

### Requirement: Lazy Loading of Archives
The system SHALL NOT load archived tasks by default when fetching the task list.

#### Scenario: Default task fetch
- GIVEN there are archived tasks
- WHEN the client requests the task list
- THEN only non-archived tasks are returned
- AND archived tasks are excluded from the response

### Requirement: Archive Viewing
The system SHALL provide an endpoint to view archived tasks on demand.

#### Scenario: View all archives
- GIVEN a user wants to see archived tasks
- WHEN the user clicks "View Archives"
- THEN the system returns all archived tasks
- AND tasks are sorted by archive date (newest first)

#### Scenario: View archives by month
- GIVEN archived tasks exist in multiple months
- WHEN the user filters by a specific month
- THEN only tasks archived in that month are returned

### Requirement: Archive Statistics
The system SHALL provide separate statistics for archived tasks.

#### Scenario: Archive count
- GIVEN there are archived tasks
- WHEN the statistics endpoint is called
- THEN the response includes the total count of archived tasks
- AND the default stats exclude archived tasks

### Requirement: Restore from Archive
The system SHALL allow restoring archived tasks to the main task list.

#### Scenario: Restore archived task
- GIVEN a task is archived
- WHEN the user clicks "Restore" on an archived task
- THEN the task is moved back to the main task list
- AND the task status is set to "todo"

## MODIFIED Requirements

### Requirement: Task Data Structure
The task data structure is extended to include an optional `archived_at` field.

#### New Fields:
- `archived_at`: ISO 8601 timestamp (optional, only present for archived tasks)
- `archived_month`: String in YYYY-MM format (optional, for organization)

### Requirement: Status Update Endpoint
The PATCH `/api/tasks/<id>/status` endpoint now triggers automatic archiving when the condition is met.

#### Modified Behavior:
- After updating task status to "done"
- Check if completed tasks exceed 10
- If yes, archive the oldest completed task(s)
