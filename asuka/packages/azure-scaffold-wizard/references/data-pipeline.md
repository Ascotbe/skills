# Data Pipeline — Scaffold Pattern

This reference file defines the scaffold pattern for **ETL/ELT data processing pipelines** deployed on Azure.

---

## Type-Specific Questions

| # | Question | Guidance |
|---|---|---|
| D1 | **Processing mode?** | `batch` (default), `streaming`, `hybrid`. Drives pipeline architecture. |
| D2 | **Data sources?** | List each source: type (database, API, file system, event stream), format (CSV, JSON, Parquet, Avro), location. |
| D3 | **Data sinks/destinations?** | List each sink: Azure Data Lake, Cosmos DB, SQL Database, Blob Storage, Synapse. |
| D4 | **Transformation engine?** | `Python/Pandas` (default for small data), `PySpark` (large data), `Azure Data Factory` (low-code), `dbt` (SQL transforms). |
| D5 | **Scheduling?** | `Timer/cron` (default), `Event-triggered`, `Manual`, `Azure Data Factory triggers`. |
| D6 | **Data volume per run?** | Small (<1GB), Medium (1-100GB), Large (>100GB). Drives compute sizing and parallelism. |
| D7 | **Data quality checks?** | `Basic` (null checks, type validation), `Advanced` (schema evolution, anomaly detection), `None`. |
| D8 | **Orchestration tool?** | `Python scripts` (default), `Azure Data Factory`, `Apache Airflow`, `Prefect`. |
| D9 | **Include AI-powered data enrichment?** | `No` (default). If `Yes`: AI classifies, extracts entities, scores quality, or summarizes data records during transformation. Triggers U11 question. |
| D10 | **What AI enrichment?** | Only ask if D9=Yes. Options: `Classification` (categorize records), `Entity extraction` (pull structured data from text), `Quality scoring` (assess data quality), `Summarization` (condense text fields). Drives enrichment agent skill. |

---

## Project Folder Structure

```
<project-slug>/
├── src/
│   ├── __init__.py
│   ├── config.py                   # Pipeline configuration
│   ├── pipeline.py                 # Main pipeline orchestrator
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract extractor interface
│   │   └── <source>.py             # One extractor per data source (from D2)
│   ├── transformers/
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract transformer interface
│   │   ├── cleaners.py             # Data cleaning transformations
│   │   ├── enrichers.py            # Data enrichment transformations
│   │   └── validators.py           # Data quality checks (from D7)
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract loader interface
│   │   └── <sink>.py               # One loader per destination (from D3)
│   └── utils/
│       ├── __init__.py
│       ├── logging.py              # Structured logging
│       └── metrics.py              # Pipeline metrics collection
│
├── pipelines/                      # Pipeline definitions
│   ├── <pipeline-name>.yaml        # Pipeline config: sources, transforms, sinks
│   └── schedules.yaml              # Scheduling configuration (from D5)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_extractors.py
│   ├── test_transformers.py
│   └── test_loaders.py
│
└── data/
    ├── sample/                     # Sample input data for testing
    └── schemas/                    # JSON Schema or Avro schema definitions
```

---

## Source File Patterns

### Pipeline Orchestrator

```python
# src/pipeline.py
import logging
from dataclasses import dataclass
from .config import PipelineConfig
from .extractors.base import Extractor
from .transformers.base import Transformer
from .loaders.base import Loader

logger = logging.getLogger(__name__)

@dataclass
class PipelineResult:
    records_extracted: int
    records_transformed: int
    records_loaded: int
    errors: list[str]

async def run_pipeline(config: PipelineConfig) -> PipelineResult:
    """Execute the ETL pipeline: extract → transform → load."""
    errors = []

    # Extract
    logger.info(f"Extracting from {config.source_name}")
    extractor = Extractor.create(config.source_type, config.source_config)
    raw_data = await extractor.extract()
    logger.info(f"Extracted {len(raw_data)} records")

    # Transform
    logger.info("Running transformations")
    transformer = Transformer.create(config.transform_steps)
    transformed_data, transform_errors = await transformer.transform(raw_data)
    errors.extend(transform_errors)
    logger.info(f"Transformed {len(transformed_data)} records ({len(transform_errors)} errors)")

    # Validate (if D7 != None)
    if config.validation_enabled:
        from .transformers.validators import validate
        validated_data, validation_errors = validate(transformed_data, config.schema)
        errors.extend(validation_errors)
        transformed_data = validated_data

    # Load
    logger.info(f"Loading to {config.sink_name}")
    loader = Loader.create(config.sink_type, config.sink_config)
    loaded_count = await loader.load(transformed_data)
    logger.info(f"Loaded {loaded_count} records")

    return PipelineResult(
        records_extracted=len(raw_data),
        records_transformed=len(transformed_data),
        records_loaded=loaded_count,
        errors=errors,
    )
```

### Extractor Base

```python
# src/extractors/base.py
from abc import ABC, abstractmethod
from typing import Any

class Extractor(ABC):
    @abstractmethod
    async def extract(self) -> list[dict[str, Any]]:
        """Extract data from source. Returns list of records."""
        ...

    @staticmethod
    def create(source_type: str, config: dict) -> "Extractor":
        """Factory: create extractor by type."""
        extractors = {
            "blob_storage": "BlobStorageExtractor",
            "cosmos_db": "CosmosDBExtractor",
            "rest_api": "RestAPIExtractor",
            "csv_file": "CSVExtractor",
        }
        # Dynamic import and instantiation
        ...
```

---

## AI Enrichment Layer (D9 = Yes, U11 = Yes)

When the pipeline includes AI-powered data enrichment via Foundry Agent Service, add these files. Read `references/foundry-agent-patterns.md` for the shared patterns.

### Additional Folder Structure

```
<project-slug>/
├── agents/
│   └── enrichment-agent/
│       ├── agent.yaml
│       ├── Dockerfile
│       ├── main.py
│       ├── requirements.txt
│       ├── schemas.py
│       └── skills/
│           └── enrichment-skill/
│               └── skill.md
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── hosted_agents.py            # Two-mode dispatcher
│   └── transformers/
│       └── ai_enricher.py              # AI enrichment transformer
├── scripts/
│   └── register_agents.py
```

### AI Enrichment Transformer

```python
# src/transformers/ai_enricher.py
"""AI-powered data enrichment transformer — calls Foundry agent for batch processing."""
from ..agents.hosted_agents import dispatch


class AIEnricher:
    """Transformer that enriches records using a Foundry agent."""

    def __init__(self, agent_name: str = "enrichment-agent", batch_size: int = 10):
        self.agent_name = agent_name
        self.batch_size = batch_size

    async def transform(self, records: list[dict]) -> tuple[list[dict], list[str]]:
        """Enrich records by sending batches to the Foundry agent."""
        enriched = []
        errors = []
        for i in range(0, len(records), self.batch_size):
            batch = records[i:i + self.batch_size]
            try:
                result = await dispatch(self.agent_name, {"records": batch})
                enriched.extend(result.get("enriched_records", batch))
            except Exception as e:
                errors.append(f"Batch {i}: {e}")
                enriched.extend(batch)  # Pass through on failure
        return enriched, errors
```

### Enrichment Agent Schema

```python
# agents/enrichment-agent/schemas.py
from pydantic import BaseModel, Field
from typing import Literal


class EnrichmentResult(BaseModel):
    """Structured output for the enrichment agent."""

    enriched_records: list[dict] = Field(description="Records with AI-added fields")
    summary: str = Field(description="Summary of enrichment results")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Overall enrichment quality 0-1")
    confidence_level: Literal["HIGH", "MEDIUM", "LOW"]
    records_processed: int = Field(description="Number of records processed")
    records_enriched: int = Field(description="Number of records successfully enriched")
    errors: list[str] = Field(default_factory=list, description="Per-record processing errors")
```

### Integration into Pipeline

Add the AI enrichment step between transform and validate in `src/pipeline.py`:

```python
# In run_pipeline(), after transform step:
if config.ai_enrichment_enabled:
    from .transformers.ai_enricher import AIEnricher
    enricher = AIEnricher(agent_name="enrichment-agent", batch_size=config.ai_batch_size)
    transformed_data, enrichment_errors = await enricher.transform(transformed_data)
    errors.extend(enrichment_errors)
    logger.info(f"AI enrichment complete ({len(enrichment_errors)} errors)")
```

### AI Mode — Hand-Rolled (D9 = Yes, U11 = No)

If the user declines Foundry, use direct Azure OpenAI SDK:

```python
# src/transformers/ai_enricher.py (hand-rolled version)
import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


class AIEnricher:
    def __init__(self):
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default",
        )
        self.client = AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_ad_token_provider=token_provider,
            api_version="2024-10-21",
        )

    async def transform(self, records: list[dict]) -> tuple[list[dict], list[str]]:
        enriched, errors = [], []
        for record in records:
            try:
                response = self.client.chat.completions.create(
                    model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
                    messages=[
                        {"role": "system", "content": "Enrich this data record. Return JSON."},
                        {"role": "user", "content": str(record)},
                    ],
                    response_format={"type": "json_object"},
                )
                import json
                enriched.append({**record, **json.loads(response.choices[0].message.content)})
            except Exception as e:
                errors.append(str(e))
                enriched.append(record)
        return enriched, errors
```

---

## Bicep Modules Required

- `monitoring.bicep` (always)
- `storage.bicep` — for Data Lake / Blob Storage (almost always needed)
- `container-apps-env.bicep` + `container-app.bicep` — if running as containerized jobs
- `cosmos.bicep` — if D3 includes Cosmos DB

If D8 = Azure Data Factory:
- `data-factory.bicep` module (additional)

If D4 = PySpark:
- `databricks.bicep` or `synapse.bicep` module (additional)

**If D9 = Yes and U11 = Yes (Foundry AI mode):**
- `ai-foundry.bicep` — Foundry account + project + model deployment
- Additional `container-app.bicep` instance for enrichment agent
- RBAC: `Cognitive Services OpenAI User` + `Azure AI User` on Foundry account

**If D9 = Yes and U11 = No (Hand-rolled AI mode):**
- `ai-foundry.bicep` — Azure OpenAI model deployment only

---

## Type-Specific Quality Checklist

- [ ] All extractors handle connection failures with retries
- [ ] All loaders implement idempotent upserts (no duplicate data on re-run)
- [ ] Data quality validators match D7 answer
- [ ] Pipeline configuration is externalized (YAML or env vars, not hardcoded)
- [ ] Scheduling matches D5 answer
- [ ] Error handling captures and logs all failed records without stopping pipeline
- [ ] Sample data in `data/sample/` exercises all code paths
- [ ] Pipeline metrics are collected and sent to Application Insights
- [ ] Schema definitions exist for all data formats
- [ ] Tests mock external data sources and sinks

**If D9 = Yes and U11 = Yes (Foundry AI mode) — also verify:**
- [ ] AI enricher is integrated into pipeline between transform and validate steps
- [ ] Enrichment handles batch failures gracefully (pass-through on error)
- [ ] Enrichment agent skill matches D10 answer
- [ ] Run Foundry quality checklist from `references/foundry-agent-patterns.md`
