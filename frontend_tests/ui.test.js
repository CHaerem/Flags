const fs = require('fs');
const { JSDOM } = require('jsdom');

// Load the UI script text
const uiScript = fs.readFileSync('./app/static/js/ui.js', 'utf8');

// Helper to execute the UI script in a JSDOM environment and return window.FlagUI
function loadFlagUI(html='<!DOCTYPE html><html><body></body></html>') {
  const dom = new JSDOM(html, { runScripts: 'dangerously', resources: 'usable' });
  dom.window.eval(uiScript);
  return { window: dom.window, FlagUI: dom.window.FlagUI };
}

test('formatNumber adds commas', () => {
  const { FlagUI } = loadFlagUI();
  expect(FlagUI.formatNumber(1234567)).toBe('1,234,567');
});

test('showStatusMessage updates DOM', () => {
  const { window, FlagUI } = loadFlagUI('<!DOCTYPE html><div id="status-message" class="hidden"></div>');
  const el = window.document.getElementById('status-message');
  FlagUI.showStatusMessage('hello');
  expect(el.textContent).toBe('hello');
  expect(el.classList.contains('success')).toBe(true);
  expect(el.classList.contains('hidden')).toBe(false);
});

test('updateUI populates fields', () => {
  const html = `<!DOCTYPE html><div id="country"></div><div id="emoji"></div><div id="timestamp"></div><div id="capital"></div>`;
  const { window, FlagUI } = loadFlagUI(html);
  const local = {country:'France',emoji:'🇫🇷',timestamp:'now',info:'Capital: Paris'};
  const extended = {population:67000000,region:'Europe',languages:{fra:'French'},currencies:{EUR:{name:'Euro',symbol:'€'}},timezones:['UTC+1'],capital:['Paris'],subregion:'Western Europe'};
  FlagUI.updateUI(local, extended);
  expect(window.document.getElementById('country').textContent).toBe('France');
  expect(window.document.getElementById('emoji').textContent).toBe('🇫🇷');
});
