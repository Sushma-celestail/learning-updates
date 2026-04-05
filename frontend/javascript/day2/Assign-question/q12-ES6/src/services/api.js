// ============================================
// API SERVICE (Default Export)
// ============================================

export default class ApiService {

  constructor(baseURL) {
    this.baseURL = baseURL;
  }

  // Simple GET request
  async get(endpoint) {
    const res = await fetch(this.baseURL + endpoint);

    if (!res.ok) throw new Error("API Error");

    return await res.json();
  }
}