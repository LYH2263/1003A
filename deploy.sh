#!/bin/bash

# =================================================================
# 龙猫图书借阅管理系统 - CentOS 一键部署脚本
# =================================================================

# 字体颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}   龙猫图书借阅管理系统 - CentOS 自动化部署${NC}"
echo -e "${BLUE}====================================================${NC}"

# 1. 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
  echo -e "${RED}错误: 请以 root 用户身份运行此脚本！${NC}"
  exit 1
fi

# 2. 检查并安装 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${GREEN}[1/4] 正在安装 Docker...${NC}"
    yum update -y
    yum install -y yum-utils device-mapper-persistent-data lvm2
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    yum install -y docker-ce docker-ce-cli containerd.io
    systemctl start docker
    systemctl enable docker
else
    echo -e "${GREEN}[1/4] Docker 已安装，跳过。${NC}"
fi

# 3. 检查并安装 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}[2/4] 正在安装 Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
else
    echo -e "${GREEN}[2/4] Docker Compose 已安装，跳过。${NC}"
fi

# 4. 构建并启动项目
echo -e "${GREEN}[3/4] 正在构建 Docker 容器...${NC}"
docker-compose up -d --build

# 5. 验证状态
echo -e "${GREEN}[4/4] 检查服务状态...${NC}"
sleep 10
docker-compose ps

echo -e "${BLUE}====================================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "访问地址: ${BLUE}http://$(curl -s ifconfig.me):8000${NC}"
echo -e "演示账号 - 管理员: ${BLUE}admin / 123456${NC}"
echo -e "演示账号 - 读者: ${BLUE}reader1 / 123456${NC}"
echo -e "${BLUE}====================================================${NC}"
