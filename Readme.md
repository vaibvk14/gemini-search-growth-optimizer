
# Gemini Search Growth & Discover Optimizer

A production-grade reference architecture and multivariate experimentation framework designed to solve a core economic friction in generative search: maximizing commercial query continuation and multi-turn session depth in AI Overviews and AI Mode without regressing P99 latency SLAs or user trust.

---

## 1. Context & The Core Search Growth Problem

As Google scales generative AI across the search surface, product teams face an acute optimization challenge:
* The Zero-Click Bottleneck: Instantaneous generative summaries satisfy informational intent immediately, creating a structural compression in traditional Click-Through Rates (CTR) and multi-turn session depth.
* The eRPM Monetization Disconnect: Informational AI queries exhibit a lower effective Revenue Per Mille (eRPM) compared to classic commercial intent queries, requiring intelligent, low-latency bridges into the Shopping Graph and commercial comparison surfaces.
* The Episodic-to-Habitual Gap: High-value search interactions remain fragmented unless anchored to personalized, recurring Google Discover interest graphs.

---

## 2. System Architecture & Latency-Bounded Guardrails

To maintain Google's strict sub-second performance bar, the architecture separates high-speed feature retrieval from deterministic intent classification:

[User Query & Session State] 
       │
       ▼
[Low-Latency Feature Store] (Redis / Session Context in <15ms)
       │
       ▼
[Gemini Propensity & Fan-Out Engine] (Intent Classification & NBA Chips)
       │
       ▼
[Pydantic Schema Validator] (Strict Zero-Hallucination JSON Guardrail)
       │
       ▼
[Kafka Telemetry & Experimentation] (Real-time A/B assignment & eRPM logging)

### Key Technical & Product Decisions
* Deterministic Intent Routing (temperature=0.0): We treat the LLM strictly as a deterministic classification and fan-out engine, preventing generative drift in commercial categorization.
* Strict Pydantic Schema Contracts: All dynamic UI chips are bounded by rigid JSON schemas, eliminating malformed client payloads or unvalidated strings.
* Circuit Breakers & Graceful Degradation: If model grounding confidence drops below 0.95 or execution latency breaches the 150ms SLA threshold, the system automatically falls back to cached lexical query expansions.

---

## 3. Multivariate Experimentation Framework (A/B Test Design)

To measure true incremental lift on session LTV rather than vanity interaction rates, this architecture implements a 4-cell multivariate design:

* Control (C0)
  * Configuration: Standard AI Overview with static related search chips.
  * North Star Metric: Baseline Session Depth and eRPM.
  * Guardrails: P99 Latency, Thumbs-Down / Dismissal Rate.

* Treatment 1 (T1)
  * Configuration: Commercial Fan-Out with dynamic high-intent comparison chips injected when Propensity > 0.65.
  * North Star Metric: Commercial Query Continuation Rate (+12% target).
  * Guardrails: Organic Satisfaction, Ad Blindness Rate.

* Treatment 2 (T2)
  * Configuration: Discover Loop with context-aware "Follow Topic" integration at summary completion.
  * North Star Metric: 7-Day Discover Return DAU (+4.5% target).
  * Guardrails: Feed Unsubscribe Rate, Next-Query Latency.

* Treatment 3 (T3)
  * Configuration: Hybrid NBA Policy with propensity-weighted allocation between commercial and Discover chips.
  * North Star Metric: Session LTV and Multi-Turn Depth (+18% target).
  * Guardrails: Overall Session Bounce Rate (Target: -5%).

---

## 4. Local Execution & Verification

To run the propensity scoring engine locally against test telemetry:

1. Install dependencies:
   ```bash
   pip install google-genai pydantic
