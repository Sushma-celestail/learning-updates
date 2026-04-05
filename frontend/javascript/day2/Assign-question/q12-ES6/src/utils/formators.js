// ============================================
// FORMATTERS MODULE (Named Exports)
// ============================================

// Format date
export function formatDate(date) {
  return new Date(date).toLocaleDateString();
}

// Format currency
export function formatCurrency(amount) {
  return "₹" + amount.toFixed(2);
}

// Capitalize first letter
export function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}