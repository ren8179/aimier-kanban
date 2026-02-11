from flask import Flask, render_template, jsonify, request
from datetime import datetime
import json
import sqlite3
import os

app = Flask(__name__)

DATABASE = 'data/kanban.db'
MAX_COMPLETED_TASKS = 10

def get_db():
    """获取数据库连接"""
    if not os.path.exists(DATABASE):
        init_db()
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库"""
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL CHECK(status IN ('todo', 'in_progress', 'done')),
            priority TEXT NOT NULL CHECK(priority IN ('low', 'medium', 'high')),
            due_date TEXT,
            tags TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archives (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            due_date TEXT,
            tags TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            archived_at TEXT NOT NULL,
            archived_month TEXT NOT NULL
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_archives_month ON archives(archived_month)')
    
    conn.commit()
    conn.close()

def row_to_dict(row):
    """将数据库行转换为字典"""
    if row is None:
        return None
    result = dict(row)
    # 解析 tags JSON
    if result.get('tags'):
        try:
            result['tags'] = json.loads(result['tags'])
        except:
            result['tags'] = []
    else:
        result['tags'] = []
    return result

# Task operations
def load_tasks():
    """从数据库加载所有任务"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(row) for row in rows]

def save_task(task):
    """保存或更新任务"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO tasks 
        (id, title, description, status, priority, due_date, tags, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        task['id'],
        task['title'],
        task.get('description', ''),
        task['status'],
        task['priority'],
        task.get('due_date', ''),
        json.dumps(task.get('tags', [])),
        task['created_at'],
        task['updated_at']
    ))
    conn.commit()
    conn.close()

def delete_task_db(task_id):
    """从数据库删除任务"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

# Archive operations
def load_archive(month):
    """加载指定月份的归档任务"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM archives WHERE archived_month = ? ORDER BY archived_at DESC', (month,))
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(row) for row in rows]

def load_all_archives():
    """加载所有归档任务"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM archives ORDER BY archived_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(row) for row in rows]

def save_archive(task):
    """保存归档任务"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO archives 
        (id, title, description, status, priority, due_date, tags, 
         created_at, updated_at, archived_at, archived_month)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        task['id'],
        task['title'],
        task.get('description', ''),
        task['status'],
        task['priority'],
        task.get('due_date', ''),
        json.dumps(task.get('tags', [])),
        task['created_at'],
        task['updated_at'],
        task['archived_at'],
        task['archived_month']
    ))
    conn.commit()
    conn.close()

def delete_archive(task_id):
    """删除归档任务"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM archives WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def auto_archive():
    """
    自动归档最旧的任务
    返回归档的任务ID列表
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取已完成任务数量
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'done'")
    count = cursor.fetchone()[0]
    
    if count <= MAX_COMPLETED_TASKS:
        conn.close()
        return []
    
    # 获取需要归档的最旧任务
    to_archive_count = count - MAX_COMPLETED_TASKS
    cursor.execute('''
        SELECT * FROM tasks 
        WHERE status = 'done' 
        ORDER BY updated_at ASC 
        LIMIT ?
    ''', (to_archive_count,))
    
    rows = cursor.fetchall()
    archived_ids = []
    
    for row in rows:
        task = row_to_dict(row)
        # 添加归档信息
        task['archived_at'] = datetime.now().isoformat()
        task['archived_month'] = datetime.now().strftime('%Y-%m')
        
        # 保存到归档表
        save_archive(task)
        archived_ids.append(task['id'])
        
        # 从任务表删除
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task['id'],))
    
    conn.commit()
    conn.close()
    
    return archived_ids

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    
    new_task = {
        'id': str(int(datetime.now().timestamp() * 1000)),
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'status': data.get('status', 'todo'),
        'priority': data.get('priority', 'medium'),
        'due_date': data.get('due_date', ''),
        'tags': data.get('tags', []),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    save_task(new_task)
    return jsonify(new_task), 201

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    tasks = load_tasks()
    
    for task in tasks:
        if task['id'] == task_id:
            task['title'] = data.get('title', task['title'])
            task['description'] = data.get('description', task['description'])
            task['priority'] = data.get('priority', task['priority'])
            task['due_date'] = data.get('due_date', task['due_date'])
            task['tags'] = data.get('tags', task.get('tags', []))
            task['updated_at'] = datetime.now().isoformat()
            save_task(task)
            return jsonify(task)
    
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    delete_task_db(task_id)
    return jsonify({'message': 'Task deleted'})

@app.route('/api/tasks/<task_id>/status', methods=['PATCH'])
def update_status(task_id):
    data = request.json
    tasks = load_tasks()
    
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = data.get('status', task['status'])
            task['updated_at'] = datetime.now().isoformat()
            save_task(task)
            
            # 触发自动归档
            if task['status'] == 'done':
                auto_archive()
            
            return jsonify(task)
    
    return jsonify({'error': 'Task not found'}), 404

# Archive API endpoints
@app.route('/api/archives', methods=['GET'])
def get_archives():
    """获取所有归档任务或按月份筛选"""
    month = request.args.get('month')
    if month:
        archives = load_archive(month)
    else:
        archives = load_all_archives()
    return jsonify(archives)

@app.route('/api/archives/<task_id>/restore', methods=['POST'])
def restore_task(task_id):
    """从归档恢复任务到主列表"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 查找归档任务
    cursor.execute('SELECT * FROM archives WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return jsonify({'error': 'Archived task not found'}), 404
    
    task = row_to_dict(row)
    
    # 移除归档字段，重置状态
    task['status'] = 'todo'
    task['updated_at'] = datetime.now().isoformat()
    
    # 保存到任务表
    save_task(task)
    
    # 从归档表删除
    delete_archive(task_id)
    
    conn.close()
    return jsonify(task)

@app.route('/api/archives/<task_id>', methods=['DELETE'])
def delete_archived_task(task_id):
    """永久删除归档任务"""
    delete_archive(task_id)
    return jsonify({'message': 'Archived task deleted permanently'})

@app.route('/api/stats')
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'todo'")
    todo = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'in_progress'")
    in_progress = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'done'")
    done = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM archives")
    archived = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total': total,
        'todo': todo,
        'in_progress': in_progress,
        'done': done,
        'archived': archived
    })

@app.route('/api/tags', methods=['GET'])
def get_tags():
    """获取所有唯一标签"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT tags FROM tasks WHERE tags IS NOT NULL AND tags != "[]"')
    rows = cursor.fetchall()
    conn.close()
    
    all_tags = set()
    for row in rows:
        try:
            tags = json.loads(row[0])
            all_tags.update(tags)
        except:
            pass
    
    return jsonify(sorted(list(all_tags)))

if __name__ == '__main__':
    # 确保数据库已初始化
    if not os.path.exists(DATABASE):
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
