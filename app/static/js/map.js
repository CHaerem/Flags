// map.js - Simple world map with marker solution using local data
// This version works completely offline without API calls

let countryCoordinates = null;

// Load the country coordinates data as soon as the script loads
document.addEventListener("DOMContentLoaded", function () {
	// Load our local country coordinates JSON file
	fetch("/static/js/country-coordinates.json")
		.then((response) => response.json())
		.then((data) => {
			countryCoordinates = data;
			console.log("Country coordinates data loaded successfully");
		})
		.catch((error) => {
			console.error("Error loading country coordinates:", error);
		});
});

/**
 * Update the map to show the country location
 * @param {string} countryName - The name of the country to display
 */
function updateMap(countryName) {
	if (!countryName) return;

	const mapContainer = document.getElementById("map-container");
	const marker = document.getElementById("map-marker");
	const label = document.getElementById("country-label");

	if (!mapContainer || !marker || !label) return;

	// Initially hide marker and label until we have coordinates
	marker.style.display = "none";
	label.style.display = "none";

	// Get country coordinates from our local data
	const coordinates = getLocalCountryCoordinates(countryName);

	if (coordinates) {
		// Show marker and label
		marker.style.display = "block";
		label.style.display = "block";

		// Set the country name in the label
		label.textContent = countryName;

		// Convert geographic coordinates to pixel positions
		const position = geoToPixel(
			coordinates.lat,
			coordinates.lng,
			mapContainer.clientWidth,
			mapContainer.clientHeight
		);

		// Position the marker
		marker.style.left = position.x + "px";
		marker.style.top = position.y + "px";

		// Position the label above the marker
		label.style.left = position.x + "px";
		label.style.top = position.y - 30 + "px";
	}
}

/**
 * Get country coordinates from local data
 * @param {string} countryName - Name of the country
 * @returns {object|null} - Country coordinates and area, or null if not found
 */
function getLocalCountryCoordinates(countryName) {
	if (!countryCoordinates || !countryName) return null;

	// Try exact match
	if (countryCoordinates[countryName]) {
		return countryCoordinates[countryName];
	}

	// Try case-insensitive match
	const lowercaseInput = countryName.toLowerCase();
	for (const country in countryCoordinates) {
		if (country.toLowerCase() === lowercaseInput) {
			return countryCoordinates[country];
		}
	}

	// Try partial match (if a country contains the search term)
	for (const country in countryCoordinates) {
		if (
			country.toLowerCase().includes(lowercaseInput) ||
			lowercaseInput.includes(country.toLowerCase())
		) {
			return countryCoordinates[country];
		}
	}

	console.warn(`No coordinates found for country: ${countryName}`);
	return null;
}

/**
 * Convert geographic coordinates (latitude, longitude) to pixel positions
 * on the equirectangular projection map
 * @param {number} lat - Latitude (-90 to 90)
 * @param {number} lng - Longitude (-180 to 180)
 * @param {number} mapWidth - Width of the map container in pixels
 * @param {number} mapHeight - Height of the map container in pixels
 * @returns {object} - {x, y} pixel coordinates
 */
function geoToPixel(lat, lng, mapWidth, mapHeight) {
	// Convert longitude from -180...180 to 0...1
	const x = (lng + 180) / 360;

	// Convert latitude from -90...90 to 0...1
	// Using the Mercator-like projection formula for better visual accuracy
	const latRad = (lat * Math.PI) / 180;
	const mercN = Math.log(Math.tan(Math.PI / 4 + latRad / 2));
	const y = 0.5 - mercN / (2 * Math.PI);

	return {
		x: x * mapWidth,
		y: y * mapHeight,
	};
}

// Make updateMap available globally
window.updateMap = updateMap;
