/**
 * autocomplete.js - Country search autocomplete functionality
 * Provides real-time suggestions as user types in a country name
 */

const CountryAutocomplete = (function () {
	// Store all country names and their data for quick lookup
	let countryList = [];
	let currentFocus = -1;

	/**
	 * Initialize the autocomplete functionality
	 */
	async function init() {
		try {
			// Load all country data once
			const countries = await loadCountryData();

			if (countries) {
				// Extract country names and store them for autocomplete
				countryList = Object.keys(countries).map((name) => ({
					name: name,
					emoji: countries[name].flag || "",
				}));

				// Set up event listeners
				setupAutocomplete();
			}
		} catch (error) {
			console.error("Failed to initialize autocomplete:", error);
		}
	}

	/**
	 * Load country data for autocomplete
	 * @returns {Promise<Object>} Dictionary of country data
	 */
	async function loadCountryData() {
		try {
			// Use cache-busting timestamp
			const timestamp = new Date().getTime();
			const response = await fetch(
				`/static/data/countries.json?_=${timestamp}`
			);

			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}

			const data = await response.json();
			return data;
		} catch (error) {
			console.error("Error loading country data for autocomplete:", error);
			return null;
		}
	}

	/**
	 * Set up autocomplete functionality for the country input
	 */
	function setupAutocomplete() {
		const input = document.getElementById("country-input");
		const suggestionsContainer = document.getElementById("country-suggestions");

		if (!input || !suggestionsContainer) {
			console.error("Required DOM elements not found for autocomplete");
			return;
		}

		// Add input event listener for showing suggestions
		input.addEventListener("input", function () {
			const value = this.value.trim();

			// Close any already open suggestion lists
			closeAllLists();

			// If empty input, don't show suggestions
			if (!value) return;

			// Filter countries that match the input
			const matches = filterCountries(value);

			// Show matching countries as suggestions
			displaySuggestions(matches, value, suggestionsContainer);
		});

		// Add keyboard navigation for suggestions
		input.addEventListener("keydown", function (e) {
			handleKeyboardNavigation(e, suggestionsContainer);
		});

		// Close suggestions when clicking elsewhere
		document.addEventListener("click", function (e) {
			if (e.target !== input) {
				closeAllLists();
			}
		});
	}

	/**
	 * Filter countries based on input
	 * @param {string} input - User input to match against
	 * @returns {Array} Array of matching country objects
	 */
	function filterCountries(input) {
		if (!countryList.length) {
			console.warn("No country data available for filtering");
			return [];
		}

		const inputLower = input.toLowerCase();

		// Filter countries that start with the input text first
		const startsWithMatches = countryList.filter((country) =>
			country.name.toLowerCase().startsWith(inputLower)
		);

		// Then add countries that contain the input text (but don't start with it)
		const containsMatches = countryList.filter(
			(country) =>
				country.name.toLowerCase().includes(inputLower) &&
				!country.name.toLowerCase().startsWith(inputLower)
		);

		// Combine both arrays, prioritizing startsWith matches
		return [...startsWithMatches, ...containsMatches].slice(0, 10); // Limit to 10 suggestions
	}

	/**
	 * Display filtered country suggestions
	 * @param {Array} matches - Array of matching country objects
	 * @param {string} userInput - Original user input
	 * @param {HTMLElement} container - Container for suggestions
	 */
	function displaySuggestions(matches, userInput, container) {
		// Show suggestions if we have matches
		if (matches.length > 0) {
			container.innerHTML = ""; // Clear previous suggestions

			matches.forEach((match) => {
				// Create a suggestion item
				const div = document.createElement("div");

				// Add country emoji if available
				if (match.emoji) {
					const emojiSpan = document.createElement("span");
					emojiSpan.className = "autocomplete-emoji";
					emojiSpan.textContent = match.emoji;
					div.appendChild(emojiSpan);
				}

				// Add country name with highlighting for matching text
				const userInputLower = userInput.toLowerCase();
				const countryNameLower = match.name.toLowerCase();
				const matchIndex = countryNameLower.indexOf(userInputLower);

				if (matchIndex >= 0) {
					// Text before match
					if (matchIndex > 0) {
						div.appendChild(
							document.createTextNode(match.name.substring(0, matchIndex))
						);
					}

					// Matched text (bold)
					const matchedText = document.createElement("strong");
					matchedText.textContent = match.name.substring(
						matchIndex,
						matchIndex + userInput.length
					);
					div.appendChild(matchedText);

					// Text after match
					if (matchIndex + userInput.length < match.name.length) {
						div.appendChild(
							document.createTextNode(
								match.name.substring(matchIndex + userInput.length)
							)
						);
					}
				} else {
					// If no direct match found (shouldn't happen with our filtering)
					div.textContent = match.name;
				}

				// Store the country name as data attribute
				div.dataset.value = match.name;

				// Add click event to select this suggestion
				div.addEventListener("click", function () {
					document.getElementById("country-input").value = this.dataset.value;
					closeAllLists();
				});

				container.appendChild(div);
			});

			container.style.display = "block";
		} else {
			container.innerHTML = "";
			container.style.display = "none";
		}
	}

	/**
	 * Handle keyboard navigation for suggestions
	 * @param {KeyboardEvent} e - Keyboard event
	 * @param {HTMLElement} container - Container with suggestions
	 */
	function handleKeyboardNavigation(e, container) {
		const items = container.getElementsByTagName("div");
		if (!items.length) return;

		// Down arrow
		if (e.key === "ArrowDown") {
			e.preventDefault();
			currentFocus++;
			addActive(items);
		}
		// Up arrow
		else if (e.key === "ArrowUp") {
			e.preventDefault();
			currentFocus--;
			addActive(items);
		}
		// Enter key
		else if (e.key === "Enter") {
			e.preventDefault();
			if (currentFocus > -1) {
				if (items[currentFocus]) {
					items[currentFocus].click();
				}
			}
		}
		// Tab key
		else if (e.key === "Tab") {
			if (currentFocus > -1) {
				if (items[currentFocus]) {
					e.preventDefault();
					items[currentFocus].click();
				}
			} else if (items[0]) {
				e.preventDefault();
				items[0].click();
			}
		}
	}

	/**
	 * Add active class to current focused item
	 * @param {HTMLCollection} items - Collection of suggestion items
	 */
	function addActive(items) {
		if (!items) return;

		// Remove active class from all items
		removeActive(items);

		// Ensure focus stays within bounds
		if (currentFocus >= items.length) currentFocus = 0;
		if (currentFocus < 0) currentFocus = items.length - 1;

		// Add active class to focused item
		if (items[currentFocus]) {
			items[currentFocus].classList.add("autocomplete-active");

			// Ensure the active item is visible in the scrollable container
			const container = document.getElementById("country-suggestions");
			const activeItem = items[currentFocus];

			if (container && activeItem) {
				// Check if active item is outside visible area
				const containerRect = container.getBoundingClientRect();
				const activeRect = activeItem.getBoundingClientRect();

				if (activeRect.bottom > containerRect.bottom) {
					// If below visible area, scroll down
					container.scrollTop += activeRect.bottom - containerRect.bottom;
				} else if (activeRect.top < containerRect.top) {
					// If above visible area, scroll up
					container.scrollTop -= containerRect.top - activeRect.top;
				}
			}
		}
	}

	/**
	 * Remove active class from all items
	 * @param {HTMLCollection} items - Collection of suggestion items
	 */
	function removeActive(items) {
		for (let i = 0; i < items.length; i++) {
			items[i].classList.remove("autocomplete-active");
		}
	}

	/**
	 * Close all autocomplete lists
	 */
	function closeAllLists() {
		const container = document.getElementById("country-suggestions");
		if (container) {
			container.innerHTML = "";
			container.style.display = "none";
		}
		currentFocus = -1;
	}

	// Return public API
	return {
		init,
	};
})();

// Initialize autocomplete when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
	CountryAutocomplete.init();
});
