# Development Log 2026-06-05

记录范围：最近 24 小时内与 Any2Screen Web MVP、导出能力、本地/远程部署和后续计划相关的开发决策、阶段完成、方向调整与关键问题定位。

## Log Format

后续开发日志统一按以下结构记录：

- 时间范围：本次日志覆盖的日期或时间段。
- 背景：触发本轮工作的用户目标、问题或环境变化。
- 决策：对架构、产品方向、部署方式、接口边界或实现策略的明确选择。
- 完成节点：已经完成并验证的开发任务、修复或文档沉淀。
- 方向变化：相较之前计划发生的优先级、范围或技术路线变化。
- 问题定位：出现过的阻塞、根因判断和证据。
- 验证结果：运行过的测试、命令、日志证据或剩余未验证项。
- 后续动作：下一步可执行任务，不记录泛泛想法。

## Background

本轮工作围绕 Web MVP 的导出链路和部署闭环推进。核心目标从“接入导出能力”推进到“本地 Docker 与远程 ECS 都能稳定部署、长图导出可用、常用运维命令可复用、后续预览体验有计划承接”。

## Decisions

- Web MVP 继续采用 API-first 方向，前端导出请求统一通过后端 API 完成，而不是前端直接生成文件。
- Web 和 demo-site 两套静态入口暂时继续并行维护，但交互行为保持一致；后续如维护成本增加，再考虑引入同步脚本或单源生成。
- 长图导出参数确认使用 `small=430 CSS px`、`large=1080 CSS px`，格式支持 `png/jpeg`。
- 导出决策规则确认：长图开启时走 image API；长图关闭且 PDF+小屏走 WeChat PDF；长图关闭且 PDF+大屏走标准 PDF；HTML 不随屏幕尺寸变化。
- 本地和远程都保留同一份 `Dockerfile`，宿主系统差异通过容器边界隔离；远程 Alibaba Cloud Linux 仍使用容器内 Debian `apt-get`，不改为宿主机 `dnf`。
- 服务器部署继续采用远端现场构建方式，即 `docker-compose -f deploy/docker-compose.yml up -d --build`，因此 `Dockerfile`、`src/`、`scripts/`、`deploy/`、`demo-site/` 仍属于同步范围。
- rsync 排除项改为集中配置在 `deploy/rsync-excludes.txt`，避免同步命令不断变长。
- 项目级 `AGENTS.md` 增加运维快捷指令映射，后续用户说“同步到服务器”“远程部署”“查看服务器状态”“查看 API 日志”时按固定命令执行。
- 开发计划新增“导出仿真预览”方向：预览窗后续应根据当前导出配置模拟小屏/大屏、长图和 PDF 版式差异。

## Completed Nodes

- 完成 D19.1-D19.4：
  - 新增 `GET /api/exports/{file_id}/wechat-pdf`。
  - 新增 `GET /api/exports/{file_id}/image?screen=small|large&format=png|jpeg`。
  - Web 与 demo-site 增加小屏/大屏、生成长图、PNG/JPG、HTML/PDF 控件。
  - 前端实现导出决策规则。
- 前端导出交互从 `window.open()` 改为 `fetch + blob + a[download]`，导出失败时在预览状态区显示具体错误。
- `FileRegistry` 从纯内存记录扩展为磁盘元数据恢复：
  - 上传时写入 `record.json`。
  - 内存未命中时从上传目录恢复 `file_id` 对应记录。
  - 解决跨进程、容器重启或内存状态丢失导致导出 404 的问题。
- 修复中文文件名导出 500：
  - `Content-Disposition` 改为 ASCII fallback + `filename*=UTF-8''...`。
  - 避免 Starlette 响应头 `latin-1` 编码失败。
- 修复 Docker 长图运行环境：
  - Dockerfile 切换 Debian apt 源到阿里云镜像。
  - 补充 Chromium/Playwright 运行依赖，如 `libnspr4`、`libnss3`、`libgbm1`、`libx*` 等。
- 优化 JPEG 长图清晰度：
  - Playwright 截图 JPEG 显式设置 `quality=95`。
  - 保持 PNG 无损路径不变。
- 前端布局微调完成：
  - 控件组顺序调整为“长图/图片格式 -> 屏宽/文档格式 -> 预览/导出”。
  - 小屏/大屏、PNG/JPG、HTML/PDF 均使用滑动开关。
  - 预览/导出按钮组字号更大、加粗。
  - 语言切换时预览按钮状态同步。
- 部署和运维沉淀：
  - 新增 `deploy/rsync-excludes.txt`。
  - 新增 `docs/prompts.md`。
  - `AGENTS.md` 记录服务器运维快捷指令。
  - `docs/demo-site-docker-deploy.md` 指向统一 prompts 文档。
- 开发计划更新：
  - D5 细化为 D5.1-D5.5，覆盖性能基线样本、采集脚本、Docker/本地环境、基线表和回归口径。
  - 新增 D19.4a-D19.4c，记录导出仿真预览计划。

## Direction Changes

- “长图导出不可用”的排查方向从前端交互问题转为后端导出链路，再定位到运行环境和响应头编码问题。
- 本地部署入口确认不应混用 `8000/8002/8082`。当前 Docker nginx 对外入口以 nginx 映射端口为准，API 容器 `8000` 只是容器内端口。
- 远程部署命令统一采用 `docker-compose`，不写 `docker compose`，以匹配用户服务器实际环境。
- 同步策略从“整项目直接 rsync 并逐项 `--exclude`”调整为“使用 `deploy/rsync-excludes.txt` 集中排除非运行文件”。
- README、docs、tests、prompts、AGENTS、DEVELOPMENT_PLAN、samples 等不再作为服务器运行同步内容；Dockerfile 已去掉对 README 的构建依赖。
- 预览窗后续方向从“单一轻量 HTML 预览”扩展为“根据当前导出配置进行版式仿真预览”。

## Problem Diagnosis

- 404 `Not Found` 曾由三类原因混淆：
  - 访问了错误端口或错误服务，如 `localhost:8002`。
  - 使用了容器内未对宿主开放的 `8000` 入口。
  - `file_id` 只在内存中，跨进程或重启后无法恢复。
- 405 `Method Not Allowed` 来自使用 `curl -I` 发送 HEAD 请求；导出接口只支持 GET，响应头 `allow: GET` 证明路由存在。
- 长图导出 500 第一阶段根因是 Chromium 缺系统库，日志证据为 `libnspr4.so: cannot open shared object file`。
- 长图导出 500 第二阶段根因是中文文件名写入 `Content-Disposition` 时触发 `UnicodeEncodeError: 'latin-1' codec can't encode characters`。
- 大屏 JPEG 长图模糊不是像素尺寸错误，而是默认 JPEG 压缩质量偏低；通过设置 `quality=95` 处理。
- `share-modal.js` 报错不属于当前项目代码，仓库中不存在该文件，判断为浏览器扩展、缓存或其他本地站点脚本注入。

## Verification Results

- Web API 测试通过：
  - `./.venv/bin/python -m unittest tests.test_web_api`
  - 最近一次结果：`Ran 21 tests ... OK (skipped=1)`。
- 前端 JS 语法检查通过：
  - `node --check src/web/static/app.js`
  - `node --check demo-site/app.js`
- Python 编译检查通过：
  - `python3 -m compileall -q src`
- 容器内 Playwright/Chromium 启动验证通过：
  - `docker exec any2screen-api python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); print('ok'); b.close(); p.stop()"`
  - 输出：`ok`。
- rsync 同步命令已实际执行过，目标路径为 `/opt/any2screen-api/`。
- Git 推送节点：
  - `ecf1f46`：D19.1-D19.4。
  - `f4a040d`：frontend layout amend。
  - `a48340a`：rsync server, add rsync-excludes。

## Follow-Up Actions

- 本地重新构建 API 容器后，复测长图导出完整链路：
  - 小屏 PNG。
  - 小屏 JPEG。
  - 大屏 PNG。
  - 大屏 JPEG。
- 将“本地只重建 API 容器”命令补充到 `docs/prompts.md` 和 `AGENTS.md` 工作流映射：
  - `docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d --build any2screen-api`
- 完成当前未提交修改的整理和提交，避免部署修复、日志、计划变更混杂过久。
- 按 D5.1 开始定义性能基线样本和采集口径。
- 按 D19.4a-D19.4c 设计导出仿真预览的第一版 CSS/状态模型。
