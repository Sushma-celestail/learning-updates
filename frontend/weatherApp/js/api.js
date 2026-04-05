/**
 * ============================================================
 * API MODULE (api.js)
 * Fetching weather data from OpenWeatherMap API using async/await.
 * ============================================================
 */

// Replace with a valid OpenWeatherMap API key (Requirement: Fetch data from a weather API)
const API_KEY = '22e9fb05f7c4f7cfb4a419e55b9c6bd8';
const BASE_URL = 'https://api.openweathermap.org/data/2.5/weather';

/**
 * Fetch Current Weather Data by City Name.
 * (Requirement: async/await with error handling)
 * @param {string} city - Name of the city to search for.
 */
export const fetchWeatherData = async (city) => {
  try {
    const response = await fetch(`${BASE_URL}?q=${city}&appid=${API_KEY}&units=metric`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`City "${city}" not found. Please try another.`);
      } else if (response.status === 429) {
        throw new Error('API request limit reached. Please try again later.');
      } else {
        throw new Error('Network error. Unable to fetch weather data.');
      }
    }

    const data = await response.json();

    // Transform OpenWeatherMap response into a standardized object (Requirement: Interfaces/POJO)
    return {
      id: data.id,
      name: data.name,
      country: data.sys.country,
      temp: Math.round(data.main.temp),
      condition: data.weather[0].main,
      description: data.weather[0].description,
      icon: data.weather[0].icon,
      humidity: data.main.humidity,
      windSpeed: data.wind.speed,
      timestamp: Date.now()
    };

  } catch (error) {
    console.error('API Fetch Error:', error);
    throw error; // Re-throw to be caught in app.js
  }
};
