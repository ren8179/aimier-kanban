#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时检查看板任务脚本
每隔2小时检查一次，如果没有进行中的任务，
就从待办任务中取第一个任务放入进行中列表
"""

import sqlite3
import json
import os
import requests
from datetime import datetime

# 配置
DATABASE = '/home/pi/.openclaw/workspace/aimier-kanban/data/kanban.db'
DINGTALK_WEBHOOK = None  # 如果需要钉钉通知，可以配置webhook

def get_db():
    """获取数据库连接"""
    # 添加 timeout=10 等待锁释放，避免数据库锁定错误
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def get_tasks_by_status(status):
    """获取指定状态的任务"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM tasks 
        WHERE status = ? 
        ORDER BY 
            CASE priority 
                WHEN 'high' THEN 1 
                WHEN 'medium' THEN 2 
                WHEN 'low' THEN 3 
            END,
            created_at ASC
    ''', (status,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_task_status(task_id, new_status):
    """更新任务状态"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tasks 
        SET status = ?, updated_at = ? 
        WHERE id = ?
    ''', (new_status, datetime.now().isoformat(), task_id))
    conn.commit()
    conn.close()

def send_dingtalk_message(message):
    """发送钉钉消息通知任琪"""
    try:
        # 使用OpenClaw的gateway发送消息
        # 这里通过HTTP调用OpenClaw的API
        import subprocess
        result = subprocess.run([
            'curl', '-s', '-X', 'POST',
            'http://127.0.0.1:18789/api/message',
            '-H', 'Content-Type: application/json',
            '-H', 'Authorization: Bearer ed82077ce8b976ab3b285d76a87c18ee2a371e4802ac4cbe',
            '-d', json.dumps({
                'channel': 'dingtalk',
                'to': '0703480433656527',
                'message': message
            })
        ], capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"发送钉钉消息失败: {e}")
        return False

def check_and_start_task():
    """检查看板任务并自动开始新任务"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始检查看板任务...")
    
    # 1. 检查是否有进行中的任务
    in_progress_tasks = get_tasks_by_status('in_progress')
    
    if in_progress_tasks:
        print(f"  ✓ 已有 {len(in_progress_tasks)} 个进行中的任务")
        for task in in_progress_tasks:
            print(f"    - [{task['priority']}] {task['title']}")
        print("  → 无需启动新任务")
        return False
    
    # 2. 没有进行中的任务，获取待办任务
    todo_tasks = get_tasks_by_status('todo')
    
    if not todo_tasks:
        print("  ✗ 没有待办任务")
        print("  → 暂无任务可启动")
        
        # 发送通知告知没有任务
        send_dingtalk_message("""📋 **任务看板检查报告**

⏰ 检查时间：{time}

📊 **当前状态：**
• 进行中任务：0个
• 待办任务：0个

💡 **建议：**
看板中没有待办任务了，请添加新任务！

查看看板：http://192.168.1.5:5000""".format(time=datetime.now().strftime('%Y-%m-%d %H:%M')))
        return False
    
    # 3. 获取第一个待办任务（按优先级和创建时间排序）
    first_task = todo_tasks[0]
    
    print(f"  → 找到待办任务: [{first_task['priority']}] {first_task['title']}")
    
    # 4. 更新任务状态为进行中
    update_task_status(first_task['id'], 'in_progress')
    print(f"  ✓ 任务已移至进行中列表")
    
    # 5. 构建任务详情
    task_info = f"""📋 **新任务已自动启动**

⏰ 启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

🎯 **任务信息：**
• 标题：{first_task['title']}
• 优先级：{'🔴 高' if first_task['priority'] == 'high' else '🟡 中' if first_task['priority'] == 'medium' else '🟢 低'}
• 状态：🔄 进行中"""
    
    if first_task.get('description'):
        task_info += f"\n• 描述：{first_task['description'][:100]}{'...' if len(first_task['description']) > 100 else ''}"
    
    if first_task.get('due_date'):
        task_info += f"\n• 截止日期：{first_task['due_date']}"
    
    task_info += f"""

📊 **看板统计：**
• 待办任务：{len(todo_tasks) - 1}个
• 进行中任务：1个

💪 **加油！** 专注完成当前任务！

查看看板：http://192.168.1.5:5000"""
    
    # 6. 发送钉钉通知
    send_dingtalk_message(task_info)
    print(f"  ✓ 钉钉通知已发送")
    
    print(f"  ✓ 任务自动启动完成！")
    return True

if __name__ == '__main__':
    try:
        success = check_and_start_task()
        exit(0 if success else 0)  # 总是返回0，避免cron报错
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
