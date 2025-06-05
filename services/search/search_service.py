from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.models import Candidate, Skill
from app.core.config import settings
from app.services.llm.extractor import InformationExtractor
import logging
import numpy as np

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.extractor = InformationExtractor()
    
    async def semantic_search(
        self,
        query: str,
        min_experience_years: Optional[int] = None,
        required_skills: Optional[List[str]] = None,
        location: Optional[str] = None,
        education_level: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Candidate]:
        """
        Perform semantic search on candidates using vector similarity.
        
        Args:
            query: Search query text
            min_experience_years: Minimum years of experience required
            required_skills: List of required skills
            location: Location filter
            education_level: Minimum education level required
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching candidates
        """
        try:
            # Generate query embedding
            query_embedding = self.extractor.embedding_model.embed_query(query)
            
            # Build base query
            base_query = self.db.query(Candidate)
            
            # Apply filters
            if min_experience_years:
                base_query = self._filter_by_experience(base_query, min_experience_years)
            
            if required_skills:
                base_query = self._filter_by_skills(base_query, required_skills)
            
            if location:
                base_query = base_query.filter(
                    func.lower(Candidate.location).contains(func.lower(location))
                )
            
            if education_level:
                base_query = self._filter_by_education(base_query, education_level)
            
            # Perform vector similarity search
            # Using cosine similarity for both experience and skills
            candidates = base_query.order_by(
                func.cosine_similarity(
                    Candidate.experience_embedding,
                    query_embedding
                ).desc(),
                func.cosine_similarity(
                    Candidate.skills_embedding,
                    query_embedding
                ).desc()
            ).offset(offset).limit(limit).all()
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            raise
    
    async def filter_candidates(
        self,
        skills: Optional[List[str]] = None,
        location: Optional[str] = None,
        min_experience_years: Optional[int] = None,
        education_level: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Candidate]:
        """
        Filter candidates using traditional database queries.
        
        Args:
            skills: List of required skills
            location: Location filter
            min_experience_years: Minimum years of experience required
            education_level: Minimum education level required
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching candidates
        """
        try:
            # Build base query
            query = self.db.query(Candidate)
            
            # Apply filters
            if skills:
                query = self._filter_by_skills(query, skills)
            
            if location:
                query = query.filter(
                    func.lower(Candidate.location).contains(func.lower(location))
                )
            
            if min_experience_years:
                query = self._filter_by_experience(query, min_experience_years)
            
            if education_level:
                query = self._filter_by_education(query, education_level)
            
            # Execute query
            candidates = query.offset(offset).limit(limit).all()
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error in filter search: {str(e)}")
            raise
    
    def _filter_by_experience(self, query, min_years: int):
        """Filter candidates by minimum years of experience."""
        min_date = datetime.now() - timedelta(days=365 * min_years)
        return query.filter(
            Candidate.work_experience.any(
                and_(
                    Candidate.work_experience.start_date <= min_date,
                    or_(
                        Candidate.work_experience.end_date >= min_date,
                        Candidate.work_experience.end_date == None
                    )
                )
            )
        )
    
    def _filter_by_skills(self, query, skills: List[str]):
        """Filter candidates by required skills."""
        return query.filter(
            Candidate.skills.any(
                Skill.name.in_([skill.lower() for skill in skills])
            )
        )
    
    def _filter_by_education(self, query, education_level: str):
        """Filter candidates by education level."""
        education_levels = {
            "high_school": ["high school", "secondary"],
            "bachelor": ["bachelor", "bsc", "ba", "undergraduate"],
            "master": ["master", "msc", "ma", "graduate"],
            "phd": ["phd", "doctorate", "doctoral"]
        }
        
        if education_level not in education_levels:
            raise ValueError(f"Invalid education level: {education_level}")
        
        # Get all levels up to and including the required level
        required_levels = []
        for level, keywords in education_levels.items():
            required_levels.extend(keywords)
            if level == education_level:
                break
        
        return query.filter(
            Candidate.education.any(
                or_(
                    *[
                        func.lower(Candidate.education.degree).contains(keyword.lower())
                        for keyword in required_levels
                    ]
                )
            )
        )
    
    async def get_all_skills(self, limit: int = 100) -> List[str]:
        """Get all unique skills in the database."""
        try:
            skills = self.db.query(Skill.name).distinct().limit(limit).all()
            return [skill[0] for skill in skills]
        except Exception as e:
            logger.error(f"Error getting skills: {str(e)}")
            raise
    
    async def get_all_locations(self, limit: int = 100) -> List[str]:
        """Get all unique locations in the database."""
        try:
            locations = self.db.query(Candidate.location).distinct().filter(
                Candidate.location != None
            ).limit(limit).all()
            return [loc[0] for loc in locations if loc[0]]
        except Exception as e:
            logger.error(f"Error getting locations: {str(e)}")
            raise 