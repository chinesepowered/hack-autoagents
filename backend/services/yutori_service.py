import json
import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)


async def fact_check_claims(claims: list[dict]) -> list[dict]:
    """Use Yutori Research API to fact-check claims from the earnings call.

    Takes extracted claims/entities and researches them against public data.
    """
    if not settings.yutori_api_key:
        logger.warning("YUTORI_API_KEY not set, using mock data")
        return _mock_fact_checks()

    results = []
    async with httpx.AsyncClient(timeout=120) as client:
        for claim in claims:
            try:
                response = await client.post(
                    "https://api.yutori.com/v1/research",
                    headers={
                        "Authorization": f"Bearer {settings.yutori_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "query": f"Verify this financial claim: {claim.get('text', claim.get('name', ''))}",
                        "instructions": (
                            "Research this claim from a corporate earnings call. "
                            "Check SEC filings, financial news, and public data. "
                            "Determine if the claim is accurate, needs context, or is misleading. "
                            "Provide specific evidence and sources."
                        ),
                    },
                )
                response.raise_for_status()
                data = response.json()

                results.append({
                    "claim": claim.get("text", claim.get("name", "")),
                    "verdict": _extract_verdict(data.get("result", "")),
                    "evidence": data.get("result", ""),
                    "sources": json.dumps(data.get("sources", [])),
                })

            except Exception as e:
                logger.error(f"Yutori fact-check failed for claim: {e}")
                results.append({
                    "claim": claim.get("text", claim.get("name", "")),
                    "verdict": "error",
                    "evidence": f"Fact-check failed: {e}",
                    "sources": "[]",
                })

    return results


async def research_entity(entity_name: str) -> dict:
    """Use Yutori Research API to enrich an entity with current data."""
    if not settings.yutori_api_key:
        return {"entity": entity_name, "data": "Mock enrichment data"}

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.yutori.com/v1/research",
                headers={
                    "Authorization": f"Bearer {settings.yutori_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "query": f"Current information about {entity_name}: stock price, recent news, market position",
                },
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        logger.error(f"Yutori entity research failed: {e}")
        return {"entity": entity_name, "error": str(e)}


def _extract_verdict(evidence: str) -> str:
    evidence_lower = evidence.lower()
    if any(w in evidence_lower for w in ["confirmed", "accurate", "verified", "correct"]):
        return "verified"
    if any(w in evidence_lower for w in ["false", "incorrect", "misleading", "disputed"]):
        return "disputed"
    if any(w in evidence_lower for w in ["context", "partially", "nuanced"]):
        return "context_needed"
    return "unverified"


def _mock_fact_checks() -> list[dict]:
    """Return mock fact-check data for development."""
    return [
        {
            "claim": "Total revenue reached $110.2 billion, up 23% year over year",
            "verdict": "verified",
            "evidence": "SEC filing 10-Q confirms Q4 2024 revenue of $110.2B vs $89.5B in Q4 2023, representing 23.1% YoY growth. Verified against Apple's official investor relations page.",
            "sources": json.dumps([
                "https://investor.apple.com/sec-filings/",
                "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=apple",
            ]),
        },
        {
            "claim": "Over 1 billion paid subscriptions across the platform",
            "verdict": "verified",
            "evidence": "Apple reported crossing 1 billion paid subscriptions in Q3 2024. This figure includes Apple Music, iCloud, Apple TV+, Apple Arcade, and third-party app subscriptions.",
            "sources": json.dumps([
                "https://www.apple.com/newsroom/",
            ]),
        },
        {
            "claim": "Gross margins at 46.2%, slightly below expectations",
            "verdict": "context_needed",
            "evidence": "Gross margin of 46.2% is confirmed, but analyst consensus was 46.5%. While 'slightly below' is accurate, the 30bps miss is within normal variance. Previous quarter was 46.6%.",
            "sources": json.dumps([
                "https://finance.yahoo.com/quote/AAPL/",
            ]),
        },
        {
            "claim": "Product pipeline has never been stronger",
            "verdict": "unverified",
            "evidence": "This is a subjective forward-looking statement. Apple has announced Vision Pro 2, M4 chip lineup, and AI features. However, 'never been stronger' is not objectively verifiable — it's a qualitative management assessment.",
            "sources": json.dumps([]),
        },
        {
            "claim": "We expect margin improvement in Q1",
            "verdict": "context_needed",
            "evidence": "Forward-looking guidance statement. Historical data shows Q1 typically has higher margins due to holiday mix. Component cost trends from suppliers suggest potential 50-80bps improvement, but macroeconomic factors could offset gains.",
            "sources": json.dumps([
                "https://finance.yahoo.com/quote/AAPL/",
            ]),
        },
    ]
