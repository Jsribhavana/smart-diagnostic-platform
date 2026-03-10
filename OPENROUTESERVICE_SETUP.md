# OpenRouteService API Setup

This application uses OpenRouteService API to calculate the shortest path from user location to hospitals.

## Setup Instructions

1. **Get your free API key:**
   - Visit: https://openrouteservice.org/dev/#/signup
   - Sign up for a free account
   - Copy your API key from the dashboard

2. **Configure the API key:**
   - Create a `.env` file in the `madhumeha-app` directory (if it doesn't exist)
   - Add the following line:
     ```
     REACT_APP_OPENROUTESERVICE_API_KEY=your_actual_api_key_here
     ```
   - Replace `your_actual_api_key_here` with your actual API key

3. **Restart the development server:**
   - Stop the current server (Ctrl+C)
   - Run `npm start` again

## How It Works

- When a user clicks "Get Directions" on a hospital card:
  1. The app requests the user's current location (browser geolocation)
  2. It uses the hospital's latitude/longitude from the Excel file (`hospitals_lat_long.xlsx`)
  3. It calls OpenRouteService API to calculate the shortest driving route
  4. The route is displayed on the map using Leaflet.js with OpenStreetMap tiles

## Notes

- The API key is stored in `.env` file and should NOT be committed to version control
- The `.env` file is already in `.gitignore`
- Free tier includes 2,000 requests per day
- The backend reads from `diabetes_stacking_model/data/hospitals_lat_long.xlsx` which should contain columns: Hospital, Latitude, Longitude (and optionally City, State, Pincode, LocalAddress)

