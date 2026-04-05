// ============================================
// STORAGE SERVICE (Default Export)
// ============================================

export default class StorageService {

  // Save data to localStorage
  set(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  // Get data
  get(key) {
    return JSON.parse(localStorage.getItem(key));
  }

  // Remove data
  remove(key) {
    localStorage.removeItem(key);
  }
}