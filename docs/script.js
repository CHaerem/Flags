// Flag Display Script
document.addEventListener('DOMContentLoaded', () => {
    const loadingContainer = document.getElementById('loading-container');
    const contentContainer = document.getElementById('content-container');
    
    // Elements to populate
    const countryElement = document.getElementById('country');
    const emojiElement = document.getElementById('emoji');
    const flagImgElement = document.getElementById('flag-img');
    const timestampElement = document.getElementById('timestamp');
    const capitalElement = document.getElementById('capital');
    const populationElement = document.getElementById('population');
    const regionElement = document.getElementById('region');
    const languagesElement = document.getElementById('languages');
    const currencyElement = document.getElementById('currency');
    const timezonesElement = document.getElementById('timezones');
    
    // Fetch flag data from local JSON
    async function fetchLocalFlagData() {
        try {
            const response = await fetch('data/flag.json');
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching flag data:', error);
            showError('Could not load flag data');
            return null;
        }
    }
    
    // Fetch extended country data from RestCountries API
    async function fetchCountryData(countryName) {
        try {
            const response = await fetch(`https://restcountries.com/v3.1/name/${encodeURIComponent(countryName)}?fields=name,capital,population,region,subregion,languages,currencies,flags,timezones`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            return data[0]; // Usually the first result is the exact match
        } catch (error) {
            console.error('Error fetching country data:', error);
            // We'll still show the basic data even if extended data fails
            return null;
        }
    }
    
    // Format large numbers with commas
    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
    
    // Update the UI with country data
    function updateUI(localData, extendedData) {
        // Always available from local data
        countryElement.textContent = localData.country;
        emojiElement.textContent = localData.emoji;
        timestampElement.textContent = `Updated: ${localData.timestamp}`;
        
        // Basic capital from local data
        const basicCapital = localData.info?.replace('Capital: ', '') || '-';
        capitalElement.textContent = basicCapital;
        
        // Get the country code from emoji to display flag image
        const countryCode = getCountryCodeFromName(localData.country);
        if (countryCode) {
            flagImgElement.src = `../flag_cache/${countryCode.toLowerCase()}.png`;
            flagImgElement.alt = `Flag of ${localData.country}`;
        } else {
            // Fallback to a flag API if we can't find the local file
            flagImgElement.src = `https://flagcdn.com/w320/${countryCode?.toLowerCase() || 'xx'}.png`;
        }
        
        // If we have extended data, use it to update UI
        if (extendedData) {
            // Update capital (might have more accurate info)
            if (extendedData.capital && extendedData.capital.length > 0) {
                capitalElement.textContent = extendedData.capital.join(', ');
            }
            
            // Population
            if (extendedData.population) {
                populationElement.textContent = formatNumber(extendedData.population);
            }
            
            // Region and subregion
            if (extendedData.region) {
                regionElement.textContent = extendedData.subregion ? 
                    `${extendedData.region} (${extendedData.subregion})` : 
                    extendedData.region;
            }
            
            // Languages
            if (extendedData.languages) {
                const languagesList = Object.values(extendedData.languages).join(', ');
                languagesElement.textContent = languagesList;
            }
            
            // Currencies
            if (extendedData.currencies) {
                const currencyList = Object.values(extendedData.currencies)
                    .map(curr => `${curr.name} (${curr.symbol || ''})`).join(', ');
                currencyElement.textContent = currencyList;
            }
            
            // Timezones
            if (extendedData.timezones) {
                timezonesElement.textContent = extendedData.timezones.join(', ');
            }
        }
        
        // Show content, hide loading spinner
        loadingContainer.style.display = 'none';
        contentContainer.style.display = 'block';
    }
    
    function showError(message) {
        loadingContainer.innerHTML = `<div style="color: red; text-align: center;">${message}</div>`;
    }
    
    // Get alpha-2 country code from country name (for flag image)
    function getCountryCodeFromName(countryName) {
        const countryMap = {
            "Afghanistan": "af", "Albania": "al", "Algeria": "dz", "Andorra": "ad",
            "Angola": "ao", "Antigua and Barbuda": "ag", "Argentina": "ar", "Armenia": "am",
            "Australia": "au", "Austria": "at", "Azerbaijan": "az", "Bahamas": "bs",
            "Bahrain": "bh", "Bangladesh": "bd", "Barbados": "bb", "Belarus": "by",
            "Belgium": "be", "Belize": "bz", "Benin": "bj", "Bhutan": "bt",
            "Bolivia": "bo", "Bosnia and Herzegovina": "ba", "Botswana": "bw", "Brazil": "br",
            "Brunei": "bn", "Bulgaria": "bg", "Burkina Faso": "bf", "Burundi": "bi",
            "Cambodia": "kh", "Cameroon": "cm", "Canada": "ca", "Cape Verde": "cv",
            "Central African Republic": "cf", "Chad": "td", "Chile": "cl", "China": "cn",
            "Colombia": "co", "Comoros": "km", "Congo": "cg", "Costa Rica": "cr",
            "Croatia": "hr", "Cuba": "cu", "Cyprus": "cy", "Czech Republic": "cz",
            "Denmark": "dk", "Djibouti": "dj", "Dominica": "dm", "Dominican Republic": "do",
            "East Timor": "tl", "Ecuador": "ec", "Egypt": "eg", "El Salvador": "sv",
            "Equatorial Guinea": "gq", "Eritrea": "er", "Estonia": "ee", "Ethiopia": "et",
            "Fiji": "fj", "Finland": "fi", "France": "fr", "Gabon": "ga",
            "Gambia": "gm", "Georgia": "ge", "Germany": "de", "Ghana": "gh",
            "Greece": "gr", "Grenada": "gd", "Guatemala": "gt", "Guinea": "gn",
            "Guinea-Bissau": "gw", "Guyana": "gy", "Haiti": "ht", "Honduras": "hn",
            "Hungary": "hu", "Iceland": "is", "India": "in", "Indonesia": "id",
            "Iran": "ir", "Iraq": "iq", "Ireland": "ie", "Israel": "il",
            "Italy": "it", "Ivory Coast": "ci", "Jamaica": "jm", "Japan": "jp",
            "Jordan": "jo", "Kazakhstan": "kz", "Kenya": "ke", "Kiribati": "ki",
            "Korea, North": "kp", "Korea, South": "kr", "Kuwait": "kw", "Kyrgyzstan": "kg",
            "Laos": "la", "Latvia": "lv", "Lebanon": "lb", "Lesotho": "ls",
            "Liberia": "lr", "Libya": "ly", "Liechtenstein": "li", "Lithuania": "lt",
            "Luxembourg": "lu", "Madagascar": "mg", "Malawi": "mw", "Malaysia": "my",
            "Maldives": "mv", "Mali": "ml", "Malta": "mt", "Marshall Islands": "mh",
            "Mauritania": "mr", "Mauritius": "mu", "Mexico": "mx", "Micronesia": "fm",
            "Moldova": "md", "Monaco": "mc", "Mongolia": "mn", "Montenegro": "me",
            "Morocco": "ma", "Mozambique": "mz", "Myanmar": "mm", "Namibia": "na",
            "Nauru": "nr", "Nepal": "np", "Netherlands": "nl", "New Zealand": "nz",
            "Nicaragua": "ni", "Niger": "ne", "Nigeria": "ng", "North Macedonia": "mk",
            "Norway": "no", "Oman": "om", "Pakistan": "pk", "Palau": "pw",
            "Panama": "pa", "Papua New Guinea": "pg", "Paraguay": "py", "Peru": "pe",
            "Philippines": "ph", "Poland": "pl", "Portugal": "pt", "Qatar": "qa",
            "Romania": "ro", "Russia": "ru", "Rwanda": "rw", "Saint Kitts and Nevis": "kn",
            "Saint Lucia": "lc", "Saint Vincent and the Grenadines": "vc", "Samoa": "ws",
            "San Marino": "sm", "Sao Tome and Principe": "st", "Saudi Arabia": "sa",
            "Senegal": "sn", "Serbia": "rs", "Seychelles": "sc", "Sierra Leone": "sl",
            "Singapore": "sg", "Slovakia": "sk", "Slovenia": "si", "Solomon Islands": "sb",
            "Somalia": "so", "South Africa": "za", "South Sudan": "ss", "Spain": "es",
            "Sri Lanka": "lk", "Sudan": "sd", "Suriname": "sr", "Sweden": "se",
            "Switzerland": "ch", "Syria": "sy", "Taiwan": "tw", "Tajikistan": "tj",
            "Tanzania": "tz", "Thailand": "th", "Togo": "tg", "Tonga": "to",
            "Trinidad and Tobago": "tt", "Tunisia": "tn", "Turkey": "tr", "Turkmenistan": "tm",
            "Tuvalu": "tv", "Uganda": "ug", "Ukraine": "ua", "United Arab Emirates": "ae",
            "United Kingdom": "gb", "United States": "us", "Uruguay": "uy", "Uzbekistan": "uz",
            "Vanuatu": "vu", "Vatican City": "va", "Venezuela": "ve", "Vietnam": "vn",
            "Yemen": "ye", "Zambia": "zm", "Zimbabwe": "zw"
        };
        
        return countryMap[countryName];
    }
    
    // Main function to initialize the page
    async function init() {
        const localData = await fetchLocalFlagData();
        if (localData) {
            const extendedData = await fetchCountryData(localData.country);
            updateUI(localData, extendedData);
        }
    }
    
    // Start the app
    init();
});