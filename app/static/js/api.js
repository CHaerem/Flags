/**
 * api.js - Flag API interaction functions
 * Handles all data fetching and API interactions
 */

const FlagAPI = (function () {
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
			console.error("Error fetching flag data:", error);
			throw error;
		}
	}

	/**
	 * Fetch extended country data from RestCountries API
	 * @param {string} countryName - Name of the country
	 * @returns {Promise<Object>} Extended country data
	 */
	async function fetchCountryData(countryName) {
		try {
			const response = await fetch(
				`https://restcountries.com/v3.1/name/${encodeURIComponent(
					countryName
				)}?fields=name,capital,population,region,subregion,languages,currencies,timezones`
			);
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}

			const data = await response.json();
			return data[0]; // Usually the first result is the exact match
		} catch (error) {
			console.error("Error fetching country data:", error);
			// We'll still show the basic data even if extended data fails
			return null;
		}
	}

	/**
	 * Change the flag via Flask API
	 * @param {string} countryName - Name of the country to set
	 * @returns {Promise<string>} Response message
	 */
	async function changeFlag(countryName) {
		const flaskApiUrl = `/change-flag?country=${encodeURIComponent(
			countryName
		)}`;

		try {
			const response = await fetch(flaskApiUrl, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
			});

			const responseText = await response.text();

			if (!response.ok) {
				throw new Error(responseText);
			}

			return responseText;
		} catch (error) {
			console.error("Error changing flag:", error);
			throw error;
		}
	}

	// Public API
	return {
		fetchLocalFlagData,
		fetchCountryData,
		changeFlag,
	};
})();

// Make available globally
window.FlagAPI = FlagAPI;
