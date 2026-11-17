from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.api.deps import get_db, get_tenant_id, get_current_user, require_role
from backend.database.models import AuditLog
from bioinformatics.annotation.firecrawl_client import firecrawl_client
from backend.services import llm_service

router = APIRouter(prefix="/research", tags=["Research & Literature (Firecrawl)"])

class SearchRequest(BaseModel):
    query: str = Field(..., description="Scientific literature search query")
    limit: int = Field(default=5, ge=1, le=10)

class ScrapeRequest(BaseModel):
    url: str = Field(..., description="Target scientific documentation or paper URL")

class CitationResponse(BaseModel):
    url: str
    title: str
    doi: Optional[str] = None
    pmid: Optional[str] = None
    summary_snippet: Optional[str] = None
    description: Optional[str] = None
    evidence_type: str = "ai_suggested_hypothesis"
    retrieved_at: str

@router.post("/search", response_model=List[CitationResponse])
def search_literature(
    req: SearchRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_role(["admin", "bioinformatician", "analyst"])),
    db: Session = Depends(get_db)
):
    if not firecrawl_client.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firecrawl research client is not configured with an API key."
        )

    try:
        results = firecrawl_client.search_literature(req.query, limit=req.limit)

        # Audit log
        audit = AuditLog(
            tenant_id=tenant_id,
            user_id=current_user.get("sub"),
            action="SEARCH",
            resource_type="external_literature",
            resource_id=req.query[:64],
            details=f"Literature search: {req.query}"
        )
        db.add(audit)
        db.commit()

        return results
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Firecrawl search error: {str(exc)}")

@router.post("/scrape", response_model=CitationResponse)
def scrape_citation(
    req: ScrapeRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_role(["admin", "bioinformatician", "analyst"])),
    db: Session = Depends(get_db)
):
    if not firecrawl_client.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firecrawl research client is not configured with an API key."
        )

    try:
        citation = firecrawl_client.scrape_citation(req.url)

        audit = AuditLog(
            tenant_id=tenant_id,
            user_id=current_user.get("sub"),
            action="SCRAPE",
            resource_type="external_citation",
            resource_id=req.url[:64],
            details=f"Documentation scraped: {req.url}"
        )
        db.add(audit)
        db.commit()

        return citation
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Firecrawl scrape error: {str(exc)}")


# ---------------------------------------------------------------------------
# AI-Assisted Annotation endpoint (Gemini Free Tier)
# ---------------------------------------------------------------------------

class AnnotateRequest(BaseModel):
    sequence: str = Field(..., min_length=10, description="Nucleotide or amino-acid sequence")
    sequence_type: str = Field(default="nucleotide", pattern="^(nucleotide|protein)$")
    context: Optional[str] = Field(default=None, description="Optional biological context hints")

class AnnotateResponse(BaseModel):
    suggestion: str
    evidence_type: str  # always "ai_suggested_hypothesis"
    model: str
    sequence_length: int
    tenant_id: str
    validation_required: bool


@router.post(
    "/ai-annotate",
    response_model=AnnotateResponse,
    summary="AI-Assisted Annotation (Gemini) — advisory only",
    description=(
        "Uses Google Gemini (free tier) to suggest a functional annotation hypothesis. "
        "Output is ALWAYS tagged `evidence_type=ai_suggested_hypothesis` and must be "
        "validated with BLAST/DIAMOND/HMMER before scientific use."
    ),
)
def ai_annotate(
    req: AnnotateRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_role(["admin", "bioinformatician", "analyst"])),
    db: Session = Depends(get_db),
):
    if not llm_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Gemini AI annotation is not available. "
                "Set GEMINI_API_KEY in .env and install google-generativeai."
            ),
        )
    try:
        result = llm_service.suggest_annotation(
            sequence=req.sequence,
            sequence_type=req.sequence_type,
            context=req.context,
            tenant_id=tenant_id,
        )
        audit = AuditLog(
            tenant_id=tenant_id,
            user_id=current_user.get("sub"),
            action="AI_ANNOTATE",
            resource_type="sequence",
            resource_id=req.sequence[:32],
            details=f"Gemini annotation requested ({req.sequence_type}, len={len(req.sequence)})",
        )
        db.add(audit)
        db.commit()
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI annotation error: {str(exc)}")
