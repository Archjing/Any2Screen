# Reusable Prompts

## Sync To Server

用途：将当前项目代码同步到 ECS 服务器的部署目录。

```bash
rsync -avz --delete --exclude-from=deploy/rsync-excludes.txt ./ root@39.105.102.5:/opt/any2screen-api/
```

## Deploy On Server

用途：在服务器上进入项目目录并重建启动容器。

```bash
ssh root@39.105.102.5 'cd /opt/any2screen-api && docker-compose -f deploy/docker-compose.yml up -d --build'
```

## Check Server Status

用途：查看服务器上当前容器状态。

```bash
ssh root@39.105.102.5 'cd /opt/any2screen-api && docker-compose -f deploy/docker-compose.yml ps'
```

## Tail API Logs

用途：查看服务器上 FastAPI 容器日志。

```bash
ssh root@39.105.102.5 'cd /opt/any2screen-api && docker-compose -f deploy/docker-compose.yml logs -f any2screen-api'
```
