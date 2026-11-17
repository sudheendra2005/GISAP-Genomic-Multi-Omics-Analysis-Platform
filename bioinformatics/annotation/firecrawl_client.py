import os
import re
import requests
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.core.config import settings

class FirecrawlResearchClient:
    """
    GISAP External Research Integration Client.
    Connects to Firecrawl API to extract scientific literature, citations, and documentation.
    Strict Governance: Outputs are strictly classified as 'ai_suggested_hypothesis' and
    never replace deterministic biological alignment (BLAST, DIAMOND, HMMER).
    """

    BASE_URL = "https://api.firecrawl.dev/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.FIRECRAWL_API_KEY
        if not self.api_key:
            self._available = False
        else:
            self._available = True

    def is_configured(self) -> bool:
        return self._available

    def scrape_citation(self, url: str) -> Dict[str, Any]:
        """
        Scrapes a scientific documentation or literature URL and extracts verified metadata.
        """
        if not self._available:
            raise RuntimeError("FIRECRAWL_API_KEY is not configured in the environment.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "formats": ["markdown"]
        }

        response = requests.post(
            f"{self.BASE_URL}/scrape",
            headers=headers,
            json=payload,
            timeout=15
        )

        if response.status_code != 200:
            raise RuntimeError(f"Firecrawl API returned {response.status_code}: {response.text[:200]}")

        res_json = response.json()
        data = res_json.get("data", {})
        metadata = data.get("metadata", {})
        markdown = data.get("markdown", "")

        # Extract DOI or PMID if present in text
        doi_match = re.search(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b", markdown)
        pmid_match = re.search(r"\bPMID:\s*(\d+)\b", markdown, re.IGNORECASE)

        return {
            "url": url,
            "title": metadata.get("title", "Untitled Document"),
            "doi": doi_match.group(1) if doi_match else None,
            "pmid": pmid_match.group(1) if pmid_match else None,
            "summary_snippet": markdown[:500] if markdown else "",
            "evidence_type": "ai_suggested_hypothesis",
            "citation_status": "unverified_hypothesis",
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }

    def search_literature(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Searches web literature and returns hypothesis citations with provenance.
        """
        if not self._available:
            raise RuntimeError("FIRECRAWL_API_KEY is not configured in the environment.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": query,
            "limit": limit
        }

        response = requests.post(
            f"{self.BASE_URL}/search",
            headers=headers,
            json=payload,
            timeout=15
        )

        if response.status_code != 200:
            raise RuntimeError(f"Firecrawl API returned {response.status_code}: {response.text[:200]}")

        res_json = response.json()
        raw_results = res_json.get("data", [])
        citations = []

        now = datetime.now(timezone.utc).isoformat()
        for item in raw_results[:limit]:
            url = item.get("url", "")
            title = item.get("title", "Untitled Reference")
            description = item.get("description", "")

            doi_match = re.search(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b", description)
            citations.append({
                "url": url,
                "title": title,
                "doi": doi_match.group(1) if doi_match else None,
                "description": description,
                "evidence_type": "ai_suggested_hypothesis",
                "retrieved_at": now
            })

        return citations

firecrawl_client = FirecrawlResearchClient()
