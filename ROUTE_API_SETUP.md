# Route API Setup (Backend Proxy)

## Overview
The routing functionality uses a backend proxy to avoid CORS issues. The Flask backend makes requests to OpenRouteService API on behalf of the frontend.

## Setup Instructions

### Step 1: Install Required Python Package
```bash
cd diabetes_stacking_model
pip install requests
```

### Step 2: Get OpenRouteService API Key
1. Visit: https://openrouteservice.org/dev/#/signup
2. Sign up for a free account
3. Copy your API key from the dashboard

### Step 3: Configure API Key on Backend

**Option A: Environment Variable (Recommended)**
```bash
# Windows PowerShell
$env:OPENROUTESERVICE_API_KEY="your_api_key_here"

# Windows CMD
set OPENROUTESERVICE_API_KEY=your_api_key_here

# Linux/Mac
export OPENROUTESERVICE_API_KEY=your_api_key_here
```

**Option B: Create .env file (if using python-dotenv)**
Create a `.env` file in `diabetes_stacking_model` directory:
```
OPENROUTESERVICE_API_KEY=your_api_key_here
```

### Step 4: Restart Flask Server
After setting the environment variable, restart your Flask server:
```bash
cd diabetes_stacking_model/app
python main.py
```

## How It Works

1. Frontend calls `/route` endpoint on Flask backend (localhost:5000)
2. Backend receives the request with start/end coordinates
3. Backend makes request to OpenRouteService API using the API key
4. Backend returns the route data to frontend
5. Frontend displays the route on the map

## API Endpoint

**POST** `/route`

**Request Body:**
```json
{
  "start": {
    "latitude": 28.6139,
    "longitude": 77.2090
  },
  "end": {
    "latitude": 28.7041,
    "longitude": 77.1025
  }
}
```

**Response:**
Returns GeoJSON format route data from OpenRouteService.

## Troubleshooting

### "OpenRouteService API key not configured on server"
- Make sure you've set the `OPENROUTESERVICE_API_KEY` environment variable
- Restart the Flask server after setting the variable
- Check that the variable is set correctly: `echo $OPENROUTESERVICE_API_KEY` (Linux/Mac) or `echo %OPENROUTESERVICE_API_KEY%` (Windows CMD)

### "Network error: Could not connect to backend server"
- Ensure Flask server is running on port 5000
- Check that `REACT_APP_BACKEND_URL` in frontend matches your Flask server URL
- Default is `http://localhost:5000`

### "Failed to get route"
- Check that coordinates are valid (latitude: -90 to 90, longitude: -180 to 180)
- Verify API key is correct and active
- Check OpenRouteService account for rate limits

