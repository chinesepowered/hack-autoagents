import logging
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)

PIONEER_API_URL = "https://api.pioneer.ai/gliner-2"

FINANCIAL_ENTITY_TYPES = [
    "person",
    "company",
    "financial_metric",
    "product",
    "date",
    "percentage",
    "currency_amount",
    "forward_looking_statement",
    "risk_factor",
    "market_segment",
]


async def _call_pioneer_api(
    text: str, schema: list[str], threshold: float = 0.5
) -> Optional[list[dict]]:
    """Call Pioneer GLiNER2 API for entity extraction."""
    if not settings.fastino_api_key:
        logger.warning("FASTINO_API_KEY not set, using mock data")
        return None

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                PIONEER_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": settings.fastino_api_key,
                },
                json={
                    "task": "extract_entities",
                    "text": text,
                    "schema": schema,
                    "threshold": threshold,
                },
            )
            response.raise_for_status()
            data = response.json()

            entities = []
            result = data.get("result", {})
            entity_dict = result.get("entities", {})

            for entity_type, entity_list in entity_dict.items():
                for entity in entity_list:
                    if isinstance(entity, dict):
                        entities.append(
                            {
                                "name": entity.get("text", ""),
                                "entity_type": entity_type,
                                "context": "",
                                "confidence": entity.get(
                                    "score", entity.get("confidence", 0.0)
                                ),
                            }
                        )
                    else:
                        entities.append(
                            {
                                "name": str(entity),
                                "entity_type": entity_type,
                                "context": "",
                                "confidence": 0.9,
                            }
                        )

            return entities

    except httpx.HTTPStatusError as e:
        logger.error(
            f"Pioneer API HTTP error: {e.response.status_code} - {e.response.text}"
        )
        return None
    except Exception as e:
        logger.error(f"Pioneer API call failed: {e}")
        return None


async def extract_entities(text: str) -> list[dict]:
    """Extract named entities from text using Pioneer GLiNER2 API."""
    schema = ["person", "company", "product", "date", "percentage", "currency_amount"]

    entities = await _call_pioneer_api(text, schema)
    if entities is None:
        return _mock_entity_extraction()

    return entities if entities else _mock_entity_extraction()


async def classify_statements(text: str) -> list[dict]:
    """Classify statements in the transcript using Pioneer GLiNER2 API."""
    schema = [
        "forward_looking_statement",
        "risk_disclosure",
        "commitment",
        "performance_metric",
        "guidance_update",
    ]

    results = await _call_pioneer_api(text, schema)
    if results is None:
        return _mock_statement_classification()

    classifications = []
    for item in results:
        classifications.append(
            {
                "text": item.get("name", ""),
                "classification": item.get("entity_type", ""),
                "confidence": item.get("confidence", 0.0),
            }
        )

    return classifications if classifications else _mock_statement_classification()


def _mock_entity_extraction() -> list[dict]:
    """Return mock entity data for development."""
    return [
        {
            "name": "Tim Cook",
            "entity_type": "person",
            "context": "CEO presenting quarterly results",
            "confidence": 0.97,
        },
        {
            "name": "Luca Maestri",
            "entity_type": "person",
            "context": "CFO discussing financials",
            "confidence": 0.95,
        },
        {
            "name": "Apple Inc.",
            "entity_type": "company",
            "context": "Parent company reporting earnings",
            "confidence": 0.99,
        },
        {
            "name": "$110.2 billion",
            "entity_type": "currency_amount",
            "context": "Total quarterly revenue",
            "confidence": 0.96,
        },
        {
            "name": "23%",
            "entity_type": "percentage",
            "context": "Year-over-year revenue growth",
            "confidence": 0.94,
        },
        {
            "name": "iPhone",
            "entity_type": "product",
            "context": "Flagship product line",
            "confidence": 0.98,
        },
        {
            "name": "Services",
            "entity_type": "market_segment",
            "context": "Fastest growing business segment",
            "confidence": 0.93,
        },
        {
            "name": "Q4 2024",
            "entity_type": "date",
            "context": "Reporting period",
            "confidence": 0.99,
        },
        {
            "name": "1 billion paid subscriptions",
            "entity_type": "financial_metric",
            "context": "Services ecosystem scale metric",
            "confidence": 0.91,
        },
        {
            "name": "46.2%",
            "entity_type": "percentage",
            "context": "Gross margin for the quarter",
            "confidence": 0.95,
        },
        {
            "name": "We expect improvement in Q1",
            "entity_type": "forward_looking_statement",
            "context": "CFO guidance on margin trajectory",
            "confidence": 0.87,
        },
        {
            "name": "Component cost headwinds",
            "entity_type": "risk_factor",
            "context": "Pressure on hardware margins",
            "confidence": 0.82,
        },
    ]


def _mock_statement_classification() -> list[dict]:
    return [
        {
            "text": "We expect margin improvement in Q1 as component costs normalize",
            "classification": "forward_looking_statement",
            "confidence": 0.91,
        },
        {
            "text": "Our product pipeline has never been stronger",
            "classification": "forward_looking_statement",
            "confidence": 0.85,
        },
        {
            "text": "Component cost pressures may persist through H1",
            "classification": "risk_disclosure",
            "confidence": 0.88,
        },
        {
            "text": "Total revenue reached $110.2 billion, up 23% YoY",
            "classification": "performance_metric",
            "confidence": 0.96,
        },
        {
            "text": "We now have over 1 billion paid subscriptions",
            "classification": "performance_metric",
            "confidence": 0.94,
        },
    ]
