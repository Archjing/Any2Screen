async function loadApiStatus() {
  const status = document.querySelector("#api-status");
  const version = document.querySelector("#api-version");

  try {
    const [healthResponse, versionResponse] = await Promise.all([
      fetch("/api/health"),
      fetch("/api/version"),
    ]);
    if (!healthResponse.ok || !versionResponse.ok) {
      throw new Error("API request failed");
    }

    const health = await healthResponse.json();
    const api = await versionResponse.json();
    status.textContent = health.status;
    version.textContent = api.api_version;
  } catch (error) {
    status.textContent = "offline";
    version.textContent = "-";
  }
}

function bindUploadForm() {
  const form = document.querySelector("#upload-form");
  const input = document.querySelector("#file-input");
  const label = document.querySelector("#file-label");
  const dropZone = document.querySelector("#drop-zone");
  const result = document.querySelector("#upload-result");

  function setSelectedFile(file) {
    if (!file) {
      label.textContent = "Select or drop file";
      return;
    }
    const transfer = new DataTransfer();
    transfer.items.add(file);
    input.files = transfer.files;
    label.textContent = file.name;
    result.textContent = "";
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
    const file = event.dataTransfer.files[0];
    setSelectedFile(file);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const file = input.files[0];
    if (!file) {
      result.textContent = "请选择一个文件。";
      return;
    }

    const data = new FormData();
    data.append("file", file);
    result.textContent = "Uploading...";

    try {
      const response = await fetch("/api/files", {
        method: "POST",
        body: data,
      });
      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const payload = await response.json();
      result.innerHTML = `
        <dl>
          <div><dt>file_id</dt><dd>${payload.file_id}</dd></div>
          <div><dt>type</dt><dd>${payload.detected_type}</dd></div>
          <div><dt>size</dt><dd>${payload.size_bytes} B</dd></div>
          <div><dt>supported</dt><dd>${payload.supported ? "yes" : "no"}</dd></div>
        </dl>
      `;
    } catch (error) {
      result.textContent = "上传失败，请稍后重试。";
    }
  });
}

loadApiStatus();
bindUploadForm();
