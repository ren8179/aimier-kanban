import sqlite3
import json
import os
from datetime import datetime

DATABASE = 'data/kanban.db'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库，创建表结构"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建 tasks 表
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
    
    # 创建 archives 表
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
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_archives_month ON archives(archived_month)')
    
    conn.commit()
    conn.close()
    print("[DONE] 任务1.1-1.4: 数据库初始化完成")

def migrate_json_to_sqlite():
    """将 JSON 数据迁移到 SQLite"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 迁移 tasks.json
    tasks_file = 'data/tasks.json'
    if os.path.exists(tasks_file):
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        for task in tasks:
            cursor.execute('''
                INSERT OR REPLACE INTO tasks 
                (id, title, description, status, priority, due_date, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.get('id'),
                task.get('title', ''),
                task.get('description', ''),
                task.get('status', 'todo'),
                task.get('priority', 'medium'),
                task.get('due_date', ''),
                json.dumps(task.get('tags', [])) if task.get('tags') else '[]',
                task.get('created_at', datetime.now().isoformat()),
                task.get('updated_at', datetime.now().isoformat())
            ))
        
        print(f"[DONE] 任务2.1-2.2: 迁移了 {len(tasks)} 个任务")
    
    # 迁移归档文件
    archive_dir = 'data/archive'
    if os.path.exists(archive_dir):
        total_archived = 0
        for filename in os.listdir(archive_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(archive_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    archives = json.load(f)
                
                for task in archives:
                    cursor.execute('''
                        INSERT OR REPLACE INTO archives 
                        (id, title, description, status, priority, due_date, tags, 
                         created_at, updated_at, archived_at, archived_month)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        task.get('id'),
                        task.get('title', ''),
                        task.get('description', ''),
                        task.get('status', 'done'),
                        task.get('priority', 'medium'),
                        task.get('due_date', ''),
                        json.dumps(task.get('tags', [])) if task.get('tags') else '[]',
                        task.get('created_at', datetime.now().isoformat()),
                        task.get('updated_at', datetime.now().isoformat()),
                        task.get('archived_at', datetime.now().isoformat()),
                        task.get('archived_month', datetime.now().strftime('%Y-%m'))
                    ))
                    total_archived += 1
        
        print(f"[DONE] 任务2.3-2.4: 迁移了 {total_archived} 个归档任务")
    
    conn.commit()
    conn.close()
    
    # 备份原文件
    import shutil
    backup_dir = 'data/backup'
    os.makedirs(backup_dir, exist_ok=True)

    if os.path.exists(tasks_file):
        backup_tasks = os.path.join(backup_dir, 'tasks.json.bak')
        if os.path.exists(backup_tasks):
            os.remove(backup_tasks)
        shutil.move(tasks_file, backup_tasks)

    if os.path.exists(archive_dir):
        backup_archive = os.path.join(backup_dir, 'archive')
        if os.path.exists(backup_archive):
            shutil.rmtree(backup_archive)
        shutil.move(archive_dir, backup_archive)

    print("[DONE] 任务2.4: JSON文件已备份")
    print("[ALL DONE] 数据迁移完成")

if __name__ == '__main__':
    print("开始初始化数据库...")
    init_db()
    print("\n开始迁移数据...")
    migrate_json_to_sqlite()
    print("\n数据库迁移完成！")
