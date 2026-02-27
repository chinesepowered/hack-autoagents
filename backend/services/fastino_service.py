import json
import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)

# Entity types for financial earnings call analysis
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


async def extract_entities(text: str) -> list[dict]:
    """Extract named entities from text using Fastino GLiNER2 API.

    Extracts financial entities: people, companies, metrics, products,
    forward-looking statements, and risk factors.
    """
    if not settings.fastino_api_key:
        logger.warning("FASTINO_API_KEY not set, using mock data")
        return _mock_entity_extraction()

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.fastino.ai/v1/gliner-2",
                headers={
                    "Authorization": f"Bearer {settings.fastino_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "text": text,
                    "labels": FINANCIAL_ENTITY_TYPES,
                    "threshold": 0.3,
                },
            )
            response.raise_for_status()
            data = response.json()

            entities = []
            for entity in data.get("entities", []):
                entities.append({
                    "name": entity.get("text", ""),
                    "entity_type": entity.get("label", "unknown"),
                    "context": entity.get("context", ""),
                    "confidence": entity.get("score", 0.0),
                })

            return entities

    except Exception as e:
        logger.error(f"Fastino entity extraction failed: {e}")
        return _mock_entity_extraction()


async def classify_statements(text: str) -> list[dict]:
    """Classify statements in the transcript using GLiNER2.

    Categories: forward-looking statement, risk disclosure, commitment,
    performance metric, guidance update.
    """
    if not settings.fastino_api_key:
        return _mock_statement_classification()

    try:
        statement_types = [
            "forward_looking_statement",
            "risk_disclosure",
            "commitment",
            "performance_metric",
            "guidance_update",
        ]

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.fastino.ai/v1/gliner-2",
                headers={
                    "Authorization": f"Bearer {settings.fastino_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "text": text,
                    "labels": statement_types,
                    "threshold": 0.4,
                },
            )
            response.raise_for_status()
            data = response.json()

            return [
                {
                    "text": e.get("text", ""),
                    "classification": e.get("label", ""),
                    "confidence": e.get("score", 0.0),
                }
                for e in data.get("entities", [])
            ]

    except Exception as e:
        logger.error(f"Fastino classification failed: {e}")
        return _mock_statement_classification()


def _mock_entity_extraction() -> list[dict]:
    """Return mock entity data for development."""
    return [
        {"name": "Tim Cook", "entity_type": "person", "context": "CEO presenting quarterly results", "confidence": 0.97},
        {"name": "Luca Maestri", "entity_type": "person", "context": "CFO discussing financials", "confidence": 0.95},
        {"name": "Apple Inc.", "entity_type": "company", "context": "Parent company reporting earnings", "confidence": 0.99},
        {"name": "$110.2 billion", "entity_type": "currency_amount", "context": "Total quarterly revenue", "confidence": 0.96},
        {"name": "23%", "entity_type": "percentage", "context": "Year-over-year revenue growth", "confidence": 0.94},
        {"name": "iPhone", "entity_type": "product", "context": "Flagship product line", "confidence": 0.98},
        {"name": "Services", "entity_type": "market_segment", "context": "Fastest growing business segment", "confidence": 0.93},
        {"name": "Q4 2024", "entity_type": "date", "context": "Reporting period", "confidence": 0.99},
        {"name": "1 billion paid subscriptions", "entity_type": "financial_metric", "context": "Services ecosystem scale metric", "confidence": 0.91},
        {"name": "46.2%", "entity_type": "percentage", "context": "Gross margin for the quarter", "confidence": 0.95},
        {"name": "We expect improvement in Q1", "entity_type": "forward_looking_statement", "context": "CFO guidance on margin trajectory", "confidence": 0.87},
        {"name": "Component cost headwinds", "entity_type": "risk_factor", "context": "Pressure on hardware margins", "confidence": 0.82},
    ]


def _mock_statement_classification() -> list[dict]:
    return [
        {"text": "We expect margin improvement in Q1 as component costs normalize", "classification": "forward_looking_statement", "confidence": 0.91},
        {"text": "Our product pipeline has never been stronger", "classification": "forward_looking_statement", "confidence": 0.85},
        {"text": "Component cost pressures may persist through H1", "classification": "risk_disclosure", "confidence": 0.88},
        {"text": "Total revenue reached $110.2 billion, up 23% YoY", "classification": "performance_metric", "confidence": 0.96},
        {"text": "We now have over 1 billion paid subscriptions", "classification": "performance_metric", "confidence": 0.94},
    ]
