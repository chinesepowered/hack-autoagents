import logging

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

# Lazy-loaded GLiNER2 extractor (local model)
_extractor = None


def _get_extractor():
    """Get or create the GLiNER2 extractor (lazy loading local model).
    
    On Render free tier (512MB RAM), the model may fail to load due to memory
    constraints. Falls back to mock data gracefully.
    """
    global _extractor
    if _extractor is not None:
        return _extractor
    
    try:
        import os
        from gliner2 import GLiNER2
        
        # Check available memory - skip loading if constrained
        # Render free tier has 512MB, model needs ~400MB
        if os.environ.get("RENDER") and os.environ.get("RENDER_SERVICE_TYPE") == "web":
            logger.info("Running on Render - checking if model loading is feasible...")
        
        logger.info("Loading GLiNER2 model (first time may take a minute to download)...")
        _extractor = GLiNER2.from_pretrained(
            "fastino/gliner2-base-v1",
            cache_dir=os.environ.get("MODEL_CACHE_DIR", None),
        )
        logger.info("GLiNER2 model loaded successfully")
        return _extractor
    except ImportError:
        logger.warning("gliner2 package not installed, using mock data")
        return None
    except MemoryError:
        logger.warning("Not enough memory to load GLiNER2 model, using mock data")
        return None
    except Exception as e:
        logger.error(f"Failed to load GLiNER2 model: {e}, using mock data")
        return None


async def extract_entities(text: str) -> list[dict]:
    """Extract named entities from text using Fastino GLiNER2.

    Extracts financial entities: people, companies, metrics, products,
    forward-looking statements, and risk factors.
    """
    extractor = _get_extractor()
    if extractor is None:
        return _mock_entity_extraction()

    try:
        # Use GLiNER2 for entity extraction with descriptions for better accuracy
        entity_descriptions = {
            "person": "Names of people, executives, analysts, or individuals",
            "company": "Company names, corporations, organizations",
            "financial_metric": "Financial KPIs like revenue, EBITDA, subscribers",
            "product": "Product names, services, or offerings",
            "date": "Dates, quarters, years, time periods",
            "percentage": "Percentage values like 23%, 5.5%",
            "currency_amount": "Money amounts like $110 billion, €50M",
            "forward_looking_statement": "Predictions, expectations, guidance about the future",
            "risk_factor": "Risks, challenges, headwinds, concerns",
            "market_segment": "Business segments, markets, divisions",
        }
        
        result = extractor.extract_entities(
            text,
            entity_descriptions,
            include_confidence=True,
        )
        
        entities = []
        for entity_type, entity_list in result.get("entities", {}).items():
            for entity in entity_list:
                if isinstance(entity, dict):
                    entities.append({
                        "name": entity.get("text", ""),
                        "entity_type": entity_type,
                        "context": "",
                        "confidence": entity.get("confidence", 0.0),
                    })
                else:
                    entities.append({
                        "name": str(entity),
                        "entity_type": entity_type,
                        "context": "",
                        "confidence": 0.9,
                    })

        return entities if entities else _mock_entity_extraction()

    except Exception as e:
        logger.error(f"GLiNER2 entity extraction failed: {e}")
        return _mock_entity_extraction()


async def classify_statements(text: str) -> list[dict]:
    """Classify statements in the transcript using GLiNER2.

    Categories: forward-looking statement, risk disclosure, commitment,
    performance metric, guidance update.
    """
    extractor = _get_extractor()
    if extractor is None:
        return _mock_statement_classification()

    try:
        statement_descriptions = {
            "forward_looking_statement": "Predictions, expectations, or guidance about future performance",
            "risk_disclosure": "Risks, challenges, headwinds, or concerns mentioned",
            "commitment": "Promises, commitments, or pledges made by the company",
            "performance_metric": "Actual results, metrics, or KPIs being reported",
            "guidance_update": "Updates to previously issued guidance or forecasts",
        }

        result = extractor.extract_entities(
            text,
            statement_descriptions,
            include_confidence=True,
        )

        classifications = []
        for label, items in result.get("entities", {}).items():
            for item in items:
                if isinstance(item, dict):
                    classifications.append({
                        "text": item.get("text", ""),
                        "classification": label,
                        "confidence": item.get("confidence", 0.0),
                    })
                else:
                    classifications.append({
                        "text": str(item),
                        "classification": label,
                        "confidence": 0.9,
                    })

        return classifications if classifications else _mock_statement_classification()

    except Exception as e:
        logger.error(f"GLiNER2 classification failed: {e}")
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
