# Demo Site Docker Deployment

目标服务器：Alibaba Cloud Linux 4 容器优化版 ECS。

部署形态：

- `any2screen-nginx`：对外暴露 80 端口，服务 `/demo-site/`，并把 `/api/` 反代到 API 容器。
- `any2screen-api`：运行 FastAPI，只在 Docker Compose 内网暴露 8000。
- `any2screen_uploads`：保存上传文件和同目录导出文件。

## 首次部署

```bash
rsync -avz --delete \
  --exclude .git \
  --exclude .venv \
  --exclude __pycache__ \
  --exclude data/uploads \
  ./ root@39.105.102.5:/opt/any2screen-api/
```

```bash
ssh root@39.105.102.5
cd /opt/any2screen-api
docker compose -f deploy/docker-compose.yml up -d --build
```

## 验证

```bash
curl http://127.0.0.1/api/health
docker compose -f deploy/docker-compose.yml ps
docker compose -f deploy/docker-compose.yml logs -f any2screen-api
```

浏览器访问：

```text
http://39.105.102.5/demo-site/
```

## 更新

```bash
rsync -avz --delete \
  --exclude .git \
  --exclude .venv \
  --exclude __pycache__ \
  --exclude data/uploads \
  ./ root@39.105.102.5:/opt/any2screen-api/
```

```bash
ssh root@39.105.102.5
cd /opt/any2screen-api
docker compose -f deploy/docker-compose.yml up -d --build
```

## 回滚和清理

停止服务：

```bash
docker compose -f deploy/docker-compose.yml down
```

保留上传数据时不要删除 volume。确认要删除上传和导出文件时再执行：

```bash
docker volume rm deploy_any2screen_uploads
```
