# Any2Screen Pipeline

Any2Screen 当前采用两段式 pipeline：

```text
input document
  -> any2html
  -> HTML intermediate
  -> html2screen
  -> HTML / A4 PDF / WeChat PDF / png / jpeg
```

## Main Command

`convert` 是主入口，会自动执行 `any2html -> html2screen`。

```bash
python3 scripts/any2screen.py convert README.md
python3 scripts/any2screen.py convert README.md --pdf
python3 scripts/any2screen.py convert README.md --wechat
python3 scripts/any2screen.py convert README.md --img --width 960 --format png
python3 scripts/any2screen.py convert README.md --html --pdf --wechat --img -o exports/
```

## Independent Stages

`any2html` 只生成 HTML 中间产物：

```bash
python3 scripts/any2screen.py any2html README.md
python3 scripts/any2screen.py any2html README.md -o exports/
python3 scripts/any2screen.py any2html README.md -o exports/readme.html
```

`html2screen` 只处理 HTML 输出：

```bash
python3 scripts/any2screen.py html2screen README.html --pdf
python3 scripts/any2screen.py html2screen README.html --wechat
python3 scripts/any2screen.py html2screen README.html --img --width 960 --format png
python3 scripts/any2screen.py html2screen README.html --html --pdf --wechat --img -o exports/
```

## Output Rules

- No output flag: HTML only.
- Any output flag: only the requested format or formats.
- `-o/--output` is an output directory for generated files.
- `--format` controls image extension when `--img` is used.

## Dependencies

Dependencies are managed by `uv`:

```bash
uv sync
```

For image output, install Playwright Chromium once:

```bash
uv run playwright install chromium
```
