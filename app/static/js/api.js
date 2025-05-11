/**
 * api.js - Flag API interaction functions
 * Handles all data fetching and API interactions
 */

const FlagAPI = (function () {
	// Cache for country data after it's loaded
	let countryDataCache = null;

	/**
	 * Fetch flag data from local JSON file
	 * @returns {Promise<Object>} Flag data object
	 */
	async function fetchLocalFlagData() {
		try {
			// Add cache-busting timestamp to prevent browser caching
			const timestamp = new Date().getTime();
			const response = await fetch(`/static/data/flag.json?_=${timestamp}`);
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}
			return await response.json();
		} catch (error) {
			throw error;
		}
	}

	/**
	 * Loads all country data once and caches it
	 * @returns {Promise<Object>} Dictionary of all countries
	 */
	async function loadAllCountryData() {
		if (countryDataCache) {
			return countryDataCache;
		}

		try {
			// Add cache-busting timestamp to prevent browser caching during development
			const timestamp = new Date().getTime();
			const response = await fetch(
				`/static/data/countries.json?_=${timestamp}`
			);
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}

			countryDataCache = await response.json();
			return countryDataCache;
		} catch (error) {
			return {};
		}
	}

	/**
	 * Fetch country data from static JSON file
	 * @param {string} countryName - Name of the country
	 * @returns {Promise<Object>} Extended country data
	 */
	async function fetchCountryData(countryName) {
		try {
			const countries = await loadAllCountryData();

			// First try direct match
			if (countries[countryName]) {
				return countries[countryName];
			}

			// If not found, try case insensitive match
			const countryNameLower = countryName.toLowerCase();
			for (const [name, data] of Object.entries(countries)) {
				if (name.toLowerCase() === countryNameLower) {
					return data;
				}
			}

			// If still not found, try partial match
			for (const [name, data] of Object.entries(countries)) {
				if (
					name.toLowerCase().includes(countryNameLower) ||
					countryNameLower.includes(name.toLowerCase())
				) {
					return data;
				}
			}

			return null;
		} catch (error) {
			return null;
		}
	}

	/**
	 * Change the flag via Flask API
	 * @param {string} countryName - Name of the country to set
	 * @returns {Promise<string>} Response message
	 */
	async function changeFlag(countryName) {
		const flaskApiUrl = `/change-flag`;

		try {
			const response = await fetch(flaskApiUrl, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ country: countryName }),
			});

			const responseText = await response.text();

			if (!response.ok) {
				throw new Error(responseText);
			}

			return responseText;
		} catch (error) {
			throw error;
		}
	}

	// Public API
	return {
		fetchLocalFlagData,
		fetchCountryData,
		changeFlag,
		loadAllCountryData,
	};
})();

// Make available globally
window.FlagAPI = FlagAPI;
