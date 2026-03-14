// ── CodeMirror 6 Editor — S1T Litestar Workbench ─────────────────────────────
import {
  EditorView, basicSetup, EditorState,
  keymap, indentWithTab,
  python,
  HighlightStyle, syntaxHighlighting,
  tags,
} from "/static/js/cm-bundle.js";

// ── State ────────────────────────────────────────────────────────────────────
let files = {};
let activeFile = null;
let volumeId = null;
let chapterId = null;
let lessonId = null;
let view = null;
let fileModified = {};
let fileUnsaved = {};
let saveTimer = null;

// ── Japandi Dark Theme ───────────────────────────────────────────────────────
const japandiTheme = EditorView.theme({
  "&": {
    color: "var(--code-text)",
    backgroundColor: "var(--code-bg)",
    fontSize: "13px",
    fontFamily: "var(--font-mono)",
  },
  ".cm-content": {
    padding: "12px 0",
    caretColor: "var(--code-text)",
  },
  ".cm-gutters": {
    backgroundColor: "var(--code-bg)",
    color: "var(--code-line-nr)",
    border: "none",
    paddingLeft: "4px",
  },
  ".cm-activeLineGutter": {
    backgroundColor: "var(--code-line-hover)",
  },
  ".cm-activeLine": {
    backgroundColor: "var(--code-line-hover)",
  },
  "&.cm-focused .cm-cursor": {
    borderLeftColor: "var(--code-text)",
  },
  "&.cm-focused .cm-selectionBackground, .cm-selectionBackground": {
    backgroundColor: "rgba(178, 152, 217, 0.25)",
  },
  ".cm-line": {
    padding: "0 12px",
  },
}, { dark: true });

const japandiHighlight = HighlightStyle.define([
  { tag: tags.keyword, color: "var(--code-keyword)" },
  { tag: tags.string, color: "var(--code-string)" },
  { tag: [tags.number, tags.bool], color: "var(--code-number)" },
  { tag: tags.comment, color: "var(--code-comment)", fontStyle: "italic" },
  { tag: [tags.function(tags.definition(tags.variableName)), tags.function(tags.variableName)], color: "var(--code-function)" },
  { tag: tags.typeName, color: "var(--code-type)" },
  { tag: [tags.meta, tags.special(tags.string)], color: "var(--code-decorator)" },
  { tag: tags.operator, color: "var(--code-operator)" },
  { tag: tags.definition(tags.variableName), color: "var(--code-text)" },
  { tag: tags.variableName, color: "var(--code-text)" },
  { tag: tags.propertyName, color: "var(--code-function)" },
  { tag: tags.self, color: "var(--code-keyword)" },
]);

// ── Ctrl+S keymap ────────────────────────────────────────────────────────────
const saveKeymap = keymap.of([{
  key: "Mod-s",
  run() {
    saveCurrentFile();
    return true;
  },
}]);

// ── Change listener (unsaved tracking + debounced auto-save) ─────────────────
const changeListener = EditorView.updateListener.of(function (update) {
  if (update.docChanged && activeFile) {
    fileUnsaved[activeFile] = true;
    updateTabIndicators();

    clearTimeout(saveTimer);
    saveTimer = setTimeout(autoSaveAndRestart, 1500);
  }
});

// ── Build extensions list ────────────────────────────────────────────────────
function buildExtensions() {
  return [
    basicSetup,
    python(),
    keymap.of([indentWithTab]),
    saveKeymap,
    changeListener,
    japandiTheme,
    syntaxHighlighting(japandiHighlight),
  ];
}

// ── Create EditorState for a file ────────────────────────────────────────────
function createState(doc) {
  return EditorState.create({ doc, extensions: buildExtensions() });
}

// ── Init ─────────────────────────────────────────────────────────────────────
export function initEditor(containerId, filesData, initialFile, vol, ch, ls) {
  volumeId = vol;
  chapterId = ch;
  lessonId = ls;
  files = Object.assign({}, filesData);
  activeFile = initialFile;
  fileModified = {};
  fileUnsaved = {};

  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = "";

  view = new EditorView({
    state: createState(files[activeFile] || ""),
    parent: container,
  });

  setupTabs();
  updateTabIndicators();
}

// ── Tab switching ────────────────────────────────────────────────────────────
function setupTabs() {
  document.querySelectorAll(".code-tab").forEach(function (tab) {
    tab.removeAttribute("hx-get");
    tab.removeAttribute("hx-target");
    tab.removeAttribute("hx-swap");
    tab.addEventListener("click", function (e) {
      e.preventDefault();
      switchFile(tab.dataset.filename);
    });
  });
}

function switchFile(filename) {
  if (!files.hasOwnProperty(filename) || filename === activeFile) return;
  if (!view) return;

  files[activeFile] = view.state.doc.toString();
  activeFile = filename;
  view.setState(createState(files[filename] || ""));

  document.querySelectorAll(".code-tab").forEach(function (t) {
    t.classList.toggle("active", t.dataset.filename === filename);
  });
}

// ── Save ─────────────────────────────────────────────────────────────────────
async function saveCurrentFile() {
  if (!activeFile) return;

  const content = view ? view.state.doc.toString() : files[activeFile];
  files[activeFile] = content;

  const indicator = document.getElementById("save-indicator");

  try {
    const res = await fetch(
      "/api/workspace/" + volumeId + "/" + chapterId + "/" + lessonId + "/save",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: activeFile, content: content }),
      }
    );
    const data = await res.json();

    fileModified[activeFile] = data.modified === "true";
    fileUnsaved[activeFile] = false;
    updateTabIndicators();

    if (indicator) {
      indicator.textContent = "Saved";
      indicator.classList.add("visible");
      setTimeout(function () { indicator.classList.remove("visible"); }, 1500);
    }
  } catch (err) {
    if (indicator) {
      indicator.textContent = "Save failed";
      indicator.classList.add("visible", "error");
      setTimeout(function () { indicator.classList.remove("visible", "error"); }, 2000);
    }
  }
}

async function saveAllFiles() {
  if (view && activeFile) {
    files[activeFile] = view.state.doc.toString();
  }
  for (const filename in files) {
    if (!files.hasOwnProperty(filename)) continue;
    try {
      await fetch(
        "/api/workspace/" + volumeId + "/" + chapterId + "/" + lessonId + "/save",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ filename: filename, content: files[filename] }),
        }
      );
      fileUnsaved[filename] = false;
    } catch (_) {}
  }
  updateTabIndicators();
}

// ── Auto-save + restart server ───────────────────────────────────────────────
async function autoSaveAndRestart() {
  await saveCurrentFile();

  const row = document.querySelector("#server-controls [data-status]");
  if (!row || row.dataset.status !== "running") return;

  try {
    await fetch("/api/server/" + volumeId + "/" + chapterId + "/" + lessonId + "/stop", { method: "POST" });
    const res = await fetch("/api/server/" + volumeId + "/" + chapterId + "/" + lessonId + "/start", { method: "POST" });
    const html = await res.text();
    const ctrl = document.getElementById("server-controls");
    if (ctrl) {
      ctrl.innerHTML = html;
      htmx.process(ctrl);
    }
  } catch (_) {}
}

// ── Reset ────────────────────────────────────────────────────────────────────
async function resetWorkspace() {
  try {
    const res = await fetch(
      "/api/workspace/" + volumeId + "/" + chapterId + "/" + lessonId + "/reset",
      { method: "POST" }
    );
    const data = await res.json();

    files = Object.assign({}, data.files);
    fileModified = {};
    fileUnsaved = {};
    updateTabIndicators();

    if (view && activeFile !== null && files[activeFile] !== undefined) {
      view.setState(createState(files[activeFile]));
    }

    const indicator = document.getElementById("save-indicator");
    if (indicator) {
      indicator.textContent = "Reset";
      indicator.classList.add("visible");
      setTimeout(function () { indicator.classList.remove("visible"); }, 1500);
    }
  } catch (err) {
    console.error("Reset failed:", err);
  }
}

// ── Tab indicators (unsaved + modified) ──────────────────────────────────────
function updateTabIndicators() {
  let hasModified = false;
  document.querySelectorAll(".code-tab").forEach(function (tab) {
    const fname = tab.dataset.filename;
    const dot = tab.querySelector(".modified-dot");
    if (!dot) return;

    const unsaved = fileUnsaved[fname];
    const modified = fileModified[fname];

    if (unsaved) {
      dot.style.display = "inline-block";
      dot.style.backgroundColor = "var(--text-muted)";
    } else if (modified) {
      dot.style.display = "inline-block";
      dot.style.backgroundColor = "var(--accent-mustard)";
      hasModified = true;
    } else {
      dot.style.display = "none";
      dot.style.backgroundColor = "";
    }
  });
  const resetBtn = document.getElementById("btn-reset");
  if (resetBtn) resetBtn.style.visibility = hasModified ? "visible" : "hidden";
}

// ── Public API ───────────────────────────────────────────────────────────────
window.s1tEditor = {
  save: saveCurrentFile,
  saveAll: saveAllFiles,
  reset: resetWorkspace,
  switchFile: switchFile,
};
