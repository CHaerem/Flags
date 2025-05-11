/**
 * app.js - Main flag application
 * Initializes the flag display application and wires up event handlers
 */

const FlagApp = (function () {
	/**
	 * Initialize the application
	 * Sets up event listeners and loads initial data
	 */
	async function init() {
		try {
			// Load and render initial flag data
			const localData = await FlagAPI.fetchLocalFlagData();
			const extendedData = await FlagAPI.fetchCountryData(localData.country);
			FlagUI.updateUI(localData, extendedData);

			// Initialize map with country location - using global function exposed by module
			if (localData.country && window.updateMap) {
				setTimeout(() => window.updateMap(localData.country), 500);
			}

			// Always show the form since we're self-hosting
			const flagChanger = document.getElementById("flag-changer");
			if (flagChanger) {
				flagChanger.style.display = "block";
			}

			// Wire up event handlers
			setupEventListeners();
		} catch (error) {
			FlagUI.showStatusMessage("Failed to load flag data", true);
		}
	}

	/**
	 * Set up all event listeners
	 */
	function setupEventListeners() {
		const changeFlagBtn = document.getElementById("change-flag-btn");
		const countryInput = document.getElementById("country-input");

		if (changeFlagBtn) {
			changeFlagBtn.addEventListener("click", handleFlagChange);
		}

		if (countryInput) {
			countryInput.addEventListener("keypress", (event) => {
				if (event.key === "Enter") {
					handleFlagChange();
				}
			});
		}
	}

	/**
	 * Handle flag change request
	 */
	async function handleFlagChange() {
		const countryInput = document.getElementById("country-input");
		const changeFlagBtn = document.getElementById("change-flag-btn");

		if (!countryInput) return;

		const country = countryInput.value.trim();
		if (!country) {
			return FlagUI.showStatusMessage("Please enter a country name", true);
		}

		if (changeFlagBtn) {
			changeFlagBtn.textContent = "Updating...";
			changeFlagBtn.disabled = true;
		}

		try {
			const responseText = await FlagAPI.changeFlag(country);
			FlagUI.showStatusMessage(`Success! ${responseText}`);

			// Refresh data after successful update
			setTimeout(async () => {
				const localData = await FlagAPI.fetchLocalFlagData();
				const extendedData = await FlagAPI.fetchCountryData(localData.country);
				FlagUI.updateUI(localData, extendedData);

				// Update map with new country location - using global function exposed by module
				if (localData.country && window.updateMap) {
					window.updateMap(localData.country);
				}
			}, 1000);
		} catch (error) {
			FlagUI.showStatusMessage(`Error: ${error.message}`, true);
		} finally {
			if (changeFlagBtn) {
				changeFlagBtn.textContent = "Update Flag";
				changeFlagBtn.disabled = false;
			}
		}
	}

	// Return the public API
	return {
		init,
	};
})();

// Initialize the app when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", FlagApp.init);
