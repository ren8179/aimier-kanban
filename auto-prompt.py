#!/usr/bin/env python3
"""
自动生成优化提示词 - 组合方案关键组件
"""
import sys
import re

def generate_prompt(change_name):
    # 读取 tasks.md
    tasks_file = f"openspec/changes/{change_name}/tasks.md"
    try:
        with open(tasks_file, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {tasks_file} not found")
        sys.exit(1)
    
    # 解析任务列表
    tasks = []
    current_section = ""
    for line in content.split('\n'):
        if line.startswith('## '):
            current_section = line[3:].strip()
        elif line.strip().startswith('- [ ]'):
            task_desc = line.strip()[6:].strip()
            tasks.append({
                'section': current_section,
                'description': task_desc
            })
    
    task_count = len(tasks)
    
    # 生成任务编号序列
    task_sequence = []
    task_num = 1
    for i, task in enumerate(tasks):
        task_sequence.append(f"{task_num}.{i+1}")
    task_sequence_str = ' → '.join(task_sequence[:6])  # 最多显示6个
    if task_count > 6:
        task_sequence_str += f" → ... ({task_count-6} more)"
    
    # 检测技术栈
    tech_stack = "Python Flask + SQLite3"
    
    # 生成提示词
    prompt = f"""请严格按照 openspec/changes/{change_name}/tasks.md 中的任务清单顺序实现功能。

执行要求（必须遵守）：
1. 按编号顺序完成每个任务（{task_sequence_str}）
2. 每完成一个任务，立即在控制台输出：
   [DONE] 任务X.X: <任务描述>
3. 全部任务完成后，输出：
   [ALL DONE]
4. 如果遇到无法解决的问题，输出：
   [ERROR]: <错误描述>

项目信息：
- 技术栈：{tech_stack}
- 任务总数：{task_count}
- 主要文件：app.py, db.py（新建）

重要提示：
- 使用Python内置sqlite3模块
- 不要使用外部库如SQLAlchemy
- 保持简单直接，不要过度设计

请开始实现，并保持进度输出。"""
    
    return prompt

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 auto-prompt.py <change-name>")
        sys.exit(1)
    
    print(generate_prompt(sys.argv[1]))
