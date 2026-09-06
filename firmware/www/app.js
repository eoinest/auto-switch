'use strict';
(() => {
  const $ = (id) => document.getElementById(id);
  let token = '', timer = null, busy = false, refreshing = false, connected = false;
  let generation = 0, lastData = null;
  let actionError = '', connectionError = '';
  const demo = new URLSearchParams(location.search).has('demo');

  async function api(path, body) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(path, {
        method: body === undefined ? 'GET' : 'POST',
        headers: {...(token ? {Authorization: `Bearer ${token}`} : {}), ...(body === undefined ? {} : {'Content-Type':'application/json'})},
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: controller.signal, cache: 'no-store'
      });
      const data = await response.json();
      if (!response.ok) {
        const error = new Error(response.status === 401 ? 'Device key wasn’t accepted.' : (data.error || 'Request failed.'));
        error.status = response.status;
        throw error;
      }
      return data;
    } catch (error) {
      if (error.name === 'AbortError' || error instanceof TypeError) throw new Error('Cannot reach the switch. Check its power and your Wi-Fi.');
      throw error;
    } finally { clearTimeout(timeout); }
  }

  function feedback() {
    const failed = (lastData?.commands || [])[0];
    $('message').textContent = connectionError || actionError ||
      (['failed', 'expired', 'uncertain'].includes(failed?.status) ? (failed.error || 'The last command failed.') : '');
  }

  function updateDisabled() {
    const unavailable = busy || !connected || !!connectionError;
    for (const channel of $('channels').children) {
      for (const button of channel.querySelectorAll('[data-state]')) button.disabled = unavailable || !!lastData?.busy || !!lastData?.calibration || channel.dataset.ready !== 'true';
      const recalibrate = channel.querySelector('.recalibrate');
      if (recalibrate) recalibrate.disabled = unavailable || !!lastData?.busy || !!lastData?.calibration;
    }
    for (const control of $('calibration').querySelectorAll('button, select')) control.disabled = unavailable || !!lastData?.busy;
    $('calibration-done').disabled = unavailable || !!lastData?.busy || lastData?.calibration?.tested !== true;
  }

  function render(data) {
    lastData = data;
    const channels = data.channels || [];
    const ids = channels.map((channel) => String(channel.id)).join(',');
    if ($('channels').dataset.ids !== ids) {
      $('channels').replaceChildren();
      $('channels').dataset.ids = ids;
      for (const channel of channels) {
        const element = $('channel-template').content.firstElementChild.cloneNode(true);
        for (const button of element.querySelectorAll('[data-state]')) {
          button.addEventListener('click', () => command(channel.id, button.dataset.state));
        }
        element.querySelector('.recalibrate').addEventListener('click', () => {
          perform('/api/calibration', {action: 'start', channel: channel.id});
        });
        $('channels').appendChild(element);
      }
    }
    channels.forEach((channel, index) => {
      const element = $('channels').children[index];
      const ready = channel.enabled === true && channel.calibrated === true && !data.battery?.low;
      element.dataset.ready = String(ready);
      element.querySelector('.recalibrate').hidden = data.calibration_available !== true;
      element.querySelector('.controls').setAttribute('aria-label', channel.name || `Switch ${channel.id + 1}`);
      element.querySelector('.channel-note').textContent = data.battery?.low ? 'Battery low. Replace or recharge it.' : ready ? '' : 'Recalibrate to set up the servo.';
      for (const button of element.querySelectorAll('[data-state]')) {
        button.setAttribute('aria-label', `Send ${button.dataset.state} command to ${channel.name || 'switch'}`);
      }
    });
    $('calibration').hidden = !data.calibration;
    if (data.calibration) {
      const draft = data.calibration;
      $('calibration-progress').textContent = `Center: ${draft.values.neutral} µs${draft.tested ? ' · Tested' : ' · Not moved yet'}`;
    }
    if (!channels.length) {
      $('channels').textContent = 'Waiting for the switch to check in.';
      delete $('channels').dataset.ids;
    }
    updateDisabled();
    feedback();
  }

  function handleError(error) {
    connectionError = error.message;
    if (error.status === 401) {
      generation++;
      connected = false;
      token = '';
      clearInterval(timer);
      $('device').hidden = true;
      $('connect').hidden = false;
    }
    updateDisabled();
    feedback();
  }

  async function refresh() {
    if (busy || refreshing || !connected) return;
    refreshing = true;
    const current = generation;
    try {
      const data = await api('/api/status');
      if (current !== generation) return;
      connectionError = '';
      render(data);
    } catch (error) { if (current === generation) handleError(error); }
    finally { refreshing = false; }
  }

  async function perform(path, body) {
    if (busy || !connected || connectionError) return;
    busy = true;
    actionError = '';
    const current = ++generation;
    updateDisabled();
    feedback();
    try { await api(path, body); }
    catch (error) {
      if (current === generation) {
        if (error.status === 401) handleError(error);
        else actionError = error.message;
      }
    } finally {
      busy = false;
      // Refresh command history; never retry a movement request automatically.
      if (current === generation && connected) {
        try {
          const data = await api('/api/status');
          if (current === generation) { connectionError = ''; render(data); }
        } catch (error) { if (current === generation) handleError(error); }
      }
      updateDisabled();
      feedback();
    }
  }

  function command(channel, state) { return perform('/api/switch', {channel, state}); }
  function calibrationAction(action, extra = {}) {
    if (!lastData?.calibration) return;
    return perform('/api/calibration', {action, revision: lastData.calibration.revision, ...extra});
  }
  $('calibration-minus').addEventListener('click', () => calibrationAction('nudge', {delta: -10}));
  $('calibration-plus').addEventListener('click', () => calibrationAction('nudge', {delta: 10}));
  $('calibration-test').addEventListener('click', () => calibrationAction('test'));
  $('calibration-cancel').addEventListener('click', () => calibrationAction('cancel'));
  $('calibration-done').addEventListener('click', () => calibrationAction('done'));
  function showConnection(data) {
    connected = true;
    generation++;
    connectionError = actionError = '';
    $('connect').hidden = true;
    $('device').hidden = false;
    $('token').value = '';
    render(data);
    clearInterval(timer);
    timer = setInterval(refresh, 2000);
  }

  $('connect-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = event.currentTarget.querySelector('button');
    button.disabled = true;
    token = $('token').value.trim();
    try { showConnection(await api('/api/status')); }
    catch (error) { token = ''; handleError(error); }
    finally { button.disabled = false; }
  });
  async function connect() {
    // Open servers opt into automatic connection. Other servers retain key entry.
    try {
      if (demo) token = 'preview-device-key-only';
      const access = demo ? {open_client: true} : await api('/api/access');
      if (access.open_client === true) showConnection(await api('/api/status'));
      else $('connect').hidden = false;
    } catch (error) {
      token = '';
      $('connect').hidden = false;
      // Older board servers may not expose /api/access; show their key form.
      if (error.status !== 401 && error.status !== 404) handleError(error);
    }
  }
  connect();
})();
