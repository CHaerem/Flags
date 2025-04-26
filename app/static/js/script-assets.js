// Flag display frontend script for self-hosted Flask server
document.addEventListener("DOMContentLoaded", async () => {
	// Load & render
	try {
		const localData = await fetchLocalFlagData();
		const extData = await fetchCountryData(localData.country);
		updateUI(localData, extData);
	} catch (e) {
		console.error(e);
		showStatusMessage("Failed to load flag data", true);
		return;
	}

	// Always show the form since we're self-hosting
	const flagChanger = document.getElementById("flag-changer");
	if (flagChanger) {
		flagChanger.style.display = "block";
	}

	// Wire up the change‐flag form
	const changeFlagBtn = document.getElementById("change-flag-btn");
	if (changeFlagBtn) {
		changeFlagBtn.addEventListener("click", async () => {
			const country = document.getElementById("country-input").value.trim();
			if (!country) return showStatusMessage("Enter a country", true);
			changeFlagBtn.textContent = "Updating…";
			try {
				const res = await fetch(
					`/change-flag?country=${encodeURIComponent(country)}`,
					{ method: "POST" }
				);
				const txt = await res.text();
				if (!res.ok) throw new Error(txt);
				showStatusMessage(`Success! ${txt}`);
				// refresh data
				const data = await fetchLocalFlagData();
				const ext = await fetchCountryData(data.country);
				updateUI(data, ext);
			} catch (err) {
				console.error(err);
				showStatusMessage(`Error: ${err.message}`, true);
			} finally {
				changeFlagBtn.textContent = "Update Flag";
			}
		});
	}
});

// Helper functions
async function fetchLocalFlagData() {
	const res = await fetch(`/static/data/flag.json?_${Date.now()}`);
	if (!res.ok) throw new Error("Flag JSON not found");
	return res.json();
}

async function fetchCountryData(name) {
	const res = await fetch(
		`https://restcountries.com/v3.1/name/${encodeURIComponent(
			name
		)}?fields=name,capital,population,region,subregion,languages,currencies,timezones`
	);
	if (!res.ok) return null;
	const [data] = await res.json();
	return data;
}

function formatNumber(n) {
	return n.toLocaleString();
}

function updateUI(localData, extData) {
	document.getElementById("country").textContent = localData.country;
	document.getElementById("emoji").textContent = localData.emoji;
	document.getElementById(
		"timestamp"
	).textContent = `Updated: ${localData.timestamp}`;

	// Basic capital info
	const capitalEl = document.getElementById("capital");
	if (capitalEl) {
		capitalEl.textContent = localData.info
			? localData.info.replace("Capital: ", "")
			: "-";
	}

	if (extData) {
		if (extData.capital && capitalEl) {
			capitalEl.textContent = extData.capital.join(", ");
		}

		const populationEl = document.getElementById("population");
		if (populationEl && extData.population) {
			populationEl.textContent = formatNumber(extData.population);
		}

		const regionEl = document.getElementById("region");
		if (regionEl && extData.region) {
			regionEl.textContent =
				extData.region + (extData.subregion ? ` (${extData.subregion})` : "");
		}

		const languagesEl = document.getElementById("languages");
		if (languagesEl && extData.languages) {
			languagesEl.textContent = Object.values(extData.languages).join(", ");
		}

		const currencyEl = document.getElementById("currency");
		if (currencyEl && extData.currencies) {
			const lst = Object.values(extData.currencies).map(
				(c) => `${c.name} (${c.symbol || ""})`
			);
			currencyEl.textContent = lst.join(", ");
		}

		const timezonesEl = document.getElementById("timezones");
		if (timezonesEl && extData.timezones) {
			timezonesEl.textContent = extData.timezones.join(", ");
		}
	}

	const loadingEl = document.getElementById("loading-container");
	const contentEl = document.getElementById("content-container");

	if (loadingEl) loadingEl.style.display = "none";
	if (contentEl) contentEl.style.display = "block";
}

function showStatusMessage(msg, isError = false) {
	const el = document.getElementById("status-message");
	if (!el) return;

	el.textContent = msg;
	el.classList.toggle("error", isError);
	el.classList.toggle("success", !isError);
	el.classList.remove("hidden");
	setTimeout(() => el.classList.add("hidden"), 4000);
}
