# Any2Screen

Any2Screen 是一个文档转换工具集，目标是把常见图文内容转换成更适合移动端阅读、传输和分享的输出格式。

当前仓库提供一个统一命令入口 `any2screen`，通过子命令调用 3 个模块：

- `doc2md`：`docx/pdf/txt -> markdown`
- `md2html`：`markdown -> 自包含 html`，可选导出 PDF
- `md2img`：`markdown -> 长图`

## 当前状态

当前代码更接近“转换能力原型”，不是完整应用。

- 统一入口已经可用：`scripts/any2screen.py`
- 子命令分发逻辑位于 `src/a2s/`
- `md2html` 是目前最完整、最适合直接使用的模块
- `md2img` 已支持参数化 CLI，可指定输入、输出、宽度和图片格式

## 目录结构

```text
Any2Screen/
├── README.md
├── DEVELOPMENT_PLAN.md
├── pyproject.toml
├── uv.lock
├── scripts/
│   └── any2screen.py
├── src/
│   └── a2s/
│       ├── __init__.py
│       ├── cli.py
│       ├── command_registry.py
│       ├── doc2md.py
│       ├── md2html.py
│       └── md2img.py
├── docs/
│   ├── md2html.md
│   └── md2html.requirements.txt
```

说明：

- `scripts/any2screen.py` 是唯一统一入口
- `src/a2s/` 是统一入口实际调用的模块实现
- 项目依赖由 `uv` 管理，声明在 `pyproject.toml`，锁定在 `uv.lock`

## 依赖安装

```bash
uv sync
```

使用 `uv` 入口：

```bash
uv run any2screen --help
uv run any2screen md2html README.md --pdf
```

继续使用脚本入口也可以：

```bash
python3 scripts/any2screen.py --help
```

## 统一命令行

总用法：

```bash
python3 scripts/any2screen.py <module> [module_args...]
```

当前支持的 `<module>`：

- `doc2md`
- `md2html`
- `md2img`

查看帮助：

```bash
python3 scripts/any2screen.py --help
python3 scripts/any2screen.py doc2md --help
python3 scripts/any2screen.py md2html --help
python3 scripts/any2screen.py md2img --help
```

## 子命令说明

### `doc2md`

将单个文件或目录中的文档转换为 Markdown。

支持格式：

- `.docx`
- `.pdf`
- `.txt`

参数：

- `input`：输入文件或目录
- `-o, --output`：输出目录，默认当前目录
- `-p, --password`：加密 `.docx` 的密码，可选

示例：

```bash
python3 scripts/any2screen.py doc2md ./report.docx
python3 scripts/any2screen.py doc2md ./report.pdf -o ./out
python3 scripts/any2screen.py doc2md ./docs -o ./out -p your_password
```

依赖：

- `python-docx`
- `PyPDF2`
- `msoffcrypto-tool` 可选，仅加密 `.docx` 需要

### `md2html`

将一个或多个 Markdown 文件转换为自包含 HTML 或 PDF。

参数：

- `paths`：一个或多个 `.md` 文件或目录
- `-o, --output`：输出目录，默认与源文件同级
- `--inplace`：将 `.html` 写到 `.md` 同目录
- `--html`：生成 HTML；默认无 PDF 参数时启用
- `--pdf`：生成 A4 PDF；默认只输出 PDF
- `--wechat`：生成适合微信阅读的 PDF；默认只输出 PDF
- `-v, --verbose`：详细输出
- `--watch`：监听变更并自动重建
- `--quiet`：仅输出错误

示例：

```bash
python3 scripts/any2screen.py md2html ./README.md
python3 scripts/any2screen.py md2html ./notes -o ./exports
python3 scripts/any2screen.py md2html ./trip.md --pdf
python3 scripts/any2screen.py md2html ./trip.md --html --pdf
python3 scripts/any2screen.py md2html ~/workspace/stok-mapping/tasks/cross-market/HK_A_SHARE_MAPPING_STRATEGIES.md --pdf
python3 scripts/any2screen.py md2html ./notes --watch -o ./exports
```

依赖：

- 运行依赖见 `pyproject.toml`
- `watchdog` 是可选依赖，使用 `--watch` 时安装 `uv sync --extra watch`

补充：

- 该模块当前是仓库里最成熟的 CLI
- `--pdf` 与 `--wechat` 默认只输出 PDF；需要同时保留 HTML 时加 `--html`

### `md2img`

将 Markdown 渲染为长图。

参数：

- `input`：输入 Markdown 文件
- `-o, --output`：输出图片文件或目录，默认与输入文件同级
- `--width`：视口/图片宽度，默认 `960`
- `--format`：输出格式，支持 `png`、`jpeg`，默认 `png`

示例：

```bash
python3 scripts/any2screen.py md2img ./README.md
python3 scripts/any2screen.py md2img ./README.md -o ./exports
python3 scripts/any2screen.py md2img ./README.md -o ./exports/readme.jpeg --width 1080 --format jpeg
```

依赖：

- 运行依赖见 `pyproject.toml`
- 首次使用截图功能前需要安装 Playwright 浏览器：`uv run playwright install chromium`

## 扩展子命令

统一入口本身不写任何具体转换逻辑，只负责路由。

新增子命令时：

1. 在 `src/a2s/` 添加模块脚本
2. 在 [src/a2s/command_registry.py](/home/zj/workspace/KMS/scripts/Any2Screen/src/a2s/command_registry.py) 注册子命令与脚本路径
3. 通过 `python3 scripts/any2screen.py <new_module> ...` 调用

## 相关文档

- `md2html` 的补充说明：`docs/md2html.md`
- `md2html` 的依赖清单：`docs/md2html.requirements.txt`
- 开发规划：`DEVELOPMENT_PLAN.md`
