# Shortest Path Routing Implementation

## Overview

This implementation adds shortest path routing from user location to hospitals using:

- **Leaflet.js** for map rendering
- **OpenStreetMap** for map tiles
- **OpenRouteService API** for shortest path calculation
- **Excel file** (`hospitals_lat_long.xlsx`) containing hospital coordinates

## Changes Made

### 1. Backend Updates (`diabetes_stacking_model/app/main.py`)

- Updated `/hospitals` endpoint to read from Excel file (`data/hospitals_lat_long.xlsx`)
- Added support for reading latitude and longitude columns
- Includes lat/long in API response when available
- Falls back to CSV file if Excel file is not available or openpyxl is not installed

### 2. Frontend Updates (`madhumeha-app/src/pages/NearbyCenters.tsx`)

- Replaced OSRM routing with OpenRouteService API
- Uses hospital lat/long directly from API response (no geocoding needed)
- Displays route on Leaflet map with OpenStreetMap tiles
- Shows user location and hospital markers with popups
- Displays route as a blue polyline on the map

### 3. Utility Functions (`madhumeha-app/src/utils/openRouteService.ts`)

- Already existed, now being used for routing
- Handles OpenRouteService API calls
- Returns GeoJSON format route data

### 4. Type Definitions (`madhumeha-app/src/types/hospital.ts`)

- Updated `RouteResponse` interface to match OpenRouteService GeoJSON format

### 5. Environment Configuration

- Created `.env.example` file with API key placeholder
- Setup instructions in `OPENROUTESERVICE_SETUP.md`

## Setup Instructions

### Step 1: Install openpyxl (for Excel file reading)

```bash
cd diabetes_stacking_model
pip install openpyxl
```

### Step 2: Install requests library (for backend)

```bash
cd diabetes_stacking_model
pip install requests
```

### Step 3: Get OpenRouteService API Key

1. Visit: https://openrouteservice.org/dev/#/signup
2. Sign up for a free account
3. Copy your API key from the dashboard

### Step 4: Configure API Key on Backend

Set the API key as an environment variable before starting the Flask server:

**Windows PowerShell:**

```powershell
$env:OPENROUTESERVICE_API_KEY="your_actual_api_key_here"
```

**Windows CMD:**

```cmd
set OPENROUTESERVICE_API_KEY=your_actual_api_key_here
```

**Linux/Mac:**

```bash
export OPENROUTESERVICE_API_KEY=your_actual_api_key_here
```

### Step 5: Restart Flask Server

After setting the environment variable, restart your Flask server:

```bash
cd diabetes_stacking_model/app
python main.py
```

**Note:** The API key is now configured on the backend, not the frontend. This solves CORS issues.

## How It Works

1. **User clicks "Get Directions"** on a hospital card
2. **Browser requests user location** via geolocation API
3. **Hospital coordinates** are retrieved from the API response (from Excel file)
4. **Frontend calls backend `/route` endpoint** with start and end coordinates
5. **Backend proxies request to OpenRouteService API** (avoids CORS issues)
6. **Backend returns route data** to frontend
7. **Route is displayed** on the map using Leaflet.js with:
   - User location marker (blue)
   - Hospital marker (red)
   - Route polyline (blue line)

## Excel File Format

The Excel file (`diabetes_stacking_model/data/hospitals_lat_long.xlsx`) should contain:

- **Hospital** (or Name) - Hospital name
- **Latitude** (or Lat) - Latitude coordinate
- **Longitude** (or Long/Lng/Lon) - Longitude coordinate
- **City** (optional) - City name
- **State** (optional) - State name
- **Pincode** (optional) - Postal code
- **LocalAddress** (optional) - Street address

## API Limits

- Free tier: 2,000 requests per day
- Paid plans available for higher limits

## Troubleshooting

### "OpenRouteService API key not configured on server"

- Make sure you've set the `OPENROUTESERVICE_API_KEY` environment variable
- Restart the Flask server after setting the variable
- Check that the variable is set correctly (see Step 4 above)

### "Geolocation unavailable"

- User needs to allow location access in browser
- HTTPS is required for geolocation (localhost works)

### "Route not available"

- Check that both user location and hospital coordinates are valid
- Verify OpenRouteService API key is set on the backend
- Ensure Flask server is running on port 5000
- Check browser console and Flask server logs for detailed error messages

### "Network error: Could not connect to backend server"

- Ensure Flask server is running on port 5000
- Check that backend URL is correct (default: http://localhost:5000)

### Excel file not loading

- Install openpyxl: `pip install openpyxl`
- Verify file path: `diabetes_stacking_model/data/hospitals_lat_long.xlsx`
- Check that columns are named correctly (case-insensitive matching)
