# API Reference

Base URL (local): `http://localhost:4000`

---

## Trip Planning

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/plan-trip` | Generate a full trip (itinerary, budget, bookings, map, weather, news) |
| `POST` | `/chat` | Modify an existing trip via conversational AI |

### `POST /plan-trip` — Single country

```json
{
  "country": "Japan",
  "locations": "Tokyo, Kyoto, Osaka",
  "days": 7,
  "origin": "LAX",
  "additionalDetails": "Interested in temples and street food",
  "detailLevel": "comprehensive"
}
```

### `POST /plan-trip` — Multi-country

```json
{
  "tripMode": "multi",
  "countries": [
    { "country": "France", "days": 4 },
    { "country": "Italy", "days": 3 }
  ],
  "origin": "JFK",
  "additionalDetails": "Art museums and local cuisine"
}
```

### Response fields

| Field | Description |
|-------|-------------|
| `itinerary` | Day-by-day plan with Wikipedia links |
| `budget` | Dual-currency cost breakdown |
| `bookings` | Hotel and flight platform links |
| `mapData` | Geocoded attraction coordinates |
| `weather` | Forecast data |
| `news` | Destination articles |
| `optimization.hallucination_check` | Fact-check report |
| `optimization.constraint_validation` | Schedule feasibility |
| `performance.cache_hit` | Whether the result was cached |
| `correctedDestination` | Autocorrected destination name |
| `wasAutocorrected` | Boolean flag |

---

## Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | Register (email + password) |
| `POST` | `/api/auth/login` | Login |
| `POST` | `/api/auth/google-auth` | Google OAuth |
| `GET` | `/api/auth/profile` | Get profile (JWT required) |
| `PUT` | `/api/auth/profile` | Update profile (JWT required) |

---

## Trip Management

All endpoints require a valid JWT in the `Authorization: Bearer <token>` header.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/save-trip` | Save a trip |
| `GET` | `/api/auth/trips` | List all saved trips (sorted by favorite, then date) |
| `GET` | `/api/auth/trips/:id` | Get a single trip with full data |
| `PUT` | `/api/auth/trips/:id` | Update trip (name, notes, favorite) |
| `DELETE` | `/api/auth/trips/:id` | Delete a trip |

---

## Analytics & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/analytics/cache` | Cache hit rates, API call reduction, per-type stats |
| `GET` | `/analytics/quality` | NDCG scores, hallucination rate, entity resolution precision, A/B test status |
| `GET` | `/analytics/optimization` | TSP algorithm details, DB index recommendations, ML model stats |
| `GET` | `/health` | Health check with DB connection status and cache stats |
| `GET` | `/` | API info with version and available endpoints |
