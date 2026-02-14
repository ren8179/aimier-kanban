#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务完成提醒脚本
检查进行中的任务，如果超过一定时间，发送提醒
"""

import sqlite3
import json
import os
import subprocess
from datetime import datetime, timedelta

# 配置
DATABASE = '/home/pi/.openclaw/workspace/aimier-kanban/data/kanban.db'
REMINDER_INTERVAL_HOURS = 2  # 每2小时提醒一次
TASK_TIMEOUT_HOURS = 4  # 任务进行超过4小时提醒

def get_db():
    """获取数据库连接"""
    # 添加 timeout=10 等待锁释放，避免数据库锁定错误
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def get_in_progress_tasks():
    """获取所有进行中的任务"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM tasks 
        WHERE status = 'in_progress'
        ORDER BY updated_at ASC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def parse_datetime(dt_str):
    """解析ISO格式时间字符串"""
    if not dt_str:
        return None
    try:
        # 处理带微秒的格式
        if '.' in dt_str:
            return datetime.fromisoformat(dt_str)
        return datetime.fromisoformat(dt_str)
    except:
        return None

def format_duration(hours):
    """格式化时间长度"""
    if hours < 1:
        return f"{int(hours * 60)}分钟"
    elif hours < 24:
        return f"{int(hours)}小时{int((hours % 1) * 60)}分钟"
    else:
        days = int(hours / 24)
        remaining_hours = int(hours % 24)
        return f"{days}天{remaining_hours}小时"

def send_dingtalk_message(message):
    """发送钉钉消息"""
    try:
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
        ], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception as e:
        print(f"发送钉钉消息失败: {e}")
        return False

def check_and_remind():
    """检查进行中的任务并发送提醒"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检查进行中任务...")
    
    tasks = get_in_progress_tasks()
    
    if not tasks:
        print("  ✓ 没有进行中的任务")
        return False
    
    now = datetime.now()
    reminders_sent = 0
    
    for task in tasks:
        # 计算任务已进行的时间
        updated_at = parse_datetime(task.get('updated_at'))
        if not updated_at:
            continue
        
        duration_hours = (now - updated_at).total_seconds() / 3600
        
        print(f"  → 任务: {task['title']}")
        print(f"    已进行: {format_duration(duration_hours)}")
        
        # 根据任务进行时长发送不同级别的提醒
        if duration_hours >= 8:
            # 超过8小时，强烈提醒
            message = f"""⏰ **任务进行时间提醒**

🚨 **任务已进行超过8小时！**

📝 **任务信息：**
• 标题：{task['title']}
• 优先级：{'🔴 高' if task['priority'] == 'high' else '🟡 中' if task['priority'] == 'medium' else '🟢 低'}
• 已进行：{format_duration(duration_hours)}
• 开始时间：{updated_at.strftime('%Y-%m-%d %H:%M')}

💡 **建议：**
1. 如果任务已完成，请在看板中标记为"已完成"
2. 如果任务需要更长时间，建议拆分为小任务
3. 如需帮助，可以询问爱弥儿

👉 **操作：** 访问 http://192.168.1.5:5000 更新任务状态"""
            
            send_dingtalk_message(message)
            reminders_sent += 1
            print(f"    ✓ 强烈提醒已发送")
            
        elif duration_hours >= 4:
            # 超过4小时，普通提醒
            message = f"""⏰ **任务进行时间提醒**

📝 **当前任务已进行 {format_duration(duration_hours)}**

📋 **任务详情：**
• 标题：{task['title']}
• 优先级：{'🔴 高' if task['priority'] == 'high' else '🟡 中' if task['priority'] == 'medium' else '🟢 低'}
• 状态：🔄 进行中

💡 **提示：**
如果任务已完成，请及时在看板中更新状态！

👉 **点击更新：** http://192.168.1.5:5000"""
            
            send_dingtalk_message(message)
            reminders_sent += 1
            print(f"    ✓ 提醒已发送")
        else:
            print(f"    ✓ 未达提醒阈值（{format_duration(duration_hours)} < 4小时）")
    
    print(f"  ✓ 检查完成，发送了 {reminders_sent} 条提醒")
    return reminders_sent > 0

if __name__ == '__main__':
    try:
        check_and_remind()
        exit(0)
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
