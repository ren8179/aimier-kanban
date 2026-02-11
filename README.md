# 爱弥儿任务看板

一个简洁高效的任务管理看板系统，使用 Flask + SQLite 构建。

## 功能特性

- ✅ 看板视图（待办/进行中/已完成）
- ✅ 拖拽排序
- ✅ 优先级管理（高/中/低）
- ✅ 截止日期设置
- ✅ 标签支持
- ✅ 搜索和筛选
- ✅ 任务归档功能
- ✅ 统计仪表盘

## 技术栈

- **后端**: Python 3 + Flask
- **数据库**: SQLite
- **前端**: HTML5 + Vanilla JavaScript + CSS3
- **架构**: RESTful API

## 快速开始

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd aimier-kanban

# 安装依赖（Flask）
pip install flask
```

### 运行

```bash
# 启动服务
python3 app.py

# 访问看板
# 本地: http://127.0.0.1:5000
# 局域网: http://<your-ip>:5000
```

### 项目结构

```
aimier-kanban/
├── app.py              # Flask 应用主文件
├── db.py               # 数据库操作
├── static/             # 静态资源
│   ├── css/           # 样式文件
│   └── js/            # JavaScript 文件
├── templates/          # HTML 模板
│   └── index.html     # 主页面
├── data/              # 数据目录（自动创建）
│   └── kanban.db      # SQLite 数据库
├── openspec/          # OpenSpec 规范文件
│   ├── changes/       # 功能变更记录
│   └── specs/         # 系统规格
└── .gitignore         # Git 忽略文件
```

## API 接口

### 任务管理

- `GET /api/tasks` - 获取所有任务
- `POST /api/tasks` - 创建新任务
- `PATCH /api/tasks/<id>` - 更新任务
- `DELETE /api/tasks/<id>` - 删除任务
- `GET /api/stats` - 获取统计数据
- `GET /api/tags` - 获取所有标签

### 归档管理

- `GET /api/archives` - 获取归档任务
- `POST /api/archives/<id>/restore` - 恢复归档任务
- `DELETE /api/archives/<id>` - 删除归档任务

## 数据库结构

### tasks 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 主键 |
| title | TEXT | 任务标题 |
| description | TEXT | 任务描述 |
| status | TEXT | 状态 |
| priority | TEXT | 优先级 |
| due_date | TEXT | 截止日期 |
| tags | TEXT | 标签（JSON数组） |
| created_at | TEXT | 创建时间 |
| updated_at | TEXT | 更新时间 |

### archives 表

与 tasks 表结构相同，额外包含：
- `archived_at` - 归档时间
- `archived_month` - 归档月份

## 开发指南

### 使用 OpenCode + OpenSpec 开发

项目支持使用 OpenCode AI 编程代理进行开发。

```bash
# 初始化 OpenSpec
openspec init --tools opencode

# 创建新功能
openspec change new feature-name

# 让 OpenCode 实现
opencode run "按 openspec/changes/feature-name/tasks.md 实现"
```

### 已实现功能

- [x] 基础任务管理（CRUD）
- [x] 看板视图和拖拽
- [x] 优先级和截止日期
- [x] 搜索和筛选
- [x] 任务归档功能
- [x] 标签功能

## 系统要求

- Python 3.6+
- Flask 2.0+

## 部署

### 生产环境建议

使用 WSGI 服务器（如 gunicorn）：

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

或使用 systemd 守护进程。

## 许可证

MIT License

## 作者

爱弥儿（任琪工作室）

---

**项目定位**: 爱弥儿的第一个项目，实践 OpenSpec + OpenCode 工作流
