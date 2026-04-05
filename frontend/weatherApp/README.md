# Weather Dashboard App

A premium, browser-based Weather Dashboard that allows users to search for cities, view real-time weather data, and manage a personalized list of favorite locations. Built entirely with Vanilla JavaScript and modern CSS.

## 🚀 Live Demo Features

- **Real-time Search**: Search for any city worldwide using the OpenWeatherMap API.
- **Debounced Input**: Optimized search bar with a 300ms delay to prevent redundant API calls.
- **Dynamic Weather Cards**: Beautifully animated cards showing temperature, conditions, humidity, and wind speed.
- **Persistent Favorites**: Save your favorite cities to `localStorage`. They persist even after a page refresh.
- **Session Continuity**: Remembers your last searched city via **Cookies** for 7 days.
- **Dark/Light Mode**: Fully responsive theme toggle with persistence.
- **Form Validation**: Built-in validation using the Constraint Validation API (letters/spaces only).
- **Accessibility**: ARIA-labeled components and keyboard navigation support.

## 🛠️ Technical Stack

- **HTML5**: Semantic structure.
- **CSS3**: Vanilla CSS with HSL variables, Grid, Flexbox, and Glassmorphism.
- **JavaScript (ES6+)**: Modular architecture (`app.js`, `api.js`, `ui.js`, `storage.js`, `utils.js`).
- **Design Pattern**: Observer Pattern for state management.
- **API**: OpenWeatherMap Geocoding & Current Weather data.

## ⚙️ How to Execute the Project

### Option 1: Direct File Open (Easiest)
1. Ensure all project files are in the same directory structure.
2. Open `index.html` in any modern web browser (Chrome, Firefox, Edge, Safari).

### Option 2: Using a Local Server (Recommended)
Using a local server prevents potential `CORS` or `file://` protocol issues in some environments.

**Using VS Code:**
- Install the **Live Server** extension.
- Right-click `index.html` and select **"Open with Live Server"**.

**Using Node.js/NPM:**
```bash
# Install and run a simple server
npx serve .
```

**Using Python:**
```bash
# Python 3
python -m http.server 8000
```
Then visit `http://localhost:8000` in your browser.

## 🔑 Configuration: API Key

The project requires an OpenWeatherMap API key to fetch real data.

1. Get your free API key at [OpenWeatherMap](https://home.openweathermap.org/api_keys).
2. Open `js/api.js`.
3. Locate the `API_KEY` variable:
   ```javascript
   const API_KEY = 'YOUR_API_KEY_HERE';
   ```
4. Replace the placeholder with your actual key (Note: The current version in this project already has a test key provided by the user).

## 📄 License

This project is open-source and available under the MIT License.
