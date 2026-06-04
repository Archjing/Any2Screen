# Web MVP 微信 PDF 与长图导出能力计划

状态：pending / 待实施

## Summary

- Web MVP 后端新增微信阅读 PDF、PNG 长图、JPEG 长图导出 API。
- 前端新增“小屏/大屏”“生成长图”“图片格式”控件。
- “生成长图”点亮时，HTML/PDF 控件禁用；点灭后恢复 HTML/PDF 导出。
- 长图渲染参数使用 CSS viewport width，而不是手机物理像素宽度。

## Screen Presets

- `small` 小屏：`430px`
  - 覆盖现代大屏手机上限，兼容 iPhone Plus/Max 与大 Android 机型。
  - 比 390 更不容易让大手机内容显得过窄。
- `large` 大屏：`1080px`
  - 用于电脑、横屏平板、7 寸以上移动设备和大屏阅读分享。
  - 文件体积会高于 960px，但视觉清晰度更好。

文件命名：

- 小屏 PNG：`{stem}.small.png`
- 小屏 JPEG：`{stem}.small.jpeg`
- 大屏 PNG：`{stem}.large.png`
- 大屏 JPEG：`{stem}.large.jpeg`
- 微信 PDF：`{stem}.wechat.pdf`

## Backend Changes

- 新增导出函数：
  - `export_wechat_pdf_path(record) -> Path`
  - `export_image_path(record, screen, image_format) -> Path`
- 新增 API：
  - `GET /api/exports/{file_id}/wechat-pdf`
  - `GET /api/exports/{file_id}/image?screen=small|large&format=png|jpeg`
- API 行为：
  - `wechat-pdf` 返回 `application/pdf`。
  - `image` 返回 `image/png` 或 `image/jpeg`。
  - 不支持文件类型仍返回 `415`。
  - 长图宽度由 `screen` 决定，不允许前端传任意 width，避免超大图片拖垮服务。
  - 导出文件继续写入上传文件同目录。
- 失败处理：
  - Playwright 未安装或 Chromium 不可用时，返回明确错误。
  - Docker 部署若要启用长图 API，必须安装 Playwright Chromium。

## Frontend Changes

- 在 `src/web/static` 和 `demo-site` 同步新增导出配置区：
  - 屏幕目标：`小屏` / `大屏`
  - 输出格式：保留当前 `HTML/PDF` 滑动开关
  - 生成长图：开关
  - 图片格式：`PNG/JPEG`，仅在“生成长图”点亮时启用
- 交互规则：
  - 默认：`小屏` + `HTML` + `生成长图=off`
  - `生成长图=off`：HTML/PDF 开关可交互，图片格式控件禁用。
  - `生成长图=on`：HTML/PDF 开关禁用，图片格式控件启用，导出调用 `/api/exports/{file_id}/image?...`。
  - `PDF + 小屏`：导出微信阅读 PDF，即 `/api/exports/{file_id}/wechat-pdf`。
  - `PDF + 大屏`：导出标准 PDF，即 `/api/exports/{file_id}/pdf`。
  - `HTML + 小屏/大屏`：仍导出 HTML；本轮不为 HTML 生成不同宽度版本。
- i18n 文案：
  - 中文：`小屏`、`大屏`、`生成长图`、`图片格式`、`PNG`、`JPEG`。
  - 英文：`Small screen`、`Large screen`、`Long image`、`Image format`。
- 移动端约束：
  - 控件保持单手可触达。
  - 不依赖 hover。
  - 禁用态必须视觉明确。

## Docker / Deployment Changes

- 如果启用长图 API，Docker 镜像必须安装 Playwright Chromium：
  - `pip install` 保留 `playwright` 依赖或移动到可选依赖后显式安装 image extra。
  - Dockerfile 执行 `python -m playwright install --with-deps chromium` 或等价安装。
- 考虑镜像体积和构建速度：
  - Web MVP 可先实现 API 和本地能力。
  - ECS demo 若暂不想装 Chromium，可在部署文档标注“长图导出未启用”。
  - 若要线上可用，必须更新 Dockerfile 并验证 `image` API。

## Test Plan

- 后端单测：
  - 路由注册包含 `wechat-pdf` 和 `image`。
  - `wechat-pdf` 返回 PDF，文件名为 `.wechat.pdf`。
  - `image?screen=small&format=png` 返回 PNG，文件名为 `.small.png`。
  - `image?screen=large&format=jpeg` 返回 JPEG，文件名为 `.large.jpeg`。
  - 非法 `screen/format` 返回 422。
  - unsupported type 返回 415。
  - 导出文件写入上传文件同目录。
- 前端检查：
  - `node --check src/web/static/app.js`
  - `node --check demo-site/app.js`
  - 手工验证长图开关点亮后 HTML/PDF 控件禁用，点灭后恢复。
- 回归：
  - `python3 -m unittest discover -s tests`
  - 现有 HTML/PDF 上传、预览、导出不回归。

## Assumptions

- 小屏/大屏使用 CSS viewport width，而不是物理像素宽度。
- 小屏固定 `430px`，大屏固定 `1080px`。
- 长图格式允许用户选择 `PNG/JPEG`。
- HTML 导出本轮不区分小屏/大屏，只由阅读页面样式自适应。
- 微信阅读 PDF 只在 `PDF + 小屏` 时触发；`PDF + 大屏` 保持标准 A4 PDF。
