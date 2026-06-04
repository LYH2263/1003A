#!/usr/bin/env bash
set -e

# 快速开发模式 - 使用缓存，只在代码变更时重建
echo "🚀 快速启动开发环境..."

# 如果服务已经在运行，直接重启即可
if docker compose ps | grep -q "Up"; then
    echo "♻️  服务正在运行，重启中..."
    docker compose restart
else
    echo "🔨 构建镜像（利用缓存）..."
    docker compose build
    
    echo "🚀 启动服务..."
    docker compose up
fi
