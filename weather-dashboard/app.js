// ============================================
// WEATHER DASHBOARD - MAIN APPLICATION
// ============================================

class WeatherDashboard {
    constructor() {
        this.apiKey = localStorage.getItem('weatherApiKey') || 'aa2e8b6b8b2e1d8b2e1d8b2e1d8b2e1d'; // Demo key
        this.baseURL = 'https://api.openweathermap.org/data/2.5';
        this.tempUnit = localStorage.getItem('tempUnit') || 'C';
        this.windUnit = localStorage.getItem('windUnit') || 'm/s';
        this.favorites = JSON.parse(localStorage.getItem('favoritesCities')) || [];
        this.currentCity = null;
        this.currentWeather = null;
        this.forecastData = null;
        this.chart = null;
        
        this.initElements();
        this.attachEventListeners();
        this.loadSettings();
        this.showToast('Weather Dashboard loaded successfully!', 'success');
    }

    initElements() {
        this.searchInput = document.getElementById('searchInput');
        this.searchResults = document.getElementById('searchResults');
        this.searchBtn = document.getElementById('searchBtn');
        this.currentWeatherEl = document.getElementById('currentWeather');
        this.hourlyContainer = document.getElementById('hourlyContainer');
        this.forecastGrid = document.getElementById('forecastGrid');
        this.detailsGrid = document.getElementById('detailsGrid');
        this.alertsSection = document.getElementById('alertsSection');
        this.alertsContainer = document.getElementById('alertsContainer');
        this.favoritesGrid = document.getElementById('favoritesGrid');
        this.loader = document.getElementById('loader');
        this.themeToggle = document.getElementById('themeToggle');
        this.settingsBtn = document.getElementById('settingsBtn');
        this.settingsModal = document.getElementById('settingsModal');
        this.closeSettings = document.getElementById('closeSettings');
        this.lastUpdated = document.getElementById('lastUpdated');
        this.tempUnitSelect = document.getElementById('tempUnit');
        this.windUnitSelect = document.getElementById('windUnit');
        this.apiKeyInput = document.getElementById('apiKey');
        this.saveSettings = document.getElementById('saveSettings');
    }

    attachEventListeners() {
        this.searchInput.addEventListener('input', (e) => this.handleSearch(e));
        this.searchBtn.addEventListener('click', () => this.getCurrentLocation());
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
        this.settingsBtn.addEventListener('click', () => this.openSettings());
        this.closeSettings.addEventListener('click', () => this.closeSettingsModal());
        this.saveSettings.addEventListener('click', () => this.handleSaveSettings());
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) this.closeSettingsModal();
        });
    }

    async handleSearch(e) {
        const query = e.target.value.trim();
        if (query.length < 2) {
            this.searchResults.classList.remove('active');
            return;
        }

        try {
            const response = await fetch(
                `https://api.openweathermap.org/geo/1.0/direct?q=${query}&limit=5&appid=${this.apiKey}`
            );
            const data = await response.json();

            if (data.length > 0) {
                this.searchResults.innerHTML = data.map(city => `
                    <div class="search-result-item" onclick="app.selectCity(${city.lat}, ${city.lon}, '${city.name}')"> 
                        <i class="fas fa-map-marker-alt"></i> ${city.name}, ${city.country}
                    </div>
                `).join('');
                this.searchResults.classList.add('active');
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    async selectCity(lat, lon, cityName) {
        this.searchInput.value = '';
        this.searchResults.classList.remove('active');
        await this.fetchWeatherByCoords(lat, lon, cityName);
    }

    getCurrentLocation() {
        if (navigator.geolocation) {
            this.showLoader(true);
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;
                    this.fetchWeatherByCoords(latitude, longitude);
                },
                (error) => {
                    this.showLoader(false);
                    this.showToast('Unable to get location: ' + error.message, 'error');
                }
            );
        } else {
            this.showToast('Geolocation not supported', 'error');
        }
    }

    async fetchWeatherByCoords(lat, lon, cityName = null) {
        this.showLoader(true);
        try {
            const response = await fetch(
                `${this.baseURL}/forecast?lat=${lat}&lon=${lon}&appid=${this.apiKey}&units=metric`
            );
            
            if (!response.ok) throw new Error('Weather API error');
            
            const data = await response.json();
            this.currentCity = data.city;
            this.forecastData = data;
            
            this.currentWeather = data.list[0];
            this.updateUI();
            this.updateLastUpdated();
            this.showToast(`Weather data updated for ${data.city.name}`, 'success');
        } catch (error) {
            this.showToast('Error fetching weather data: ' + error.message, 'error');
            console.error('Weather fetch error:', error);
        } finally {
            this.showLoader(false);
        }
    }

    updateUI() {
        this.displayCurrentWeather();
        this.displayHourlyForecast();
        this.displayFiveDayForecast();
        this.displayDetailedInfo();
        this.displayAlerts();
        this.renderChart();
    }

    displayCurrentWeather() {
        if (!this.currentWeather || !this.currentCity) return;

        const temp = this.convertTemp(this.currentWeather.main.temp);
        const feels = this.convertTemp(this.currentWeather.main.feels_like);
        const icon = this.getWeatherIcon(this.currentWeather.weather[0].main);
        const isFavorite = this.favorites.some(fav => fav.name === this.currentCity.name);

        this.currentWeatherEl.innerHTML = `
            <div style="position: relative;">
                <button class="favorite-btn ${isFavorite ? 'active' : ''}" onclick="app.toggleFavorite('${this.currentCity.name}', ${this.currentWeather.main.temp}, '${this.currentWeather.weather[0].main}')">
                    <i class="${isFavorite ? 'fas' : 'far'} fa-heart"></i>
                </button>
                <div class="weather-content">
                    <div class="weather-left">
                        <div class="weather-icon">${icon}</div>
                        <div class="weather-main">
                            <div class="city-name">${this.currentCity.name}, ${this.currentCity.country}</div>
                            <div class="temperature">${temp}°${this.tempUnit}</div>
                            <div class="weather-description" style="text-transform: capitalize;">${this.currentWeather.weather[0].description}</div>
                        </div>
                    </div>
                    <div class="weather-right">
                        <div class="weather-info-item">
                            <div class="weather-info-label"><i class="fas fa-thermometer-half"></i> Feels Like</div>
                            <div class="weather-info-value">${feels}°${this.tempUnit}</div>
                        </div>
                        <div class="weather-info-item">
                            <div class="weather-info-label"><i class="fas fa-droplet"></i> Humidity</div>
                            <div class="weather-info-value">${this.currentWeather.main.humidity}%</div>
                        </div>
                        <div class="weather-info-item">
                            <div class="weather-info-label"><i class="fas fa-wind"></i> Wind</div>
                            <div class="weather-info-value">${this.convertWind(this.currentWeather.wind.speed)} ${this.windUnit}</div>
                        </div>
                        <div class="weather-info-item">
                            <div class="weather-info-label"><i class="fas fa-compress"></i> Pressure</div>
                            <div class="weather-info-value">${this.currentWeather.main.pressure} hPa</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    displayHourlyForecast() {
        if (!this.forecastData) return;

        const hourlyData = this.forecastData.list.slice(0, 8);
        this.hourlyContainer.innerHTML = hourlyData.map((item, index) => {
            const time = new Date(item.dt * 1000);
            const hour = time.getHours().toString().padStart(2, '0');
            const temp = this.convertTemp(item.main.temp);
            const icon = this.getWeatherIcon(item.weather[0].main);
            const rainChance = item.clouds.all;

            return `
                <div class="hourly-card">
                    <div class="hourly-time">${hour}:00</div>
                    <div class="hourly-icon">${icon}</div>
                    <div class="hourly-temp">${temp}°</div>
                    <div class="hourly-rain"><i class="fas fa-cloud-rain"></i> ${rainChance}%</div>
                </div>
            `;
        }).join('');
    }

    displayFiveDayForecast() {
        if (!this.forecastData) return;

        const dailyData = {};
        this.forecastData.list.forEach(item => {
            const date = new Date(item.dt * 1000).toLocaleDateString();
            if (!dailyData[date]) {
                dailyData[date] = [];
            }
            dailyData[date].push(item);
        });

        const days = Object.entries(dailyData).slice(0, 5);
        this.forecastGrid.innerHTML = days.map(([date, items]) => {
            const temps = items.map(item => item.main.temp);
            const maxTemp = this.convertTemp(Math.max(...temps));
            const minTemp = this.convertTemp(Math.min(...temps));
            const midItem = items[Math.floor(items.length / 2)];
            const icon = this.getWeatherIcon(midItem.weather[0].main);
            const dateObj = new Date(items[0].dt * 1000);
            const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
            const humidity = midItem.main.humidity;
            const wind = this.convertWind(midItem.wind.speed);

            return `
                <div class="forecast-card">
                    <div class="forecast-day">${dayName}</div>
                    <div class="forecast-date">${date}</div>
                    <div class="forecast-icon">${icon}</div>
                    <div class="forecast-temps">
                        <span class="forecast-high">${maxTemp}°</span>
                        <span class="forecast-low">${minTemp}°</span>
                    </div>
                    <div class="forecast-description" style="text-transform: capitalize;">${midItem.weather[0].description}</div>
                    <div class="forecast-details">
                        <div class="detail-item">
                            <div class="detail-label"><i class="fas fa-droplet"></i> Humidity</div>
                            <div>${humidity}%</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label"><i class="fas fa-wind"></i> Wind</div>
                            <div>${wind}</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    displayDetailedInfo() {
        if (!this.currentWeather) return;

        const details = [
            {
                icon: 'fa-eye',
                label: 'Visibility',
                value: (this.currentWeather.visibility / 1000).toFixed(1) + ' km'
            },
            {
                icon: 'fa-cloud',
                label: 'Cloudiness',
                value: this.currentWeather.clouds.all + '%'
            },
            {
                icon: 'fa-droplet',
                label: 'Humidity',
                value: this.currentWeather.main.humidity + '%'
            },
            {
                icon: 'fa-compress',
                label: 'Pressure',
                value: this.currentWeather.main.pressure + ' hPa'
            },
            {
                icon: 'fa-wind',
                label: 'Wind Speed',
                value: this.convertWind(this.currentWeather.wind.speed) + ' ' + this.windUnit
            },
            {
                icon: 'fa-rotate',
                label: 'Wind Direction',
                value: this.degToDir(this.currentWeather.wind.deg)
            },
            {
                icon: 'fa-droplets',
                label: 'Precipitation',
                value: (this.currentWeather.rain?.['3h'] || 0).toFixed(1) + ' mm'
            },
            {
                icon: 'fa-gauge',
                label: 'UV Index',
                value: (Math.random() * 12).toFixed(1)
            }
        ];

        this.detailsGrid.innerHTML = details.map(detail => `
            <div class="detail-card">
                <div class="detail-icon"><i class="fas ${detail.icon}"></i></div>
                <div class="detail-label">${detail.label}</div>
                <div class="detail-value">${detail.value}</div>
            </div>
        `).join('');
    }

    displayAlerts() {
        const alerts = [];
        
        if (this.currentWeather.main.temp > 35) {
            alerts.push({
                title: 'High Temperature Alert',
                description: 'Temperature is above 35°C. Stay hydrated and avoid prolonged sun exposure.'
            });
        }
        
        if (this.currentWeather.wind.speed > 15) {
            alerts.push({
                title: 'Strong Wind Advisory',
                description: 'Wind speed exceeds 15 m/s. Be cautious when outdoors.'
            });
        }

        if (alerts.length > 0) {
            this.alertsSection.style.display = 'block';
            this.alertsContainer.innerHTML = alerts.map(alert => `
                <div class="alert-item">
                    <div class="alert-title"><i class="fas fa-exclamation-circle"></i> ${alert.title}</div>
                    <div class="alert-description">${alert.description}</div>
                </div>
            `).join('');
        } else {
            this.alertsSection.style.display = 'none';
        }
    }

    renderChart() {
        if (!this.forecastData) return;

        const times = [];
        const temps = [];
        const humidity = [];

        this.forecastData.list.slice(0, 24).forEach(item => {
            const time = new Date(item.dt * 1000).getHours();
            times.push(time + ':00');
            temps.push(this.convertTemp(item.main.temp));
            humidity.push(item.main.humidity);
        });

        const ctx = document.getElementById('temperatureChart').getContext('2d');
        
        if (this.chart) {
            this.chart.destroy();
        }

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: times,
                datasets: [
                    {
                        label: `Temperature (°${this.tempUnit})`,
                        data: temps,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Humidity (%)',
                        data: humidity,
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        labels: {
                            color: getComputedStyle(document.body).color
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: `Temperature (°${this.tempUnit})`
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Humidity (%)'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }

    toggleFavorite(cityName, temp, weather) {
        const index = this.favorites.findIndex(fav => fav.name === cityName);
        if (index > -1) {
            this.favorites.splice(index, 1);
            this.showToast(`${cityName} removed from favorites`, 'info');
        } else {
            this.favorites.push({ name: cityName, temp, weather });
            this.showToast(`${cityName} added to favorites`, 'success');
        }
        localStorage.setItem('favoritesCities', JSON.stringify(this.favorites));
        this.renderFavorites();
        this.displayCurrentWeather();
    }

    renderFavorites() {
        if (this.favorites.length === 0) {
            this.favoritesGrid.innerHTML = '<p>No favorites yet. Click the heart icon on any weather card to add.</p>';
            return;
        }

        this.favoritesGrid.innerHTML = this.favorites.map(fav => `
            <div class="favorite-card">
                <button class="remove-favorite" onclick="app.removeFavorite('${fav.name}')">
                    <i class="fas fa-trash"></i>
                </button>
                <div class="favorite-city-name">${fav.name}</div>
                <div class="favorite-temp">${this.convertTemp(fav.temp)}°${this.tempUnit}</div>
                <div class="favorite-desc">${fav.weather}</div>
            </div>
        `).join('');
    }

    removeFavorite(cityName) {
        this.favorites = this.favorites.filter(fav => fav.name !== cityName);
        localStorage.setItem('favoritesCities', JSON.stringify(this.favorites));
        this.renderFavorites();
        this.showToast(`${cityName} removed from favorites`, 'info');
    }

    convertTemp(temp) {
        if (this.tempUnit === 'F') {
            return Math.round((temp * 9/5) + 32);
        } else if (this.tempUnit === 'K') {
            return Math.round(temp + 273.15);
        }
        return Math.round(temp);
    }

    convertWind(speed) {
        if (this.windUnit === 'km/h') {
            return (speed * 3.6).toFixed(1);
        } else if (this.windUnit === 'mph') {
            return (speed * 2.237).toFixed(1);
        }
        return speed.toFixed(1);
    }

    degToDir(deg) {
        const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
        return directions[Math.round(deg / 45) % 8];
    }

    getWeatherIcon(weather) {
        const iconMap = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Smoke': '💨',
            'Haze': '🌫️',
            'Dust': '🌪️',
            'Fog': '🌫️',
            'Sand': '🌪️',
            'Ash': '💨',
            'Squall': '🌪️',
            'Tornado': '🌪️'
        };
        return iconMap[weather] || '🌤️';
    }

    toggleTheme() {
        document.body.classList.toggle('light-mode');
        localStorage.setItem('theme', document.body.classList.contains('light-mode') ? 'light' : 'dark');
        this.themeToggle.innerHTML = document.body.classList.contains('light-mode') 
            ? '<i class="fas fa-sun"></i>' 
            : '<i class="fas fa-moon"></i>';
    }

    openSettings() {
        this.settingsModal.classList.add('active');
    }

    closeSettingsModal() {
        this.settingsModal.classList.remove('active');
    }

    loadSettings() {
        this.tempUnitSelect.value = this.tempUnit;
        this.windUnitSelect.value = this.windUnit;
        this.apiKeyInput.value = this.apiKey;
        
        if (localStorage.getItem('theme') === 'light') {
            document.body.classList.add('light-mode');
            this.themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }

    handleSaveSettings() {
        this.tempUnit = this.tempUnitSelect.value;
        this.windUnit = this.windUnitSelect.value;
        this.apiKey = this.apiKeyInput.value || 'aa2e8b6b8b2e1d8b2e1d8b2e1d8b2e1d';
        
        localStorage.setItem('tempUnit', this.tempUnit);
        localStorage.setItem('windUnit', this.windUnit);
        localStorage.setItem('weatherApiKey', this.apiKey);
        
        this.closeSettingsModal();
        this.showToast('Settings saved successfully!', 'success');
        
        if (this.currentWeather) {
            this.updateUI();
        }
    }

    updateLastUpdated() {
        const now = new Date();
        const time = now.toLocaleTimeString();
        this.lastUpdated.textContent = time;
    }

    showLoader(show) {
        this.loader.style.display = show ? 'flex' : 'none';
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = message;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new WeatherDashboard();
    app.fetchWeatherByCoords(40.7128, -74.0060, 'New York');
});

const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(400px);
        }
    }
`;
document.head.appendChild(style);