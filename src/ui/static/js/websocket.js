// ── WebSocket client for S1T Litestar Workbench ─────────────────────────────
(function() {
  let ws = null;
  let port = null;

  function init(lessonPort) {
    port = lessonPort;
    const label = document.getElementById('ws-host-label');
    if (label) label.textContent = `ws://${window.location.hostname}:${port}`;
  }

  function getUrl() {
    const path = document.getElementById('ws-path-input')?.value || '/ws';
    return `ws://${window.location.hostname}:${port}${path}`;
  }

  function toggle() {
    if (ws && ws.readyState === WebSocket.OPEN) {
      disconnect();
    } else {
      connect();
    }
  }

  function connect() {
    if (ws) {
      ws.close();
      ws = null;
    }

    const url = getUrl();
    clearMessages();

    try {
      ws = new WebSocket(url);

      setConnectBtn('Connecting...', true);

      ws.onopen = () => {
        setConnectBtn('Disconnect', false);
        appendMessage('system', `Connected to ${url}`);
      };

      ws.onmessage = (event) => {
        appendMessage('received', event.data);
      };

      ws.onerror = () => {
        appendMessage('error', 'Connection error');
      };

      ws.onclose = (event) => {
        setConnectBtn('Connect', false);
        appendMessage('system', `Disconnected (code ${event.code})`);
        ws = null;
      };
    } catch (err) {
      appendMessage('error', `Failed to connect: ${err.message}`);
      setConnectBtn('Connect', false);
    }
  }

  function disconnect() {
    if (ws) {
      ws.close();
      ws = null;
    }
  }

  function send() {
    const input = document.getElementById('ws-send-input');
    if (!input) return;
    const text = input.value.trim();
    if (!text) return;

    if (!ws || ws.readyState !== WebSocket.OPEN) {
      appendMessage('error', 'Not connected');
      return;
    }

    ws.send(text);
    appendMessage('sent', text);
    input.value = '';
  }

  function sendText(text) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      appendMessage('error', 'Not connected');
      return;
    }
    ws.send(text);
    appendMessage('sent', text);
  }

  function appendMessage(type, text) {
    const container = document.getElementById('ws-messages');
    if (!container) return;

    const empty = container.querySelector('.ws-empty');
    if (empty) empty.remove();

    const now = new Date();
    const time = now.toTimeString().slice(0, 8);

    const el = document.createElement('div');
    el.className = `ws-msg ws-msg-${type}`;
    el.innerHTML =
      `<span class="ws-msg-time">${time}</span>` +
      `<span class="ws-msg-dir">${dirLabel(type)}</span>` +
      `<span class="ws-msg-text">${escapeHtml(text)}</span>`;

    container.appendChild(el);
    container.scrollTop = container.scrollHeight;
  }

  function clearMessages() {
    const container = document.getElementById('ws-messages');
    if (container) container.innerHTML = '<div class="ws-empty">Not connected</div>';
  }

  function setConnectBtn(label, disabled) {
    const btn = document.getElementById('ws-connect-btn');
    if (btn) {
      btn.textContent = label;
      btn.disabled = disabled;
    }
  }

  function dirLabel(type) {
    switch (type) {
      case 'sent':     return '↑';
      case 'received': return '↓';
      case 'system':   return '·';
      case 'error':    return '!';
      default:         return '';
    }
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  window.s1tWS = { init, connect, disconnect, toggle, send, sendText };
})();
