import os
import json
import time
from typing import List, Literal
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# =====================================================================
# 1. DETERMINISTIC DATA CONTRACTS (PYDANTIC SCHEMAS FOR SEARCH UI)
# =====================================================================

class FollowUpChip(BaseModel):
    chip_label: str = Field(
        description="Concise 4-7 word clickable follow-up query chip for the Search UI."
    )
    intent_category: Literal[
        "COMMERCIAL_COMPARISON", 
        "DEEP_RESEARCH_CONTINUATION", 
        "DISCOVER_FEED_SUBSCRIPTION"
    ] = Field(description="Strategic growth bucket for multivariate A/B routing.")
    target_surface: Literal["AI_MODE_THREAD", "SHOPPING_GRAPH", "GOOGLE_DISCOVER"] = Field(
        description="Google surface where clicking this chip routes the user."
    )
    estimated_erpm_multiplier: float = Field(
        description="Projected monetization multiplier relative to baseline informational query (e.g., 1.0 to 3.5)."
    )

class SearchGrowthPropensityDecision(BaseModel):
    original_query: str
    query_intent_stage: Literal["INFORMATIONAL", "CONSIDERATION", "TRANSACTIONAL", "HABITUAL_TOPIC"]
    commercial_propensity_score: float = Field(
        description="Probability (0.00 to 1.00) that user will convert to a high-intent commercial query within 2 turns."
    )
    discover_retention_score: float = Field(
        description="Probability (0.00 to 1.00) that this topic is suitable for recurring Google Discover feed cards."
    )
    grounding_confidence: float = Field(
        description="Confidence score (0.00 to 1.00) that follow-up suggestions are factually grounded without hallucination."
    )
    fallback_to_lexical_cache: bool = Field(
        description="True if grounding_confidence < 0.95 or safety/compliance ambiguity is detected."
    )
    recommended_experiment_bucket: Literal["T1_COMMERCIAL_FANOUT", "T2_DISCOVER_LOOP", "T3_HYBRID_NBA", "C0_FALLBACK"]
    next_best_action_chips: List[FollowUpChip] = Field(
        description="Exactly 3 high-converting follow-up chips tailored to maximize session depth and retention."
    )

# =====================================================================
# 2. SYSTEM GUARDRAILS PROMPT (ZERO-HALLUCINATION & GROWTH ROUTING)
# =====================================================================

SEARCH_GROWTH_SYSTEM_PROMPT = """
You are the Core Decisioning Engine for Google Search Growth (AI Overviews, AI Mode, and Google Discover).
Your objective is to eliminate 'Zero-Click' session dead-ends by analyzing an incoming user query and session context,
scoring its commercial and habitual retention propensity, and generating 3 high-conversion Next-Best-Action (NBA) chips.

STRICT GUARDRAILS & ROUTING RULES:
1. ZERO HALLUCINATION: Never invent specific product prices, unverified medical/financial claims, or non-existent model numbers in chip labels.
2. COMMERCIAL FAN-OUT (Closing the AI Mode Monetization Gap): If a query is informational but has latent purchase or B2B/B2C decision intent (e.g., travel, electronics, financial tools, home infrastructure), generate at least one chip that bridges the user into a concrete comparison or Shopping Graph evaluation.
3. DISCOVER HABIT LOOP: Always include one chip that frames an ongoing interest topic suitable for a 1-tap Google Discover subscription (target_surface = "GOOGLE_DISCOVER").
4. CIRCUIT BREAKER: If grounding_confidence < 0.95, set fallback_to_lexical_cache = True and recommended_experiment_bucket = "C0_FALLBACK".
"""

# =====================================================================
# 3. ENGINE EXECUTION & REAL-TIME TELEMETRY WRAPPER
# =====================================================================

def evaluate_search_session(query: str, user_context: dict) -> dict:
    # Safely pull from your terminal environment variables
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY environment variable. Run 'export GEMINI_API_KEY=\"your-key\"' in your terminal.")

    client = genai.Client(api_key=api_key)

    prompt_payload = f"""
    USER QUERY: "{query}"
    SESSION TELEMETRY CONTEXT: {json.dumps(user_context)}
    """
# Ensure time is imported at the top of your file (import time)
    start_time = time.time()

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt_payload,
        config=types.GenerateContentConfig(
            system_instruction=SEARCH_GROWTH_SYSTEM_PROMPT,
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=SearchGrowthPropensityDecision,
        ),
    )

    latency_ms = round((time.time() - start_time) * 1000, 2)
    decision_data = json.loads(response.text)

    telemetry_event = {
        "event_type": "SEARCH_GROWTH_NBA_DECISION",
        "latency_ms": latency_ms,
        "sla_compliant": latency_ms < 1500,
        "decision_payload": decision_data
    }
    return telemetry_event

if __name__ == "__main__":
    sample_queries = [
        {
            "query": "best commuter road bike for hilly terrain and rain",
            "context": {"surface": "iOS_Google_App", "prior_queries_in_session": 1, "geo": "US-NY"}
        },
        {
            "query": "how does international flight upgrade priority work on partner airlines",
            "context": {"surface": "Chrome_Mobile", "prior_queries_in_session": 2, "geo": "US-NY"}
        }
    ]

    print("Running Google Search Growth Propensity & Query Fan-Out Engine...\n")
    for item in sample_queries:
        result = evaluate_search_session(item["query"], item["context"])
        print(json.dumps(result, indent=2))
        print("-" * 80)