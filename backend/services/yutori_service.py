import asyncio
import json
import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)

YUTORI_BASE_URL = "https://api.yutori.com"


async def fact_check_claims(claims: list[dict]) -> list[dict]:
    """Use Yutori Research API to fact-check claims from the earnings call.

    Takes extracted claims/entities and researches them against public data.
    """
    if not settings.yutori_api_key:
        logger.warning("YUTORI_API_KEY not set, using mock data")
        return _mock_fact_checks()

    results = []
    async with httpx.AsyncClient(timeout=180) as client:
        for claim in claims[:5]:  # Limit to 5 claims to avoid rate limits
            try:
                claim_text = claim.get("text", claim.get("name", ""))
                
                # Create research task
                response = await client.post(
                    f"{YUTORI_BASE_URL}/v1/research/tasks",
                    headers={
                        "X-API-KEY": settings.yutori_api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "query": f"Verify this financial claim from an earnings call: {claim_text}. Check SEC filings, financial news, and public data. Is it accurate, needs context, or misleading?",
                    },
                )
                response.raise_for_status()
                task_data = response.json()
                task_id = task_data.get("task_id")
                
                if not task_id:
                    raise ValueError("No task_id returned")
                
                # Poll for results (research tasks are async)
                result = await _poll_research_task(client, task_id)
                
                results.append({
                    "claim": claim_text,
                    "verdict": _extract_verdict(result.get("result", "")),
                    "evidence": result.get("result", "Research pending..."),
                    "sources": json.dumps(result.get("sources", [])),
                })

            except Exception as e:
                logger.error(f"Yutori fact-check failed for claim: {e}")
                results.append({
                    "claim": claim.get("text", claim.get("name", "")),
                    "verdict": "unverified",
                    "evidence": f"Research pending or failed: {e}",
                    "sources": "[]",
                })

    return results if results else _mock_fact_checks()


async def _poll_research_task(client: httpx.AsyncClient, task_id: str, max_attempts: int = 10) -> dict:
    """Poll for research task completion."""
    for attempt in range(max_attempts):
        try:
            response = await client.get(
                f"{YUTORI_BASE_URL}/v1/research/tasks/{task_id}",
                headers={"X-API-KEY": settings.yutori_api_key},
            )
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status", "")
            if status == "completed":
                return data
            elif status == "failed":
                return {"result": "Research failed", "sources": []}
            
            # Wait before polling again
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.warning(f"Poll attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(2)
    
    return {"result": "Research timed out", "sources": []}


async def research_entity(entity_name: str) -> dict:
    """Use Yutori Research API to enrich an entity with current data."""
    if not settings.yutori_api_key:
        return {"entity": entity_name, "data": "Mock enrichment data"}

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{YUTORI_BASE_URL}/v1/research/tasks",
                headers={
                    "X-API-KEY": settings.yutori_api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "query": f"Current information about {entity_name}: stock price, recent news, market position",
                },
            )
            response.raise_for_status()
            task_data = response.json()
            task_id = task_data.get("task_id")
            
            if task_id:
                return await _poll_research_task(client, task_id)
            return task_data

    except Exception as e:
        logger.error(f"Yutori entity research failed: {e}")
        return {"entity": entity_name, "error": str(e)}


def _extract_verdict(evidence: str) -> str:
    evidence_lower = evidence.lower()
    if any(w in evidence_lower for w in ["confirmed", "accurate", "verified", "correct", "true"]):
        return "verified"
    if any(w in evidence_lower for w in ["false", "incorrect", "misleading", "disputed", "inaccurate"]):
        return "disputed"
    if any(w in evidence_lower for w in ["context", "partially", "nuanced", "depends"]):
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
