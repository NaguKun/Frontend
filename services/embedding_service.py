from typing import Tuple, List
from openai import OpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_embeddings(text: str) -> Tuple[List[float], List[float]]:
    """
    Generate experience and skills embeddings for a candidate's CV text.
    Returns a tuple of (experience_embedding, skills_embedding).
    """
    try:
        # Split the text into experience and skills sections
        # This is a simple implementation - you might want to use more sophisticated text analysis
        experience_text = _extract_experience_text(text)
        skills_text = _extract_skills_text(text)
        
        # Generate embeddings for both sections
        experience_embedding = _get_embedding(experience_text)
        skills_embedding = _get_embedding(skills_text)
        
        return experience_embedding, skills_embedding
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise

def generate_query_embeddings(query: str) -> Tuple[List[float], List[float]]:
    """
    Generate embeddings for a search query, optimized for both experience and skills matching.
    Returns a tuple of (experience_embedding, skills_embedding).
    """
    try:
        # For queries, we use the same text for both embeddings but with different prompts
        experience_prompt = f"Find candidates with experience in: {query}"
        skills_prompt = f"Find candidates with skills in: {query}"
        
        # Generate embeddings for both aspects
        experience_embedding = _get_embedding(experience_prompt)
        skills_embedding = _get_embedding(skills_prompt)
        
        return experience_embedding, skills_embedding
        
    except Exception as e:
        logger.error(f"Error generating query embeddings: {str(e)}")
        raise

def _get_embedding(text: str) -> List[float]:
    """Get embeddings for a text using OpenAI's API"""
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error getting embedding from OpenAI: {str(e)}")
        raise

def _extract_experience_text(text: str) -> str:
    """
    Extract the experience-related text from the CV.
    This is a simple implementation - you might want to use more sophisticated text analysis.
    """
    # Look for common experience-related keywords
    experience_keywords = [
        "experience", "work", "employment", "job", "position",
        "responsibilities", "achievements", "duties", "role"
    ]
    
    # Split text into sentences
    sentences = text.split('.')
    
    # Filter sentences that contain experience-related keywords
    experience_sentences = [
        sentence for sentence in sentences
        if any(keyword in sentence.lower() for keyword in experience_keywords)
    ]
    
    return ' '.join(experience_sentences)

def _extract_skills_text(text: str) -> str:
    """
    Extract the skills-related text from the CV.
    This is a simple implementation - you might want to use more sophisticated text analysis.
    """
    # Look for common skills-related keywords
    skills_keywords = [
        "skills", "technologies", "tools", "languages", "frameworks",
        "proficient", "expertise", "knowledge", "abilities", "competencies"
    ]
    
    # Split text into sentences
    sentences = text.split('.')
    
    # Filter sentences that contain skills-related keywords
    skills_sentences = [
        sentence for sentence in sentences
        if any(keyword in sentence.lower() for keyword in skills_keywords)
    ]
    
    return ' '.join(skills_sentences) 