<div align="center">
<img src=".\img\image-20260602181032888.png" alt="发给我妈看！！" width="60%" align="center">
</div>

# Any2Screen



Any2Screen 是一个文档转换工具集，目标是把常见图文内容转换成更适合移动端阅读、传输和分享的输出格式。

[项目当前开发计划：.\DEVELOPMENT_PLAN.md](.\DEVELOPMENT_PLAN.md)

当前仓库提供一个统一命令入口 `any2screen`，通过子命令调用主 pipeline 或独立阶段模块：

- `convert`：运行完整 `any2html -> html2screen` pipeline
- `any2html`：将输入文档转换为 HTML 中间产物
- `html2screen`：将 HTML 转换为 A4 PDF、WeChat PDF、HTML 或图片
- `doc2md`：将 DOCX/PDF/TXT 转换为 Markdown，作为独立工具保留

## 当前状态

当前代码更接近“转换能力原型”，不是完整应用。

- 统一入口已经可用：`scripts/any2screen.py`
- 子命令分发逻辑位于 `src/a2s/`
- `convert` 作为主 CLI pipeline，内部执行 `any2html -> html2screen`
- `any2html` 和 `html2screen` 可独立调用，便于调试、复用和后续扩展
- `doc2md` 作为独立转换工具保留，后续可作为 DOCX/PDF/TXT 接入 `any2html` 的基础

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
│       ├── convert_cli.py
│       ├── any2html_cli.py
│       ├── html2screen_cli.py
│       ├── doc2md.py
│       ├── pipeline.py
│       ├── any2html/
│       │   └── markdown.py
│       └── html2screen/
│           └── renderers.py
├── docs/
│   ├── pipeline.md
│   └── runtime.requirements.txt
```

说明：

- `scripts/any2screen.py` 是唯一统一入口
- `src/a2s/` 是统一入口实际调用的模块实现
- `src/a2s/any2html/` 负责把输入文档转换为 HTML 中间产物
- `src/a2s/html2screen/` 负责把 HTML 输出为 A4 PDF、WeChat PDF、长图等屏幕友好格式
- `src/a2s/pipeline.py` 负责串接 `any2html -> html2screen`
- 项目依赖由 `uv` 管理，声明在 `pyproject.toml`，锁定在 `uv.lock`

## 依赖安装

```bash
uv sync
```

使用 `uv` 入口：

```bash
uv run any2screen --help
uv run any2screen convert README.md --pdf
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

- `convert`
- `any2html`
- `html2screen`
- `doc2md`

查看帮助：

```bash
python3 scripts/any2screen.py --help
python3 scripts/any2screen.py convert --help
python3 scripts/any2screen.py any2html --help
python3 scripts/any2screen.py html2screen --help
python3 scripts/any2screen.py doc2md --help
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

### `convert`

运行完整 pipeline，将一个或多个输入文档转换为 HTML、PDF、微信阅读 PDF 或长图。

参数：

- `paths`：一个或多个 `.md` 文件或目录
- `-o, --output`：输出目录，默认与源文件同级
- `--html`：生成 HTML；默认无 PDF 参数时启用
- `--pdf`：生成 A4 PDF；默认只输出 PDF
- `--wechat`：生成适合微信阅读的 PDF；默认只输出 PDF
- `--img`：生成长图；默认只输出图片
- `--width`：图片视口宽度，默认 `960`
- `--format`：图片格式，支持 `png`、`jpeg`，默认 `png`
- `-v, --verbose`：详细输出

示例：

```bash
python3 scripts/any2screen.py convert ./README.md
python3 scripts/any2screen.py convert ./notes -o ./exports
python3 scripts/any2screen.py convert ./trip.md --pdf
python3 scripts/any2screen.py convert ./trip.md --html --pdf
python3 scripts/any2screen.py convert ./trip.md --img --width 1080 --format png
python3 scripts/any2screen.py convert ./trip.md --img --format jpeg -o ./exports
python3 scripts/any2screen.py convert ./trip.md --html --pdf --wechat --img
python3 scripts/any2screen.py convert ~/workspace/stok-mapping/tasks/cross-market/HK_A_SHARE_MAPPING_STRATEGIES.md --pdf
```

依赖：

- 运行依赖见 `pyproject.toml`
- `watchdog` 是可选依赖，使用 `--watch` 时安装 `uv sync --extra watch`

补充：

- 该模块当前是仓库里最成熟的 CLI
- 指定任一输出 flag 时只输出指定格式；需要多格式时组合使用，比如 `--html --pdf --img`

图片输出依赖：

- 运行依赖见 `pyproject.toml`
- 首次使用 `--img` 前需要安装 Playwright 浏览器：`uv run playwright install chromium`

### `any2html`

只执行预处理阶段，将输入文档转换为 HTML 中间产物。

```bash
python3 scripts/any2screen.py any2html ./README.md
python3 scripts/any2screen.py any2html ./README.md -o ./exports
python3 scripts/any2screen.py any2html ./README.md -o ./exports/readme.html
```

### `html2screen`

只执行输出渲染阶段，将 HTML 中间产物转换为屏幕友好格式。

```bash
python3 scripts/any2screen.py html2screen ./README.html --pdf
python3 scripts/any2screen.py html2screen ./README.html --wechat
python3 scripts/any2screen.py html2screen ./README.html --img --width 960 --format png
python3 scripts/any2screen.py html2screen ./README.html --html --pdf --wechat --img -o ./exports
```

## 扩展子命令

统一入口本身不写任何具体转换逻辑，只负责路由。

新增子命令时：

1. 在 `src/a2s/` 添加模块脚本
2. 在 [src/a2s/command_registry.py](/home/zj/workspace/KMS/scripts/Any2Screen/src/a2s/command_registry.py) 注册子命令与脚本路径
3. 通过 `python3 scripts/any2screen.py <new_module> ...` 调用

## 相关文档

- pipeline 补充说明：`docs/pipeline.md`
- 运行依赖清单：`docs/runtime.requirements.txt`
- 开发规划：`DEVELOPMENT_PLAN.md`


<div align="center">

## 📋 License

This project is licensed under **CC BY-NC-SA 4.0**.
<p align="center">You are free to:</p>
<p align="center">1. Share — copy and redistribute the material in any medium or format.</p>
<p align="center">2. Adapt — remix, transform, and build upon the material.</p>
<p align="center">The licensor cannot revoke these freedoms as long as you **follow the license terms**.</p>

<p align="center">本项目采用 CC BY-NC-SA 4.0 许可证。</p>
<p align="center">你可以自由：</p>
<p align="center">分享 — 以任何媒介或格式复制、再分发本素材</p>
<p align="center">改编 — 对本素材进行混编、转换、二次创作</p>
<p align="center">只要你遵守许可证条款，许可人就不能撤销这些自由</p>

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-blue.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

</div>

