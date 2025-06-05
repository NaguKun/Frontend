from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from app.core.supabase import get_supabase_client
from app.schemas.candidate import CandidateDetail
from app.services.search_service import SearchService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/semantic", response_model=List[CandidateDetail])
def semantic_search(
    query: str,
    min_experience_years: Optional[int] = Query(None, ge=0, description="Minimum years of experience required"),
    required_skills: Optional[List[str]] = Query(None, description="List of required skills"),
    location: Optional[str] = None,
    education_level: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    supabase=Depends(get_supabase_client)
):
    """
    Search candidates using semantic search with additional filters.
    
    - **query**: Search query text
    - **min_experience_years**: Minimum years of experience required
    - **required_skills**: List of required skills
    - **location**: Location filter
    - **education_level**: Education level filter
    - **limit**: Maximum number of results to return
    - **offset**: Number of results to skip
    """
    try:
        search_service = SearchService(supabase)
        results = search_service.semantic_search(
            query=query,
            min_experience_years=min_experience_years,
            required_skills=required_skills,
            location=location,
            education_level=education_level,
            limit=limit,
            offset=offset
        )
        return results
    except Exception as e:
        logger.error(f"Error performing semantic search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/filter", response_model=List[CandidateDetail])
def filter_candidates(
    min_experience_years: Optional[int] = Query(None, ge=0, description="Minimum years of experience required"),
    required_skills: Optional[List[str]] = Query(None, description="List of required skills"),
    location: Optional[str] = None,
    education_level: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    supabase=Depends(get_supabase_client)
):
    """
    Filter candidates based on various criteria.
    
    - **min_experience_years**: Minimum years of experience required
    - **required_skills**: List of required skills
    - **location**: Location filter
    - **education_level**: Education level filter
    - **limit**: Maximum number of results to return
    - **offset**: Number of results to skip
    """
    try:
        search_service = SearchService(supabase)
        results = search_service.filter_candidates(
            skills=required_skills,
            location=location,
            min_experience_years=min_experience_years,
            education_level=education_level,
            limit=limit,
            offset=offset
        )
        return results
    except Exception as e:
        logger.error(f"Error filtering candidates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Filtering failed: {str(e)}"
        )

@router.get("/skills", response_model=List[str])
def get_skills(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of skills to return"),
    supabase=Depends(get_supabase_client)
):
    """
    Get all available skills.
    
    - **limit**: Maximum number of skills to return
    """
    try:
        search_service = SearchService(supabase)
        return search_service.get_all_skills(limit=limit)
    except Exception as e:
        logger.error(f"Error getting skills: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get skills: {str(e)}"
        )

@router.get("/locations", response_model=List[str])
def get_locations(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of locations to return"),
    supabase=Depends(get_supabase_client)
):
    """
    Get all available locations.
    
    - **limit**: Maximum number of locations to return
    """
    try:
        search_service = SearchService(supabase)
        return search_service.get_all_locations(limit=limit)
    except Exception as e:
        logger.error(f"Error getting locations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get locations: {str(e)}"
        ) 