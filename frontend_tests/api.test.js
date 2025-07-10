const fs = require('fs');
const { JSDOM } = require('jsdom');

// Load the API script text
const apiScript = fs.readFileSync('./app/static/js/api.js', 'utf8');

// Helper to execute API script in a JSDOM environment and return window.FlagAPI
function loadFlagAPI() {
  const dom = new JSDOM('<!DOCTYPE html><html></html>', { runScripts: 'dangerously' });
  dom.window.fetch = jest.fn((url) => {
    if (url.includes('flag.json')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({country:'France'}) });
    }
    if (url.includes('countries.json')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({France:{capital:['Paris']},Germany:{capital:['Berlin']}}) });
    }
    return Promise.reject(new Error('unexpected url '+url));
  });
  dom.window.eval(apiScript);
  return { window: dom.window, FlagAPI: dom.window.FlagAPI };
}

test('fetchLocalFlagData returns JSON', async () => {
  const { FlagAPI } = loadFlagAPI();
  const data = await FlagAPI.fetchLocalFlagData();
  expect(data.country).toBe('France');
});

test('fetchCountryData finds country', async () => {
  const { FlagAPI } = loadFlagAPI();
  const data = await FlagAPI.fetchCountryData('Germany');
  expect(data.capital[0]).toBe('Berlin');
});
