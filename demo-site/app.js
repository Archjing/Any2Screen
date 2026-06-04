const I18N = {
  zh: {
    apiChecking: "检查中",
    apiOffline: "离线",
    versionLabel: "版本",
    heroEyebrow: "API 优先的文档转换",
    uploadTitle: "上传文档",
    uploadDescription: "选择一个文件，服务端会返回统一的 file_id 和格式识别结果。",
    uploadButton: "上传",
    filePlaceholder: "选择或拖放文件",
    noFile: "请选择一个文件。",
    uploading: "上传中...",
    waitingUpload: "等待上传结果。",
    uploadFailed: "上传失败，请稍后重试。",
    previewUnavailable: "预览不可用。",
    previewTitle: "阅读预览",
    previewInitial: "上传 Markdown、TXT、DOCX 或 PDF 后会在这里显示轻量预览。",
    previewUnsupported: "当前只支持 Markdown、TXT、DOCX 和 PDF 预览。",
    previewGenerating: "正在生成预览...",
    previewFailed: "预览生成失败。",
    previewTruncated: (included, total) => `已显示 ${included}/${total} 个内容块。`,
    previewComplete: (total) => `已显示完整预览，共 ${total} 个内容块。`,
    exportButton: "导出",
    smallScreen: "小屏",
    largeScreen: "大屏",
    longImage: "生成长图",
    enterReading: "进入阅读",
    exitReading: "退出阅读",
    workflowUploadTitle: "上传",
    workflowUploadDescription: "文件上传接口会作为 Web、小程序和 App 的共同入口。",
    workflowPreviewTitle: "预览",
    workflowPreviewDescription: "快速预览复用服务端的轻量 HTML 生成能力。",
    workflowExportTitle: "导出",
    workflowExportDescription: "HTML、PDF、微信阅读 PDF 和长图导出统一走任务 API。",
    resultType: "类型",
    resultSize: "大小",
    resultSupported: "支持",
    resultYes: "是",
    resultNo: "否",
    switchLabel: "EN",
  },
  en: {
    apiChecking: "checking",
    apiOffline: "offline",
    versionLabel: "Version",
    heroEyebrow: "API-first document conversion",
    uploadTitle: "Upload a document",
    uploadDescription: "Choose a file. The server returns a unified file_id and detected format.",
    uploadButton: "Upload",
    filePlaceholder: "Select or drop file",
    noFile: "Please select a file.",
    uploading: "Uploading...",
    waitingUpload: "Waiting for upload result.",
    uploadFailed: "Upload failed. Please try again later.",
    previewUnavailable: "Preview is unavailable.",
    previewTitle: "Reader Preview",
    previewInitial: "Upload Markdown, TXT, DOCX, or PDF to show a lightweight preview here.",
    previewUnsupported: "Preview currently supports Markdown, TXT, DOCX, and PDF only.",
    previewGenerating: "Generating preview...",
    previewFailed: "Preview generation failed.",
    previewTruncated: (included, total) => `Showing ${included}/${total} content blocks.`,
    previewComplete: (total) => `Showing the full preview with ${total} content blocks.`,
    exportButton: "Export",
    smallScreen: "Small",
    largeScreen: "Large",
    longImage: "Long image",
    enterReading: "Enter reading",
    exitReading: "Exit reading",
    workflowUploadTitle: "Upload",
    workflowUploadDescription: "The file upload API is the shared entry for Web, mini programs, and apps.",
    workflowPreviewTitle: "Preview",
    workflowPreviewDescription: "Quick preview reuses the server-side lightweight HTML generator.",
    workflowExportTitle: "Export",
    workflowExportDescription: "HTML, PDF, WeChat reading PDF, and long-image exports use the task API.",
    resultType: "type",
    resultSize: "size",
    resultSupported: "supported",
    resultYes: "yes",
    resultNo: "no",
    switchLabel: "中文",
  },
};

I18N.zh.apiOk = "正常";
I18N.en.apiOk = "ok";

let currentLanguage = "zh";
let selectedFileName = "";
let currentPreviewState = { key: "previewInitial" };
let currentApiStatus = "apiChecking";
let lastUploadPayload = null;
let currentFileId = null;

function text(key, ...args) {
  const value = I18N[currentLanguage][key];
  return typeof value === "function" ? value(...args) : value;
}

function apiUrl(path) {
  return path;
}

function translatePage() {
  document.documentElement.lang = currentLanguage === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = text(element.dataset.i18n);
  });

  document.querySelector("#language-toggle").textContent = text("switchLabel");
  document.querySelector("#file-label").textContent = selectedFileName || text("filePlaceholder");
  document.querySelector("#api-status").textContent = text(currentApiStatus);
  renderPreviewStatus();
  renderUploadResult();
  updateReaderButton();
}

function setPreviewStatus(key, ...args) {
  currentPreviewState = { key, args };
  renderPreviewStatus();
}

function renderPreviewStatus() {
  const previewStatus = document.querySelector("#preview-status");
  previewStatus.textContent = text(currentPreviewState.key, ...(currentPreviewState.args || []));
}

function renderUploadResult() {
  const result = document.querySelector("#upload-result");
  if (!lastUploadPayload) {
    return;
  }

  result.innerHTML = `
    <dl>
      <div><dt>file_id</dt><dd>${lastUploadPayload.file_id}</dd></div>
      <div><dt>${text("resultType")}</dt><dd>${lastUploadPayload.detected_type}</dd></div>
      <div><dt>${text("resultSize")}</dt><dd>${lastUploadPayload.size_bytes} B</dd></div>
      <div><dt>${text("resultSupported")}</dt><dd>${lastUploadPayload.supported ? text("resultYes") : text("resultNo")}</dd></div>
    </dl>
  `;
}

function updateReaderButton() {
  const previewSurface = document.querySelector(".preview-surface");
  const readerToggle = document.querySelector("#reader-toggle");
  const isReading = previewSurface.classList.contains("is-reading");
  readerToggle.textContent = isReading ? text("exitReading") : text("enterReading");
}

async function loadApiStatus() {
  const status = document.querySelector("#api-status");
  const version = document.querySelector("#api-version");

  try {
    const [healthResponse, versionResponse] = await Promise.all([
      fetch(apiUrl("/api/health")),
      fetch(apiUrl("/api/version")),
    ]);
    if (!healthResponse.ok || !versionResponse.ok) {
      throw new Error("API request failed");
    }

    const health = await healthResponse.json();
    const api = await versionResponse.json();
    currentApiStatus = health.status === "ok" ? "apiOk" : "apiChecking";
    status.textContent = text(currentApiStatus);
    version.textContent = api.api_version;
  } catch (error) {
    currentApiStatus = "apiOffline";
    status.textContent = text("apiOffline");
    version.textContent = "-";
  }
}

function bindApp() {
  const form = document.querySelector("#upload-form");
  const input = document.querySelector("#file-input");
  const label = document.querySelector("#file-label");
  const dropZone = document.querySelector("#drop-zone");
  const result = document.querySelector("#upload-result");
  const previewFrame = document.querySelector("#preview-frame");
  const readerToggle = document.querySelector("#reader-toggle");
  const exportFormatToggle = document.querySelector("#export-format-toggle");
  const documentFormatSwitch = document.querySelector("#document-format-switch");
  const longImageToggle = document.querySelector("#long-image-toggle");
  const imageFormatOptions = document.querySelector("#image-format-options");
  const imageFormatInputs = document.querySelectorAll('input[name="image-format"]');
  const exportRun = document.querySelector("#export-run");
  const previewSurface = document.querySelector(".preview-surface");

  function selectedRadioValue(name) {
    const checked = document.querySelector(`input[name="${name}"]:checked`);
    return checked ? checked.value : "";
  }

  function syncExportControls() {
    const longImage = longImageToggle.checked;
    exportFormatToggle.disabled = longImage;
    documentFormatSwitch.classList.toggle("is-disabled", longImage);
    imageFormatOptions.classList.toggle("is-disabled", !longImage);
    imageFormatInputs.forEach((input) => {
      input.disabled = !longImage;
    });
  }

  function clearPreview() {
    currentFileId = null;
    previewFrame.removeAttribute("src");
    previewFrame.removeAttribute("srcdoc");
    readerToggle.disabled = true;
    exportRun.disabled = true;
    previewSurface.classList.remove("is-reading");
    document.body.classList.remove("reader-active");
    updateReaderButton();
  }

  function setSelectedFile(file) {
    if (!file) {
      selectedFileName = "";
      label.textContent = text("filePlaceholder");
      return;
    }

    const transfer = new DataTransfer();
    transfer.items.add(file);
    input.files = transfer.files;
    selectedFileName = file.name;
    label.textContent = file.name;
    result.textContent = "";
    lastUploadPayload = null;
    setPreviewStatus("previewInitial");
    clearPreview();
  }

  input.addEventListener("change", () => {
    setSelectedFile(input.files[0]);
  });

  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.classList.add("is-dragging");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.classList.remove("is-dragging");
    });
  });

  dropZone.addEventListener("drop", (event) => {
    setSelectedFile(event.dataTransfer.files[0]);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const file = input.files[0];
    if (!file) {
      result.textContent = text("noFile");
      return;
    }
    await uploadFile(file);
  });

  async function uploadFile(file) {
    const data = new FormData();
    data.append("file", file);
    result.textContent = text("uploading");
    setPreviewStatus("waitingUpload");
    clearPreview();

    try {
      const response = await fetch(apiUrl("/api/files"), {
        method: "POST",
        body: data,
      });
      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const payload = await response.json();
      lastUploadPayload = payload;
      renderUploadResult();
      await loadPreview(payload);
    } catch (error) {
      result.textContent = text("uploadFailed");
      setPreviewStatus("previewUnavailable");
    }
  }

  async function loadPreview(file) {
    if (!["markdown", "text", "docx", "pdf"].includes(file.detected_type)) {
      setPreviewStatus("previewUnsupported");
      return;
    }

    setPreviewStatus("previewGenerating");
    try {
      const response = await fetch(apiUrl(`/api/previews/${file.file_id}?blocks=20`));
      if (!response.ok) {
        throw new Error("Preview failed");
      }
      const preview = await response.json();
      clearPreview();
      currentFileId = file.file_id;
      previewFrame.src = apiUrl(`/api/previews/${file.file_id}/html?blocks=20`);
      readerToggle.disabled = false;
      exportRun.disabled = false;
      if (preview.truncated) {
        setPreviewStatus("previewTruncated", preview.included_blocks, preview.total_blocks);
      } else {
        setPreviewStatus("previewComplete", preview.total_blocks);
      }
    } catch (error) {
      setPreviewStatus("previewFailed");
    }
  }

  readerToggle.addEventListener("click", () => {
    const nextState = !previewSurface.classList.contains("is-reading");
    previewSurface.classList.toggle("is-reading", nextState);
    document.body.classList.toggle("reader-active", nextState);
    updateReaderButton();
    if (nextState) {
      previewSurface.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });

  exportRun.addEventListener("click", () => {
    if (!currentFileId) {
      return;
    }
    const format = exportFormatToggle.checked ? "pdf" : "html";
    const screen = selectedRadioValue("screen-target") || "small";
    if (longImageToggle.checked) {
      const imageFormat = selectedRadioValue("image-format") || "png";
      window.open(apiUrl(`/api/exports/${currentFileId}/image?screen=${screen}&format=${imageFormat}`), "_blank");
      return;
    }
    const endpoint = format === "pdf" && screen === "small" ? "wechat-pdf" : format;
    window.open(apiUrl(`/api/exports/${currentFileId}/${endpoint}`), "_blank");
  });

  longImageToggle.addEventListener("change", syncExportControls);

  document.querySelector("#language-toggle").addEventListener("click", () => {
    currentLanguage = currentLanguage === "zh" ? "en" : "zh";
    translatePage();
  });

  syncExportControls();
}

translatePage();
loadApiStatus();
bindApp();
