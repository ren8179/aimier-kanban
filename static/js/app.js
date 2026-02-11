let tasks = [];
let archives = [];
let currentEditingId = null;
let archiveMonths = new Set();

// Load tasks on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    loadStats();
    loadTags();
});

// Load tasks from API
async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        tasks = await response.json();
        renderTasks();
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        document.getElementById('stat-total').textContent = stats.total;
        document.getElementById('stat-todo').textContent = stats.todo;
        document.getElementById('stat-in-progress').textContent = stats.in_progress;
        document.getElementById('stat-done').textContent = stats.done;

        document.getElementById('count-todo').textContent = stats.todo;
        document.getElementById('count-in-progress').textContent = stats.in_progress;
        document.getElementById('count-done').textContent = stats.done;

        // Update archive badge
        const archiveBadge = document.getElementById('archive-count-badge');
        const archivedBadge = document.getElementById('stat-archived-badge');

        if (stats.archived > 0) {
            archiveBadge.textContent = stats.archived;
            archiveBadge.style.display = 'inline';
            archivedBadge.style.display = 'inline';
        } else {
            archiveBadge.style.display = 'none';
            archivedBadge.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load tags from API
async function loadTags() {
    try {
        const response = await fetch('/api/tags');
        const tags = await response.json();
        const select = document.getElementById('tag-filter');

        // Clear existing options except "All Tags"
        while (select.options.length > 1) {
            select.remove(1);
        }

        // Add tag options
        tags.forEach(tag => {
            const option = document.createElement('option');
            option.value = tag;
            option.textContent = tag;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading tags:', error);
    }
}

// Render tasks to columns
function renderTasks(filteredTasks = null) {
    const tasksToRender = filteredTasks || tasks;
    
    const todoList = document.getElementById('todo-list');
    const inProgressList = document.getElementById('in-progress-list');
    const doneList = document.getElementById('done-list');
    
    todoList.innerHTML = '';
    inProgressList.innerHTML = '';
    doneList.innerHTML = '';
    
    const todoTasks = tasksToRender.filter(t => t.status === 'todo');
    const inProgressTasks = tasksToRender.filter(t => t.status === 'in_progress');
    const doneTasks = tasksToRender.filter(t => t.status === 'done');
    
    todoTasks.forEach(task => todoList.appendChild(createTaskCard(task)));
    inProgressTasks.forEach(task => inProgressList.appendChild(createTaskCard(task)));
    doneTasks.forEach(task => doneList.appendChild(createTaskCard(task)));
    
    // Add empty state if no tasks
    if (todoTasks.length === 0) todoList.appendChild(createEmptyState('暂无待办任务'));
    if (inProgressTasks.length === 0) inProgressList.appendChild(createEmptyState('暂无进行中任务'));
    if (doneTasks.length === 0) doneList.appendChild(createEmptyState('暂无已完成任务'));
}

// Create task card element
function createTaskCard(task) {
    const card = document.createElement('div');
    card.className = `task-card priority-${task.priority}`;
    card.draggable = true;
    card.dataset.id = task.id;

    const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString('zh-CN') : '';
    const tagsHtml = task.tags && task.tags.length > 0
        ? `<div class="task-tags">${task.tags.map(tag => `<span class="tag-badge">${escapeHtml(tag)}</span>`).join('')}</div>`
        : '';

    card.innerHTML = `
        <div class="task-header">
            <div class="task-title">${escapeHtml(task.title)}</div>
            <div class="task-actions">
                <button onclick="editTask('${task.id}')" title="编辑">✏️</button>
                <button onclick="deleteTask('${task.id}')" title="删除">🗑️</button>
            </div>
        </div>
        ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
        ${tagsHtml}
        <div class="task-meta">
            <span class="priority-badge">${getPriorityLabel(task.priority)}</span>
            ${dueDate ? `<span class="task-date">📅 ${dueDate}</span>` : ''}
        </div>
    `;

    card.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', task.id);
        card.classList.add('dragging');
    });

    card.addEventListener('dragend', () => {
        card.classList.remove('dragging');
    });

    return card;
}

// Create empty state element
function createEmptyState(message) {
    const div = document.createElement('div');
    div.className = 'empty-state';
    div.innerHTML = `
        <div class="empty-state-icon">📭</div>
        <div class="empty-state-text">${message}</div>
    `;
    return div;
}

// Drag and drop handlers
function allowDrop(e) {
    e.preventDefault();
    const list = e.currentTarget;
    list.classList.add('drag-over');
}

function drop(e, status) {
    e.preventDefault();
    const list = e.currentTarget;
    list.classList.remove('drag-over');
    
    const taskId = e.dataTransfer.getData('text/plain');
    updateTaskStatus(taskId, status);
}

// Remove drag-over class when leaving
['todo-list', 'in-progress-list', 'done-list'].forEach(id => {
    const list = document.getElementById(id);
    if (list) {
        list.addEventListener('dragleave', () => {
            list.classList.remove('drag-over');
        });
    }
});

// Update task status
async function updateTaskStatus(taskId, status) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });

        if (response.ok) {
            await loadTasks();
            await loadStats();
        }
    } catch (error) {
        console.error('Error updating task status:', error);
    }
}

// Modal functions
function openModal(taskId = null) {
    const modal = document.getElementById('task-modal');
    const title = document.getElementById('modal-title');
    const form = document.getElementById('task-form');
    
    if (taskId) {
        const task = tasks.find(t => t.id === taskId);
        if (task) {
            title.textContent = '编辑任务';
            document.getElementById('task-id').value = task.id;
            document.getElementById('task-title').value = task.title;
            document.getElementById('task-description').value = task.description || '';
            document.getElementById('task-priority').value = task.priority;
            document.getElementById('task-due-date').value = task.due_date || '';
            document.getElementById('task-tags').value = task.tags ? task.tags.join(', ') : '';
            currentEditingId = taskId;
        }
    } else {
        title.textContent = '新建任务';
        form.reset();
        document.getElementById('task-id').value = '';
        currentEditingId = null;
    }
    
    modal.classList.add('active');
}

function closeModal() {
    const modal = document.getElementById('task-modal');
    modal.classList.remove('active');
    currentEditingId = null;
}

// Close modal on outside click
window.onclick = function(e) {
    const modal = document.getElementById('task-modal');
    const archiveModal = document.getElementById('archive-modal');
    if (e.target === modal) {
        closeModal();
    }
    if (e.target === archiveModal) {
        closeArchiveModal();
    }
}

// Save task
async function saveTask(e) {
    e.preventDefault();
    
    const taskData = {
        title: document.getElementById('task-title').value,
        description: document.getElementById('task-description').value,
        priority: document.getElementById('task-priority').value,
        due_date: document.getElementById('task-due-date').value,
        tags: document.getElementById('task-tags').value
            .split(',')
            .map(t => t.trim())
            .filter(t => t.length > 0)
    };
    
    try {
        let response;
        if (currentEditingId) {
            response = await fetch(`/api/tasks/${currentEditingId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            });
        } else {
            taskData.status = 'todo';
            response = await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            });
        }
        
        if (response.ok) {
            closeModal();
            await loadTasks();
            await loadStats();
            await loadTags();
        }
    } catch (error) {
        console.error('Error saving task:', error);
    }
}

// Edit task
function editTask(taskId) {
    openModal(taskId);
}

// Delete task
async function deleteTask(taskId) {
    if (!confirm('确定要删除这个任务吗？')) return;

    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            await loadTasks();
            await loadStats();
            await loadTags();
        }
    } catch (error) {
        console.error('Error deleting task:', error);
    }
}

// Search tasks
function searchTasks() {
    const query = document.getElementById('search-input').value.toLowerCase();
    const priority = document.getElementById('priority-filter').value;
    const tag = document.getElementById('tag-filter').value;

    filterAndRender(query, priority, tag);
}

// Filter tasks
function filterTasks() {
    const query = document.getElementById('search-input').value.toLowerCase();
    const priority = document.getElementById('priority-filter').value;
    const tag = document.getElementById('tag-filter').value;

    filterAndRender(query, priority, tag);
}

// Filter and render
function filterAndRender(query, priority, tag) {
    let filtered = tasks;

    if (query) {
        filtered = filtered.filter(t =>
            t.title.toLowerCase().includes(query) ||
            (t.description && t.description.toLowerCase().includes(query))
        );
    }

    if (priority) {
        filtered = filtered.filter(t => t.priority === priority);
    }

    if (tag) {
        filtered = filtered.filter(t => t.tags && t.tags.includes(tag));
    }

    renderTasks(filtered);
}

// Archive Modal Functions
function openArchiveModal() {
    const modal = document.getElementById('archive-modal');
    modal.classList.add('active');
    loadArchives();
}

function closeArchiveModal() {
    const modal = document.getElementById('archive-modal');
    modal.classList.remove('active');
}

// Load archives from API
async function loadArchives() {
    try {
        const response = await fetch('/api/archives');
        archives = await response.json();
        
        // Extract unique months
        archiveMonths = new Set();
        archives.forEach(archive => {
            if (archive.archived_month) {
                archiveMonths.add(archive.archived_month);
            }
        });
        
        updateArchiveMonthFilter();
        renderArchives();
    } catch (error) {
        console.error('Error loading archives:', error);
    }
}

// Update month filter dropdown
function updateArchiveMonthFilter() {
    const select = document.getElementById('archive-month-filter');
    const currentValue = select.value;
    
    // Clear existing options except "All Months"
    while (select.options.length > 1) {
        select.remove(1);
    }
    
    // Add month options sorted descending
    const sortedMonths = Array.from(archiveMonths).sort().reverse();
    sortedMonths.forEach(month => {
        const option = document.createElement('option');
        option.value = month;
        option.textContent = formatMonth(month);
        select.appendChild(option);
    });
    
    // Restore selected value if still valid
    if (currentValue && archiveMonths.has(currentValue)) {
        select.value = currentValue;
    }
}

// Format month for display
function formatMonth(monthStr) {
    const [year, month] = monthStr.split('-');
    return `${year}年${month}月`;
}

// Render archived tasks
function renderArchives(filteredArchives = null) {
    const list = document.getElementById('archive-list');
    const archivesToRender = filteredArchives || archives;
    
    list.innerHTML = '';
    
    if (archivesToRender.length === 0) {
        list.appendChild(createEmptyState('暂无归档任务'));
        return;
    }
    
    archivesToRender.forEach(archive => {
        list.appendChild(createArchiveCard(archive));
    });
}

// Create archive card element
function createArchiveCard(archive) {
    const card = document.createElement('div');
    card.className = `archive-card priority-${archive.priority}`;
    card.dataset.id = archive.id;
    
    const dueDate = archive.due_date ? new Date(archive.due_date).toLocaleDateString('zh-CN') : '';
    const archivedDate = archive.archived_at ? new Date(archive.archived_at).toLocaleDateString('zh-CN') : '';
    
    card.innerHTML = `
        <div class="archive-header">
            <div class="archive-title">${escapeHtml(archive.title)}</div>
            <div class="archive-actions">
                <button onclick="restoreTask('${archive.id}')" title="恢复到任务列表">↩️ 恢复</button>
                <button onclick="deleteArchivedTask('${archive.id}')" title="永久删除">🗑️ 删除</button>
            </div>
        </div>
        ${archive.description ? `<div class="archive-description">${escapeHtml(archive.description)}</div>` : ''}
        <div class="archive-meta">
            <span class="priority-badge">${getPriorityLabel(archive.priority)}</span>
            ${dueDate ? `<span class="archive-date">📅 ${dueDate}</span>` : ''}
            <span class="archived-at">📦 归档于 ${archivedDate}</span>
        </div>
    `;
    
    return card;
}

// Filter archives by month
function filterArchives() {
    const month = document.getElementById('archive-month-filter').value;
    
    if (month) {
        const filtered = archives.filter(a => a.archived_month === month);
        renderArchives(filtered);
    } else {
        renderArchives();
    }
}

// Restore task from archive
async function restoreTask(taskId) {
    try {
        const response = await fetch(`/api/archives/${taskId}/restore`, {
            method: 'POST'
        });
        
        if (response.ok) {
            // Remove from archives list
            archives = archives.filter(a => a.id !== taskId);
            renderArchives();
            
            // Refresh main tasks and stats
            await loadTasks();
            await loadStats();
            
            alert('任务已恢复到任务列表');
        }
    } catch (error) {
        console.error('Error restoring task:', error);
        alert('恢复任务失败');
    }
}

// Delete archived task permanently
async function deleteArchivedTask(taskId) {
    if (!confirm('确定要永久删除这个归档任务吗？此操作无法撤销。')) return;
    
    try {
        const response = await fetch(`/api/archives/${taskId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // Remove from archives list
            archives = archives.filter(a => a.id !== taskId);
            renderArchives();
            await loadStats();
            
            alert('归档任务已永久删除');
        }
    } catch (error) {
        console.error('Error deleting archived task:', error);
        alert('删除归档任务失败');
    }
}

// Helper functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getPriorityLabel(priority) {
    const labels = {
        high: '🔴 高',
        medium: '🟡 中',
        low: '🟢 低'
    };
    return labels[priority] || priority;
}
