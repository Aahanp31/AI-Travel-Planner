# Architecture

## The Agent System

Each agent is an independent async Python function that runs concurrently with all others. The orchestrator in `app.py` uses `asyncio.gather()` to run them in parallel, then feeds their outputs through the post-processing pipeline.

| Agent | What It Does | Data Source | Key Detail |
|-------|-------------|-------------|------------|
| **Itinerary** | Day-by-day activities with morning/afternoon/evening slots, food recommendations, cultural highlights | Google Gemini 2.5 Flash | Supports 3 detail levels (quick/standard/comprehensive), 3 planning modes (single city, multi-city, country explore), and respects pre-booked activities the user specifies |
| **Budget** | Cost breakdown in destination currency + origin currency with exchange rates | Google Gemini 2.5 Flash | Low temperature (0.1) for consistent JSON output; validates all required fields before returning |
| **Booking** | Links to Hotels.com, Booking.com, Expedia, Google Flights, Kayak, Skyscanner | URL templates | Ready for real API integration (Amadeus/RapidAPI) |
| **Map** | Geocodes top attractions and places them on an interactive Leaflet map | OpenStreetMap Nominatim | Sequential geocoding with 1.1s stagger to respect Nominatim's 1 req/s limit; capped at 5 attractions for performance |
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

**Benchmarked result**: Up to 15.3% distance reduction on spread-out itineraries (15+ attractions across a region), 0% on tightly-clustered city attractions where greedy is already near-optimal.

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

Results are cached per claim+destination pair.

### Entity Resolution Pipeline

Resolves attraction names mentioned in itineraries to canonical Wikipedia entities:

1. **Text cleaning**: Strips action verbs ("Visit the..."), trailing descriptions, and common prefixes
2. **Candidate generation**: Wikipedia API search with location context, returns top 5 candidates
3. **Candidate ranking**: `SequenceMatcher` fuzzy similarity + exact substring bonus + context relevance bonus + article size bonus
4. **Entity linking**: Top candidate selected if score >= 0.6 (configurable threshold)

Offline evaluation on a 10-mention test set: **precision 0.78, recall 0.78, F1 0.78**.

### Quality Metrics

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

### Exploration Bandit (Thompson Sampling)

A **multi-armed bandit** balances suggesting familiar favorites (exploitation) with trying new attractions (exploration):

- **Algorithm**: Thompson Sampling with Beta distribution priors (`Beta(successes+1, failures+1)`)
- **Exploration bonus**: Under-explored arms (< 5 pulls) receive a configurable bonus that decreases linearly
- **Context-awareness**: Tracks arm statistics per destination context, merges with global stats
- **Category filtering**: Can restrict selections to specific activity categories
- **Feedback**: Binary success/failure from user interactions (save, like, high rating = success)

### A/B Testing Framework

**Active experiments**:
1. `personalized_vs_generic` — Personalized ML itineraries vs standard AI-generated
2. `optimization_algorithm` — Simulated Annealing vs greedy nearest-neighbor

**Implementation**:
- **User assignment**: Consistent hashing (`hash(experiment:user_id) % 10000`) for stable variant assignment
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

**Benchmarked impact**: Cache hit rates reach **99%+** under Zipf-distributed traffic. p99 latency for cached responses: **<2s** (vs 30-60s uncached).

### Database Optimization

PostgreSQL with SQLAlchemy, optimized for concurrent access:

| Optimization | What It Does |
|-------------|-------------|
| Composite indexes on `(user_id, updated_at)` | Eliminates full table scans for user trip lookups |
| Connection pooling (pool_size=20, max_overflow=30) | Reuses DB connections across concurrent requests |
| Pre-ping + keepalive settings | Detects and replaces stale connections before queries fail |

**Indexes defined in `models.py`**:
- `idx_trip_user_id` — fast user trip lookups
- `idx_trip_user_updated` — sorted trip retrieval without filesort
- `idx_trip_country` — destination-based analytics
- `idx_pref_user_item` — collaborative filtering preference lookups
- `idx_analytics_experiment` — A/B test result queries

---

## Frontend Architecture

Built with **Next.js 16**, **React 19**, **TypeScript**, and **Tailwind CSS 4**.

### Pages

| Page | Route | Description |
|------|-------|-------------|
| **Home** | `/` | Trip planning form with single/multi-country toggle, origin geolocation, date picker, travel style selector |
| **Trip Results** | `/trip` | Tabbed view with 6 tabs: Itinerary, Budget, Bookings, Map, Weather, News. Includes floating chatbot and save modal |
| **Saved Trips** | `/saved-trips` | Grid of saved trips with cover images, favorites, notes, delete. JWT-protected |
| **Profile** | `/profile` | User profile management |
| **Shared Trip** | `/shared/[token]` | Public read-only trip view via shareable link |

### Key Components

| Component | What It Does |
|-----------|-------------|
| **ItineraryCard** | Day-by-day itinerary with Wikipedia links and markdown parsing |
| **BudgetCard** | Dual-currency budget breakdown with color-coded categories |
| **MapEmbed** | Interactive Leaflet map with geocoded attraction markers |
| **WeatherCard** | Weather forecast with condition icons, C/F toggle |
| **ChatBot** | Floating chat window that sends messages to the chat agent with full trip context |
| **AuthModal** | Login/signup modal with email/password and Google OAuth |
| **ShareModal** | Share trip via WhatsApp, email, or copyable link |

### State Management

- **AuthContext** — React Context for user authentication state
- **SessionStorage** — Trip data passed between home page and trip results page
- **localStorage** — JWT token and user profile persistence

---

## Database Schema

4 models defined in `backend/models.py`:

| Model | Purpose | Key Fields |
|-------|---------|------------|
| **User** | User accounts | `email` (unique), `username` (unique), `password_hash`, `google_id`, `profile_picture` |
| **SavedTrip** | Persisted trips | `user_id` (FK), `trip_name`, `country`, `locations`, `days`, itinerary/budget/bookings/map/weather/news (JSON), `is_favorite`, `notes` |
| **UserPreference** | ML training data | `user_id` (FK), `item_id`, `rating` (1-5), `category`, `destination` |
| **AnalyticsEvent** | A/B test tracking | `event_type`, `user_id`, `experiment_name`, `variant`, `metric_name`, `metric_value`, `metadata` (JSON) |
