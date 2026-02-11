# Design: Task Archive Feature

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Flask API     │────▶│  Task Storage   │
│                 │◀────│                 │◀────│                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  Archive Store  │
                                                │ data/archive/   │
                                                │   YYYY-MM.json  │
                                                └─────────────────┘
```

## Backend Design

### File Structure
```
data/
├── tasks.json          # Main task list (max 10 completed)
└── archive/
    ├── 2025-01.json    # Archived tasks by month
    ├── 2025-02.json
    └── ...
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/archives` | List all archived tasks |
| GET | `/api/archives?month=YYYY-MM` | List archives for specific month |
| POST | `/api/archives/<task_id>/restore` | Restore task from archive |
| DELETE | `/api/archives/<task_id>` | Permanently delete archived task |

### Archive Logic

```python
def auto_archive():
    """
    Automatically archive oldest completed tasks if count > 10
    Keep only 10 most recent completed tasks
    """
    completed = [t for t in tasks if t['status'] == 'done']
    if len(completed) > 10:
        # Sort by updated_at, oldest first
        completed.sort(key=lambda x: x.get('updated_at', x['created_at']))
        to_archive = completed[:len(completed) - 10]
        for task in to_archive:
            archive_task(task)

def archive_task(task):
    """
    Move task to archive file for current month
    """
    task['archived_at'] = datetime.now().isoformat()
    task['archived_month'] = datetime.now().strftime('%Y-%m')
    # Save to archive file
    # Remove from main tasks
```

## Frontend Design

### UI Components

1. **Archive Button** in toolbar
   - Icon: 📦 or 🗃️
   - Badge showing archive count
   - Click opens archive modal

2. **Archive Modal**
   - Tabbed view by month
   - List of archived tasks
   - Restore button per task
   - Delete button per task

3. **Statistics Update**
   - Show "已完成" as "10+" when there are archived tasks
   - Tooltip showing actual count

### State Management

```javascript
// New state
archives: [],           // Archived tasks (lazy loaded)
showArchives: false,    // Archive modal visibility
archiveStats: {         // Archive statistics
  total: 0,
  byMonth: {}
}
```

## Data Flow

### Auto-archive on status change
1. User moves task to "done"
2. PATCH `/api/tasks/<id>/status` called
3. Server updates task status
4. Server checks completed task count
5. If > 10, archive oldest task(s)
6. Return updated task list (without archived tasks)

### View archives
1. User clicks "View Archives"
2. GET `/api/archives` called
3. Server reads all archive files
4. Return combined list sorted by archive date
5. Frontend displays in modal

### Restore from archive
1. User clicks "Restore" on archived task
2. POST `/api/archives/<id>/restore` called
3. Server moves task from archive to main list
4. Task status set to "todo"
5. Return success
6. Frontend refreshes both lists

## Error Handling

- Archive file corruption: Log error, skip corrupted file
- Restore non-existent task: Return 404
- Archive directory missing: Auto-create on first archive
- Permission errors: Return 500 with descriptive message
