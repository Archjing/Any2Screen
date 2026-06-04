# D19 飞书协作与微信阅读导出预设重构计划

状态：pending / 暂不实施

## Summary

- D19 重新定义为“导出预设与飞书协作能力地基”，不一次性完成飞书账号登录和云文档自动写入。
- 最终产品目标明确：网页版/微信小程序支持飞书账号登录；登录后，用户可将 Any2Screen 转换结果通过飞书 OpenAPI 导入到飞书云文档。
- 当前 D19 交付最小可验证能力：微信阅读 PDF、飞书协作本地导出格式、飞书云文档 API 导入的数据格式准备和接口边界。

## Research Basis

- 飞书 OAuth 可获取 `user_access_token`，用于以用户身份调用 OpenAPI；授权码有效期短，token 需要刷新和安全存储。
  来源：https://open.feishu.cn/document/authentication-management/access-token/get-user-access-token
- 飞书云文档支持创建文档，但新版文档创建接口只支持标题和目录，不支持直接带内容创建。
  来源：https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/create
- 飞书支持将本地 Word、TXT、Markdown、Excel 等文件通过“上传文件/素材 -> 创建导入任务 -> 查询结果”导入为飞书云文档。
  来源：https://open.feishu.cn/document/server-docs/docs/drive-v1/import_task/create?lang=zh-CN
- 飞书云文档区分应用云空间和个人云空间；最终用户协作场景应优先使用 `user_access_token` 写入用户可见空间。
  来源：https://open.feishu.cn/document/ukTMukTMukTMukTM/uUDN04SN0QjL1QDN

## D19 Scope

- D19.1：微信阅读 PDF 预设
  - 新增 `GET /api/exports/{file_id}/wechat-pdf`。
  - 复用 `render_pdf(..., wechat=True)`。
  - 输出 `{stem}.wechat.pdf`，写入上传文件同目录。
  - 前端导出预设增加“微信阅读 PDF”。

- D19.2：飞书协作 Markdown 预设
  - 新增 `GET /api/exports/{file_id}/feishu-markdown`。
  - 输出 `{stem}.feishu.md`。
  - 内容来自当前文档解析后的 Markdown，作为后续飞书导入任务的主格式。
  - 这是未来调用飞书导入 API 的核心中间格式。

- D19.3：飞书协作 HTML 预设
  - 新增 `GET /api/exports/{file_id}/feishu-html`。
  - 输出 `{stem}.feishu.html`。
  - 用于人工复制、浏览器打开、飞书文档粘贴验证。
  - 不作为飞书 API 自动导入的主格式，避免 HTML 导入兼容性不确定。

- D19.4：导出预设 UI
  - 将当前 HTML/PDF 二选一开关改为预设选择控件。
  - 选项：`HTML`、`PDF`、`微信阅读 PDF`、`飞书协作 Markdown`、`飞书协作 HTML`。
  - `Export/导出` 按当前预设下载对应文件。
  - 前端统一使用 `src/web/static` 作为单一静态源。

- D19.5：飞书 API 集成边界文档
  - 新增文档说明最终飞书协作链路：
    `飞书登录 -> 获取 user_access_token -> 上传 Markdown 文件 -> 创建导入任务 -> 轮询任务结果 -> 返回云文档链接`。
  - 明确本轮 D19 不保存飞书 App Secret、不实现 OAuth、不调用飞书 OpenAPI。
  - 将登录、授权、token 存储、导入任务状态纳入后续任务。

## Future Feishu Account + Cloud Docs Plan

- `D31.1：飞书协作格式验证`：验证 `.feishu.md` 导入飞书云文档后的标题、列表、表格、代码块、图片占位表现。
- `D32.1：飞书账号登录方案`：设计 Web 与微信小程序的飞书 OAuth/绑定流程、token 生命周期、安全存储和退出登录。
- `D32.2：飞书云文档导入 API`：实现上传 Markdown、创建导入任务、查询导入结果、返回云文档链接。
- `D32.3：飞书导出任务状态`：将飞书导入过程接入 D22-D23 的任务状态、进度和错误详情。

最终产品行为：

- 未登录飞书：只能下载 `.feishu.md/.feishu.html`。
- 已登录飞书：导出按钮可选择“发送到飞书云文档”，成功后返回飞书文档链接。
- 微信小程序端不直接依赖 DOM 或浏览器 OAuth 假设，优先通过后端授权会话或可验证的账号绑定流程实现。

## Explicit Non-Goals For D19

- 不实现飞书账号登录。
- 不实现飞书 OAuth callback。
- 不保存用户 token 或 App Secret。
- 不调用飞书上传文件、创建导入任务、查询导入结果 API。
- 不自动创建飞书云文档。
- 不处理飞书权限申请、租户授权、企业自建应用发布。
- 不承诺飞书导入后的版式完全一致；真实兼容性验证放到 D31/D32。

## Acceptance Criteria

- 新增 3 个导出 API：`wechat-pdf`、`feishu-markdown`、`feishu-html`。
- 所有新增导出文件写入上传文件同目录。
- 前端能选择并下载新增预设。
- 现有 HTML/PDF 导出不回归。
- 测试覆盖路由注册、响应类型、文件名、同目录写入、unsupported type 415。
- 文档明确说明：D19 的飞书协作是“飞书导入格式准备”，不是“已接入飞书账号和云文档 API”。

## Assumptions

- 飞书云文档自动写入的主路径采用 Markdown 文件导入任务，而不是直接创建带内容的 docx 文档。
- 飞书账号登录和云文档导入必须依赖域名、HTTPS、飞书应用配置和 token 安全设计，不能塞进 D19。
- 微信小程序最终支持飞书账号登录，但实现方式需单独设计，不能直接套用 Web OAuth 页面逻辑。
