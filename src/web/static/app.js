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

loadApiStatus();
