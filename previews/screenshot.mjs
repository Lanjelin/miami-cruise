/* Chromium/CDP screenshots of generated preview HTML. Node 22+; no npm packages.
 * Usage: SIZE OUT.png INPUT.html [SELECTOR NAME...]
 * Optional CDP_URL attaches to an existing headless browser. Otherwise BRAVE
 * selects the executable (default: brave-origin), started with a disposable profile.
 * Named outputs capture freshly rendered DOM panels, never existing PNG files.
 */
import { spawn } from 'node:child_process';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [size, output, input, selector, ...names] = process.argv.slice(2);
const [width, height] = (size || '').split(',').map(Number);
if (!width || !height || !output || !input || (!!selector !== !!names.length)) {
  throw Error('Usage: screenshot.mjs WIDTH,HEIGHT OUT.png INPUT.html [SELECTOR NAME...]');
}
let browser, browserError, profile, ws, endpoint = process.env.CDP_URL, target;
const pending = new Map();
let serial = 0;
try {
  if (!endpoint) {
    profile = await mkdtemp(path.join(tmpdir(), 'miami-browser-'));
    browser = spawn(process.env.BRAVE || 'brave-origin', ['--headless=new', '--no-sandbox', '--disable-gpu',
      '--remote-debugging-port=0', '--user-data-dir=' + profile, '--no-first-run', '--no-default-browser-check',
      '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });
    browser.on('error', error => { browserError = error; });
    const ready = path.join(profile, 'DevToolsActivePort');
    for (let attempt = 0; attempt < 100; attempt++) {
      if (browserError) throw browserError;
      if (browser.exitCode !== null) throw Error('Headless browser exited: ' + browser.exitCode);
      try { endpoint = 'http://127.0.0.1:' + (await readFile(ready, 'utf8')).split('\n')[0]; break; }
      catch (e) { if (e.code !== 'ENOENT') throw e; }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    if (!endpoint) throw Error('Headless browser did not become ready');
  }
  target = await (await fetch(endpoint + '/json/new?about:blank', { method: 'PUT' })).json();
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { ws.addEventListener('open', resolve, { once: true }); ws.addEventListener('error', reject, { once: true }); });
  ws.addEventListener('message', event => {
    const reply = JSON.parse(event.data), task = pending.get(reply.id);
    if (task) { clearTimeout(task.timer); pending.delete(reply.id); reply.error ? task.reject(Error(reply.error.message)) : task.resolve(reply.result); }
  });
  const call = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++serial;
    const timer = setTimeout(() => { pending.delete(id); reject(Error('CDP timeout: ' + method)); }, 15000);
    pending.set(id, { resolve, reject, timer }); ws.send(JSON.stringify({ id, method, params }));
  });
  const evaluate = async expression => {
    const result = await call('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (result.exceptionDetails) throw Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  };
  await call('Page.enable');
  await call('Network.enable');
  await call('Network.setCacheDisabled', { cacheDisabled: true });
  await call('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
  await call('Emulation.setDefaultBackgroundColorOverride', { color: { r: 0, g: 0, b: 0, a: 0 } });
  const url = pathToFileURL(path.resolve(input)).href;
  const navigation = await call('Page.navigate', { url });
  if (navigation.errorText) throw Error(navigation.errorText);
  await evaluate(`(async () => {
    if (document.readyState !== 'complete') await new Promise(resolve => addEventListener('load', resolve, { once: true }));
    await document.fonts.ready;
    await Promise.all([...document.images].map(image => image.decode()));
    const style = document.createElement('style'); style.textContent = 'html{scrollbar-width:none}::-webkit-scrollbar{display:none}'; document.head.append(style);
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  })()`);
  const save = async (filename, clip) => {
    const image = await call('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, ...(clip ? { clip } : {}) });
    await writeFile(filename, Buffer.from(image.data, 'base64'));
  };
  await save(output);
  if (selector) {
    const panels = await evaluate(`Array.from(document.querySelectorAll(${JSON.stringify(selector)}), element => {
      const r = element.getBoundingClientRect();
      return { x: Math.floor(r.x), y: Math.floor(r.y), width: Math.ceil(r.width), height: Math.ceil(r.height), scale: 1 };
    })`);
    if (panels.length !== names.length) throw Error(`Expected ${names.length} panels, found ${panels.length}: ${input}`);
    for (let i = 0; i < panels.length; i++) {
      if (panels[i].width <= 0 || panels[i].height <= 0) throw Error('Empty preview panel');
      await save(path.join(path.dirname(output), names[i] + '.png'), panels[i]);
    }
  }
} finally {
  for (const task of pending.values()) clearTimeout(task.timer);
  ws?.close();
  if (target && endpoint) await fetch(endpoint + '/json/close/' + target.id).catch(() => {});
  if (browser?.pid) {
    browser.kill();
    if (browser.exitCode === null) await new Promise(resolve => browser.once('exit', resolve));
  }
  if (profile) await rm(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
}
