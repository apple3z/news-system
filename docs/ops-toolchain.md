# 全球化运营服务平台 - 运维工具链文档

## 1. 系统环境

| 项目 | 值 |
|------|------|
| 主机名 | zhangvm |
| IP 地址 | 192.168.36.132 |
| 操作系统 | Ubuntu 24.04 LTS (Noble) |
| 内核版本 | Linux 6.17.0-14-generic |
| 架构 | x86_64 |
| 内存 | 15GB |
| 用户 | zhang |

---

## 2. 工具链清单

### 2.1 容器与编排

| 工具 | 版本 | 安装方式 | 状态 |
|------|------|----------|------|
| Docker | 28.2.2 | apt | ✅ 运行中 |
| Docker Compose | 2.37.1 | apt | ✅ |

### 2.2 运行时 - Node.js

| 工具 | 版本 | 安装方式 | 状态 |
|------|------|----------|------|
| Node.js | 18.19.1 | apt (nodesource) | ✅ 已安装 |
| npm | 9.2.0 | apt | ✅ |

### 2.3 运行时 - Python

| 工具 | 版本 | 安装方式 | 状态 |
|------|------|----------|------|
| Python | 3.12.3 | 系统自带 | ✅ |
| pip | 24.0 | apt | ✅ |
| venv | 3.12.3 | 系统自带 | ✅ |

### 2.4 数据库

| 工具 | 版本 | 端口 | 状态 |
|------|------|------|------|
| PostgreSQL | 16.11 | 5432 | ✅ 运行中 |
| Redis | 7.0.15 | 6379 | ✅ 运行中 |
| MongoDB | 7.0.30 | 27017 | ✅ 运行中 |

### 2.5 Web 服务器

| 工具 | 版本 | 端口 | 状态 |
|------|------|------|------|
| Nginx | 1.24.0 | 80 | ✅ 运行中 |

### 2.6 版本控制

| 工具 | 版本 |
|------|------|
| Git | 2.43.0 |

### 2.7 终端工具

| 工具 | 版本 |
|------|------|
| tmux | 3.4 |
| htop | - |
| vim | 9.1 |

### 2.8 网络工具

| 工具 | 版本 |
|------|------|
| jq | 1.7 |
| wget | 1.21.4 |
| curl | 8.5.0 |

---

## 3. 服务管理

### 3.1 服务启动/停止/重启

```bash
# Docker
sudo systemctl start docker
sudo systemctl stop docker
sudo systemctl restart docker

# PostgreSQL
sudo systemctl start postgresql
sudo systemctl stop postgresql
sudo systemctl restart postgresql

# Redis
sudo systemctl start redis-server
sudo systemctl stop redis-server
sudo systemctl restart redis-server

# MongoDB
sudo systemctl start mongod
sudo systemctl stop mongod
sudo systemctl restart mongod

# Nginx
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
```

### 3.2 服务状态查看

```bash
# 查看所有服务状态
systemctl status docker redis-server mongod postgresql nginx

# 查看单个服务状态
systemctl status docker
```

### 3.3 服务开机自启

```bash
# 启用开机自启
sudo systemctl enable docker redis-server mongod postgresql nginx

# 禁用开机自启
sudo systemctl disable docker
```

---

## 4. 常用命令

### 4.1 Docker

```bash
# 查看 Docker 版本
docker --version
docker compose version

# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 查看镜像
docker images

# 启动 Docker
sudo systemctl start docker
```

### 4.2 PostgreSQL

```bash
# 连接 PostgreSQL (需要先配置用户)
psql -U postgres -h localhost -p 5432

# 查看数据库列表
sudo -u postgres psql -c "\l"
```

### 4.3 Redis

```bash
# 测试 Redis 连接
redis-cli ping

# 连接 Redis
redis-cli

# 查看 Redis 信息
redis-cli info
```

### 4.4 MongoDB

```bash
# 连接 MongoDB (需要先配置用户)
mongosh -u admin -p --authenticationDatabase admin

# 查看数据库
mongosh --eval "db.adminCommand('listDatabases')"
```

### 4.5 Nginx

```bash
# 测试配置
sudo nginx -t

# 重新加载配置
sudo systemctl reload nginx

# 查看日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 5. 目录结构

```
/
├── /home/zhang/                  # 用户目录
├── /var/lib/postgresql/16/main   # PostgreSQL 数据目录
├── /var/lib/mongodb              # MongoDB 数据目录
├── /var/lib/redis                # Redis 数据目录
├── /etc/nginx/                   # Nginx 配置目录
├── /etc/docker/                  # Docker 配置目录
└── /etc/mongod.conf              # MongoDB 配置
```

---

## 6. 端口说明

| 服务 | 端口 | 协议 |
|------|------|------|
| SSH | 22 | TCP |
| Nginx | 80 | TCP |
| Nginx HTTPS | 443 | TCP |
| PostgreSQL | 5432 | TCP |
| Redis | 6379 | TCP |
| MongoDB | 27017 | TCP |
| Copaw | 8088 | TCP |

---

## 7. 维护记录

| 日期 | 操作 | 操作人 |
|------|------|--------|
| 2026-03-02 | 初始环境搭建，安装全部工具链 | CoPaw |

---

## 8. 注意事项

1. **MongoDB 安装**: 使用官方 apt 源安装，版本 7.0.30
2. **Docker 组**: 用户 zhang 已加入 docker 组，无需 sudo 即可运行 docker 命令
3. **PostgreSQL**: 默认配置，本地连接使用 peer 认证
4. **Redis**: 默认配置，仅监听本地 127.0.0.1

---

## 9. 待配置项

- [ ] PostgreSQL 用户和密码配置
- [ ] Redis 密码配置
- [ ] MongoDB 用户和密码配置
- [ ] Nginx 反向代理配置
- [ ] 防火墙端口开放
- [ ] 备份策略配置
