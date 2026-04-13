/**
 * ============================================================
 * MAIN APPLICATION MODULE (app.js)
 * Orchestrates the entire application logic.
 * (Concept: Event Handling / Bubbling / Delegation / Debounce)
 * ============================================================
 */

import { fetchWeatherData } from './api.js';
import { AppState } from './storage.js';
import { elements, setLoading, showToast, renderWeatherCard, renderFavorites, updateThemeUI, clearError, showError } from './ui.js';
import { debounce, setCookie, getCookie, validateCityInput } from './utils.js';

// --- INITIAL STATE ---
const init = async () => {
  // 1. Initial UI update from persistent storage
  updateThemeUI(AppState.getTheme());
  renderFavorites(AppState.getFavorites());

  // 2. Subscribe to state changes (Observer Pattern)
  AppState.subscribe(favorites => {
    // Re-render favorites list whenever state changes
    renderFavorites(favorites);
  });

  // 3. Check for last searched city in cookies (Requirement: Cookies)
  const lastCity = getCookie('lastSearch');
  if (lastCity) {
    elements.cityInput.value = lastCity;
    handleSearch(lastCity);
  }
};

// --- CORE LOGIC ---

/**
 * Handle Search Flow: Validate -> Fetch -> Render -> Storage
 */
const handleSearch = async (city) => {
  if (!city) return;

  try {
    setLoading(true);
    clearError();

    const data = await fetchWeatherData(city);
    
    // Check if currently a favorite (Concept: storage.js)
    const isFav = AppState.isFavorite(data.name);
    
    // Render current result (Concept: DOM Manipulation / DocumentFragment)
    renderWeatherCard(data, isFav);

    // Save last city searched in cookie for 7 days (Requirement: Cookies)
    setCookie('lastSearch', data.name, 7);

    // Show success toast (Concept: Error handling/Notifications)
    showToast(`Weather for ${data.name} loaded successfully!`, 'success');
  } catch (err) {
    showToast(err.message, 'error');
    showError(err.message);
  } finally {
    setLoading(false);
  }
};

/**
 * Debounced search input handler (Requirement: Debounce 300ms)
 */
const debouncedInputHandler = debounce((e) => {
  const input = e.target;
  const val = input.value.trim();
  
  // Show/Hide clear button
  elements.clearBtn.hidden = val === '';
  
  // Custom validation feedback (Concept: Form Validation)
  if (val && !validateCityInput(input)) {
    showError(input.validationMessage);
  } else {
    clearError();
  }
}, 300);

// --- EVENT LISTENERS ---

// 1. Theme Toggle: State update + persist
elements.themeToggle.addEventListener('click', () => {
  const current = AppState.getTheme();
  const next = current === 'dark' ? 'light' : 'dark';
  AppState.setTheme(next);
  updateThemeUI(next);
});

// 2. Form Submission (Requirement: Event Handling - keyboard Enter)
elements.searchForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  const input = elements.cityInput;
  if (validateCityInput(input)) {
    handleSearch(input.value.trim());
  } else {
    showError(input.validationMessage);
  }
});

// 3. Debounced Input Handling
elements.cityInput.addEventListener('input', debouncedInputHandler);

// 4. Clear Search Button
elements.clearBtn.addEventListener('click', () => {
  elements.cityInput.value = '';
  elements.cityInput.focus();
  elements.clearBtn.hidden = true;
  clearError();
});

// 5. Favorites List Actions (Concept: Event Delegation / Bubbling)
// Single listener on <ul> for clicks on buttons inside.
elements.favoritesList.addEventListener('click', (e) => {
  // Bubbling: Find the closest button or target
  const target = e.target;
  const action = target.getAttribute('data-action');
  const city = target.getAttribute('data-city');

  if (!action || !city) return;

  if (action === 'load') {
    elements.cityInput.value = city;
    handleSearch(city);
  } else if (action === 'delete') {
    // (Requirement: alert / prompt / confirm)
    if (confirm(`Are you sure you want to remove "${city}" from your favorites?`)) {
      AppState.removeFavorite(city);
      showToast(`${city} removed from favorites`, 'info');
    }
  }
});

// 6. Favorite Toggle button on weather card (Concept: Event Delegation / Bubbling)
// Single listener on weatherContainer for the dynamic favorite button.
elements.weatherContainer.addEventListener('click', (e) => {
  const btn = e.target.closest('.fav-btn');
  if (!btn) return;

  const city = btn.getAttribute('data-city');
  if (AppState.isFavorite(city)) {
    AppState.removeFavorite(city);
    btn.classList.remove('is-fav');
    btn.innerHTML = '☆';
    showToast(`${city} removed from favorites`, 'info');
  } else {
    AppState.addFavorite(city);
    btn.classList.add('is-fav');
    btn.innerHTML = '★';
    showToast(`${city} added to favorites!`, 'success');
  }
});

/**
 * Performance Animation (Concept: Performance / rAF)
 * Apply a small entrance animation to the search section on load.
 */
const animateEntrance = () => {
  let start = null;
  const duration = 1000;
  const element = document.querySelector('.search-section');
  element.style.opacity = '0';
  element.style.transform = 'translateY(-20px)';

  const step = (timestamp) => {
    if (!start) start = timestamp;
    const progress = timestamp - start;
    const opacity = Math.min(progress / duration, 1);
    const y = Math.max(20 - (progress / duration) * 20, 0);
    
    element.style.opacity = opacity;
    element.style.transform = `translateY(${y}px)`;

    if (progress < duration) {
       window.requestAnimationFrame(step);
    }
  };
  window.requestAnimationFrame(step);
};

// START APP
window.addEventListener('DOMContentLoaded', () => {
  init();
  animateEntrance(); // Concept: Performance / rAF
});


