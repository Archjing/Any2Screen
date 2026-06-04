# Reusable Prompts

## Sync To Server

用途：将当前项目代码同步到 ECS 服务器的部署目录。

```bash
rsync -avz --delete --exclude-from=deploy/rsync-excludes.txt ./ root@39.105.102.5:/opt/any2screen-api/
```
