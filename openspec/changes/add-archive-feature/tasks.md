# Tasks: Task Archive Feature Implementation

## 1. Backend - Archive Infrastructure

- [ ] 1.1 Create archive directory structure (`data/archive/`)
- [ ] 1.2 Add archive helper functions (`load_archives`, `save_archive`, `archive_task`)
- [ ] 1.3 Add `archived_at` and `archived_month` fields to task schema
- [ ] 1.4 Implement `auto_archive()` function to check and archive excess completed tasks

## 2. Backend - API Endpoints

- [ ] 2.1 Create GET `/api/archives` endpoint
  - Support optional `?month=YYYY-MM` filter
  - Return list of archived tasks sorted by `archived_at` desc
- [ ] 2.2 Create POST `/api/archives/<task_id>/restore` endpoint
  - Move task from archive back to main list
  - Set status to "todo"
  - Remove `archived_at` field
- [ ] 2.3 Create DELETE `/api/archives/<task_id>` endpoint
  - Permanently remove task from archive
- [ ] 2.4 Update PATCH `/api/tasks/<task_id>/status` endpoint
  - Call `auto_archive()` after status update to "done"
- [ ] 2.5 Update GET `/api/tasks` endpoint
  - Ensure archived tasks are never returned
- [ ] 2.6 Update GET `/api/stats` endpoint
  - Add `archived` count to statistics

## 3. Frontend - UI Components

- [ ] 3.1 Add "查看归档" button to toolbar
  - Show archive icon (📦)
  - Display badge with archived task count
- [ ] 3.2 Create archive modal component
  - Header with title and close button
  - Month filter dropdown
  - List of archived tasks
- [ ] 3.3 Create archived task card component
  - Show title, description, original completion date
  - Restore button
  - Delete button (with confirmation)
- [ ] 3.4 Update statistics display
  - Show "已完成" count with indicator when archives exist

## 4. Frontend - JavaScript Logic

- [ ] 4.1 Add archive state management
  - `archives` array
  - `showArchives` boolean
  - `archiveStats` object
- [ ] 4.2 Implement `loadArchives()` function
  - Call GET `/api/archives`
  - Update state
- [ ] 4.3 Implement `restoreTask(taskId)` function
  - Call POST `/api/archives/<id>/restore`
  - Refresh both main tasks and archives
- [ ] 4.4 Implement `deleteArchivedTask(taskId)` function
  - Call DELETE `/api/archives/<id>`
  - Confirm before delete
  - Refresh archives list
- [ ] 4.5 Update `updateTaskStatus()` function
  - Handle auto-archive response
  - Refresh task list after status change

## 5. Testing & Validation

- [ ] 5.1 Test auto-archive trigger
  - Create 11 completed tasks
  - Verify oldest is archived automatically
- [ ] 5.2 Test archive viewing
  - Open archive modal
  - Verify archived tasks are displayed
- [ ] 5.3 Test restore functionality
  - Restore archived task
  - Verify it appears in main list with "todo" status
- [ ] 5.4 Test delete functionality
  - Delete archived task
  - Verify it's permanently removed
- [ ] 5.5 Test month filtering
  - Archive tasks in different months
  - Verify filter works correctly

## 6. Documentation

- [ ] 6.1 Update README with archive feature documentation
- [ ] 6.2 Add inline code comments for archive logic
- [ ] 6.3 Update API documentation
