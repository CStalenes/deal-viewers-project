# Deal Viewers Project

A FastAPI + MongoDB application that manages commercial deals and uses **display templates** to control which fields are visible to different users or teams.

## Concept: Why two collections?

### The `deals` collection

A deal is a rich business object representing a commercial opportunity. It contains **30+ fields** organized into nested groups:

```json
{
  "title": "Déploiement CRM Europe 2026",
  "clientName": "ACME Corporation",
  "status": "NEGOTIATION",
  "estimatedRevenue": 120000,
  "financials": {
    "totalExclTax": 99750,
    "totalInclTax": 119700,
    "expectedProfit": 34750
  },
  "commercial": {
    "competitors": ["Salesforce", "HubSpot"],
    "nextStep": "Validation juridique"
  },
  "delivery": { ... },
  "governance": { ... }
}
```

Every deal stores **all** the data. But not every user needs to see everything.

### The `templates` collection

A template is a **display adapter**. It does not hold business data — it defines **how to view** a deal.

```json
{
  "name": "Finance View",
  "code": "FINANCE_VIEW",
  "visibleFields": ["title", "clientName", "financials.totalExclTax", "financials.expectedProfit"]
}
```

The key idea: **the deal data never changes, only the lens through which it is displayed changes.**

This is similar to how a SQL `SELECT` chooses columns, but applied dynamically at runtime through a configuration object. Different teams get different views of the same deal:

| Template | Visible fields |
|---|---|
| Finance View | `title`, `clientName`, `financials.totalExclTax`, `financials.expectedProfit` |
| Commercial View | `title`, `clientName`, `commercial.competitors`, `commercial.nextStep` |
| Delivery View | `title`, `delivery.deliveryMode`, `delivery.estimatedDeliveryWeeks` |

One deal, multiple perspectives — without duplicating data.

## API Routes

### Deals

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/deals/` | Create a new deal |
| `GET` | `/deals/` | List all deals (with optional filters) |
| `GET` | `/deals/{id}` | Get a single deal by ID |
| `PUT` | `/deals/{id}` | Update a deal |
| `DELETE` | `/deals/{id}` | Delete a deal |
| `GET` | `/deals/{deal_id}/view?templateId=` | **View a deal through a template (projection)** |

### Templates

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/templates/` | Create a new display template |
| `GET` | `/templates/` | List all templates |
| `GET` | `/templates/{id}` | Get a single template by ID |

## How projection works

The projection endpoint `GET /deals/{deal_id}/view?templateId={template_id}` combines a deal with a template to return only the fields listed in the template's `visibleFields`.

### Step-by-step example

**1. A deal exists in the database:**

```json
{
  "_id": "deal_001",
  "title": "Déploiement CRM Europe 2026",
  "clientName": "ACME Corporation",
  "status": "NEGOTIATION",
  "estimatedRevenue": 120000,
  "currency": "EUR",
  "financials": {
    "totalExclTax": 99750,
    "totalInclTax": 119700,
    "expectedProfit": 34750
  },
  "commercial": {
    "competitors": ["Salesforce", "HubSpot"]
  }
}
```

**2. A "Finance View" template is created:**

```json
{
  "_id": "tmpl_finance_001",
  "name": "Finance View",
  "code": "FINANCE_VIEW",
  "visibleFields": ["title", "clientName", "financials.totalExclTax", "financials.expectedProfit"]
}
```

**3. Call the projection endpoint:**

```
GET /deals/deal_001/view?templateId=tmpl_finance_001
```

**4. Result — only the template's fields are returned:**

```json
{
  "title": "Déploiement CRM Europe 2026",
  "clientName": "ACME Corporation",
  "financials.totalExclTax": 99750,
  "financials.expectedProfit": 34750
}
```

The fields `status`, `estimatedRevenue`, `currency`, `commercial`, and everything else are **excluded**. The template acts as a filter that controls what is visible.

Nested fields use dot notation (`financials.totalExclTax`): the projection function traverses the deal object by splitting on `.` and extracting the nested value.

## Filters: client name and date range

The `GET /deals/` endpoint supports query parameters for filtering.

### Filter by client name (`$regex`)

```
GET /deals?clientName=ACME
```

Uses MongoDB's `$regex` operator with case-insensitive matching (`$options: "i"`):

```python
{"clientName": {"$regex": "ACME", "$options": "i"}}
```

This matches `"ACME Corporation"`, `"acme industries"`, `"Acme Ltd"` — any deal whose `clientName` contains the search term, regardless of case.

### Filter by date range

```
GET /deals?startDate=2026-03-01&endDate=2026-03-31
```

Filters deals by their `createdAt` field using MongoDB's `$gte` (greater than or equal) and `$lte` (less than or equal) operators:

```python
{"createdAt": {"$gte": "2026-03-01", "$lte": "2026-03-31"}}
```

### Combined filters

All filters can be combined:

```
GET /deals?clientName=ACME&startDate=2026-03-01&endDate=2026-03-31
```

Returns only ACME deals created in March 2026.

## Tech Stack

- **FastAPI** — Python web framework
- **MongoDB** — NoSQL database (via PyMongo)
- **Pydantic v2** — Data validation for template schema

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Set up .env file
MONGO_URI=mongodb+srv://...
DB_NAME=deal-viewer

# Run the server
cd deal-viewers-project
python -m uvicorn backend.main:app --reload --reload-dir backend
```

API documentation is available at `http://127.0.0.1:8000/docs` (Swagger UI).
