// country_picker.js - Mobile-friendly country picker modal for flag selection

let CountryPicker = (function () {
  let countryList = [];
  let modal, searchInput, listContainer, closeButton;
  let onSelect = null;

  async function init(pickerButtonId, inputId, countriesUrl = '/static/data/countries.json') {
    countryList = await loadCountryList(countriesUrl);
    createModal();
    const pickerBtn = document.getElementById(pickerButtonId);
    const input = document.getElementById(inputId);
    if (pickerBtn) {
      pickerBtn.addEventListener('click', openModal);
    }
    if (input) {
      input.addEventListener('focus', closeModal); // hide if user types
    }
  }

  async function loadCountryList(url) {
    const res = await fetch(url);
    const data = await res.json();
    return Object.keys(data).map((name) => ({
      name: name,
      emoji: data[name].flag || '',
      region: data[name].region || '',
    })).sort((a, b) => a.name.localeCompare(b.name));
  }

  function createModal() {
    if (document.getElementById('country-picker-modal')) return;
    modal = document.createElement('div');
    modal.id = 'country-picker-modal';
    modal.className = 'country-picker-modal';
    modal.innerHTML = `
      <div class="picker-sheet">
        <div class="picker-header">
          <input type="text" id="picker-search" placeholder="Search country..." autocomplete="off" />
          <button id="picker-close" aria-label="Close">×</button>
        </div>
        <div class="picker-list" id="picker-list"></div>
      </div>
    `;
    document.body.appendChild(modal);
    searchInput = modal.querySelector('#picker-search');
    listContainer = modal.querySelector('#picker-list');
    closeButton = modal.querySelector('#picker-close');
    closeButton.onclick = closeModal;
    modal.onclick = (e) => { if (e.target === modal) closeModal(); };
    searchInput.oninput = () => renderList(searchInput.value);
    renderList('');
  }

  function openModal() {
    modal.style.display = 'flex';
    searchInput.value = '';
    renderList('');
    searchInput.focus();
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }

  function renderList(filter) {
    const query = filter.trim().toLowerCase();
    let matches = countryList;
    if (query) {
      matches = countryList.filter(c => c.name.toLowerCase().includes(query) || c.region.toLowerCase().includes(query));
    }
    // Use grid layout for flag selection
    listContainer.classList.add('grid');
    listContainer.innerHTML = matches.map(c => `
      <div class="picker-item grid" tabindex="0" data-name="${c.name}">
        <span class="picker-emoji">${c.emoji}</span>
        <span class="picker-name">${c.name}</span>
        <span class="picker-region">${c.region}</span>
      </div>
    `).join('');
    Array.from(listContainer.children).forEach(item => {
      item.onclick = () => selectCountry(item.getAttribute('data-name'));
      item.onkeydown = (e) => { if (e.key === 'Enter') selectCountry(item.getAttribute('data-name')); };
    });
  }

  function selectCountry(name) {
    if (onSelect && typeof onSelect === 'function') {
      onSelect(name);
    } else {
      // Default: set input value and close
      const input = document.getElementById('country-input');
      if (input) input.value = name;
      closeModal();
    }
  }

  function setOnSelect(fn) {
    onSelect = fn;
  }

  return { init, openModal, closeModal, setOnSelect };
})();

document.addEventListener('DOMContentLoaded', function () {
  CountryPicker.init('country-picker-btn', 'country-input');
});
