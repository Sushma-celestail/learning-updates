/**
 * ============================================================
 * UTILS MODULE (utils.js)
 * Helper functions for debounce, cookie management, 
 * date formatting, and form validation.
 * ============================================================
 */

/**
 * Debounce function to limit the execution frequency of a function.
 * (Used for search bar to avoid redundant API calls)
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 */
export const debounce = (func, wait) => {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Cookie Management: Create a cookie that expires in 'days'.
 * (Requirement: Store last searched city in a cookie for 7 days)
 */
export const setCookie = (name, value, days) => {
  const date = new Date();
  date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
  const expires = `expires=${date.toUTCString()}`;
  document.cookie = `${name}=${encodeURIComponent(value)};${expires};path=/;SameSite=Lax`;
};

/**
 * Cookie Management: Retrieve a cookie by name.
 */
export const getCookie = (name) => {
  const prefix = `${name}=`;
  const cookies = document.cookie.split(';');
  for (let c of cookies) {
    c = c.trim();
    if (c.indexOf(prefix) === 0) return decodeURIComponent(c.substring(prefix.length));
  }
  return null;
};

/**
 * Date Formatter: Returns a human-readable date string.
 */
export const formatDate = (timestamp = Date.now()) => {
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  }).format(new Date(timestamp));
};

/**
 * Form Validator: Custom logic using Constraint Validation API
 * (Requirement: Non-empty, letters/spaces only)
 */
export const validateCityInput = (inputElement) => {
  const value = inputElement.value.trim();
  const pattern = /^[A-Za-z\s\-]+$/;

  if (value === '') {
    inputElement.setCustomValidity('City name cannot be empty');
  } else if (!pattern.test(value)) {
    inputElement.setCustomValidity('Please enter only letters, spaces, or hyphens');
  } else {
    inputElement.setCustomValidity(''); // Clear errors
  }

  return inputElement.checkValidity();
};

/**
 * Sanitize Strings for display (Prevents XSS when using innerHTML, 
 * though the project requirements specify using DOM manipulation for user data)
 */
export const sanitize = (str) => {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
};
