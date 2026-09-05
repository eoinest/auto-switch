'use strict';
(() => {
  const $ = (id) => document.getElementById(id);
  let token = '', timer = null, busy = false, refreshing = false, connected = false, generation = 0, gateway = false, currentMode = 'daily';
  const demo = new URLSearchParams(location.search).has('demo');
  $('demo').hidden = !demo;
  if (demo) $('token').value = 'preview-device-key-only';

  async function api(path, body) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(path, {
        method: body === undefined ? 'GET' : 'POST',
        headers: {Authorization: `Bearer ${token}`, ...(body === undefined ? {} : {'Content-Type':'application/json'})},
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: controller.signal, cache: 'no-store'
      });
      const data = await response.json();
      if (!response.ok) throw new Error(response.status === 401 ? 'Device key wasn’t accepted. Check your key and reconnect.' : (data.error || 'The device could not complete this request.'));
      return data;
    } catch (error) {
      if (error.name === 'AbortError' || error instanceof TypeError) throw new Error('Device is unreachable. Check its power and your Wi-Fi connection.');
      throw error;
    } finally { clearTimeout(timeout); }
  }

  function render(data) {
    gateway = data.gateway === true;
    currentMode = data.mode || 'daily';
    $('mode-panel').hidden = !gateway;
    if (data.preview) $('demo').hidden = false;
    $('device-name').textContent = data.device || 'Auto Switch';
    $('connection').textContent = demo ? 'Simulated device' : 'On your network';
    if (gateway && !demo) $('connection').textContent = data.last_seen_age_s === null ? 'Waiting for first check-in' : `Last check-in ${data.last_seen_age_s}s ago`;
    if (gateway) {
      $('mode-badge').textContent = `${currentMode.toUpperCase()} REQUESTED`;
      $('mode-daily').setAttribute('aria-pressed', String(currentMode === 'daily'));
      $('mode-demo').setAttribute('aria-pressed', String(currentMode === 'demo'));
      const interval = String(data.poll_interval_s);
      if (![...$('interval').options].some((o) => o.value === interval)) $('interval').add(new Option(`${interval} seconds`, interval));
      if (document.activeElement !== $('interval')) $('interval').value = interval;
      $('mode-note').textContent = currentMode === 'daily' ? `Radio off between check-ins. Commands can wait ${data.poll_interval_s}s plus reconnection time. Mode changes apply at the next check-in.` : 'Requests quick polling at the next check-in. The radio stays on and uses more battery.';
      const latest = (data.commands || [])[0];
      $('queue-note').textContent = data.pending ? `${data.pending} command(s) awaiting completion.` : latest ? `Latest request: ${latest.status}${latest.error ? ' · ' + latest.error : ''}` : 'No commands waiting.';
    }
    const battery = data.battery;
    $('battery').textContent = battery && typeof battery.voltage === 'number'
      ? `${battery.low ? 'Low · ' : ''}${battery.voltage.toFixed(2)} V${typeof battery.percent === 'number' ? ` · ~${Math.round(battery.percent)}%` : ''}` : 'Not measured';
    $('schedule-status').textContent = data.clock_synced ? 'Clock synchronized. Configured UTC schedules are active.' : 'Clock not synchronized. Scheduled actions are paused.';
    $('channels').replaceChildren();
    for (const channel of data.channels || []) {
      const card = $('channel-template').content.firstElementChild.cloneNode(true);
      const state = ['on', 'off'].includes(channel.state) ? channel.state : 'unknown';
      card.dataset.state = state;
      card.querySelector('.channel-number').textContent = `SWITCH ${String(channel.id + 1).padStart(2, '0')}`;
      card.querySelector('.state').textContent = state === 'unknown' ? 'Unknown' : `Last sent: ${state}`;
      card.querySelector('h3').textContent = channel.name || `Switch ${channel.id + 1}`;
      const ready = channel.enabled === true && channel.calibrated === true && !battery?.low;
      card.querySelector('.channel-note').textContent = battery?.low ? 'Battery low · replace or recharge cells' : ready ? 'Ready for a brief press' : 'Calibrate and enable during setup';
      for (const button of card.querySelectorAll('button')) {
        button.disabled = !ready || busy;
        button.setAttribute('aria-label', `Turn ${channel.name || 'switch'} ${button.dataset.state}`);
        button.addEventListener('click', () => command(channel.id, button.dataset.state));
      }
      $('channels').appendChild(card);
    }
  }

  async function refresh() {
    if (busy || refreshing || !connected) return;
    refreshing = true;
    const current = generation;
    try { const data = await api('/api/status'); if (current !== generation) return; render(data); $('message').textContent = ''; }
    catch (error) {
      if (current !== generation) return;
      $('connection').textContent = 'Unavailable'; $('message').textContent = error.message;
      for (const button of $('channels').querySelectorAll('button')) button.disabled = true;
    }
    finally { refreshing = false; }
  }

  async function command(channel, state) {
    if (busy) return;
    busy = true;
    const current = ++generation;
    for (const button of $('channels').querySelectorAll('button')) button.disabled = true;
    $('message').textContent = `Sending ${state}…`;
    try {
      const result = await api('/api/switch', {channel, state});
      if (current === generation) $('message').textContent = result.status === 'queued' ? `Queued ${state} for the next check-in.` : `Sent ${state}.`;
    } catch (error) { if (current === generation) $('message').textContent = error.message + ' The physical switch position is unverified.'; }
    finally {
      busy = false;
      // Get confirmed command history without retrying a movement request.
      if (current === generation && connected) {
        try { const data = await api('/api/status'); if (current === generation) render(data); }
        catch (_) { if (current === generation) $('connection').textContent = 'Unavailable'; }
      }
    }
  }

  $('connect-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = event.currentTarget.querySelector('button');
    button.disabled = true; token = $('token').value.trim(); $('message').textContent = 'Connecting…';
    try {
      const data = await api('/api/status'); connected = true; generation++;
      $('connect').hidden = true; $('intro').hidden = true; $('device').hidden = false; $('token').value = '';
      render(data); $('message').textContent = '';
      clearInterval(timer); timer = setInterval(refresh, 2000);
    } catch (error) { token = ''; $('message').textContent = error.message; }
    finally { button.disabled = false; }
  });
  $('disconnect').addEventListener('click', () => {
    generation++; connected = false; token = ''; clearInterval(timer);
    $('device').hidden = true; $('connect').hidden = false; $('intro').hidden = false; $('channels').replaceChildren(); $('message').textContent = '';
  });
  async function setMode(mode) {
    if (busy || !gateway) return;
    const current = ++generation;
    busy = true;
    try {
      await api('/api/mode', {mode, poll_interval_s: Number($('interval').value)});
      if (current === generation) $('message').textContent = 'Saved. The device will pick this up at its next check-in.';
    } catch (error) { if (current === generation) $('message').textContent = error.message; }
    finally {
      busy = false;
      if (current === generation) {
        try { const data = await api('/api/status'); if (current === generation) render(data); } catch (_) {}
      }
    }
  }
  $('mode-daily').addEventListener('click', () => setMode('daily'));
  $('mode-demo').addEventListener('click', () => setMode('demo'));
  $('interval').addEventListener('change', () => setMode(currentMode));
})();
