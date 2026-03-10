# Hospital Routing System

A web application that finds the shortest path from user location to hospitals using Leaflet.js, OpenStreetMap, and OpenRouteService API.

## Features

- **Interactive Map**: Built with Leaflet.js and OpenStreetMap tiles
- **Real-time Geolocation**: Automatically detects user location or allows manual selection
- **Hospital Selection**: Browse and select hospitals from a list or directly on the map
- **Shortest Path Routing**: Uses OpenRouteService API to find the optimal route
- **Distance & Time Calculation**: Shows route distance and estimated travel time
- **Responsive Design**: Works on desktop and mobile devices

## Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Set Up OpenRouteService API Key

1. Sign up for a free account at [OpenRouteService](https://openrouteservice.org/dev/#/signup)
2. Get your API key from the dashboard
3. Open the `.env` file in the project root
4. Replace `your_api_key_here` with your actual API key:

```env
# OpenRouteService API Key
REACT_APP_OPENROUTESERVICE_API_KEY=your_actual_api_key_here
```

### 3. Start the Development Server
```bash
npm start
```

The application will be available at `http://localhost:3000`

## Usage

1. **Access the Hospital Routing page**: Navigate to `/hospital-routing` or click "Hospital Routing" in the navigation menu

2. **Set Your Location**: 
   - Allow browser geolocation when prompted, OR
   - Click anywhere on the map to set your location manually

3. **Select a Hospital**:
   - Choose from the hospital list on the left, OR
   - Click on a red hospital marker on the map

4. **Get Directions**:
   - Click the "Get Directions" button
   - The shortest route will be displayed as a blue line
   - Distance and estimated travel time will be shown

## File Structure

```
src/
├── components/
│   ├── HospitalRoutingMap.tsx    # Main map component with routing
│   └── HospitalList.tsx          # Hospital selection list
├── pages/
│   └── HospitalRouting.tsx       # Main page component
├── types/
│   └── hospital.ts               # TypeScript interfaces
├── utils/
│   ├── hospitalData.ts           # Hospital data management
│   └── openRouteService.ts       # API integration
└── .env                          # Environment variables
```

## Hospital Data

The application currently uses sample hospital data for Hyderabad, India. To use your own hospital data:

1. Place your Excel file with hospital coordinates in the `data/` folder
2. Update `src/utils/hospitalData.ts` to parse your Excel file
3. Install the `xlsx` package: `npm install xlsx @types/xlsx`
4. Uncomment and implement the Excel parsing code in `parseHospitalExcel` function

## API Integration

The application uses the OpenRouteService Directions API:
- **Endpoint**: `https://api.openrouteservice.org/v2/directions/driving-car`
- **Method**: POST
- **Authentication**: Bearer token (API key)
- **Response**: GeoJSON format with route geometry and metadata

## Technologies Used

- **React 19**: Frontend framework
- **TypeScript**: Type safety
- **Leaflet.js**: Interactive maps
- **React-Leaflet**: React integration for Leaflet
- **OpenStreetMap**: Map tiles
- **OpenRouteService**: Routing API
- **React Bootstrap**: UI components
- **Bootstrap 5**: Styling

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure you've set a valid OpenRouteService API key in the `.env` file
2. **Location Access**: Ensure you've granted location permissions to your browser
3. **Map Not Loading**: Check your internet connection and browser console for errors
4. **Route Not Found**: Verify that both user location and hospital are selected

### Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Future Enhancements

- [ ] Excel file upload and parsing
- [ ] Multiple route options
- [ ] Traffic-aware routing
- [ ] Hospital details and ratings
- [ ] Turn-by-turn navigation
- [ ] Offline map support
- [ ] Mobile app version

## License

This project is part of the Madhumeha application suite.
