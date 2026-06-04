# 龙猫图书借阅管理系统 (Longmao Library CMS)

[![Docker](https://img.shields.io/badge/Docker-Supported-blue?logo=docker)](https://www.docker.com/) 
[![Django](https://img.shields.io/badge/Framework-Django%204.2-green?logo=django)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个基于 Python Django + MySQL 8 构建的现代化图书管理系统，具备精美的 UI 设计和流畅的交互体验。

---

## 🛠 技术栈

- **后端**: Python 3.9 + Django 4.2
- **数据库**: MySQL 8.0 (通过 PyMySQL 连接)
- **前端**: HTML5 + Tailwind CSS + Vanilla JS (原生 JavaScript)
- **容器化**: Docker + Docker Compose

## 🚀 核心特性

- **双端视角**: 区分管理员后台管理与读者前台浏览。
- **美学 UI**: 采用玻璃拟态 (Glassmorphism)、平滑渐变及现代排版。
- **自定义交互**: 摒弃原生弹窗，实现 UI 设计感的删除确认模态框。
- **数据自动化**: 包含 `seed_data.py` 脚本，启动即有演示数据。
- **一键部署**: 支持 CentOS 系统下一键脚本部署。

## 📥 快速启动 (Docker)

### 环境准备
确保已安装 [Docker](https://www.docker.com/) 和 Docker Compose。

### 🚀 一键启动

#### 方式 1: 快速开发启动（推荐日常使用）
```bash
sh dev.sh
```
- ✅ 利用 Docker 缓存，启动速度快（5-30秒）
- ✅ 适用于日常开发调试
- ✅ 如服务已运行，会自动重启

#### 方式 2: 完整重建启动
```bash
sh run.sh
```
- 🔄 停止并清理旧容器
- 🔨 重新构建所有镜像（约 4-6 分钟）
- 🚀 强制重建容器
- 💡 适用于清理环境或首次启动

#### 方式 3: 传统 Docker Compose 命令
```bash
docker compose up --build -d
```

### 访问系统
- **Web 界面**: [http://localhost:8000](http://localhost:8000)
- **管理员账号**: `admin` / `123456`
- **测试读者**: `reader1` / `123456`
- **数据库**: `localhost:3306`

## 📦 CentOS 离线/在线部署

如果您在 CentOS 环境下：
```bash
chmod +x deploy.sh
./deploy.sh
```

## 🏗 项目结构

```text
├── backend/
│   ├── apps/           # 业务逻辑 (books, users)
│   ├── core/           # 框架配置
│   ├── templates/      # HTML 模板
│   ├── static/         # 静态资源
│   ├── Dockerfile      # 构建镜像
│   └── seed_data.py    # 演示数据脚本
├── docker-compose.yml  # 容器编排
└── deploy.sh           # 一键部署脚本
```

---
Built with 💖 by Antigravity.
