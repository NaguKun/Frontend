from typing import List, Optional, Dict, Any
from datetime import datetime
from supabase import Client
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateDetail,
    EducationCreate,
    WorkExperienceCreate,
    CertificationCreate,
    ProjectCreate,
    Skill
)
from app.services.embedding_service import generate_embeddings
import logging

logger = logging.getLogger(__name__)

class CandidateService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def create_candidate(self, candidate: CandidateCreate) -> CandidateResponse:
        """Create a new candidate with all related data"""
        try:
            # Insert candidate
            candidate_data = candidate.model_dump(exclude={'skills', 'education', 'work_experience', 'certifications', 'projects'})
            candidate_data['created_at'] = datetime.utcnow().isoformat()
            
            result = self.supabase.table('candidates').insert(candidate_data).execute()
            if not result.data:
                raise Exception("Failed to create candidate")
            
            candidate_id = result.data[0]['id']
            
            # Handle skills
            if candidate.skills:
                self._handle_skills(candidate_id, candidate.skills)
            
            # Handle education
            if candidate.education:
                self._handle_education(candidate_id, candidate.education)
            
            # Handle work experience
            if candidate.work_experience:
                self._handle_work_experience(candidate_id, candidate.work_experience)
            
            # Handle certifications
            if candidate.certifications:
                self._handle_certifications(candidate_id, candidate.certifications)
            
            # Handle projects
            if candidate.projects:
                self._handle_projects(candidate_id, candidate.projects)
            
            # Generate embeddings if CV text is available
            if candidate_data.get('cv_text'):
                self._generate_and_store_embeddings(candidate_id, candidate_data['cv_text'])
            
            # Return created candidate
            return self.get_candidate_by_id(candidate_id)
                
        except Exception as e:
            logger.error(f"Error creating candidate: {str(e)}")
            raise

    def get_candidates(self, skip: int = 0, limit: int = 10) -> List[CandidateResponse]:
        """Get a list of candidates with pagination"""
        try:
            result = self.supabase.table('candidates')\
                .select('*, skills(*)')\
                .range(skip, skip + limit - 1)\
                .execute()
            
            return [CandidateResponse(**candidate) for candidate in result.data]
        except Exception as e:
            logger.error(f"Error getting candidates: {str(e)}")
            raise

    def get_candidate_by_id(self, candidate_id: int) -> Optional[CandidateDetail]:
        """Get a candidate by ID with all related data"""
        try:
            result = self.supabase.table('candidates')\
                .select('*, skills(*), education(*), work_experience(*), certifications(*), projects(*)')\
                .eq('id', candidate_id)\
                .single()\
                .execute()
            
            if not result.data:
                return None
            
            return CandidateDetail(**result.data)
        except Exception as e:
            logger.error(f"Error getting candidate {candidate_id}: {str(e)}")
            raise

    def update_candidate(self, candidate_id: int, candidate: CandidateUpdate) -> Optional[CandidateResponse]:
        """Update a candidate's information"""
        try:
            # Update candidate
            update_data = candidate.model_dump(exclude_unset=True)
            if update_data:
                update_data['updated_at'] = datetime.utcnow().isoformat()
                
                result = self.supabase.table('candidates')\
                    .update(update_data)\
                    .eq('id', candidate_id)\
                    .execute()
                
                if not result.data:
                    return None
            
            # Handle skills update if provided
            if candidate.skills is not None:
                self._handle_skills(candidate_id, candidate.skills, replace=True)
            
            # Generate new embeddings if CV text was updated
            if candidate.cv_text:
                self._generate_and_store_embeddings(candidate_id, candidate.cv_text)
            
            # Return updated candidate
            return self.get_candidate_by_id(candidate_id)
                
        except Exception as e:
            logger.error(f"Error updating candidate {candidate_id}: {str(e)}")
            raise

    def delete_candidate(self, candidate_id: int) -> bool:
        """Delete a candidate and all related data"""
        try:
            # Delete related records first
            self.supabase.table('candidate_skills').delete().eq('candidate_id', candidate_id).execute()
            self.supabase.table('education').delete().eq('candidate_id', candidate_id).execute()
            self.supabase.table('work_experience').delete().eq('candidate_id', candidate_id).execute()
            self.supabase.table('certifications').delete().eq('candidate_id', candidate_id).execute()
            self.supabase.table('projects').delete().eq('candidate_id', candidate_id).execute()
            
            # Delete candidate
            result = self.supabase.table('candidates')\
                .delete()\
                .eq('id', candidate_id)\
                .execute()
            
            return bool(result.data)
                
        except Exception as e:
            logger.error(f"Error deleting candidate {candidate_id}: {str(e)}")
            raise

    def _handle_skills(self, candidate_id: int, skills: List[str], replace: bool = False) -> None:
        """Handle skill creation and association with candidate"""
        try:
            if replace:
                # Remove existing skills
                self.supabase.table('candidate_skills').delete().eq('candidate_id', candidate_id).execute()
            
            # Get or create skills
            skill_ids = []
            for skill_name in skills:
                # Try to get existing skill
                result = self.supabase.table('skills')\
                    .select('id')\
                    .eq('name', skill_name)\
                    .single()\
                    .execute()
                
                if result.data:
                    skill_ids.append(result.data['id'])
                else:
                    # Create new skill
                    result = self.supabase.table('skills')\
                        .insert({'name': skill_name})\
                        .execute()
                    skill_ids.append(result.data[0]['id'])
            
            # Associate skills with candidate
            for skill_id in skill_ids:
                self.supabase.table('candidate_skills')\
                    .insert({'candidate_id': candidate_id, 'skill_id': skill_id})\
                    .execute()
                    
        except Exception as e:
            logger.error(f"Error handling skills for candidate {candidate_id}: {str(e)}")
            raise

    def _handle_education(self, candidate_id: int, education: List[EducationCreate]) -> None:
        """Handle education records creation"""
        try:
            for edu in education:
                edu_data = edu.model_dump()
                edu_data['candidate_id'] = candidate_id
                self.supabase.table('education').insert(edu_data).execute()
        except Exception as e:
            logger.error(f"Error handling education for candidate {candidate_id}: {str(e)}")
            raise

    def _handle_work_experience(self, candidate_id: int, experience: List[WorkExperienceCreate]) -> None:
        """Handle work experience records creation"""
        try:
            for exp in experience:
                exp_data = exp.model_dump()
                exp_data['candidate_id'] = candidate_id
                self.supabase.table('work_experience').insert(exp_data).execute()
        except Exception as e:
            logger.error(f"Error handling work experience for candidate {candidate_id}: {str(e)}")
            raise

    def _handle_certifications(self, candidate_id: int, certifications: List[CertificationCreate]) -> None:
        """Handle certification records creation"""
        try:
            for cert in certifications:
                cert_data = cert.model_dump()
                cert_data['candidate_id'] = candidate_id
                self.supabase.table('certifications').insert(cert_data).execute()
        except Exception as e:
            logger.error(f"Error handling certifications for candidate {candidate_id}: {str(e)}")
            raise

    def _handle_projects(self, candidate_id: int, projects: List[ProjectCreate]) -> None:
        """Handle project records creation"""
        try:
            for project in projects:
                project_data = project.model_dump()
                project_data['candidate_id'] = candidate_id
                self.supabase.table('projects').insert(project_data).execute()
        except Exception as e:
            logger.error(f"Error handling projects for candidate {candidate_id}: {str(e)}")
            raise

    def _generate_and_store_embeddings(self, candidate_id: int, cv_text: str) -> None:
        """Generate and store embeddings for candidate's CV"""
        try:
            # Generate embeddings
            experience_embedding, skills_embedding = generate_embeddings(cv_text)
            
            # Update candidate with embeddings
            self.supabase.table('candidates')\
                .update({
                    'experience_embedding': experience_embedding,
                    'skills_embedding': skills_embedding
                })\
                .eq('id', candidate_id)\
                .execute()
                
        except Exception as e:
            logger.error(f"Error generating embeddings for candidate {candidate_id}: {str(e)}")
            raise 