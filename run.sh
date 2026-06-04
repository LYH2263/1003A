#!/usr/bin/env bash
set -e

echo "🧹 停掉旧容器..."
docker compose down --remove-orphans

echo "🔥 构建镜像（使用缓存）..."
docker compose build

echo "🚀 启动服务（强制重建容器）..."
docker compose up --force-recreate --renew-anon-volumes
