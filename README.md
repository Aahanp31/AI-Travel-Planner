<div align="center">

# 🌍 AI Travel Planner

**An intelligent full-stack travel planning application powered by AI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)

<!-- [View Demo](#usage) · [Report Bug](https://github.com/your_username/ai-travel-planner/issues) · [Request Feature](https://github.com/your_username/ai-travel-planner/issues) -->

</div>

---

## 📋 Table of Contents

- [About The Project](#about-the-project)
- [Features](#features)
- [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
<!-- - [Contact](#contact) -->
- [Acknowledgments](#acknowledgments)

---

## 🎯 About The Project

**AI Travel Planner** is a comprehensive full-stack application that leverages Google's Gemini AI to create personalized travel itineraries. Whether you're planning a weekend getaway or a multi-city adventure, this app generates detailed day-by-day plans with activities, budget estimates, booking options, weather forecasts, and interactive maps.

### Why AI Travel Planner?

- **🤖 AI-Powered Planning**: Uses Google Gemini AI to create intelligent, personalized itineraries
- **🌍 Multi-City Support**: Plan trips with multiple locations in one country
- **💰 Smart Budget Estimates**: Dual-currency support with realistic cost breakdowns
- **🗺️ Interactive Maps**: Visualize your trip with geocoded attractions
- **🌤️ Weather Integration**: Get weather forecasts for your destination
- **📰 Destination News**: Stay updated with latest news and events
- **📚 Wikipedia Links**: Automatic links to learn more about locations
- **🌓 Dark/Light Mode**: Toggle between themes for comfortable viewing
- **⚡ Fast & Parallel**: All agents run in parallel for optimal performance
- **🆓 Free APIs**: Uses free services like OpenStreetMap and Wikipedia

---

## ✨ Features

- **📅 Itinerary Agent**: Creates detailed day-by-day travel plans with:
  - Morning, afternoon, and evening activities
  - Food recommendations
  - Cultural highlights
  - Multi-city support with transportation details

- **💰 Budget Agent**: Estimates travel costs with:
  - Local currency and USD conversion
  - Hotel, food, transport, and activities breakdown
  - Realistic exchange rates

- **🏨 Booking Agent**: Quick links to popular booking platforms:
  - Hotels.com, Booking.com, Expedia
  - Google Flights, Kayak, Skyscanner

- **🗺️ Map Agent**: Interactive maps with:
  - Geocoded attractions from your itinerary
  - OpenStreetMap integration (completely free!)

- **📖 Wikipedia Agent**: Automatic Wikipedia links for:
  - Destinations and attractions
  - Cultural sites and landmarks

- **📰 News Agent**: Latest destination news and updates:
  - Local news articles about your destination
  - Travel advisories and updates
  - Cultural events and happenings

- **🌤️ Weather Agent**: 3-day weather forecasts (optional)

---

## 🛠️ Built With

This section lists the major frameworks and libraries used in this project.

### Backend
- [Python](https://www.python.org/) - Programming language
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Google Gemini AI](https://ai.google.dev/) - AI model for itinerary generation
- [aiohttp](https://docs.aiohttp.org/) - Async HTTP client
- [python-dotenv](https://pypi.org/project/python-dotenv/) - Environment variables

### Frontend
- [Next.js](https://nextjs.org/) - React framework
- [React](https://react.dev/) - UI library
- [TypeScript](https://www.typescriptlang.org/) - Type safety
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [React Leaflet](https://react-leaflet.js.org/) - Interactive maps
- [Axios](https://axios-http.com/) - HTTP client
- [Heroicons](https://heroicons.com/) - Beautiful icons
- [next-themes](https://github.com/pacocoursey/next-themes) - Dark mode support

### APIs & Services
- [Google Gemini API](https://ai.google.dev/) - AI itinerary generation
- [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org/) - Geocoding (free)
- [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page) - Location links (free)
- [NewsData.io API](https://newsdata.io/) - Destination news (optional)
- [WeatherAPI](https://www.weatherapi.com/) - Weather forecasts (optional)

---

## 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.

- **Python 3.12+**
  ```bash
  python3 --version
  ```

- **Node.js 18+ and npm**
  ```bash
  node --version
  npm --version
  ```

- **Git**
  ```bash
  git --version
  ```

### Installation

1. **Get a free Gemini API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key (free tier available)

2. **Clone the repository**
   ```bash
   git clone https://github.com/your_username/ai-travel-planner.git
   cd ai-travel-planner
   ```

3. **Set up the Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the `backend` directory:
   ```env
   PORT=4000
   GEMINI_API_KEY=your_gemini_api_key_here
   WEATHER_API_KEY=your_weather_api_key_here  # Optional
   NEWS_API_KEY=your_news_api_key_here  # Optional
   ```
   > **Note**: Weather and News API keys are optional. Get them free at:
   > - [weatherapi.com](https://www.weatherapi.com/) for weather forecasts
   > - [newsdata.io](https://newsdata.io/) for destination news

5. **Set up the Frontend**
   ```bash
   cd ../frontend
   npm install
   ```

6. **Start the Backend Server**
   ```bash
   cd backend
   python3 app.py
   ```
   The backend will run on [http://localhost:4000](http://localhost:4000)

7. **Start the Frontend Development Server**
   ```bash
   cd frontend
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) in your browser

---

## 💡 Usage

1. **Select your destination**
   - Choose a country from the dropdown
   - Optionally add specific cities/locations (comma-separated for multi-city trips)
   - Use geolocation to auto-detect your current location as origin

2. **Set trip details**
   - Select number of days (1-14)
   - Enter departure location (airport code or city name)
   - Choose start date (optional)
   - Add additional details (dietary preferences, interests, accessibility needs)

3. **Plan your trip**
   - Click "Plan My Trip"
   - Wait for AI to generate your personalized itinerary (runs 7 agents in parallel)

4. **Explore your trip**
   - View day-by-day activities with morning, afternoon, and evening plans
   - Check budget estimates in local currency and USD
   - Access booking links for hotels and flights
   - Explore interactive map with all attractions
   - Read Wikipedia articles about destinations
   - Check weather forecast for your dates
   - Browse latest news about your destination

### Example Request

```json
{
  "country": "Japan",
  "locations": "Tokyo, Kyoto, Osaka",
  "days": 7,
  "origin": "LAX",
  "additionalDetails": "Interested in temples, traditional food, and anime culture"
}
```

---

## 📡 API Documentation

### POST `/plan-trip`

Plans a complete trip with itinerary, budget, bookings, map data, weather, and news.

**Request Body:**
```json
{
  "country": "France",
  "locations": "Paris, Nice",
  "days": 5,
  "origin": "LAX",
  "additionalDetails": "Interested in art museums and French cuisine"
}
```

**Request Parameters:**
- `country` (required): Country name
- `locations` (optional): Comma-separated list of cities
- `days` (optional, default: 3): Number of days (1-14)
- `origin` (optional, default: "LAX"): Departure location
- `additionalDetails` (optional): Extra preferences or requirements

**Response:**
```json
{
  "itinerary": {
    "day1": {
      "morning": ["Visit the Eiffel Tower", "Walk along the Seine"],
      "afternoon": ["Explore the Louvre Museum"],
      "evening": ["Dinner at a Montmartre bistro"],
      "food_recommendation": "Try authentic French baguettes and croissants",
      "cultural_highlight": "Paris is known as the City of Light",
      "wikipedia_links": {
        "Eiffel Tower": "https://en.wikipedia.org/wiki/Eiffel_Tower",
        "Louvre Museum": "https://en.wikipedia.org/wiki/Louvre"
      }
    }
  },
  "budget": {
    "hotel": { "per_night_local": "€120", "per_night_usd": "$130 USD" },
    "food": { "per_day_local": "€50-80", "per_day_usd": "$55-87 USD" },
    "transport": { "per_day_local": "€20-30", "per_day_usd": "$22-33 USD" },
    "activities": { "per_day_local": "€40-60", "per_day_usd": "$44-66 USD" },
    "total_estimated": { "local": "€1,150-1,550", "usd": "$1,265-1,705 USD" }
  },
  "bookings": {
    "hotels": [
      { "name": "Hotels.com", "url": "https://www.hotels.com/..." },
      { "name": "Booking.com", "url": "https://www.booking.com/..." }
    ],
    "flights": [
      { "name": "Google Flights", "url": "https://www.google.com/flights/..." },
      { "name": "Kayak", "url": "https://www.kayak.com/..." }
    ]
  },
  "mapData": [
    {
      "name": "Eiffel Tower",
      "location": { "lat": 48.8584, "lng": 2.2945 }
    },
    {
      "name": "Louvre Museum",
      "location": { "lat": 48.8606, "lng": 2.3376 }
    }
  ],
  "weather": {
    "current": { "temp_c": 15, "condition": { "text": "Partly cloudy" } },
    "forecast": [
      { "date": "2024-06-15", "maxtemp_c": 22, "mintemp_c": 14, "condition": { "text": "Sunny" } }
    ]
  },
  "news": [
    {
      "title": "Paris Hosts Major Art Exhibition",
      "description": "The Louvre announces new Renaissance exhibition...",
      "url": "https://...",
      "pubDate": "2024-06-10"
    }
  ]
}
```

---

## 🗺️ Roadmap

- [ ] Add user authentication and trip saving
- [ ] Real booking integration (Amadeus/RapidAPI)
- [ ] PDF export functionality
- [ ] Collaborative trip planning
- [ ] Mobile app version
- [ ] Multi-language support
- [ ] Enhanced UI animations
- [ ] Database integration for trip history
- [ ] Social sharing features
- [ ] Trip comparison tool

See the [open issues](https://github.com/Aahanp31/AI-Travel-Planner/issues) for a full list of proposed features (and known issues).

---

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📧 Contact

Aahan Patel - aahanpatel06@gmail.com

Project Link: [https://github.com/Aahanp31/AI-Travel-Planner](https://github.com/Aahanp31/AI-Travel-Planner)

---

## 🙏 Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

- [Google Gemini AI](https://ai.google.dev/) - Powerful AI for itinerary generation
- [OpenStreetMap](https://www.openstreetmap.org/) - Free and open geocoding service
- [Wikipedia](https://www.wikipedia.org/) - Free knowledge base
- [React Leaflet](https://react-leaflet.js.org/) - Open-source mapping library
- [Next.js Documentation](https://nextjs.org/docs) - Excellent framework docs
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Best README Template](https://github.com/othneildrew/Best-README-Template) - README template inspiration

---

<div align="center">

**[⬆ Back to Top](#-ai-travel-planner)**

Made with Aahan Patel (https://github.com/Aahanp31)

</div>
