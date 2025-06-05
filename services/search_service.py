from typing import List, Optional, Tuple
from supabase import Client
from app.schemas.candidate import CandidateResponse, CandidateDetail
from app.services.embedding_service import generate_query_embeddings
import logging

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def semantic_search(
        self,
        query: str,
        min_experience_years: Optional[int] = None,
        required_skills: Optional[List[str]] = None,
        location: Optional[str] = None,
        education_level: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[CandidateDetail]:
        """
        Perform semantic search using vector similarity on experience and skills embeddings,
        with filters compatible with Supabase schema.
        """
        try:
            # Generate embeddings for the search query
            experience_embedding, skills_embedding = generate_query_embeddings(query)

            # Start with base query
            base_query = self.supabase.table('candidates') \
                .select('id, experience_embedding, skills_embedding')

            # Filter: location
            if location:
                base_query = base_query.ilike('location', f'%{location}%')

            # Filter: education_level (by degree field)
            if education_level:
                # Get candidate_ids with matching degree
                edu_res = self.supabase.table('education') \
                    .select('candidate_id') \
                    .eq('degree', education_level) \
                    .execute()
                edu_ids = [row['candidate_id'] for row in edu_res.data or []]
                if edu_ids:
                    base_query = base_query.in_('id', edu_ids)
                else:
                    return []  # No candidates match

            # Filter: required_skills (must have ALL skills)
            if required_skills:
                # Get skill_ids for required_skills
                skill_res = self.supabase.table('skills') \
                    .select('id, name') \
                    .in_('name', required_skills) \
                    .execute()
                skill_ids = [row['id'] for row in skill_res.data or []]
                if not skill_ids or len(skill_ids) < len(required_skills):
                    return []  # Some skills not found
                # Get candidate_ids that have all required skills
                cand_skill_res = self.supabase.table('candidate_skills') \
                    .select('candidate_id, skill_id') \
                    .in_('skill_id', skill_ids) \
                    .execute()
                # Count skills per candidate
                from collections import Counter
                cand_skill_pairs = [(row['candidate_id'], row['skill_id']) for row in cand_skill_res.data or []]
                cand_skill_count = Counter([pair[0] for pair in cand_skill_pairs])
                # Only candidates with all required skills
                candidate_ids = [cand_id for cand_id, count in cand_skill_count.items() if count == len(skill_ids)]
                if not candidate_ids:
                    return []
                base_query = base_query.in_('id', candidate_ids)

            # Filter: min_experience_years (sum years in work_experience)
            if min_experience_years:
                # Get candidate_ids with enough experience
                work_exp_res = self.supabase.table('work_experience') \
                    .select('candidate_id, start_date, end_date') \
                    .execute()
                from datetime import datetime
                from collections import defaultdict
                exp_years = defaultdict(float)
                now = datetime.now()
                for row in work_exp_res.data or []:
                    start = row.get('start_date')
                    end = row.get('end_date') or now.isoformat()
                    try:
                        start_dt = datetime.fromisoformat(str(start))
                        end_dt = datetime.fromisoformat(str(end))
                        years = (end_dt - start_dt).days / 365.25
                        exp_years[row['candidate_id']] += max(0, years)
                    except Exception:
                        continue
                qualified_ids = [cand_id for cand_id, years in exp_years.items() if years >= min_experience_years]
                if not qualified_ids:
                    return []
                base_query = base_query.in_('id', qualified_ids)

            # Pagination
            base_query = base_query.range(offset, offset + limit - 1)

            # Execute the query
            result = base_query.execute()
            if not result.data:
                return []

            # Calculate similarity scores and sort
            candidates_with_scores = []
            for candidate in result.data:
                if candidate['experience_embedding'] and candidate['skills_embedding']:
                    exp_similarity = self._cosine_similarity(
                        experience_embedding,
                        candidate['experience_embedding']
                    )
                    skills_similarity = self._cosine_similarity(
                        skills_embedding,
                        candidate['skills_embedding']
                    )
                    avg_similarity = (exp_similarity + skills_similarity) / 2
                    candidates_with_scores.append((candidate['id'], avg_similarity))

            # Sort by similarity score
            candidates_with_scores.sort(key=lambda x: x[1], reverse=True)

            # Get full candidate details (top N)
            candidate_ids = [c[0] for c in candidates_with_scores[:limit]]

            return self._get_candidates_by_ids(candidate_ids)
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            raise

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import numpy as np
            vec1 = np.array(vec1, dtype=float)
            vec2 = np.array(vec2, dtype=float)

            return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0

    def filter_candidates(
        self,
        skills: Optional[List[str]] = None,
        location: Optional[str] = None,
        min_experience_years: Optional[int] = None,
        education_level: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[CandidateDetail]:
        """
        Filter candidates based on specific criteria using traditional database queries
        """
        try:
            # Start with base query
            query = self.supabase.table('candidates')\
                .select('id')\
                .range(offset, offset + limit - 1)
            
            # Apply filters
            if location:
                query = query.ilike('location', f'%{location}%')
            
            if min_experience_years:
                # Filter by experience using a subquery
                query = query.filter(
                    'id',
                    'in',
                    self.supabase.table('work_experience')
                    .select('candidate_id')
                    .filter('end_date', 'is', 'null')
                    .or_('end_date.gt.now()')
                    .execute()
                    .data
                )
            
            if education_level:
                # Filter by education level
                query = query.filter(
                    'id',
                    'in',
                    self.supabase.table('education')
                    .select('candidate_id')
                    .eq('degree', education_level)
                    .execute()
                    .data
                )
            
            if skills:
                # Filter by skills
                query = query.filter(
                    'id',
                    'in',
                    self.supabase.table('candidate_skills')
                    .select('candidate_id')
                    .filter(
                        'skill_id',
                        'in',
                        self.supabase.table('skills')
                        .select('id')
                        .in_('name', skills)
                        .execute()
                        .data
                    )
                    .execute()
                    .data
                )
            
            # Execute the query
            result = query.execute()
            
            if not result.data:
                return []
            
            # Get full candidate details
            candidate_ids = [candidate['id'] for candidate in result.data]
            return self._get_candidates_by_ids(candidate_ids)
            
        except Exception as e:
            logger.error(f"Error in filter search: {str(e)}")
            raise

    def _get_candidates_by_ids(self, candidate_ids: List[int]) -> List[CandidateDetail]:
        """Get full candidate details for a list of candidate IDs"""
        try:
            if not candidate_ids:
                return []
                
            result = self.supabase.table('candidates')\
                .select('*, skills(*), education(*), work_experience(*), certifications(*), projects(*)')\
                .in_('id', candidate_ids)\
                .execute()
            
            return [CandidateDetail(**candidate) for candidate in result.data]
        except Exception as e:
            logger.error(f"Error getting candidates by IDs: {str(e)}")
            raise

    def get_all_skills(self, limit: int = 100) -> List[str]:
        """Get a list of all unique skills"""
        try:
            result = self.supabase.table('skills')\
                .select('name')\
                .order('name')\
                .limit(limit)\
                .execute()
            
            return [skill['name'] for skill in result.data]
        except Exception as e:
            logger.error(f"Error getting skills: {str(e)}")
            raise

    def get_all_locations(self, limit: int = 100) -> List[str]:
        """Get a list of all unique locations"""
        try:
            result = self.supabase.table('candidates')\
                .select('location')\
                .not_.is_('location', 'null')\
                .order('location')\
                .limit(limit)\
                .execute()
            
            # Get unique locations
            locations = set()
            for candidate in result.data:
                if candidate['location']:
                    locations.add(candidate['location'])
            
            return sorted(list(locations))
        except Exception as e:
            logger.error(f"Error getting locations: {str(e)}")
            raise 