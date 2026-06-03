# Intermediate Document Model

Any2Screen 当前运行时中间产物仍是 HTML。后续接入 DOCX、PDF、TXT 和快速预览时，需要一个更稳定的中间文档结构，用来承载不同输入格式解析后的共同语义。

## 目标

- 让 `any2html` 的输入解析结果不直接绑定 HTML 字符串。
- 让 Markdown、TXT、DOCX、PDF 共享同一套文档块结构。
- 让快速预览可以只渲染前几个块，而不是必须生成完整 HTML。
- 让 `html2screen` 继续以 HTML 为渲染入口，避免打断现有 pipeline。

## Pipeline Position

```text
input document
  -> parser
  -> IntermediateDocument
  -> HTML renderer
  -> html2screen
  -> HTML / A4 PDF / WeChat PDF / png / jpeg
```

短期兼容策略：

- Markdown 仍可直接走现有 `generate_html()`。
- 新格式优先解析为 `IntermediateDocument`。
- `IntermediateDocument` 先渲染成现有 HTML 模板，再交给 `html2screen`。

## Data Shape

建议先用 Python dataclass 表达，后续需要跨进程或 Web API 时再序列化成 JSON。

```python
@dataclass
class IntermediateDocument:
    title: str
    source_name: str
    language: str
    blocks: list[Block]
    metadata: dict[str, str]
```

`Block` 是文档内容的最小渲染单元。首版只覆盖 Web MVP 和导出需要的常见类型：

```python
Block =
    HeadingBlock
    | ParagraphBlock
    | ListBlock
    | TableBlock
    | ImageBlock
    | CodeBlock
    | QuoteBlock
    | HorizontalRuleBlock
```

## Block Types

### HeadingBlock

字段：

- `level`: `1` 到 `6`
- `text`: 纯文本标题
- `anchor`: 可选，供目录和页面内跳转使用

### ParagraphBlock

字段：

- `inlines`: 行内内容列表

行内内容首版支持：

- text
- strong
- emphasis
- code
- link
- line_break

### ListBlock

字段：

- `ordered`: 是否有序列表
- `items`: 列表项，每项包含 `blocks`

列表项使用 `blocks`，便于承载嵌套段落、代码块和子列表。

### TableBlock

字段：

- `headers`: 表头单元格
- `rows`: 表格行
- `alignments`: 可选，对齐方式

单元格首版存纯文本或行内内容，不承载复杂块。

### ImageBlock

字段：

- `src`: 图片路径或 data URI
- `alt`: 替代文本
- `title`: 可选标题

解析器负责把相对路径解析到可被 HTML 渲染器引用的位置。

### CodeBlock

字段：

- `language`: 可选语言标识
- `code`: 原始代码文本

### QuoteBlock

字段：

- `blocks`: 引用中的块列表

### HorizontalRuleBlock

无必需字段。

## Preview Rules

快速预览接口可以基于 `blocks` 截断：

- 默认取前 `20` 个块。
- 遇到超大表格时只取前 `20` 行，并标记 `truncated = true`。
- 图片保留占位和尺寸信息，具体加载策略由 Web 层决定。
- 代码块按行数截断，默认最多 `120` 行。

## Implementation Steps

1. 在 `src/a2s/any2html/document.py` 添加 dataclass。
2. 增加 `render_document_to_html(document)`，复用现有 HTML 模板和样式。
3. 增加 Markdown 到 `IntermediateDocument` 的解析适配，不替换当前 `generate_html()`。
4. 为 `IntermediateDocument` 到 HTML 增加单元测试和快照样例。
5. 后续 DOCX/PDF/TXT 解析器直接输出 `IntermediateDocument`。
