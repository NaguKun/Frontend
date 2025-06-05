import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from functools import lru_cache
from openai import OpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings
from app.schemas.candidate import (
    CandidateCreate,
    EducationCreate,
    WorkExperienceCreate,
    ProjectCreate,
    CertificationCreate
)

logger = logging.getLogger(__name__)

class InformationExtractor:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = self._initialize_embedding_model()
        self.output_parser = PydanticOutputParser(pydantic_object=CandidateCreate)
        self.system_prompt = self._create_system_prompt()
        self._embedding_cache = {}  # Simple in-memory cache for embeddings
    
    def _initialize_embedding_model(self) -> OpenAIEmbeddings:
        """Initialize the OpenAI embeddings model."""
        return OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def _create_system_prompt(self) -> str:
        """Create a highly detailed and strict system prompt for CV extraction."""
        return f"""You are an expert-level CV parser with deep expertise in recruitment, HR standards, and structured data extraction. 
        Your task is to convert unstructured CV/resume text into perfectly structured JSON that strictly complies with the following Pydantic schema.

        🔒 **STRICT COMPLIANCE REQUIRED**:
        1. ✅ **NEVER** omit required fields or return invalid formats
        2. 🧠 Use **intelligent inference** when data is implied but not explicit
        3. 📐 **Always** maintain schema validity - use placeholders when necessary

        ---
        📜 **SCHEMA REQUIREMENTS**:

        ### ROOT LEVEL (MANDATORY):
        - `full_name`: string (e.g., "Jane Doe")
        - `email`: valid email format (use "unknown@example.com" if missing)
        - `phone`: string (use "000-000-0000" if missing)
        - `location`: string (city/country preferred, "Unknown Location" if missing)

        ### EDUCATION (Array of objects):
        Each must contain:
        - `institution`: string (required)
        - `degree`: string (e.g., "Bachelor's in Computer Science")
        - `field_of_study`: string (required)
        - `start_date`: ISO date (YYYY-MM-DD, use "YYYY-01-01" if only year known)
        - `end_date`: ISO date or null if ongoing
        - `description`: string or null

        ### WORK EXPERIENCE (Array of objects):
        Each must contain:
        - `company`: string (use "Anonymous Corp" if unknown)
        - `position`: string (use "Unknown Role" if missing)
        - `start_date`: ISO date (required)
        - `end_date`: ISO date or null if current
        - `description`: string (required, summarize key responsibilities)
        - `achievements`: array of strings or null
        - `location`: string or null

        ### SKILLS (Array of strings):
        - Include both technical (e.g., "Python", "Docker") and soft skills (e.g., "Team Leadership")

        ### PROJECTS (Array of objects):
        Each must contain:
        - `name`: string (required)
        - `description`: string (required)
        - `start_date`: ISO date or null
        - `end_date`: ISO date or null
        - `technologies`: array of strings or null
        - `url`: valid HTTP URL or null

        ### CERTIFICATIONS (Array of objects):
        Each must contain:
        - `name`: string (required)
        - `issuer`: string (use "Unknown Issuer" if missing)
        - `issue_date`: ISO date (required)
        - `expiry_date`: ISO date or null
        - `credential_id`: string or null
        - `credential_url`: HTTP URL or null

        ---
        🛠 **PROCESSING RULES**:
        1. 📅 **Date Handling**:
        - Always use ISO format (YYYY-MM-DD)
        - Use "01-01" for unknown month/day (e.g., "2015-01-01")
        - For current positions: set `end_date` to null

        2. 🧠 **Inference Guidelines**:
        - Prioritize most recent 5 years of work experience
        - Infer dates from context when possible (e.g., "2015-2017" → "2015-01-01" to "2017-01-01")
        - Extract skills from project descriptions and work experience

        3. ⚠ **Error Prevention**:
        - Reject ambiguous data rather than guessing incorrectly
        - Use schema-compliant placeholders for missing required fields
        - Never return null for required fields

        4. 🔍 **Data Prioritization**:
        - Focus on recent and relevant experience
        - Include all certifications with verifiable details
        - Capture project technologies and methodologies

        ---
        📌 **OUTPUT REQUIREMENTS**:
        {self.output_parser.get_format_instructions()}

        🕒 **Context**:
        - Current Year: {datetime.now().year}
        - This output will be strictly validated against Pydantic models
        - Incomplete or invalid data will cause pipeline failures

        🚨 **Critical Reminder**: Your output must be 100% schema-compliant. When in doubt:
        1) Infer intelligently 2) Use placeholders 3) Never omit required fields
        """

    def _preprocess_text(self, text: str) -> str:
        """Preprocess CV text for better extraction."""
        text = ' '.join(text.split())
        text = text.replace('\x00', '')
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        return text.strip()
    
    def _split_long_text(self, text: str, max_length: int = 4000) -> List[str]:
        """Split long CV text into manageable chunks."""
        if len(text) <= max_length:
            return [text]
            
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_length,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        return splitter.split_text(text)
    
    def _extract_from_chunk(self, chunk: str) -> Dict[str, Any]:
        """Extract information from a single chunk of text."""
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": f"Here is the CV text to analyze:\n\n{chunk}\n\nPlease extract the information in the specified format. Remember to NEVER return null values for required fields. Make reasonable inferences if information is not explicitly stated."
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.1,
                max_tokens=4000
            )
            result_text = response.choices[0].message.content
            
            try:
                # First try to parse as is
                parsed_data = self.output_parser.parse(result_text)
                # Convert to dict immediately to avoid Pydantic model issues
                return parsed_data.model_dump() if hasattr(parsed_data, 'model_dump') else parsed_data
            except Exception as parse_error:
                logger.warning(f"Initial parse failed, attempting to clean and retry: {str(parse_error)}")
                
                # Try to clean the response and parse again
                cleaned_text = self._clean_llm_response(result_text)
                try:
                    parsed_data = self.output_parser.parse(cleaned_text)
                    # Convert to dict immediately to avoid Pydantic model issues
                    return parsed_data.model_dump() if hasattr(parsed_data, 'model_dump') else parsed_data
                except Exception as second_parse_error:
                    logger.error(f"Failed to parse even after cleaning: {str(second_parse_error)}")
                    raise ValueError(f"Failed to parse LLM response into valid CandidateCreate format: {str(second_parse_error)}")
                    
        except Exception as e:
            logger.error(f"Error processing chunk: {str(e)}")
            raise
    
    def _clean_llm_response(self, text: str) -> str:
        """Clean and normalize the LLM response for better parsing."""
        try:
            # Try to parse as JSON first
            data = json.loads(text)
            
            # Replace None/null values with empty strings for required string fields
            if isinstance(data, dict):
                for key in ['full_name', 'email', 'phone', 'location']:
                    if key in data and data[key] is None:
                        data[key] = ""
                
                # Handle education entries
                if 'education' in data and isinstance(data['education'], list):
                    for edu in data['education']:
                        for key in ['institution', 'degree', 'field_of_study']:
                            if key in edu and edu[key] is None:
                                edu[key] = ""
                
                # Handle work experience entries
                if 'work_experience' in data and isinstance(data['work_experience'], list):
                    for exp in data['work_experience']:
                        for key in ['company', 'position', 'description']:
                            if key in exp and exp[key] is None:
                                exp[key] = ""
                
                # Handle certification entries
                if 'certifications' in data and isinstance(data['certifications'], list):
                    for cert in data['certifications']:
                        for key in ['name', 'issuer']:
                            if key in cert and cert[key] is None:
                                cert[key] = ""
            
            return json.dumps(data)
        except json.JSONDecodeError:
            # If not valid JSON, return as is
            return text
    
    def _combine_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine and deduplicate results from multiple chunks."""
        if not results:
            raise ValueError("No results to combine")
            
        # First result is already a dict from _extract_from_chunk
        combined = results[0].copy() if isinstance(results[0], dict) else results[0].model_dump()
        
        for result in results[1:]:
            # Convert result to dict if it's a Pydantic model
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            
            # Merge education (avoid duplicates)
            combined["education"].extend([
                edu for edu in result_dict["education"]
                if edu not in combined["education"]
            ])
            
            # Merge work experience (avoid duplicates)
            combined["work_experience"].extend([
                exp for exp in result_dict["work_experience"]
                if exp not in combined["work_experience"]
            ])
            
            # Merge skills (avoid duplicates)
            combined["skills"] = list(set(combined["skills"] + result_dict["skills"]))
            
            # Merge projects (avoid duplicates)
            combined["projects"].extend([
                proj for proj in result_dict["projects"]
                if proj not in combined["projects"]
            ])
            
            # Merge certifications (avoid duplicates)
            combined["certifications"].extend([
                cert for cert in result_dict["certifications"]
                if cert not in combined["certifications"]
            ])
        
        # Convert HttpUrl objects to strings before returning
        def convert_httpurl_to_str(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    data[key] = convert_httpurl_to_str(value)
            elif isinstance(data, list):
                data = [convert_httpurl_to_str(item) for item in data]
            elif isinstance(data, object) and hasattr(data, '__class__') and data.__class__.__name__ == 'HttpUrl':
                return str(data)
            return data

        combined = convert_httpurl_to_str(combined)

        return combined
    
    def extract_information(self, cv_text: str) -> CandidateCreate:
        """
        Extract structured information from CV text using OpenAI.
        
        Args:
            cv_text: Raw text extracted from CV
            
        Returns:
            CandidateCreate: Structured candidate information
            
        Raises:
            Exception: If extraction fails
        """
        try:
            # Preprocess text
            cv_text = self._preprocess_text(cv_text)
            
            # Split text if too long
            text_chunks = self._split_long_text(cv_text)
            
            # Process each chunk
            all_results = []
            for chunk in text_chunks:
                result = self._extract_from_chunk(chunk)
                all_results.append(result)
            
            # Combine results
            candidate_dict = self._combine_results(all_results)
            
            # Remove any extra fields that aren't in CandidateCreate
            candidate_dict.pop('experience_embedding', None)
            candidate_dict.pop('skills_embedding', None)
            
            # Create final CandidateCreate instance
            return CandidateCreate(**candidate_dict)
            
        except Exception as e:
            logger.error(f"Error extracting information from CV: {str(e)}")
            raise

    @lru_cache(maxsize=100)
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text with caching."""
        # Clean and normalize text first
        text = ' '.join(text.split())
        if not text:
            return []
            
        try:
            return self.embedding_model.embed_query(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []

    def generate_embeddings(self, candidate: CandidateCreate, cv_text: str) -> dict:
        """
        Generate embeddings for a candidate profile with optimized processing.
        
        Args:
            candidate: The CandidateCreate object
            cv_text: The raw CV text
            
        Returns:
            dict: Dictionary containing the embeddings with at least 1 dimension
        """
        try:
            # Convert candidate to dict for processing
            candidate_dict = candidate.model_dump()
            
            # Generate experience embedding from work experience descriptions
            # Only use the most recent experiences to keep text length manageable
            recent_experiences = sorted(
                candidate_dict["work_experience"],
                key=lambda x: x.get('start_date', '1900-01-01'),
                reverse=True
            )[:3]  # Only use 3 most recent experiences
            
            experience_text = " ".join([
                f"{exp['position']} at {exp['company']}: {exp['description']}"
                for exp in recent_experiences
            ])
            
            # Generate skills embedding - limit to top skills to keep text length manageable
            skills_text = " ".join(candidate_dict["skills"][:20])  # Limit to top 20 skills
            
            # Get embeddings with caching
            experience_embedding = self._get_embedding(experience_text)
            skills_embedding = self._get_embedding(skills_text)
            
            # Ensure we have valid embeddings with at least 1 dimension
            # If empty or invalid, use a fallback embedding
            if not experience_embedding or len(experience_embedding) == 0:
                # Use a simple fallback embedding with 1536 dimensions (standard OpenAI embedding size)
                experience_embedding = [0.0] * 1536
                
            if not skills_embedding or len(skills_embedding) == 0:
                # Use a simple fallback embedding with 1536 dimensions
                skills_embedding = [0.0] * 1536
            
            return {
                "experience_embedding": experience_embedding,
                "skills_embedding": skills_embedding
            }
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            # Return fallback embeddings with 1536 dimensions in case of error
            return {
                "experience_embedding": [0.0] * 1536,
                "skills_embedding": [0.0] * 1536
            }