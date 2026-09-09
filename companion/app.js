(() => {
  'use strict';
  const token = document.querySelector('meta[name=csrf]').content;
  const port = document.getElementById('port');
  const status = document.getElementById('status');
  const password = document.getElementById('password');
  const controls = Array.from(document.querySelectorAll('input,select,button'));
  let busy = false;
  function message(text, error = false) { status.textContent = text; status.dataset.error = String(error); }
  function lock(value) { busy = value; controls.forEach(control => { control.disabled = value; }); }
  async function refresh() {
    if (busy) return;
    lock(true);
    try {
      const response = await fetch('/ports', {cache: 'no-store', headers: {'X-AutoSwitch-CSRF': token}});
      const data = await response.json();
      if (!response.ok) throw new Error('refused');
      const previous = port.value;
      port.replaceChildren();
      data.ports.forEach(name => { const option = document.createElement('option'); option.value = name; option.textContent = name; port.append(option); });
      if (data.ports.includes(previous)) port.value = previous;
      message(data.ports.length ? 'Select your S2 Mini’s port.' : 'No USB serial ports found. Connect the S2 Mini with a data cable, then refresh.');
    } catch (_) { message('Could not load ports. Check that the local companion is running and reload this page.', true); }
    finally { lock(false); }
  }
  document.getElementById('refresh').addEventListener('click', refresh);
  document.getElementById('setup').addEventListener('submit', async event => {
    event.preventDefault();
    if (busy) return;
    const ssid = document.getElementById('ssid').value;
    if (!port.value || !ssid || ssid.includes('\0') || new TextEncoder().encode(ssid).length > 32 || !/^[\x20-\x7e]{8,63}$/.test(password.value)) {
      message('Select a USB port and enter a network name (1–32 bytes) and personal Wi-Fi password (8–63 printable ASCII characters).', true); return;
    }
    const body = JSON.stringify({port: port.value, ssid, password: password.value});
    password.value = '';
    lock(true);
    message('Saving over USB… Keep the cable connected.');
    try {
      const response = await fetch('/wifi', {method: 'POST', cache: 'no-store', redirect: 'error', headers: {'Content-Type': 'application/json', 'X-AutoSwitch-CSRF': token}, body});
      const data = await response.json();
      if (!response.ok || data.ok !== true) { message(data.error || 'Setup was not confirmed. Check the connection.', true); return; }
      message(data.rebooting ? 'Wi-Fi saved. The device is restarting. Join the same Wi-Fi on your phone and open http://auto-switch.local/.' : 'Wi-Fi saved, but restart was not confirmed. Press RST on the S2 Mini, then open http://auto-switch.local/ from the same Wi-Fi.');
    } catch (_) { message('Connection lost before confirmation. Settings may have been saved. Check the device before trying again.', true); }
    finally { lock(false); }
  });
  document.getElementById('quit').addEventListener('click', async () => {
    if (busy) return;
    lock(true);
    try {
      const response = await fetch('/quit', {method: 'POST', headers: {'X-AutoSwitch-CSRF': token}});
      if (!response.ok) { message('Wait for setup to finish before quitting.', true); lock(false); return; }
      password.value = '';
      message('Setup app closed. You can close this browser tab.');
    } catch (_) { message('The setup app is no longer reachable. You can close this tab.'); }
  });
  refresh();
})();
