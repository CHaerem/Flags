/**
 * ui.js - Flag UI manipulation functions
 * Handles all DOM updates and UI interactions
 */

const FlagUI = (function () {
	/**
	 * Format large numbers with commas
	 * @param {number} num - The number to format
	 * @returns {string} Formatted number with commas
	 */
	function formatNumber(num) {
		return num.toLocaleString();
	}

	/**
	 * Update the UI with country data
	 * @param {Object} localData - Basic flag data
	 * @param {Object} extendedData - Extended country data
	 */
	function updateUI(localData, extendedData) {
		// Always available from local data
		document.getElementById("country").textContent = localData.country;
		document.getElementById("emoji").textContent = localData.emoji;
		document.getElementById(
			"timestamp"
		).textContent = `Updated: ${localData.timestamp}`;

		// Basic capital from local data
		const capitalElement = document.getElementById("capital");
		if (capitalElement) {
			const basicCapital = localData.info?.replace("Capital: ", "") || "-";
			capitalElement.textContent = basicCapital;
		}

		// If we have extended data, use it to update UI
		if (extendedData) {
			// Update capital (might have more accurate info)
			if (
				extendedData.capital &&
				extendedData.capital.length > 0 &&
				capitalElement
			) {
				capitalElement.textContent = extendedData.capital.join(", ");
			}

			// Population
			const populationElement = document.getElementById("population");
			if (populationElement && extendedData.population) {
				populationElement.textContent = formatNumber(extendedData.population);
			}

			// Region and subregion
			const regionElement = document.getElementById("region");
			if (regionElement && extendedData.region) {
				regionElement.textContent = extendedData.subregion
					? `${extendedData.region} (${extendedData.subregion})`
					: extendedData.region;
			}

			// Languages
			const languagesElement = document.getElementById("languages");
			if (languagesElement && extendedData.languages) {
				const languagesList = Object.values(extendedData.languages).join(", ");
				languagesElement.textContent = languagesList;
			}

			// Currencies
			const currencyElement = document.getElementById("currency");
			if (currencyElement && extendedData.currencies) {
				const currencyList = Object.values(extendedData.currencies)
					.map((curr) => `${curr.name} (${curr.symbol || ""})`)
					.join(", ");
				currencyElement.textContent = currencyList;
			}

			// Timezones
			const timezonesElement = document.getElementById("timezones");
			if (timezonesElement && extendedData.timezones) {
				timezonesElement.textContent = extendedData.timezones.join(", ");
			}
		}

		// Show content, hide loading spinner
		const loadingContainer = document.getElementById("loading-container");
		const contentContainer = document.getElementById("content-container");

		if (loadingContainer) {
			loadingContainer.style.display = "none";
		}

		if (contentContainer) {
			contentContainer.style.display = "block";
		}
	}

	/**
	 * Show status messages for flag changes
	 * @param {string} message - The message to display
	 * @param {boolean} isError - Whether this is an error message
	 */
	function showStatusMessage(message, isError = false) {
		const statusMessage = document.getElementById("status-message");
		if (!statusMessage) return;

		statusMessage.textContent = message;
		statusMessage.className = "status-message";

		if (isError) {
			statusMessage.classList.add("error");
		} else {
			statusMessage.classList.add("success");
		}

		statusMessage.classList.remove("hidden");

		// Hide the message after a delay
		setTimeout(() => {
			statusMessage.classList.add("hidden");
		}, 4000);
	}

	// Public API
	return {
		updateUI,
		showStatusMessage,
		formatNumber,
	};
})();

// Make available globally
window.FlagUI = FlagUI;
