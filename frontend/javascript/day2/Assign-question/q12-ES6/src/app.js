// ============================================
// MAIN APPLICATION ENTRY
// ============================================

// Import ONLY what we need (tree-shaking benefit)
import { validateEmail } from "./utils/index.js";

// Import services (default exports)
import ApiService from "./services/api.js";
import StorageService from "./services/storage.js";

// Create service instances
const api = new ApiService("https://jsonplaceholder.typicode.com");
const storage = new StorageService();


// ============================================
// DEMO: Validate Email
// ============================================

console.log("Valid Email:", validateEmail("test@example.com"));


// ============================================
// DEMO: API CALL
// ============================================

api.get("/posts?_limit=2")
  .then(data => console.log("API Data:", data));


// ============================================
// DYNAMIC IMPORT (MODAL)
// ============================================

// Button to trigger modal
const btn = document.createElement("button");
btn.textContent = "Open Modal";
document.body.appendChild(btn);

// Load modal ONLY when clicked
btn.addEventListener("click", async () => {

  // Dynamic import (lazy loading)
  const module = await import("./components/modal.js");

  const Modal = module.default;

  const modal = new Modal("Hello from Dynamic Modal!");
  modal.open();
});