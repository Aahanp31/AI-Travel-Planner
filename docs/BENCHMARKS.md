# Benchmarks

All quantitative claims were verified by running `backend/benchmark.py` — a self-contained test suite that exercises each module with synthetic but realistic data. No external APIs or databases are needed to reproduce these results.

```bash
cd backend && python3 benchmark.py
```

---

## Results

| Claim | How It Was Tested | Result |
|-------|-------------------|--------|
| **TSP route optimization** | Ran the optimizer on 6 real-world location datasets (Tokyo 5, Paris 8, London 10, Rome 12, New York 15, SE Asia 20) using actual lat/lng coordinates. Compared optimized route distance against greedy nearest-neighbor baseline. | **0–15.3% improvement** depending on problem size. Greedy is near-optimal for tightly-clustered city attractions. SA shows gains on spread-out itineraries (15+ points). |
| **Constraint solver feasibility** | Tested 4 schedule configurations: simple (4 activities), tight (7), dependency-ordered (4), and overloaded (12). | **50% feasibility rate** on mixed scenarios. Correctly schedules feasible days and falls back to greedy with violation tracking on impossible schedules. |
| **NDCG@5 recommendation quality** | Generated 200 simulated itinerary pairs — optimized (60–90% relevant, mostly ordered) vs baseline (30–50% relevant, random order). | **Optimized: 0.94, Baseline: 0.38** |
| **Cache API call reduction** | Simulated 1000–2000 trip requests with Zipf-distributed popularity. | **99%+ hit rate** with realistic traffic. Even with 31 unique keys over 500 operations, LRU hit rate is 93.8%. |
| **Collaborative filtering** | Trained on 747 synthetic ratings from 50 users across 100 attractions in 5 categories. | **RMSE: 0.40** (on 1–5 scale). **48% category-match** in top-5 recommendations. |
| **Thompson Sampling bandit** | Created 10 arms with known reward probabilities (0.1–0.9). Ran 1000 rounds. | Top-3 selected arms have avg true probability of **0.80**. Cumulative regret ratio: 0.031. |
| **A/B testing framework** | Ran 3 experiments: 30% effect (n=200), null effect (n=50), 10% effect (n=500). | 30% effect: **detected (p < 0.05)**. Null: **correctly non-significant (p=0.69)**. 10% effect: **detected with larger sample**. |
| **Hallucination detection** | Tested entity extraction pipeline offline on a 2-day Paris itinerary (9 claims). | Extraction pipeline: **working**. Live hallucination rate requires Wikipedia API at runtime. |
| **Entity resolution** | Evaluated against a 10-mention gold standard. | Offline **P/R/F1: 0.78/0.78/0.78**. Live accuracy expected higher with real Wikipedia candidates. |

---

## What Wasn't Tested

| Claim | Why Not Tested |
|-------|---------------|
| **Database query latency** | Requires a populated PostgreSQL database with realistic data volume. |
| **Live hallucination rate** | Requires a Gemini API key to generate itineraries, then Wikipedia API calls to check each claim. |
| **Live entity resolution accuracy** | Requires Wikipedia API calls for candidate generation. |
| **Concurrent user capacity** | Requires load testing (Locust/k6) against a deployed instance. Connection pooling is configured (pool_size=20, max_overflow=30) but not stress-tested. |

---

## Reproducing Results

The benchmark uses `random.seed(42)` for reproducibility. Results may vary slightly across Python versions due to floating-point differences.

```bash
cd backend && python3 benchmark.py
```

Full output includes per-test breakdowns and a summary table comparing all claims to measured results.
