from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from app.core.supabase import get_supabase_client
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateDetail
)
from app.services.candidate_service import CandidateService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=CandidateResponse)
def create_candidate(
    candidate: CandidateCreate,
    supabase=Depends(get_supabase_client)
):
    """
    Create a new candidate
    """
    try:
        candidate_service = CandidateService(supabase)
        return candidate_service.create_candidate(candidate)
    except Exception as e:
        logger.error(f"Error creating candidate: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create candidate: {str(e)}"
        )

@router.get("/", response_model=List[CandidateResponse])
def get_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    supabase=Depends(get_supabase_client)
):
    """
    Get all candidates with pagination
    """
    try:
        candidate_service = CandidateService(supabase)
        return candidate_service.get_candidates(skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error getting candidates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get candidates: {str(e)}"
        )

@router.get("/{candidate_id}", response_model=CandidateDetail)
def get_candidate(
    candidate_id: int,
    supabase=Depends(get_supabase_client)
):
    """
    Get a specific candidate by ID with all related data
    """
    try:
        candidate_service = CandidateService(supabase)
        candidate = candidate_service.get_candidate_by_id(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return candidate
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candidate {candidate_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get candidate: {str(e)}"
        )

@router.put("/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: int,
    candidate: CandidateUpdate,
    supabase=Depends(get_supabase_client)
):
    """
    Update a candidate's information
    """
    try:
        candidate_service = CandidateService(supabase)
        updated_candidate = candidate_service.update_candidate(candidate_id, candidate)
        if not updated_candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return updated_candidate
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating candidate {candidate_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update candidate: {str(e)}"
        )

@router.delete("/{candidate_id}")
def delete_candidate(
    candidate_id: int,
    supabase=Depends(get_supabase_client)
):
    """
    Delete a candidate and all related data
    """
    try:
        candidate_service = CandidateService(supabase)
        success = candidate_service.delete_candidate(candidate_id)
        if not success:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return {"message": "Candidate deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting candidate {candidate_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete candidate: {str(e)}"
        ) 