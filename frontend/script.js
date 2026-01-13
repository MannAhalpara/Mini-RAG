const API_BASE = "https://mini-rag-backendd.onrender.com";

// Tabs
const tabPaste = document.getElementById("tabPaste");
const tabUpload = document.getElementById("tabUpload");
const panelPaste = document.getElementById("panelPaste");
const panelUpload = document.getElementById("panelUpload");

// Global UI
const topStatus = document.getElementById("topStatus");
const resetBtn = document.getElementById("resetBtn");

// Paste ingest UI
const titleEl = document.getElementById("title");
const docTextEl = document.getElementById("docText");
const ingestBtn = document.getElementById("ingestBtn");
const ingestStatus = document.getElementById("ingestStatus");

// Upload ingest UI
const uploadTitleEl = document.getElementById("uploadTitle");
const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");

// Ask UI
const questionEl = document.getElementById("question");
const askBtn = document.getElementById("askBtn");
const askStatus = document.getElementById("askStatus");
const answerEl = document.getElementById("answer");
const sourcesEl = document.getElementById("sources");
const latencyEl = document.getElementById("latency");
const sourcesCountEl = document.getElementById("sourcesCount");

// ---------- Tabs ----------
tabPaste.addEventListener("click", () => {
  tabPaste.classList.add("active");
  tabUpload.classList.remove("active");
  panelPaste.classList.remove("hidden");
  panelUpload.classList.add("hidden");
});

tabUpload.addEventListener("click", () => {
  tabUpload.classList.add("active");
  tabPaste.classList.remove("active");
  panelUpload.classList.remove("hidden");
  panelPaste.classList.add("hidden");
});

// ---------- Reset ----------
resetBtn.addEventListener("click", async () => {
  topStatus.textContent = "Resetting...";
  try {
    const res = await fetch(`${API_BASE}/reset`, { method: "POST" });
    const data = await res.json();
    topStatus.textContent = `✅ ${data.message || "Reset done"}`;
  } catch (err) {
    console.error(err);
    topStatus.textContent = "❌ Reset failed";
  }
});

// ---------- Paste Ingest ----------
ingestBtn.addEventListener("click", async () => {
  ingestStatus.textContent = "Ingesting...";
  topStatus.textContent = "Working...";

  try {
    const res = await fetch(`${API_BASE}/ingest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: titleEl.value || "User Notes",
        text: docTextEl.value || ""
      })
    });

    const data = await res.json();
    ingestStatus.textContent = `✅ Inserted: ${data.inserted ?? 0}, Chunks: ${data.chunks ?? 0}`;
    topStatus.textContent = "Ready ✅";
  } catch (err) {
    console.error(err);
    ingestStatus.textContent = "❌ Ingest failed";
    topStatus.textContent = "❌ Error";
  }
});

// ---------- Upload Ingest ----------
uploadBtn.addEventListener("click", async () => {
  uploadStatus.textContent = "Uploading...";
  topStatus.textContent = "Working...";

  const file = fileInput.files[0];
  if (!file) {
    uploadStatus.textContent = "❌ Please choose a file.";
    topStatus.textContent = "Ready ✅";
    return;
  }

  try {
    const formData = new FormData();
    formData.append("title", uploadTitleEl.value || "Uploaded Document");
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData
    });

    const data = await res.json();

    if (data.error) {
      uploadStatus.textContent = `❌ ${data.error}`;
    } else {
      uploadStatus.textContent =
        `✅ ${data.filename} • chars: ${data.chars_extracted} • inserted: ${data.ingest_result?.inserted ?? 0}`;
    }

    topStatus.textContent = "Ready ✅";
  } catch (err) {
    console.error(err);
    uploadStatus.textContent = "❌ Upload failed";
    topStatus.textContent = "❌ Error";
  }
});

// ---------- Ask ----------
askBtn.addEventListener("click", async () => {
  askStatus.textContent = "Thinking...";
  topStatus.textContent = "Working...";
  answerEl.textContent = "Generating answer...";
  sourcesEl.innerHTML = "";
  latencyEl.textContent = "Latency: —";
  sourcesCountEl.textContent = "Sources: —";

  try {
    const res = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: questionEl.value || "" })
    });

    const data = await res.json();

    if (data.error) {
      askStatus.textContent = `❌ ${data.error}`;
      answerEl.textContent = "Please fix backend configuration.";
      topStatus.textContent = "❌ Error";
      return;
    }

    askStatus.textContent = "✅ Done";
    topStatus.textContent = "Ready ✅";

    answerEl.textContent = data.answer || "No answer generated.";
    latencyEl.textContent = `Latency: ${data.latency_ms ?? "-"} ms`;

    const sources = data.sources || [];
    sourcesCountEl.textContent = `Sources: ${sources.length}`;

    if (sources.length === 0) {
      sourcesEl.innerHTML = `<div class="sourceItem">No sources found (maybe threshold filtered them).</div>`;
      return;
    }

    sources.forEach((s) => {
      const div = document.createElement("div");
      div.className = "sourceItem";

      div.innerHTML = `
        <div class="sourceTop">
          <div class="sourceTitle">[${s.ref}] ${s.title}</div>
          <div class="sourceMeta">chunk ${s.chunk_index} • rerank ${Number(s.rerank_score).toFixed(4)}</div>
        </div>
        <div class="sourceText">${escapeHtml(s.text)}</div>
      `;
      sourcesEl.appendChild(div);
    });

  } catch (err) {
    console.error(err);
    askStatus.textContent = "❌ Ask failed";
    answerEl.textContent = "Something went wrong.";
    topStatus.textContent = "❌ Error";
  }
});

// Helpers
function escapeHtml(str) {
  return (str || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}
