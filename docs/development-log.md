# Development Log

## 2026-06-02：模块架构重新构思

👤 用户：

> 现在重新构思一下软件的模块架构，主逻辑不变，pipeline微调，我想改为用any2html命名一个“预处理”模块，其中any可以是md、doc、docx等文档格式，他们做的是相同的工作就是把对应的格式的文档转换为html中间产物，写另一个html2Screen模块，作用是将html转换为A4 PDF、wechat pdf，更适合手机小屏浏览的html，以及图片（png或jpg）格式，这样后续开发优化升级可以更模块化更清晰。

🤖 助手：

这个架构方向是对的：把“输入格式解析”和“输出适配渲染”拆开，当前 `md2html` 同时承担了两件事，后续会越来越难维护。

建议改成两段 pipeline：

```text
任意文档输入
  ↓
any2html
  ↓
HTML 中间产物
  ↓
html2screen
  ↓
A4 PDF / WeChat PDF / mobile HTML / png / jpg
```

**建议模块结构**

```text
src/a2s/
├── cli.py
├── command_registry.py
├── pipeline.py
├── any2html/
│   ├── __init__.py
│   ├── base.py
│   ├── markdown.py
│   ├── text.py
│   ├── docx.py
│   └── pdf.py
└── html2screen/
    ├── __init__.py
    ├── base.py
    ├── templates.py
    ├── pdf.py
    ├── image.py
    └── mobile_html.py
```

**职责边界**

`any2html` 只负责把输入文档转成统一 HTML 中间产物：

```text
md -> html
txt -> html
docx -> html
pdf -> html
```

它不关心最终输出是 PDF、长图还是手机 HTML。

`html2screen` 只负责把 HTML 中间产物渲染成适合屏幕/分享的结果：

```text
html -> A4 PDF
html -> WeChat PDF
html -> mobile HTML
html -> png/jpeg
```

它不关心原始输入是 Markdown、Word 还是 PDF。

**CLI 可以这样收口**

主命令仍然保持 `any2screen`，用户不用理解内部 pipeline：

```bash
python3 scripts/any2screen.py convert input.md --html
python3 scripts/any2screen.py convert input.docx --pdf
python3 scripts/any2screen.py convert input.pdf --wechat
python3 scripts/any2screen.py convert input.md --img --format png --width 960
python3 scripts/any2screen.py convert input.md --html --pdf --wechat --img
```

也可以保留调试用子命令：

```bash
python3 scripts/any2screen.py any2html input.md -o intermediate.html
python3 scripts/any2screen.py html2screen intermediate.html --pdf --img
```

**迁移顺序**

1. 把当前 `md2html.py` 里的 Markdown 渲染逻辑迁到 `any2html/markdown.py`
2. 把当前 PDF 和 image 渲染逻辑迁到 `html2screen/pdf.py`、`html2screen/image.py`
3. 新增 `pipeline.py` 串接 `any2html -> html2screen`
4. 把 CLI 改成统一 `convert` 子命令
5. 删除 `md2html`、`md2img` 这类格式绑定命名，避免后续继续混乱

你现在这个想法比“把 md2html 和 md2img 合并成一个模块”更清晰：不是合并成大模块，而是拆成两个稳定阶段。当前未提交的 `md2html/md2img` 整合改动可以继续作为中间步骤，但下一步应该按这个架构拆分。

## 2026-06-02：架构调整方案落地

👤 用户：

> any2screen可以用这种方式实现pipeline，any2html和html2any仍能独立使用

👤 用户：

> 我以为可以保留doc2md的设计，这个模块有价值

🤖 助手：

最终采用的命令结构：

```bash
python3 scripts/any2screen.py <subcommand> [params] [args]
```

当前保留 4 个子命令：

- `convert`：主 pipeline，自动执行 `any2html -> html2screen`
- `any2html`：独立预处理阶段，输入文档转 HTML 中间产物
- `html2screen`：独立输出阶段，HTML 转 PDF / WeChat PDF / HTML / image
- `doc2md`：独立保留，DOCX / PDF / TXT 转 Markdown

实现结果：

- 新增 `src/a2s/convert_cli.py`
- 新增 `src/a2s/any2html_cli.py`
- 新增 `src/a2s/html2screen_cli.py`
- 新增 `src/a2s/pipeline.py`
- 新增 `src/a2s/any2html/markdown.py`
- 新增 `src/a2s/html2screen/renderers.py`
- 删除旧的 `src/a2s/md2html.py`
- 删除旧的 `src/a2s/md2img.py`
- 保留 `src/a2s/doc2md.py`
- 更新 `src/a2s/command_registry.py`，注册 `convert`、`any2html`、`html2screen`、`doc2md`
- 将旧 `docs/md2html.md` 替换为 `docs/pipeline.md`
- 将 `docs/md2html.requirements.txt` 重命名为 `docs/runtime.requirements.txt`

验证过的命令：

```bash
python3 scripts/any2screen.py --help
python3 scripts/any2screen.py doc2md --help
python3 scripts/any2screen.py convert README.md --pdf -o /tmp/out
python3 scripts/any2screen.py any2html README.md -o /tmp/stage
python3 scripts/any2screen.py html2screen /tmp/stage/README.html --pdf -o /tmp/final
python3 scripts/any2screen.py convert README.md --img --format jpeg --width 720 -o /tmp/out
```

Git 结果：

- 本次架构落地提交：`5aec3ed reconstruct architecture, modulized`
- 已推送到 `origin/main`
- 推送后工作区状态：clean
