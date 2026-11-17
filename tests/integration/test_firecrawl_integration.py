import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from bioinformatics.annotation.firecrawl_client import firecrawl_client

client = TestClient(app)

def test_firecrawl_configuration():
    assert firecrawl_client.is_configured() is True

def test_firecrawl_scrape_and_evidence_boundary():
    # Test scrape on standard reference URL
    url = "https://example.com"
    citation = firecrawl_client.scrape_citation(url)

    assert citation["url"] == url
    assert "Example Domain" in citation["title"]
    # Strict biological governance constraint: AI/web research must be tagged as hypothesis
    assert citation["evidence_type"] == "ai_suggested_hypothesis"
    assert citation["citation_status"] == "unverified_hypothesis"
    assert "retrieved_at" in citation

def test_firecrawl_api_endpoint():
    headers = {"X-Tenant-ID": "ssit-tumakuru"}
    req = {"url": "https://example.com"}
    res = client.post("/api/v1/research/scrape", json=req, headers=headers)

    assert res.status_code == 200
    data = res.json()
    assert data["url"] == "https://example.com"
    assert data["evidence_type"] == "ai_suggested_hypothesis"
