/**
 * ============================================================
 * STORAGE MODULE (storage.js)
 * Manages favorites list and theme preference in localStorage.
 * Includes Observer pattern for state changes.
 * ============================================================
 */

// Keys for localStorage
const FAVS_KEY = 'weatherApp_favorites';
const THEME_KEY = 'weatherApp_theme';

/**
 * WeatherAppState (Concept: TypeScript Interfaces/AppState POJO)
 * Holds the reactive application state.
 */
class WeatherAppState {
  constructor() {
    this.favorites = this._loadFromStorage(FAVS_KEY, []);
    this.theme = this._loadFromStorage(THEME_KEY, 'dark');
    this.subscribers = []; // List of functions to call when favorites update
  }

  // --- Theme State Management ---
  getTheme() { return this.theme; }
  setTheme(newTheme) {
    this.theme = newTheme;
    this._saveToStorage(THEME_KEY, this.theme);
  }

  // --- Favorite State Management (Requirement: JSON parse/stringify) ---
  getFavorites() { return this.favorites; }
  
  addFavorite(city) {
    if (!this.favorites.find(f => f.toLowerCase() === city.toLowerCase())) {
      this.favorites.push(city);
      this._persistAndNotify();
      return true;
    }
    return false;
  }

  removeFavorite(city) {
    this.favorites = this.favorites.filter(f => f.toLowerCase() !== city.toLowerCase());
    this._persistAndNotify();
  }

  isFavorite(city) {
    return this.favorites.some(f => f.toLowerCase() === city.toLowerCase());
  }

  // --- Observer Pattern (Requirement: Observer pattern for state changes) ---
  subscribe(callback) {
    this.subscribers.push(callback);
  }

  _persistAndNotify() {
    this._saveToStorage(FAVS_KEY, this.favorites);
    this.subscribers.forEach(cb => cb(this.favorites));
  }

  // --- Storage Helpers (Concept: JSON parse/stringify) ---
  _saveToStorage(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  _loadFromStorage(key, defaultValue) {
    const data = localStorage.getItem(key);
    try {
      return data ? JSON.parse(data) : defaultValue;
    } catch (e) {
      console.error(`Error parsing localStorage key "${key}":`, e);
      return defaultValue;
    }
  }
}

// Export a singleton instance of the app state
export const AppState = new WeatherAppState();
