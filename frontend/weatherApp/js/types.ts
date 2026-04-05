/**
 * ============================================================
 * TYPES / INTERFACES (types.ts)
 * Bonus: TypeScript version providing structured data models.
 * ============================================================
 */

/**
 * Standardized Weather Data Interface
 * Used by api.js to transform raw API responses.
 */
export interface WeatherData {
  id: number;
  name: string;
  country: string;
  temp: number;
  condition: string;
  description: string;
  icon: string;
  humidity: number;
  windSpeed: number;
  timestamp: number;
}

/**
 * Favorite City State Interface
 * Managed by AppState.
 */
export interface FavoriteCity {
  cityName: string;
}

/**
 * Application State Interface
 * Requirement: Observer pattern implementation details.
 */
export interface AppStateInterface {
  favorites: string[];
  theme: 'light' | 'dark';
  subscribers: Function[];
  
  getTheme(): 'light' | 'dark';
  setTheme(newTheme: 'light' | 'dark'): void;
  getFavorites(): string[];
  addFavorite(city: string): boolean;
  removeFavorite(city: string): void;
  isFavorite(city: string): boolean;
  subscribe(callback: (favs: string[]) => void): void;
}

/**
 * UI Component DOM Element Manifest
 */
export interface UISelectors {
  themeToggle: HTMLElement;
  searchForm: HTMLFormElement;
  cityInput: HTMLInputElement;
  clearBtn: HTMLButtonElement;
  inputError: HTMLElement;
  weatherContainer: HTMLElement;
  favoritesList: HTMLUListElement;
  favoritesCount: HTMLElement;
  favoritesEmpty: HTMLElement;
  toastContainer: HTMLElement;
  spinnerOverlay: HTMLElement;
  weatherSection: HTMLElement;
}
