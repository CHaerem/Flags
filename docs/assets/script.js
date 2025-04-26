// Flag display frontend script for self-hosted Flask server
document.addEventListener("DOMContentLoaded", async () => {
	// Load & render
	try {
		const localData = await FlagApp.fetchLocalFlagData();
		const extData = await FlagApp.fetchCountryData(localData.country);
		FlagApp.updateUI(localData, extData);
	} catch (e) {
		console.error(e);
		FlagApp.showStatusMessage("Failed to load flag data", true);
		return;
	}

	// Always show the form now since we're self-hosting
	const flagChanger = document.getElementById("flag-changer");
	if (flagChanger) {
		flagChanger.style.display = "block";
	}

	// Wire up the change‐flag form
	const changeFlagBtn = document.getElementById("change-flag-btn");
	if (changeFlagBtn) {
		changeFlagBtn.addEventListener("click", async () => {
			const country = document.getElementById("country-input").value.trim();
			if (!country) return FlagApp.showStatusMessage("Enter a country", true);
			changeFlagBtn.textContent = "Updating…";
			try {
				const res = await fetch(
					`/change-flag?country=${encodeURIComponent(country)}`,
					{ method: "POST" }
				);
				const txt = await res.text();
				if (!res.ok) throw new Error(txt);
				FlagApp.showStatusMessage(`Success! ${txt}`);
				// refresh data
				const data = await FlagApp.fetchLocalFlagData();
				const ext = await FlagApp.fetchCountryData(data.country);
				FlagApp.updateUI(data, ext);
			} catch (err) {
				console.error(err);
				FlagApp.showStatusMessage(`Error: ${err.message}`, true);
			} finally {
				changeFlagBtn.textContent = "Update Flag";
			}
		});
	}
});
