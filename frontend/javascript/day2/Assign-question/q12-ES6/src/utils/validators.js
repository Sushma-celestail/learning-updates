// ============================================
// VALIDATORS MODULE (Named Exports)
// ============================================

// Validate email using regex
export function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Validate phone (10 digits)
export function validatePhone(phone) {
  return /^\d{10}$/.test(phone);
}

// Validate password (strong)
export function validatePassword(password) {
  return /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$/.test(password);
}