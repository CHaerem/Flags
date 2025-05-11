// Flag Display Script
document.addEventListener("DOMContentLoaded", () => {
	const loadingContainer = document.getElementById("loading-container");
	const contentContainer = document.getElementById("content-container");

	// Elements to populate
	const countryElement = document.getElementById("country");
	const emojiElement = document.getElementById("emoji");
	const timestampElement = document.getElementById("timestamp");
	const capitalElement = document.getElementById("capital");
	const populationElement = document.getElementById("population");
	const regionElement = document.getElementById("region");
	const languagesElement = document.getElementById("languages");
	const currencyElement = document.getElementById("currency");
	const timezonesElement = document.getElementById("timezones");

	// Flag changer elements
	const countryInput = document.getElementById("country-input");
	const changeFlagBtn = document.getElementById("change-flag-btn");
	const statusMessage = document.getElementById("status-message");

	// Fetch flag data from data JSON
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
			showError("Could not load flag data");
			return null;
		}
	}

	// Fetch extended country data from RestCountries API
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
			// We'll still show the basic data even if extended data fails
			return null;
		}
	}

	// Format large numbers with commas
	function formatNumber(num) {
		return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
	}

	// Update the UI with country data
	function updateUI(localData, extendedData) {
		// Always available from local data
		countryElement.textContent = localData.country;
		emojiElement.textContent = localData.emoji;
		timestampElement.textContent = `Updated: ${localData.timestamp}`;

		// Basic capital from local data
		const basicCapital = localData.info?.replace("Capital: ", "") || "-";
		capitalElement.textContent = basicCapital;

		// If we have extended data, use it to update UI
		if (extendedData) {
			// Update capital (might have more accurate info)
			if (extendedData.capital && extendedData.capital.length > 0) {
				capitalElement.textContent = extendedData.capital.join(", ");
			}

			// Population
			if (extendedData.population) {
				populationElement.textContent = formatNumber(extendedData.population);
			}

			// Region and subregion
			if (extendedData.region) {
				regionElement.textContent = extendedData.subregion
					? `${extendedData.region} (${extendedData.subregion})`
					: extendedData.region;
			}

			// Languages
			if (extendedData.languages) {
				const languagesList = Object.values(extendedData.languages).join(", ");
				languagesElement.textContent = languagesList;
			}

			// Currencies
			if (extendedData.currencies) {
				const currencyList = Object.values(extendedData.currencies)
					.map((curr) => `${curr.name} (${curr.symbol || ""})`)
					.join(", ");
				currencyElement.textContent = currencyList;
			}

			// Timezones
			if (extendedData.timezones) {
				timezonesElement.textContent = extendedData.timezones.join(", ");
			}
		}

		// Show content, hide loading spinner
		loadingContainer.style.display = "none";
		contentContainer.style.display = "block";
	}

	function showError(message) {
		loadingContainer.innerHTML = `<div style="color: red; text-align: center;">${message}</div>`;
	}

	// Show status messages for flag changes
	function showStatusMessage(message, isError = false) {
		statusMessage.textContent = message;
		statusMessage.classList.remove("hidden", "success", "error");
		statusMessage.classList.add(isError ? "error" : "success");

		// Auto-hide after 5 seconds
		setTimeout(() => {
			statusMessage.classList.add("hidden");
		}, 5000);
	}

	// Function to change the flag via Flask API
	async function changeFlag(countryName) {
		try {
			const flaskApiUrl = `/change-flag?country=${encodeURIComponent(
				countryName
			)}`;

			changeFlagBtn.disabled = true;
			changeFlagBtn.textContent = "Updating...";

			const response = await fetch(flaskApiUrl, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
			});

			const responseText = await response.text();

			if (!response.ok) {
				throw new Error(`Error: ${responseText}`);
			}

			showStatusMessage(`Success! ${responseText}`);

			// Reload the flag data after a short delay to allow the backend to update
			setTimeout(async () => {
				const localData = await fetchLocalFlagData();
				if (localData) {
					const extendedData = await fetchCountryData(localData.country);
					updateUI(localData, extendedData);
				}
			}, 1500);
		} catch (error) {
			showStatusMessage(`Failed to change flag: ${error.message}`, true);
		} finally {
			changeFlagBtn.disabled = false;
			changeFlagBtn.textContent = "Update Flag";
		}
	}

	// Main function to initialize the page
	async function init() {
		const localData = await fetchLocalFlagData();
		if (localData) {
			const extendedData = await fetchCountryData(localData.country);
			updateUI(localData, extendedData);
		}

		// Set up event listeners for the flag changer
		changeFlagBtn.addEventListener("click", () => {
			const country = countryInput.value.trim();
			if (country) {
				changeFlag(country);
			} else {
				showStatusMessage("Please enter a country name", true);
			}
		});

		// Allow pressing enter in the input field
		countryInput.addEventListener("keypress", (event) => {
			if (event.key === "Enter") {
				const country = countryInput.value.trim();
				if (country) {
					changeFlag(country);
				} else {
					showStatusMessage("Please enter a country name", true);
				}
			}
		});
	}

	// Start the app
	init();
});
