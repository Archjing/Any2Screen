# Any2Screen

`Any2Screen` 是一个统一入口的文档转换工具集，通过一个前导命令调用不同子模块。

## 功能概览

- `doc2md`：将常见文档转换为 Markdown（支持 `.docx`、`.pdf`、`.txt`）
- `md2html`：将 Markdown 批量转换为自包含 HTML（可选导出 PDF）
- `md2img`：将 Markdown 渲染为长图（当前实现为脚本内固定输入/输出路径）

## 目录结构

- `scripts/any2screen.py`：统一命令入口（前导路由）
- `src/a2s/cli.py`：子命令分发层（不包含具体转换逻辑）
- `src/a2s/command_registry.py`：子命令注册表（后续扩展在这里添加）
- `src/a2s/*.py`：各模块具体实现

## 命令行总用法

```bash
python3 scripts/any2screen.py <module> [module_args...]
```

- `<module>` 目前支持：`doc2md`、`md2html`、`md2img`
- `[module_args...]` 会原样透传给对应模块

查看帮助：

```bash
python3 scripts/any2screen.py --help
python3 scripts/any2screen.py doc2md --help
python3 scripts/any2screen.py md2html --help
```

## 子命令说明

### 1) doc2md

将文件或目录中的文档转换为 Markdown。

支持格式：
- `.docx`（可配合密码解密，依赖 `msoffcrypto`）
- `.pdf`
- `.txt`

参数：
- `input`：输入文件或目录（必填）
- `-o, --output`：输出目录，默认当前目录
- `-p, --password`：加密 `.docx` 的密码（可选）

示例：

```bash
# 单文件
python3 scripts/any2screen.py doc2md ./report.docx

# 指定输出目录
python3 scripts/any2screen.py doc2md ./report.pdf -o ./out

# 目录批量转换 + 密码
python3 scripts/any2screen.py doc2md ./docs -o ./out -p your_password
```

### 2) md2html

将一个或多个 Markdown 文件转换为自包含 HTML，可选生成 PDF。

参数：
- `paths`：一个或多个 `.md` 文件或目录（必填）
- `-o, --output`：输出目录（默认与源文件同级）
- `--inplace`：将 `.html` 写入 `.md` 同目录
- `--pdf`：额外生成 A4 PDF（需 Playwright）
- `--wechat`：额外生成适合微信阅读的 PDF（需 Playwright）
- `-v, --verbose`：详细输出
- `--watch`：监听文件变化自动重建（需 watchdog）
- `--quiet`：仅输出错误

示例：

```bash
# 单文件转 HTML
python3 scripts/any2screen.py md2html ./README.md

# 目录批量输出到指定目录
python3 scripts/any2screen.py md2html ./notes -o ./exports

# 生成 HTML + PDF
python3 scripts/any2screen.py md2html ./trip.md --pdf

# 监听模式
python3 scripts/any2screen.py md2html ./notes --watch -o ./exports
```

### 3) md2img

将 Markdown 转为长图。

注意：当前版本没有公开命令行参数，输入/输出路径在脚本内部常量中定义：
- 输入：`INPUT`
- 输出：`OUTPUT`

运行示例：

```bash
python3 scripts/any2screen.py md2img
```

## 依赖说明（按模块）

- `doc2md`：`python-docx`、`PyPDF2`（可选 `msoffcrypto-tool`）
- `md2html`：`markdown-it-py`、`mdit-py-plugins`、`linkify-it-py`（`--pdf/--wechat` 需 `playwright`）
- `md2img`：`markdown-it-py`、`playwright`

## 扩展子命令

新增模块时：
1. 在 `src/a2s/` 新建模块脚本
2. 在 `src/a2s/command_registry.py` 增加子命令到脚本路径的映射
3. 即可通过 `python3 scripts/any2screen.py <new_module> ...` 调用
