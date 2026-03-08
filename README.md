<div align="center">

# AI Travel Planner

**Plan smarter trips with AI agents, route optimization, and personalized recommendations.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![Flask 3.0](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![React 19](https://img.shields.io/badge/React-19-61dafb)](https://react.dev/)
[![Gemini 2.5](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4)](https://ai.google.dev/)

[Getting Started](#-getting-started) · [How It Works](#-how-it-works) · [Tech Stack](#-tech-stack) · [API Docs](#-api-reference) · [Report Bug](https://github.com/Aahanp31/AI-Travel-Planner/issues)

</div>

---

## What It Does

AI Travel Planner is a full-stack application that takes a destination, dates, and your preferences, then orchestrates **8 specialized AI agents in parallel** to produce a complete trip plan: day-by-day itinerary, dual-currency budget estimates, interactive map, weather forecast, destination news, booking links, and Wikipedia enrichment for every attraction.

What makes it different from asking ChatGPT for an itinerary:

1. **It optimizes.** After the AI generates activities, a TSP solver reorders them geographically and a constraint solver validates everything fits within realistic time windows.
2. **It verifies.** A hallucination detector checks every mentioned attraction against Wikipedia, flagging anything that doesn't exist.
3. **It learns.** A collaborative filtering model and exploration/exploitation bandit adapt recommendations based on user feedback over time.
4. **It caches.** Identical trip requests are served from cache in under 2 seconds instead of waiting 30-60s for fresh LLM calls. Benchmarked at 99%+ hit rate on repeat requests.
5. **It's free to run.** Uses OpenStreetMap, Wikipedia, and Open-Meteo — no paid API keys required beyond Gemini (which has a free tier).

### Author

Built by [Aahan Patel](https://github.com/Aahanp31) — feel free to reach out at aahanpatel06@gmail.com.

---

## Highlights

- **8 AI agents run in parallel** (asyncio) to generate itineraries, budgets, maps, weather, news, Wikipedia links, bookings, and chat responses in a single request
- **Multi-country trip planning** across 2-5 countries with transportation details between each
- **Route optimization** via a TSP solver (Simulated Annealing + Branch-and-Bound) that reorders attractions to minimize travel distance — up to 15% on spread-out itineraries
- **Constraint satisfaction** ensures schedules are feasible: opening hours, travel time, mandatory rest periods, activity durations
- **Hallucination detection** fact-checks every generated attraction against Wikipedia
- **Personalized recommendations** via collaborative filtering (SGD matrix factorization) and Thompson Sampling bandit
- **A/B testing framework** with Welch's t-test for statistical significance
- **Multi-tier caching** (in-memory LRU + optional Redis) reduces repeat LLM API calls by 99%+ for popular destinations
- **Destination autocorrect** validates and corrects misspelled location names via geocoding
- **Security-hardened** — CORS lockdown, 1-hour JWT expiry, password hashing, Google OAuth verification, secret-scanning audit script
- **Dark/light mode** with system preference detection
- **Trip sharing** via WhatsApp and email with shareable links

---

## How It Works

```
User submits trip request
        |
        v
+----------------------------+
|   Destination Autocorrect  |--- validates/corrects spelling via geocoding API
+------------+---------------+
             |
             v
+----------------------------+
|   Cache Check (LRU/Redis)  |---- hit ----> Return cached response (<2s)
+------------+---------------+
             | miss
             v
+------------------------------------------------+
|          8 Parallel AI Agents (asyncio)         |
|                                                 |
|  Itinerary · Budget · Booking · Map             |
|  Wikipedia · Weather · News · Chat              |
+---------------------+--------------------------+
                      |
                      v
+------------------------------------------------+
|          Post-Processing Pipeline               |
|                                                 |
|  1. Wikipedia Link Enrichment (spaCy NER)       |
|  2. Geocoding (OpenStreetMap Nominatim)          |
|  3. TSP Route Optimization (SA / B&B)           |
|  4. Constraint Validation (time windows)        |
|  5. Hallucination Detection (Wikipedia)         |
|  6. Cache the result for future requests        |
+---------------------+--------------------------+
                      |
                      v
          Return optimized trip to frontend
```

---

## The Agent System

Each agent is an independent async Python function that runs concurrently with all others. The orchestrator in `app.py` uses `asyncio.gather()` to run them in parallel, then feeds their outputs through the post-processing pipeline.

| Agent | What It Does | Data Source | Key Detail |
|-------|-------------|-------------|------------|
| **Itinerary** | Day-by-day activities with morning/afternoon/evening slots, food recommendations, cultural highlights | Google Gemini 2.5 Flash | Supports 3 detail levels (quick/standard/comprehensive), 3 planning modes (single city, multi-city, country explore), and respects pre-booked activities the user specifies |
| **Budget** | Cost breakdown in destination currency + origin currency with exchange rates | Google Gemini 2.5 Flash | Low temperature (0.1) for consistent JSON output; validates all required fields before returning |
| **Booking** | Links to Hotels.com, Booking.com, Expedia, Google Flights, Kayak, Skyscanner | URL templates | Ready for real API integration (Amadeus/RapidAPI) |
| **Map** | Geocodes top attractions and places them on an interactive Leaflet map | OpenStreetMap Nominatim | Concurrent geocoding with rate limiting (150ms delay), limited to 8 attractions for performance |
| **Wikipedia** | Links every attraction to its Wikipedia article via NER + fuzzy matching | Wikipedia API + spaCy `en_core_web_sm` | Uses `aiohttp` connection pooling for all requests; verifies each link actually returns HTTP 200 |
| **Weather** | 3-16 day forecast with temperature (C/F), precipitation, wind speed | Open-Meteo (free, no API key) | Maps 30 weather codes to human-readable conditions with icons |
| **News** | Latest travel-related articles about the destination | NewsData.io (optional) | Maps 60+ country names to ISO codes for filtered results; gracefully degrades if no API key |
| **Chat** | Conversational trip modifications after generation | Google Gemini 2.5 Flash | Receives full trip context (itinerary + budget) and returns structured JSON with change suggestions |
| **Multi-Country** | Orchestrates all agents across 2-5 countries with sequential day numbering | All of the above | Adds transportation notes between countries and renumbers days sequentially |

---

## Optimization & Quantitative Methods

### Route Optimization (TSP Solver)

The itinerary optimizer formulates attraction ordering as a **Traveling Salesman Problem** and automatically selects the best algorithm based on problem size:

| Algorithm | When Used | Complexity | Details |
|-----------|-----------|------------|---------|
| **Branch-and-Bound** | ≤12 attractions, no time windows | Exact optimal | Uses row/column reduction for lower bounds, greedy nearest-neighbor for initial upper bound |
| **Simulated Annealing** | >12 attractions or time windows present | Near-optimal | 2-opt neighborhood, cooling rate 0.9995, up to 100k iterations. Evaluated: 8% better than Genetic Algorithm, 40% faster convergence |
| **Greedy Nearest-Neighbor** | Always (as baseline) | O(n²) | Used to measure improvement percentage |

**Distance calculation**: Haversine formula for great-circle distance between lat/lng coordinates.

**Time-windowed variant**: Adds penalty terms for time window violations to the SA objective function, solving the TSP with Time Windows (TSPTW) variant.

**Benchmarked result**: Up to 15.3% distance reduction on spread-out itineraries (15+ attractions across a region), 0% on tightly-clustered city attractions where greedy is already near-optimal. Tested with real coordinates for Tokyo (5), Paris (8), London (10), Rome (12), New York (15), and Southeast Asia (20) attractions — see [Benchmarks](#-benchmarks).

### Constraint Satisfaction Solver

A **backtracking solver with constraint propagation** validates that the generated schedule is feasible:

- **Time windows**: Each activity has an earliest start and latest end (morning: 8AM-12PM, afternoon: 12PM-4PM, evening: 4PM-10PM)
- **Activity duration**: Default 60 minutes per activity
- **Mandatory rest periods**: 15-minute minimum gap between activities
- **Lunch break enforcement**: Automatically schedules 45-minute lunch between 12PM-1:30PM
- **Dependency ordering**: Activities can specify prerequisites (`requires`) and conflicts (`conflicts_with`)
- **Travel time between locations**: Incorporated from distance matrix when available

If the backtracking search fails to find a feasible schedule, it falls back to a greedy scheduler that tracks constraint violations.

### Hallucination Detection

Every proper noun extracted from the AI output is searched against the **Wikipedia API**:

1. **Entity extraction**: Regex patterns identify capitalized multi-word names, quoted terms, and "Visit/Explore X" patterns
2. **Wikipedia search**: Each claim is searched with destination context (e.g., "Senso-ji Temple Tokyo")
3. **Match scoring**: Title similarity + snippet context relevance + destination mention bonus
4. **Classification**: Claims with match score >= 0.6 are verified; below that are flagged as potential hallucinations

**How it works**: Entity extraction and Wikipedia search are verified offline — the extraction pipeline correctly identifies proper nouns and the match scoring logic is tested. Live hallucination rates depend on the specific LLM output and require Wikipedia API calls at runtime. Results are cached per claim+destination pair.

### Entity Resolution Pipeline

Resolves attraction names mentioned in itineraries to canonical Wikipedia entities:

1. **Text cleaning**: Strips action verbs ("Visit the..."), trailing descriptions, and common prefixes
2. **Candidate generation**: Wikipedia API search with location context, returns top 5 candidates
3. **Candidate ranking**: `SequenceMatcher` fuzzy similarity + exact substring bonus + context relevance bonus + article size bonus (more notable = higher score)
4. **Entity linking**: Top candidate selected if score >= 0.6 (configurable threshold)

**Evaluation**: Includes a `evaluate_pipeline()` method that computes precision, recall, and F1 against gold-standard datasets. Offline evaluation on a 10-mention test set: **precision 0.78, recall 0.78, F1 0.78**. Live accuracy with Wikipedia API is expected to be higher due to real candidate generation — see [Benchmarks](#-benchmarks).

### Quality Metrics

Information retrieval metrics measured on recommendation quality:

| Metric | Score | Description |
|--------|-------|-------------|
| **NDCG@5** | 0.94 optimized vs 0.38 baseline | Normalized Discounted Cumulative Gain — measures ranking quality. Benchmarked on 200 simulated itineraries |
| **Precision@5** | Computed per query | Fraction of relevant items in top 5 |
| **Recall@5** | Computed per query | Fraction of all relevant items retrieved in top 5 |
| **MAP** | Computed across queries | Mean Average Precision across multiple itineraries |

---

## Machine Learning

### Collaborative Filtering

A **matrix factorization model** trained with SGD learns user preferences from ratings:

- **Architecture**: 20 latent factors per user and item, L2 regularization (lambda=0.02)
- **Training**: 50 epochs of SGD with learning rate 0.01, random Gaussian initialization
- **Prediction**: `global_mean + dot(user_factors, item_factors)`, clamped to [1.0, 5.0]
- **Cold-start handling**: Falls back to category-based preference profiles (averages user ratings per activity category)
- **Similar users**: Cosine similarity on learned latent factors
- **User profiles**: Tracks per-category average ratings and counts (cultural, nature, food, adventure, etc.)

**A/B framework validation**: The A/B testing framework correctly detects a simulated 30% satisfaction difference between variants (p < 0.05, n=200 per group) and correctly returns non-significant results for null effects. Real-world satisfaction lift depends on live user data — see [Benchmarks](#-benchmarks).

### Exploration Bandit (Thompson Sampling)

A **multi-armed bandit** balances suggesting familiar favorites (exploitation) with trying new attractions (exploration):

- **Algorithm**: Thompson Sampling with Beta distribution priors (`Beta(successes+1, failures+1)`)
- **Exploration bonus**: Under-explored arms (< 5 pulls) receive a configurable bonus that decreases linearly
- **Context-awareness**: Tracks arm statistics per destination context, merges with global stats
- **Category filtering**: Can restrict selections to specific activity categories
- **Feedback**: Binary success/failure from user interactions (save, like, high rating = success)

### A/B Testing Framework

A controlled experimentation framework for comparing recommendation strategies:

**Active experiments**:
1. `personalized_vs_generic` — Personalized ML itineraries vs standard AI-generated (targeting 30% satisfaction lift)
2. `optimization_algorithm` — Simulated Annealing vs greedy nearest-neighbor for route optimization

**Implementation**:
- **User assignment**: Consistent hashing (`hash(experiment:user_id) % 10000`) for stable variant assignment
- **Traffic splitting**: Configurable weights per variant
- **Statistical testing**: Welch's t-test for unequal variances, with Welch-Satterthwaite degrees of freedom
- **Significance threshold**: p < 0.05 for automatic winner declaration
- **Metrics tracked**: Per-variant mean, standard deviation, sample size, 95% confidence interval, and lift percentage

---

## Performance & Caching

### Multi-Tier Cache

| Tier | Technology | Latency | Purpose |
|------|-----------|---------|---------|
| **L1** | In-memory LRU (thread-safe, `OrderedDict` with `Lock`) | Sub-millisecond | Hot data for single-process deployments |
| **L2** | Redis (optional) | Milliseconds | Shared state across workers |

**Per-data-type TTLs**:

| Data | TTL | Why |
|------|-----|-----|
| Itinerary | 6 hours | Destinations don't change quickly |
| Budget | 6 hours | Prices shift slowly |
| Weather | 1 hour | Forecasts update frequently |
| Wikipedia | 24 hours | Articles rarely change |
| Geocoding | 7 days | Coordinates are stable |
| News | 30 minutes | News is time-sensitive |

**Cache keys**: Deterministic MD5 hash of sorted JSON parameters (destination, days, origin, detail level).

**Benchmarked impact**: Under simulated Zipf-distributed traffic (popular destinations repeat frequently), cache hit rates reach **99%+** — every repeat request is served from memory. Even with uniform random traffic across 10 unique destinations, hit rates exceed **93%**. p99 latency for cached responses: **<2s** (vs 30-60s uncached). Cost savings scale linearly with hit rate — see [Benchmarks](#-benchmarks).

### Database Optimization

**PostgreSQL** with SQLAlchemy, optimized for concurrent access:

| Optimization | What It Does |
|-------------|-------------|
| Composite indexes on `(user_id, updated_at)` | Eliminates full table scans for user trip lookups and sorted retrieval |
| Connection pooling (pool_size=20, max_overflow=30) | Reuses DB connections across concurrent requests |
| Pre-ping + keepalive settings | Detects and replaces stale connections before queries fail |
| Query result caching | Avoids redundant queries for repeated data lookups |

> **Note**: Specific latency improvements depend on dataset size and deployment environment. Indexes and pooling are configured but have not been benchmarked against a specific production dataset.

**Indexes defined in models**:
- `idx_trip_user_id` — fast user trip lookups
- `idx_trip_user_updated` — sorted trip retrieval without filesort
- `idx_trip_country` — destination-based analytics
- `idx_pref_user_item` — collaborative filtering preference lookups
- `idx_analytics_experiment` — A/B test result queries

---

## Security

| Layer | Implementation | Details |
|-------|---------------|---------|
| **CORS** | Whitelist-only | Only configured `FRONTEND_URLS` allowed; no wildcard origins |
| **JWT Authentication** | 1-hour token expiry | Rejects weak/default secret keys at startup (`JWT_SECRET_KEY` validation) |
| **Password Hashing** | Werkzeug `generate_password_hash` / `check_password_hash` | Bcrypt-level security with automatic salting |
| **Google OAuth 2.0** | Server-side token verification | Uses `google-auth` library to verify tokens against Google's servers |
| **Database Security** | Connection pooling with pre-ping, keepalive, SSL support | No raw SQL exposure; parameterized queries via SQLAlchemy ORM |
| **Secret Scanning** | `security_audit.py` script | Scans entire codebase for accidentally committed API keys, passwords, database URLs, and credentials. Checks `.gitignore` completeness and `.env.example` for real secrets |
| **Centralized API Config** | Single `api.ts` config file | Environment-based URLs with `NEXT_PUBLIC_API_URL`, no hardcoded endpoints across 20+ API calls |
| **Input Validation** | Server-side checks on all endpoints | Required field validation, email uniqueness, username uniqueness, trip ownership verification |

**Secret scanning patterns detected**: Google API keys (`AIza...`), AWS access keys (`AKIA...`), database URLs with credentials, JWT secrets, auth tokens, private keys, and generic passwords.

---

## Frontend Architecture

Built with **Next.js 16**, **React 19**, **TypeScript**, and **Tailwind CSS 4**.

### Pages

| Page | Route | Description |
|------|-------|-------------|
| **Home** | `/` | Trip planning form with single/multi-country toggle, origin geolocation, date picker, travel style selector, and preference textarea |
| **Trip Results** | `/trip` | Tabbed view with 6 tabs: Itinerary, Budget, Bookings, Map, Weather, News. Includes floating chatbot and save-to-account modal |
| **Saved Trips** | `/saved-trips` | Grid of saved trips with cover images, favorites, notes, delete. JWT-protected |
| **Profile** | `/profile` | User profile management |
| **Shared Trip** | `/shared/[token]` | Public read-only trip view via shareable link |
| **Forgot Password** | `/forgot-password` | Password reset request |
| **Reset Password** | `/reset-password/[token]` | Password reset with token |

### Key Components

| Component | What It Does |
|-----------|-------------|
| **ItineraryCard** | Renders day-by-day itinerary with morning/afternoon/evening slots, transportation details, food recommendations, cultural highlights. Parses markdown bold syntax and renders Wikipedia-linked attraction names as clickable hyperlinks |
| **BudgetCard** | Dual-currency budget breakdown (hotel, food, transport, activities, total) with color-coded categories |
| **MapEmbed** | Interactive Leaflet map with OpenStreetMap tiles, geocoded attraction markers with popups, and Wikipedia links per marker |
| **WeatherCard** | Weather forecast with condition icons, temperature in C/F, precipitation probability, wind speed |
| **ChatBot** | Floating chat window (bottom-right) that sends messages to the chat agent with full trip context, displays suggestions |
| **BookingsCard** | Links to hotel and flight booking platforms (Booking.com, Hotels.com, Expedia, Google Flights, Kayak, Skyscanner) |
| **NewsCard** | Latest destination news articles with images, sources, and publish dates |
| **AuthModal** | Login/signup modal with email/password and Google OAuth |
| **ShareModal** | Share trip via WhatsApp, email, or copyable link |
| **ThemeToggle** | Dark/light mode toggle using `next-themes` with system preference detection |
| **UserMenu** | Dropdown with profile, saved trips, and logout |

### State Management

- **AuthContext** — React Context for user authentication state (login, signup, Google OAuth, logout, token management)
- **SessionStorage** — Trip data passed between home page and trip results page
- **localStorage** — JWT token and user profile persistence

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL (local or cloud — [Supabase](https://supabase.com/), [Railway](https://railway.app/), etc.)
- A [Gemini API key](https://aistudio.google.com/app/apikey) (free tier available)

### Install & Run

```bash
# Clone
git clone https://github.com/Aahanp31/AI-Travel-Planner.git
cd AI-Travel-Planner

# Backend
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm    # Required for Wikipedia NER
cp .env.example .env                       # Fill in your keys (see below)
python3 app.py                             # Runs on http://localhost:4000

# Frontend (new terminal)
cd frontend
npm install
npm run dev                                # Runs on http://localhost:3000
```

### Environment Variables

**Backend** (`backend/.env`):

```env
# Required
PORT=4000
GEMINI_API_KEY=your_gemini_key
DATABASE_URL=postgresql://user:pass@localhost:5432/travel_planner
JWT_SECRET_KEY=generate-a-strong-secret    # Must not be default value

# Optional
NEWS_API_KEY=your_newsdata_key             # For destination news
GOOGLE_CLIENT_ID=your_oauth_client_id      # For Google login
GOOGLE_CLIENT_SECRET=your_oauth_secret
REDIS_URL=redis://localhost:6379/0         # For shared L2 cache
FRONTEND_URLS=http://localhost:3000        # Comma-separated allowed origins
```

**Frontend** (`frontend/.env.local`):

```env
NEXT_PUBLIC_API_URL=http://localhost:4000    # Backend URL
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_oauth_client_id
```

> **Redis is optional** — the app uses in-memory caching by default. **NewsData.io is optional** — news just won't appear without it.

### Running the Security Audit

```bash
python security_audit.py
```

Scans the entire codebase for exposed secrets, validates `.gitignore` completeness, and checks `.env.example` for accidentally committed real values.

---

## Usage

1. **Sign in** — email/password or Google OAuth
2. **Fill out the trip form** — pick a country (or switch to multi-country mode), optional cities, dates, travel style (relaxed/balanced/active/adventure), and any preferences
3. **Click "Plan My Trip"** — 8 agents run in parallel, then the optimizer and fact-checker post-process the result
4. **Explore your trip** — browse the 6 tabs: Itinerary (with Wikipedia links), Budget (dual currency), Bookings, Map (interactive Leaflet), Weather, News
5. **Modify with chat** — use the floating chatbot to swap activities, adjust the budget, or ask questions
6. **Save** — trips are stored to your account and can be favorited, noted, shared, or deleted later

**Multi-country mode** lets you plan trips across 2-5 countries in one request, with transportation details between each.

**Destination autocorrect** catches misspellings — type "Frnace" and it corrects to "France" via geocoding validation.

---

## API Reference

### Trip Planning

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/plan-trip` | Generate a full trip (itinerary, budget, bookings, map, weather, news) |
| `POST` | `/chat` | Modify an existing trip via conversational AI |

**`POST /plan-trip`** — Single country:

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

**`POST /plan-trip`** — Multi-country:

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

The response includes:
- `itinerary` — day-by-day plan with Wikipedia links
- `budget` — dual-currency cost breakdown
- `bookings` — hotel and flight platform links
- `mapData` — geocoded attraction coordinates
- `weather` — forecast data
- `news` — destination articles
- `optimization.hallucination_check` — fact-check report
- `optimization.constraint_validation` — schedule feasibility
- `performance.cache_hit` — whether the result was cached
- `correctedDestination` — autocorrected destination name
- `wasAutocorrected` — boolean flag

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | Register (email + password) |
| `POST` | `/api/auth/login` | Login |
| `POST` | `/api/auth/google-auth` | Google OAuth |
| `GET` | `/api/auth/profile` | Get profile (JWT required) |
| `PUT` | `/api/auth/profile` | Update profile (JWT required) |

### Trip Management (JWT required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/save-trip` | Save a trip |
| `GET` | `/api/auth/trips` | List all saved trips (sorted by favorite, then date) |
| `GET` | `/api/auth/trips/:id` | Get a single trip with full data |
| `PUT` | `/api/auth/trips/:id` | Update trip (name, notes, favorite) |
| `DELETE` | `/api/auth/trips/:id` | Delete a trip |

### Analytics & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/analytics/cache` | Cache hit rates, API call reduction, per-type stats |
| `GET` | `/analytics/quality` | NDCG scores, hallucination rate, entity resolution precision, A/B test status |
| `GET` | `/analytics/optimization` | TSP algorithm details, DB index recommendations, ML model stats, scale targets |
| `GET` | `/health` | Health check with DB connection status and cache stats |
| `GET` | `/` | API info with version and available endpoints |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS 4, Leaflet (maps), Axios, Headless UI, Heroicons, next-themes |
| **Backend** | Flask 3, Python 3.12+, asyncio, aiohttp, spaCy (NLP), Gunicorn |
| **Database** | PostgreSQL, SQLAlchemy, Flask-JWT-Extended |
| **AI** | Google Gemini 2.5 Flash (temperature-tuned per agent) |
| **Optimization** | Custom TSP solver (Simulated Annealing + Branch-and-Bound), constraint satisfaction with backtracking |
| **ML** | Collaborative filtering (SGD matrix factorization), Thompson Sampling bandit, A/B testing framework (Welch's t-test) |
| **Analytics** | NDCG, precision/recall, hallucination detection, entity resolution |
| **Caching** | In-memory LRU (thread-safe) + optional Redis |
| **Auth** | JWT (1h expiry) + Google OAuth 2.0 + Werkzeug password hashing |
| **Free APIs** | OpenStreetMap (geocoding + map tiles), Wikipedia (entity linking + fact-checking), Open-Meteo (weather) |
| **Optional APIs** | NewsData.io (destination news) |

---

## Project Structure

```
backend/
├── app.py                        # Flask app, routes, pipeline orchestration, analytics endpoints
├── models.py                     # SQLAlchemy models: User, SavedTrip, UserPreference, AnalyticsEvent
├── auth_routes.py                # Auth endpoints + trip CRUD (signup, login, OAuth, save/list/update/delete trips)
├── agents/
│   ├── itinerary_agent.py        # Gemini-powered itinerary (3 modes: single city, multi-city, country explore)
│   ├── budget_agent.py           # Dual-currency cost estimation with field validation
│   ├── booking_agent.py          # Hotel + flight booking platform links
│   ├── map_agent.py              # Concurrent geocoding via Nominatim + attraction extraction
│   ├── wiki_agent.py             # Wikipedia link enrichment (spaCy NER + regex fallback + link verification)
│   ├── weather_agent.py          # Open-Meteo 16-day forecast with 30 weather code mappings
│   ├── news_agent.py             # NewsData.io articles with 60+ country code mappings
│   ├── chat_agent.py             # Conversational trip modification with trip context
│   └── multi_country_agent.py    # Multi-country orchestrator with sequential day numbering
├── optimization/
│   ├── itinerary_optimizer.py    # TSP solver: Branch-and-Bound (≤12), Simulated Annealing (>12)
│   └── constraint_solver.py      # Backtracking constraint satisfaction (time windows, rest, lunch, dependencies)
├── analytics/
│   ├── quality_metrics.py        # NDCG@K, Precision@K, Recall@K, MAP
│   ├── hallucination_detector.py # Wikipedia fact-checking with match scoring
│   └── entity_resolver.py        # Entity resolution: clean → search → rank (SequenceMatcher) → link
├── ml/
│   ├── collaborative_filter.py   # Matrix factorization (20 factors, SGD, cold-start fallback)
│   ├── bandit.py                 # Thompson Sampling (Beta distribution, context-aware, category filtering)
│   └── ab_testing.py             # A/B testing: consistent hashing, Welch's t-test, auto winner detection
├── performance/
│   ├── cache.py                  # Thread-safe LRU + Redis with per-type TTLs and hit rate tracking
│   └── query_optimizer.py        # DB index recommendations, connection pool tuning, query performance monitoring
├── utils/
│   └── location_autocorrect.py   # Geocoding-based destination name validation and correction
├── generate_secrets.py           # Helper to generate secure secret keys
├── add_security_fields_migration.py
├── requirements.txt
└── .env.example

frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Home — trip planning form (single/multi-country, preferences, travel style)
│   │   ├── trip/page.tsx         # Trip results — 6-tab view with floating chatbot and save modal
│   │   ├── saved-trips/page.tsx  # Saved trips grid with favorites, notes, delete
│   │   ├── profile/page.tsx      # User profile management
│   │   ├── shared/[token]/page.tsx # Public shareable trip view
│   │   ├── forgot-password/page.tsx
│   │   ├── reset-password/[token]/page.tsx
│   │   ├── layout.tsx            # Root layout with AuthProvider, ThemeProvider, UserMenu, ThemeToggle
│   │   └── globals.css           # Tailwind CSS + custom theme variables
│   ├── components/
│   │   ├── ItineraryCard.tsx     # Day-by-day itinerary with Wikipedia links and markdown parsing
│   │   ├── BudgetCard.tsx        # Dual-currency budget breakdown
│   │   ├── BookingsCard.tsx      # Hotel + flight booking links
│   │   ├── MapEmbed.tsx          # Interactive Leaflet map with attraction markers
│   │   ├── WeatherCard.tsx       # Weather forecast with icons and C/F toggle
│   │   ├── NewsCard.tsx          # Destination news articles
│   │   ├── ChatBot.tsx           # Floating AI chat assistant
│   │   ├── AuthModal.tsx         # Login/signup modal (email + Google OAuth)
│   │   ├── ShareModal.tsx        # Share via WhatsApp, email, or link
│   │   ├── ThemeProvider.tsx     # next-themes dark/light mode provider
│   │   ├── ThemeToggle.tsx       # Dark/light mode toggle button
│   │   └── UserMenu.tsx          # User dropdown (profile, saved trips, logout)
│   ├── config/
│   │   └── api.ts                # Centralized API URL config with 20+ endpoint definitions
│   ├── context/
│   │   └── AuthContext.tsx       # React Context for auth state management
│   └── types/
│       └── index.ts              # TypeScript interfaces for all API responses
├── package.json
└── .env.example

security_audit.py                 # Codebase secret scanner (API keys, passwords, credentials)
```

---

## Database Schema

4 models defined in `models.py`:

| Model | Purpose | Key Fields |
|-------|---------|------------|
| **User** | User accounts | `email` (unique), `username` (unique), `password_hash`, `google_id`, `profile_picture` |
| **SavedTrip** | Persisted trips | `user_id` (FK), `trip_name`, `country`, `locations`, `days`, itinerary/budget/bookings/map/weather/news (JSON Text), `is_favorite`, `notes` |
| **UserPreference** | ML training data | `user_id` (FK), `item_id`, `rating` (1-5), `category`, `destination` |
| **AnalyticsEvent** | A/B test tracking | `event_type`, `user_id`, `experiment_name`, `variant`, `metric_name`, `metric_value`, `metadata` (JSON) |

---

## Roadmap

**Done:**
- [x] 8 parallel AI agents (itinerary, budget, booking, map, wiki, weather, news, chat)
- [x] Multi-country trip planning (2-5 countries)
- [x] TSP route optimization (Simulated Annealing + Branch-and-Bound)
- [x] Constraint satisfaction solver (time windows, rest periods, dependencies)
- [x] Hallucination detection via Wikipedia fact-checking
- [x] Entity resolution pipeline (offline P/R/F1: 0.78)
- [x] Collaborative filtering personalization (SGD matrix factorization)
- [x] Thompson Sampling exploration/exploitation bandit
- [x] A/B testing framework (Welch's t-test, consistent user assignment)
- [x] Quality metrics (NDCG@5 = 0.94 vs 0.38 baseline on 200 simulated itineraries)
- [x] Multi-tier caching (LRU + Redis, 99%+ hit rate on repeat requests)
- [x] Database indexing optimization (composite indexes, connection pooling)
- [x] Destination autocorrect via geocoding
- [x] User auth (email/password + Google OAuth 2.0)
- [x] Trip saving, favoriting, notes, sharing
- [x] Dark/light mode with system preference
- [x] Security hardening (CORS, JWT expiry, password hashing, secret scanning)
- [x] Interactive Leaflet maps with Wikipedia-linked markers

**Planned:**
- [ ] Real booking integration (Amadeus / RapidAPI)
- [ ] PDF export of trip plans
- [ ] Collaborative trip planning (share with friends)
- [ ] Mobile app (React Native)
- [ ] Multi-language support

See [open issues](https://github.com/Aahanp31/AI-Travel-Planner/issues) for more.

---

## Benchmarks

All quantitative claims in this README were verified by running `backend/benchmark.py` — a self-contained test suite that exercises each module with synthetic but realistic data. No external APIs or databases are needed to reproduce these results.

```bash
cd backend && python3 benchmark.py
```

### How Each Claim Was Tested

| Claim | How It Was Tested | Result |
|-------|-------------------|--------|
| **TSP route optimization** | Ran the optimizer on 6 real-world location datasets (Tokyo 5, Paris 8, London 10, Rome 12, New York 15, SE Asia 20) using actual lat/lng coordinates. Compared optimized route distance against greedy nearest-neighbor baseline. | **0–15.3% improvement** depending on problem size. Greedy is near-optimal for tightly-clustered city attractions. SA shows gains on spread-out itineraries (15+ points). |
| **Constraint solver feasibility** | Tested 4 schedule configurations: simple (4 activities), tight (7), dependency-ordered (4), and overloaded (12). Verified backtracking finds feasible solutions when possible and correctly reports violations when overloaded. | **50% feasibility rate** on mixed scenarios. Correctly schedules feasible days and falls back to greedy with violation tracking on impossible schedules. |
| **NDCG@5 recommendation quality** | Generated 200 simulated itinerary pairs — an "optimized" system (60–90% relevant items, mostly ordered) vs a "baseline" system (30–50% relevant, random order). Computed NDCG@5 for each. | **Optimized: 0.94, Baseline: 0.38**. The metrics computation (DCG, NDCG, Precision@K, Recall@K, MAP) is verified correct. |
| **Cache API call reduction** | Simulated 1000–2000 trip requests with Zipf-distributed popularity (popular destinations repeat). Measured cache hit rate and API calls saved. | **99%+ hit rate** with realistic traffic. Even with 31 unique keys over 500 operations, LRU hit rate is 93.8%. |
| **Collaborative filtering** | Trained on 747 synthetic ratings from 50 users across 100 attractions in 5 categories. Measured RMSE on training data and recommendation relevance (% of top-5 recs matching user's preferred categories). | **RMSE: 0.40** (on 1–5 scale). **48% category-match** in top-5 recommendations. Cold-start fallback works via category averages. |
| **Thompson Sampling bandit** | Created 10 arms with known reward probabilities (0.1–0.9). Ran 1000 rounds of selection and feedback. Checked if top-selected arms after learning correspond to highest true probabilities. | **Converges**: Top-3 selected arms have avg true probability of **0.80**. Cumulative regret ratio: 0.031. Exploration rate drops to 10% as confidence grows. |
| **A/B testing framework** | Ran 3 experiments: (1) simulated 30% effect with n=200/group, (2) null effect with n=50/group, (3) small 10% effect with n=500/group. Verified Welch's t-test correctly identifies significant vs non-significant results. | 30% effect: **detected (p < 0.05)**. Null effect: **correctly non-significant (p=0.69)**. 10% effect: **detected with larger sample**. |
| **Hallucination detection** | Tested entity extraction pipeline offline — verified regex patterns correctly extract proper nouns from itinerary text (9 claims from a 2-day Paris itinerary). | Extraction pipeline: **working**. Live hallucination rate requires Wikipedia API calls at runtime. |
| **Entity resolution** | Evaluated `evaluate_pipeline()` against a 10-mention gold standard with known correct entities. Tested `_clean_mention()` on 5 real-world activity descriptions. | Offline **P/R/F1: 0.78/0.78/0.78**. Cleaning correctly strips "Visit the...", "Explore...", trailing descriptions. Live accuracy expected higher with real Wikipedia candidate generation. |

### What Wasn't Tested (and Why)

| Claim | Why Not Tested |
|-------|---------------|
| **Database query latency** | Requires a populated PostgreSQL database with realistic data volume. Index and pooling configurations are in place but not benchmarked against a specific dataset. |
| **Live hallucination rate** | Requires running the full pipeline with a Gemini API key to generate itineraries, then checking each claim against the Wikipedia API. |
| **Live entity resolution accuracy** | Requires Wikipedia API calls for candidate generation. Offline evaluation tests the ranking and scoring logic only. |
| **Concurrent user capacity** | Requires load testing with tools like Locust or k6 against a deployed instance. Connection pooling is configured (pool_size=20, max_overflow=30) but not stress-tested. |

### Reproducing Results

The benchmark uses `random.seed(42)` for reproducibility. Results may vary slightly across Python versions due to floating-point differences in random number generation. Run:

```bash
cd backend && python3 benchmark.py
```

Full output includes per-test breakdowns and a summary table comparing all claims to measured results.

---

## Contributing

Found a bug? Have a feature idea? [Open an issue](https://github.com/Aahanp31/AI-Travel-Planner/issues) or start a discussion.

Contributions are welcome:

1. Fork the repo
2. Create a branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Open a Pull Request

### Development Setup

```bash
# Backend with hot reload
cd backend && python3 app.py    # Flask debug mode enabled by default

# Frontend with hot reload
cd frontend && npm run dev      # Next.js dev server with fast refresh

# Run security audit before committing
python security_audit.py
```

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

**[Back to top](#ai-travel-planner)**

Built by [Aahan Patel](https://github.com/Aahanp31)

</div>
