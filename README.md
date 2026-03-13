<div align="center">

# AI Travel Planner

**Plan smarter trips with AI agents, route optimization, and personalized recommendations.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![Flask 3.0](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![React 19](https://img.shields.io/badge/React-19-61dafb)](https://react.dev/)
[![Gemini 2.5](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4)](https://ai.google.dev/)

[Getting Started](#-getting-started) · [How It Works](#-how-it-works) · [Tech Stack](#-tech-stack) · [Architecture](docs/ARCHITECTURE.md) · [API](docs/API.md) · [Deployment](docs/DEPLOYMENT.md) · [Report Bug](https://github.com/Aahanp31/AI-Travel-Planner/issues)

</div>

---

## What It Does

AI Travel Planner takes a destination, dates, and your preferences, then orchestrates **8 specialized AI agents in parallel** to produce a complete trip plan: day-by-day itinerary, dual-currency budget estimates, interactive map, weather forecast, destination news, booking links, and Wikipedia enrichment for every attraction.

What makes it different from asking ChatGPT for an itinerary:

1. **It optimizes.** A TSP solver reorders activities geographically and a constraint solver validates everything fits within realistic time windows.
2. **It verifies.** A hallucination detector checks every mentioned attraction against Wikipedia.
3. **It learns.** A collaborative filtering model and Thompson Sampling bandit adapt recommendations based on user feedback.
4. **It caches.** Repeat requests are served in under 2 seconds instead of waiting 30-60s for fresh LLM calls (99%+ hit rate).
5. **It's free to run.** Uses OpenStreetMap, Wikipedia, and Open-Meteo — no paid APIs required beyond Gemini (free tier available).

### Author

Built by [Aahan Patel](https://github.com/Aahanp31) — feel free to reach out at aahanpatel06@gmail.com.

---

## Highlights

- **8 AI agents run in parallel** (asyncio) — itinerary, budget, map, weather, news, Wikipedia, bookings, chat
- **Multi-country trip planning** across 2-5 countries with transportation details between each
- **Route optimization** via TSP solver (Simulated Annealing + Branch-and-Bound) — up to 15% distance reduction
- **Constraint satisfaction** ensures schedules are feasible: opening hours, travel time, rest periods
- **Hallucination detection** fact-checks every generated attraction against Wikipedia
- **Personalized recommendations** via collaborative filtering (SGD matrix factorization) and Thompson Sampling bandit
- **Multi-tier caching** (in-memory LRU + optional Redis) — 99%+ hit rate on repeat requests
- **Destination autocorrect** validates and corrects misspelled location names via geocoding
- **Security-hardened** — CORS lockdown, 1-hour JWT expiry, password hashing, Google OAuth, secret scanning
- **Dark/light mode** with system preference detection
- **Trip sharing** via WhatsApp and email

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

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full details on agents, optimization algorithms, ML models, caching, and database schema.

---

## Getting Started

### Prerequisites

- A [Gemini API key](https://aistudio.google.com/app/apikey) (free tier available)
- **Docker** (recommended) — [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Or manually: Python 3.12+, Node.js 18+, PostgreSQL

---

### Option 1: Docker (Recommended)

The easiest way to run the full stack (frontend + backend + PostgreSQL) with a single command.

```bash
# Clone
git clone https://github.com/Aahanp31/AI-Travel-Planner.git
cd AI-Travel-Planner

# Set up backend environment
cp backend/.env.example backend/.env      # Fill in your keys
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id
GEMINI_API_KEY=your_gemini_key
```

Create a root `.env` (used by Docker for the frontend build):
```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id
GEMINI_API_KEY=your_gemini_key
```

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:4000`
- PostgreSQL runs automatically with persistent storage

```bash
docker compose down          # Stop everything
docker compose up            # Start again (no rebuild needed)
docker compose logs backend  # View backend logs
```

---

### Option 2: Manual Setup

```bash
git clone https://github.com/Aahanp31/AI-Travel-Planner.git
cd AI-Travel-Planner

# Backend
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env          # Fill in your keys
python3 app.py                # Runs on http://localhost:4000

# Frontend (new terminal)
cd frontend
npm install
npm run dev                   # Runs on http://localhost:3000
```

### Environment Variables

**Backend** (`backend/.env`):

```env
PORT=4000
GEMINI_API_KEY=your_gemini_key
DATABASE_URL=postgresql://user:pass@localhost:5432/travel_planner
JWT_SECRET_KEY=generate-a-strong-secret

# Optional
NEWS_API_KEY=your_newsdata_key
GOOGLE_CLIENT_ID=your_oauth_client_id
GOOGLE_CLIENT_SECRET=your_oauth_secret
REDIS_URL=redis://localhost:6379/0
FRONTEND_URLS=http://localhost:3000
```

**Frontend** (`frontend/.env.local`):

```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_oauth_client_id
GEMINI_API_KEY=your_gemini_key
```

> **Redis is optional** — in-memory caching is used by default. **NewsData.io is optional** — news tab won't appear without it.

---

## Usage

1. **Sign in** — email/password or Google OAuth
2. **Fill out the form** — destination, dates, travel style, and any preferences
3. **Click "Plan My Trip"** — 8 agents run in parallel, then the optimizer and fact-checker post-process the result
4. **Explore your trip** — Itinerary (Wikipedia-linked), Budget (dual currency), Bookings, Map, Weather, News
5. **Modify with chat** — use the floating chatbot to swap activities or adjust the budget
6. **Save** — trips can be favorited, noted, shared, or deleted

**Multi-country mode** lets you plan trips across 2-5 countries in one request.
**Destination autocorrect** catches misspellings via geocoding validation.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS 4, Leaflet, Axios, next-themes |
| **Backend** | Flask 3, Python 3.12+, asyncio, aiohttp, spaCy, Gunicorn |
| **Database** | PostgreSQL, SQLAlchemy, Flask-JWT-Extended |
| **AI** | Google Gemini 2.5 Flash (temperature-tuned per agent) |
| **Optimization** | Custom TSP solver (Simulated Annealing + Branch-and-Bound), backtracking constraint satisfaction |
| **ML** | Collaborative filtering (SGD matrix factorization), Thompson Sampling bandit, A/B testing (Welch's t-test) |
| **Caching** | In-memory LRU (thread-safe) + optional Redis |
| **Auth** | JWT (1h expiry) + Google OAuth 2.0 + Werkzeug password hashing |
| **Free APIs** | OpenStreetMap (geocoding + maps), Wikipedia (entity linking + fact-checking), Open-Meteo (weather) |
| **Optional APIs** | NewsData.io (destination news) |

---

## Project Structure

```
backend/
├── app.py                        # Flask app, routes, pipeline orchestration
├── models.py                     # SQLAlchemy models
├── auth_routes.py                # Auth endpoints + trip CRUD
├── agents/                       # 9 async AI agents
├── ml/                           # Thompson Sampling bandit, A/B testing
├── optimization/                 # TSP solver + constraint satisfaction
├── performance/                  # LRU + Redis cache, query optimizer
├── utils/                        # Destination autocorrect
├── scripts/                      # Dev utilities (security_audit.py)
└── requirements.txt

frontend/
├── src/
│   ├── app/                      # Next.js pages (home, trip, saved-trips, profile, shared)
│   ├── components/
│   │   ├── trip/                 # Trip display components (ItineraryCard, BudgetCard, MapEmbed, ChatBot, ...)
│   │   ├── auth/                 # Auth components (AuthModal, UserMenu)
│   │   └── ui/                  # Layout components (ThemeProvider, ThemeToggle)
│   ├── config/api.ts             # Centralized API URL config + getAuthHeaders
│   ├── context/AuthContext.tsx   # Auth state management
│   └── types/index.ts            # TypeScript interfaces
└── package.json

docs/
├── ARCHITECTURE.md               # Agents, optimization, ML, caching, DB schema
├── API.md                        # Full API reference
├── BENCHMARKS.md                 # How claims were tested and reproduced
├── SECURITY.md                   # Security measures and secret scanning
├── DEPLOYMENT.md                 # Deploying to Vercel + Render
└── SETUP_DATABASE.md             # Manual PostgreSQL setup

docker-compose.yml                # Local dev: frontend + backend + PostgreSQL
render.yaml                       # Render deployment config
```

---

## Roadmap

**Done:**
- [x] 8 parallel AI agents
- [x] Multi-country trip planning
- [x] TSP route optimization (Simulated Annealing + Branch-and-Bound)
- [x] Constraint satisfaction solver
- [x] Hallucination detection via Wikipedia
- [x] Collaborative filtering personalization
- [x] Thompson Sampling bandit
- [x] A/B testing framework
- [x] Multi-tier caching (LRU + Redis)
- [x] Destination autocorrect
- [x] User auth (email/password + Google OAuth 2.0)
- [x] Trip saving, favoriting, notes, sharing
- [x] Dark/light mode
- [x] Docker support
- [x] Interactive Leaflet maps with Wikipedia-linked markers

**Planned:**
- [ ] Real booking integration (Amadeus / RapidAPI)
- [ ] PDF export of trip plans
- [ ] Collaborative trip planning (share with friends)
- [ ] Mobile app (React Native)
- [ ] Multi-language support

---

## Contributing

Found a bug? Have a feature idea? [Open an issue](https://github.com/Aahanp31/AI-Travel-Planner/issues) or start a discussion.

1. Fork the repo
2. Create a branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Open a Pull Request

```bash
# With Docker (recommended)
docker compose up --build

# Without Docker
cd backend && python3 app.py    # Flask backend on :4000
cd frontend && npm run dev      # Next.js frontend on :3000

# Run security audit before committing
cd backend && python scripts/security_audit.py
```

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

**[Back to top](#ai-travel-planner)**

Built by [Aahan Patel](https://github.com/Aahanp31)

</div>
