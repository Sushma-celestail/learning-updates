/**
 * ============================================================
 * UI MODULE (ui.js)
 * Building all UI elements dynamically (cards, list, notifications).
 * (Concept: DOM Selection & Manipulation / Performance / Accessibility)
 * ============================================================
 */

import { formatDate, sanitize } from './utils.js';

// --- DOM Selectors (Concept: DOM Selection) ---
export const elements = {
  themeToggle: document.getElementById('theme-toggle'),
  searchForm: document.getElementById('search-form'),
  cityInput: document.getElementById('city-input'),
  clearBtn: document.getElementById('clear-btn'),
  inputError: document.getElementById('input-error'),
  weatherContainer: document.getElementById('weather-cards-container'),
  favoritesList: document.getElementById('favorites-list'),
  favoritesCount: document.getElementById('favorites-count'),
  favoritesEmpty: document.getElementById('favorites-empty'),
  toastContainer: document.getElementById('toast-container'),
  spinnerOverlay: document.getElementById('spinner-overlay'),
  weatherSection: document.querySelector('.weather-section')
};

/**
 * Update the Loading State indicator (Concept: Loading state / Accessibility)
 */
export const setLoading = (isLoading) => {
  elements.spinnerOverlay.hidden = !isLoading;
  elements.weatherSection.setAttribute('aria-busy', isLoading);
};

/**
 * Toast Notification (Concept: Error handling / Notifications)
 */
export const showToast = (message, type = 'info') => {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.setAttribute('role', 'alert');
  
  // Use textContent for safety (Concept: DOM Manipulation - No innerHTML)
  toast.textContent = message;
  
  elements.toastContainer.appendChild(toast);
  
  // Auto-remove toast after 3 seconds
  setTimeout(() => {
    toast.classList.add('fade-out');
    toast.addEventListener('animationend', () => toast.remove());
  }, 3000);
};

/**
 * Render Weather Card (Concept: DOM Selection & Manipulation / DocumentFragment)
 * Using a fragment increases performance by minimizing reflows.
 */
export const renderWeatherCard = (data, isFavorite = false) => {
  // Clear previous card (if we only show one)
  elements.weatherContainer.innerHTML = '';
  
  const fragment = document.createDocumentFragment();
  const card = document.createElement('article');
  card.className = 'weather-card';
  card.setAttribute('aria-label', `Current weather in ${data.name}`);
  
  // -- Build Card Contents dynamically (Concept: DOM Manipulation - No innerHTML for data) --
  
  // 1. Header
  const header = document.createElement('div');
  header.className = 'card-header';
  
  const locationInfo = document.createElement('div');
  locationInfo.className = 'location-info';
  
  const title = document.createElement('h2');
  title.textContent = `${data.name}, ${data.country}`;
  
  const date = document.createElement('p');
  date.className = 'date';
  date.textContent = formatDate(data.timestamp);
  
  locationInfo.append(title, date);
  
  const favBtn = document.createElement('button');
  favBtn.className = `fav-btn ${isFavorite ? 'is-fav' : ''}`;
  favBtn.setAttribute('aria-label', isFavorite ? 'Remove from favorites' : 'Add to favorites');
  favBtn.setAttribute('data-city', data.name);
  favBtn.innerHTML = isFavorite ? '★' : '☆'; // Unicode icons are safe here
  
  header.append(locationInfo, favBtn);
  
  // 2. Main Conditions
  const mainWeather = document.createElement('div');
  mainWeather.className = 'main-weather';
  
  const temp = document.createElement('div');
  temp.className = 'temp-large';
  temp.textContent = `${data.temp}°C`;
  
  const infoGroup = document.createElement('div');
  infoGroup.className = 'weather-main-info';
  
  const icon = document.createElement('img');
  icon.className = 'weather-icon-large';
  icon.src = `https://openweathermap.org/img/wn/${data.icon}@2x.png`;
  icon.alt = data.description;
  
  const condition = document.createElement('p');
  condition.className = 'weather-description';
  condition.textContent = data.description;
  
  infoGroup.append(icon, condition);
  mainWeather.append(temp, infoGroup);
  
  // 3. Details (Humidity/Wind)
  const details = document.createElement('div');
  details.className = 'weather-details';
  
  const createDetail = (label, value) => {
    const item = document.createElement('div');
    item.className = 'detail-item';
    const l = document.createElement('span');
    l.className = 'detail-label';
    l.textContent = label;
    const v = document.createElement('span');
    v.className = 'detail-value';
    v.textContent = value;
    item.append(l, v);
    return item;
  };
  
  details.append(
    createDetail('Humidity', `${data.humidity}%`),
    createDetail('Wind Speed', `${data.windSpeed} m/s`)
  );
  
  // Combine all
  card.append(header, mainWeather, details);
  fragment.appendChild(card);
  elements.weatherContainer.appendChild(fragment);
};

/**
 * Render Favorites List (Concept: Event Delegation / Performance)
 */
export const renderFavorites = (favorites) => {
  elements.favoritesList.innerHTML = '';
  elements.favoritesCount.textContent = favorites.length;
  elements.favoritesEmpty.hidden = favorites.length > 0;
  
  const fragment = document.createDocumentFragment();
  
  favorites.forEach(city => {
    const li = document.createElement('li');
    li.className = 'fav-item';
    
    const cityBtn = document.createElement('button');
    cityBtn.className = 'fav-city-btn';
    cityBtn.textContent = city;
    cityBtn.setAttribute('data-action', 'load');
    cityBtn.setAttribute('data-city', city);
    
    const removeBtn = document.createElement('button');
    removeBtn.className = 'remove-fav-btn';
    removeBtn.textContent = '✕';
    removeBtn.setAttribute('data-action', 'delete');
    removeBtn.setAttribute('data-city', city);
    removeBtn.setAttribute('aria-label', `Remove ${city} from favorites`);
    
    li.append(cityBtn, removeBtn);
    fragment.appendChild(li);
  });
  
  elements.favoritesList.appendChild(fragment);
};

/**
 * UI State: Clear input error
 */
export const clearError = () => {
  elements.cityInput.setCustomValidity('');
  elements.cityInput.setAttribute('aria-invalid', 'false');
  elements.inputError.textContent = '';
};

/**
 * UI State: Show specific error
 */
export const showError = (message) => {
  elements.cityInput.setAttribute('aria-invalid', 'true');
  elements.inputError.textContent = message;
};

/**
 * Theme UI Manager (Concept: Theme persist / localStorage)
 */
export const updateThemeUI = (theme) => {
  document.documentElement.setAttribute('data-theme', theme);
  const icon = theme === 'dark' ? '☀️' : '🌙';
  const label = theme === 'dark' ? 'Light' : 'Dark';
  
  elements.themeToggle.querySelector('.theme-icon').textContent = icon;
  elements.themeToggle.querySelector('.theme-label').textContent = label;
};
