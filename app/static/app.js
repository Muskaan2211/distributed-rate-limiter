const log = document.getElementById('log');
const allowedEl = document.getElementById('allowed');
const blockedEl = document.getElementById('blocked');
const lastStatusEl = document.getElementById('lastStatus');
const remainingEl = document.getElementById('remaining');
let allowed = 0;
let blocked = 0;

function append(message) {
  const now = new Date().toLocaleTimeString();
  log.textContent = `[${now}] ${message}\n` + log.textContent;
}

async function loadStatus() {
  try {
    const [health, config] = await Promise.all([fetch('/health'), fetch('/api/v1/config')]);
    const cfg = await config.json();
    document.getElementById('serviceState').textContent = health.ok ? 'Gateway online' : 'Gateway degraded';
    document.getElementById('policy').textContent = `Active algorithm: ${cfg.algorithm}. Header identity: ${cfg.api_key_header}.`;
  } catch (error) {
    document.getElementById('serviceState').textContent = 'Service unavailable';
    document.getElementById('policy').textContent = error.message;
  }
}

async function sendRequest() {
  const res = await fetch('/api/v1/limited', { headers: { 'X-API-Key': 'dashboard-demo-user' } });
  const body = await res.json().catch(() => ({}));
  const remaining = res.headers.get('X-RateLimit-Remaining') ?? '-';
  if (res.status === 429) blocked += 1; else allowed += 1;
  allowedEl.textContent = allowed;
  blockedEl.textContent = blocked;
  lastStatusEl.textContent = res.status;
  remainingEl.textContent = remaining;
  append(`${res.status} ${res.statusText} | remaining=${remaining} | ${JSON.stringify(body)}`);
}

document.getElementById('sendOne').addEventListener('click', sendRequest);
document.getElementById('burst').addEventListener('click', async () => {
  append('Starting 25-request burst...');
  for (let i = 0; i < 25; i++) await sendRequest();
});
document.getElementById('reset').addEventListener('click', async () => {
  const res = await fetch('/api/v1/demo/reset', { method: 'POST' });
  append(`Reset demo state: ${JSON.stringify(await res.json())}`);
  allowed = 0; blocked = 0; allowedEl.textContent = '0'; blockedEl.textContent = '0';
});

loadStatus();
