# Any2Screen

一个轻量的文档转换脚本集合，目标是把常见文档转成适合阅读、分享和二次处理的格式。

当前包含 3 个脚本：

- `doc2md/doc2md.py`：`docx/pdf/txt -> markdown`
- `md2html/md2html.py`：`markdown -> 自包含 html`（可选导出 PDF）
- `md2img/md2img.py`：`markdown -> 长图`（基于 Playwright 截图）

## 项目状态（截至 2026-05-31）

整体状态：**可用，偏脚本化，适合个人工作流**。

现状结论：

1. 仓库 Git 状态干净（无未提交改动）。
2. `md2html` 功能最完整，支持批量、递归、watch、暗色、响应式、表格优化、可选 PDF。
3. `doc2md` 可处理目录批量转换，支持加密 `docx`（提供密码且安装 `msoffcrypto` 时）。
4. `md2img` 当前是固定输入输出路径，更像项目内专用脚本，不是通用 CLI。
5. 依赖管理当前仅覆盖 `md2html/requirements.txt`，根目录尚无统一 `requirements.txt`。

## 目录结构

```text
Any2Screen/
├── doc2md/
│   └── doc2md.py
└── md2html/
│   ├── md2html.py
│   ├── README.md
│   └── requirements.txt
└── md2img/
    └── md2img.py
```

## 环境要求

- Python 3.8+
- Playwright（仅 `md2img.py` 和 `md2html.py --pdf/--wechat` 需要）

安装示例（按需）：

```bash
# md2html 基础依赖
pip install -r md2html/requirements.txt

# doc2md 依赖
pip install python-docx PyPDF2

# 如果要处理加密 docx
pip install msoffcrypto-tool

# 如果要导出 PDF 或使用 md2img
pip install playwright
playwright install chromium

# 如果要使用 watch 模式
pip install watchdog
```

## 快速使用

### 1) doc2md：文档转 Markdown

```bash
# 单文件
python3 doc2md/doc2md.py report.docx

# 批量目录
python3 doc2md/doc2md.py ./docs -o ./out

# 加密 docx
python3 doc2md/doc2md.py secret.docx -p "your-password" -o ./out
```

### 2) md2html：Markdown 转自包含 HTML（可选 PDF）

```bash
# 单文件
python3 md2html/md2html.py README.md

# 批量目录到指定输出目录
python3 md2html/md2html.py ./notes -o ./exports

# 同时导出 A4 PDF
python3 md2html/md2html.py ./notes -o ./exports --pdf

# 导出适合手机阅读的 WeChat PDF
python3 md2html/md2html.py ./notes -o ./exports --wechat

# 监听模式
python3 md2html/md2html.py ./notes --watch -o ./exports
```

### 3) md2img：Markdown 转长图

当前脚本内写死了输入输出路径（`INPUT` / `OUTPUT`），使用前先编辑 [md2img.py](/home/zj/workspace/KMS/scripts/Any2Screen/md2img/md2img.py) 顶部常量，再执行：

```bash
python3 md2img/md2img.py
```

## 已知限制

- `doc2md.py`
  - 主要做文本提取与基础标题映射，不保留复杂版式。
  - 对 PDF 的结构化语义（表格、多栏）不做深度还原。
- `md2img.py`
  - 非参数化 CLI，复用性较弱。
  - 样式目前内嵌在脚本里，定制需改代码。
- `md2html.py`
  - PDF 导出依赖本机 Chromium（Playwright 安装）。
  - `--wechat` 模式为阅读优化，不保证所有阅读器表现完全一致。

## 建议的下一步改进

1. 为 `md2img.py` 增加 argparse 参数（输入、输出、宽度、主题），和 `doc2md/md2html` 风格统一。
2. 在仓库根目录补充统一依赖文件（或 `pyproject.toml`），降低环境搭建成本。
3. 增加最小回归样例（至少覆盖中英文、表格、代码块、超长文档）。
